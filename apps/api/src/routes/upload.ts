import type { FastifyPluginAsync } from "fastify";
import { prisma } from "../lib/prisma.js";
import fs from "fs";
import path from "path";
import FormData from "form-data";
import { aiClient } from "../clients/ai.js";

export const uploadRoutes: FastifyPluginAsync = async (app) => {
  app.post("/upload", async (req, res) => {
    const data = await req.file();

    if (!data) {
      return res.status(400).send({ error: "No file uploaded" });
    }

    const uploadDir = path.join(process.cwd(), "uploads");

    await fs.promises.mkdir(uploadDir, {
      recursive: true,
    });

    const filePath = path.join(uploadDir, data.filename);

    const buffer = await data.toBuffer();

    await fs.promises.writeFile(filePath, buffer);

    const document = await prisma.document.create({
      data: {
        filename: data.filename,
        originalName: data.filename,
      },
    });

    const form = new FormData();

    form.append("document_id", document.id);

    form.append("file", fs.createReadStream(filePath));

    const aiResponse = await aiClient.post("/parse", form, {
      headers: form.getHeaders(),
    });

    return {
      success: true,
      document,
      ai: aiResponse.data,
    };
  });
};
