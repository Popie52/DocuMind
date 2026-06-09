import { prisma } from "../lib/prisma.js";

export async function createSession(telegramId: string, name: string) {
  await prisma.session.updateMany({
    where: {
      telegramId,
    },
    data: {
      isActive: false,
    },
  });

  const session = await prisma.session.create({
    data: {
      telegramId,
      name,
      isActive: true,
    },
  });

  await prisma.userState.upsert({
    where: {
      telegramId,
    },
    update: {
      activeSessionId: session.id,
    },
    create: {
      telegramId,
      activeSessionId: session.id,
    },
  });

  return session;
}

export async function getActiveSession(telegramId: string) {
  const state = await prisma.userState.findUnique({
    where: {
      telegramId,
    },
    include: {
      session: true,
    },
  });

  return state?.session ?? null;
}

export async function listSessions(telegramId: string) {
  return prisma.session.findMany({
    where: {
      telegramId,
    },
    orderBy: {
      createdAt: "desc",
    },
  });
}

export async function switchSession(telegramId: string, sessionId: string) {
  const session = await prisma.session.findFirst({
    where: {
      id: sessionId,
      telegramId,
    },
  });

  if (!session) {
    throw new Error("Session not found");
  }

  await prisma.session.updateMany({
    where: {
      telegramId,
    },
    data: {
      isActive: false,
    },
  });

  await prisma.session.update({
    where: {
      id: sessionId,
    },
    data: {
      isActive: true,
    },
  });

  await prisma.userState.upsert({
    where: {
      telegramId,
    },
    update: {
      activeSessionId: sessionId,
    },
    create: {
      telegramId,
      activeSessionId: sessionId,
    },
  });

  return session;
}

export async function deleteSession(telegramId: string, sessionId: string) {
  const allSessions = await prisma.session.findMany({
    where: { telegramId },
    orderBy: {
      createdAt: "desc",
    },
  });

  if (allSessions.length === 1) {
    throw new Error("Cannot delete last session");
  }

  const session = allSessions.find(s => s.id === sessionId);
  if (!session) {
    throw new Error("Session not found");
  }

  const state = await prisma.userState.findUnique({
    where: { telegramId },
  });

  const isActive = state?.activeSessionId === sessionId;

  await prisma.$transaction([
    prisma.message.deleteMany({
      where: { sessionId },
    }),
    prisma.document.deleteMany({
      where: { sessionId },
    }),
    prisma.session.delete({
      where: { id: sessionId },
    }),
  ]);

  if (isActive) {
    const nextSession = await prisma.session.findFirst({
      where: {
        telegramId,
        NOT: {
          id: sessionId,
        },
      },
      orderBy: {
        createdAt: "desc",
      },
    });

    if (nextSession) {
      await prisma.session.update({
        where: {
          id: nextSession.id,
        },
        data: {
          isActive: true,
        },
      });

      await prisma.userState.update({
        where: {
          telegramId,
        },
        data: {
          activeSessionId: nextSession.id,
        },
      });
    }
  }

  return { success: true };
}

export async function clearSessionMessages(sessionId: string) {
  return prisma.message.deleteMany({
    where: { sessionId },
  });
}

export async function getSessionStatus(sessionId: string) {
  return prisma.document.findMany({
    where: { sessionId },
    select: {
      filename: true,
      status: true,
    },
    orderBy: {
      uploadedAt: "desc",
    },
  });
}
