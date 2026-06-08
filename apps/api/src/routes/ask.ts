import type { FastifyInstance } from "fastify";
import { aiClient } from "../clients/ai.js";
import { prisma } from "../lib/prisma.js";

export async function askRoutes(app: FastifyInstance) {
  app.post("/ask", async (request) => {
    const body = request.body as {
      question: string;
      session_id?: string;
      telegramId?: string;
    };

    let sessionId = body.session_id;

    if (!sessionId && body.telegramId) {
      const state = await prisma.userState.findUnique({
        where: { telegramId: body.telegramId },
      });

      sessionId = state?.activeSessionId ?? undefined;
    }

    if (!sessionId) {
      throw new Error("No active session");
    }

    await prisma.message.create({
      data: {
        sessionId,
        role: "user",
        content: body.question,
      },
    });

    const history = await prisma.message.findMany({
      where: { sessionId },
      orderBy: { createdAt: "desc" },
      take: 10,
    });

    history.reverse();

    let aiResponse;

    try {
      aiResponse = await aiClient.post("/query", {
        question: body.question,
        session_id: sessionId,
        history,
      });
    } catch (err) {
      console.error("AI QUERY FAILED:", err);
      throw new Error("AI service unavailable");
    }

    await prisma.message.create({
      data: {
        sessionId,
        role: "assistant",
        content: aiResponse.data.answer,
      },
    });

    return aiResponse.data;
  });
}
