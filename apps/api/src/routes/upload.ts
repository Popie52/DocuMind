import type { FastifyPluginAsync } from "fastify";
import { prisma } from "../lib/prisma.js";
import fs from "node:fs";
import path from "node:path";
import FormData from "form-data";
import { aiClient } from "../clients/ai.js";

export const uploadRoutes: FastifyPluginAsync = async (app) => {
  app.post("/upload", async (req, res) => {
    const parts = req.parts();

    let telegramId: string | undefined;
    let file: any;

    for await (const part of parts) {
      if (part.type === "file") {
        file = part;
        continue;
      }

      if (part.fieldname === "telegramId") {
        telegramId = part.value as string;
      }
    }

    if (!file) {
      return res.status(400).send({ error: "No file uploaded" });
    }

    if (!telegramId) {
      return res.status(400).send({ error: "telegramId is required" });
    }

    const userState = await prisma.userState.findUnique({
      where: { telegramId },
    });

    if (!userState?.activeSessionId) {
      return res.status(400).send({ error: "No active session found" });
    }

    const uploadDir = path.join(process.cwd(), "uploads");

    await fs.promises.mkdir(uploadDir, { recursive: true });

    const document = await prisma.document.create({
      data: {
        filename: file.filename,
        originalName: file.filename,
        sessionId: userState.activeSessionId,
        status: "INDEXING",
      },
    });

    const filePath = path.join(uploadDir, `${document.id}-${file.filename}`);
    let finalStatus = "FAILED";

    try {
      const buffer = await file.toBuffer();
      await fs.promises.writeFile(filePath, buffer);

      const form = new FormData();

      form.append("document_id", document.id);
      form.append("session_id", userState.activeSessionId);
      form.append("file", fs.createReadStream(filePath));

      const aiResponse = await aiClient.post("/parse", form, {
        headers: form.getHeaders(),
      });

      finalStatus = "READY";

      return {
        success: true,
        document,
        ai: aiResponse.data,
      };
    } finally {
      try {
        await prisma.document.update({
          where: { id: document.id },
          data: { status: finalStatus },
        });
      } catch (updateError) {
        console.error("Failed to finalize document status:", updateError);
      }

      if (filePath) {
        try {
          await fs.promises.unlink(filePath);
        } catch (cleanupError) {
          console.warn("Failed to delete temporary upload file:", cleanupError);
        }
      }
    }
  });
};
