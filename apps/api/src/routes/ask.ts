import type { FastifyInstance } from "fastify";
import { aiClient } from "../clients/ai.js";

export async function askRoutes(app: FastifyInstance) {
  app.post("/ask", async (request) => {
    const body = request.body as {
      question: string;
    };

    const response = await aiClient.post("/query", {
      question: body.question,
    });
    return response.data;
  });
}
