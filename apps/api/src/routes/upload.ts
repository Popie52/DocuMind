import type { FastifyPluginAsync } from "fastify";
import { prisma } from "../lib/prisma.js";

export const uploadRoutes: FastifyPluginAsync = async (app) => {
  app.get("/upload", async () => {
    return { message: "list uploads" };
  });
  
  app.post("/upload", async (req, res) => {
    const data = await req.file();

    if (!data) {
      return res.status(400).send({ error: "No file uploaded" });
    }

    const document = await prisma.document.create({
      data: {
        filename: data.filename,
        originalName: data.filename,
      },
    });

    return {
      success: true,
      document,
    };
  });
};
