import type { FastifyPluginAsync } from "fastify";
import { prisma } from "../lib/prisma.js";
import fs from "node:fs";
import path from "node:path";
import FormData from "form-data";
import { aiClient } from "../clients/ai.js";
import crypto from "node:crypto";

export const uploadRoutes: FastifyPluginAsync = async (app) => {
  app.post("/upload", async (req, res) => {
    const reqId =
      (req.headers["x-request-id"] as string) || crypto.randomUUID();

    console.log(`[API][${reqId}] /upload started`);

    try {
      console.log(`[API] [${reqId}] STEP 1`);
      const parts = req.parts();
      console.log(`[API] [${reqId}] STEP 2`);
      
      let telegramId: string | undefined;
      let filename = "";
      let fileBuffer: Buffer | undefined;

      for await (const part of parts) {
        console.log(`[API] [${reqId}] PART:`, part.fieldname, part.type);
        if (part.type === "file") {
          console.log(`[API] [${reqId}] FILE FOUND`);
          filename = part.filename;
          fileBuffer = await part.toBuffer();
          continue;
        } else if (part.fieldname === "telegramId") {
          console.log(`[API] [${reqId}] TG FOUND`);
          telegramId = part.value as string;
        }
      }
      console.log(`[API] [${reqId}] STEP 3`);

      // ✅ FIX: enforce string (removes string | null error)
      if (typeof telegramId !== "string" || !telegramId.trim()) {
        return res.status(400).send({ error: "telegramId is required" });
      }

      if (!fileBuffer) {
        return res.status(400).send({ error: "file is required" });
      }

      const userState = await prisma.userState.findUnique({
        where: { telegramId },
      });

      if (!userState?.activeSessionId) {
        return res.status(400).send({ error: "No active session found" });
      }

      const sessionId = userState.activeSessionId;

      const document = await prisma.document.create({
        data: {
          filename: filename,
          originalName: filename,
          sessionId,
          status: "INDEXING",
        },
      });

      const uploadDir = path.join(process.cwd(), "uploads");
      await fs.promises.mkdir(uploadDir, { recursive: true });

      const filePath = path.join(uploadDir, `${document.id}-${filename}`);

      try {
        await fs.promises.writeFile(filePath, fileBuffer);

        console.log(`[API][${reqId}] file saved (${fileBuffer.length} bytes)`);

        const form = new FormData();
        form.append("document_id", document.id);
        form.append("session_id", sessionId);
        form.append("file", fs.createReadStream(filePath));

        console.log(`[API][${reqId}] calling AI /parse`);

        const aiResponse = await aiClient.post("/parse", form, {
          headers: form.getHeaders(),
          timeout: 10 * 60 * 1000,
          maxBodyLength: Infinity,
          maxContentLength: Infinity,
        });

        await prisma.document.update({
          where: { id: document.id },
          data: { status: "READY" },
        });

        console.log(`[API][${reqId}] upload complete`);

        return res.send({
          success: true,
          documentId: document.id,
          status: "READY",
          ai: aiResponse.data,
        });
      } catch (err: any) {
        console.error(`[API][${reqId}] upload failed`, err);

        await prisma.document.update({
          where: { id: document.id },
          data: { status: "FAILED" },
        });

        return res.status(500).send({
          success: false,
          error: err?.message || "Upload failed",
        });
      } finally {
        try {
          await fs.promises.unlink(filePath);
        } catch {}
      }
    } catch (outerErr: any) {
      console.error(`[API] fatal upload error`, outerErr);

      return res.status(500).send({ error: "Internal Server Error" });
    }
  });
};
