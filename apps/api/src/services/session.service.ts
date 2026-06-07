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
  const session = await prisma.session.findFirst({
    where: {
      id: sessionId,
      telegramId,
    },
  });

  if (!session) {
    throw new Error("Session not found");
  }

  await prisma.session.delete({
    where: {
      id: sessionId,
    },
  });

  return {
    success: true,
  };
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
