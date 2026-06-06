import type { FastifyPluginAsync } from "fastify";
import {
  createSession,
  deleteSession,
  getActiveSession,
  listSessions,
  switchSession,
} from "../services/session.service.js";

export const sessionRoutes: FastifyPluginAsync = async (app) => {
  app.get("/sessions", async (req) => {
    const query = req.query as {
      telegramId: string;
    };

    return listSessions(query.telegramId);
  });

  app.get("/sessions/active", async (req) => {
    const query = req.query as {
      telegramId: string;
    };

    return getActiveSession(query.telegramId);
  });

  app.post("/sessions", async (req) => {
    const body = req.body as {
      telegramId: string;
      name: string;
    };

    return createSession(body.telegramId, body.name);
  });

  app.patch("/sessions/:id/activate", async (req) => {
    const params = req.params as {
      id: string;
    };

    const body = req.body as {
      telegramId: string;
    };

    return switchSession(body.telegramId, params.id);
  });

  app.delete("/sessions/:id", async (req) => {
    const params = req.params as {
      id: string;
    };

    const body = req.body as {
      telegramId: string;
    };

    return deleteSession(body.telegramId, params.id);
  });
};
