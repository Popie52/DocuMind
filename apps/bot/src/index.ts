import { Bot } from "grammy";
import dotenv from "dotenv";
import axios from "axios";
import FormData from "form-data";
import { api } from "./services/api.js";

dotenv.config();

const token = process.env.TELEGRAM_BOT_TOKEN;

if (!token) {
  throw new Error("TELEGRAM_BOT_TOKEN missing");
}

const bot = new Bot(token);

/**
 * helper → detect commands
 */
function isCommand(text: string) {
  return text.startsWith("/");
}

/**
 * START
 */
bot.command("start", async (ctx) => {
  await ctx.reply("Telegram RAG Agent is running");
});

function getDisplayName(ctx: any) {
  return (
    [ctx.from?.first_name, ctx.from?.last_name]
      .filter(Boolean)
      .join(" ")
      .trim() || "Telegram user"
  );
}

async function resolveSessionId(telegramId: string, displayName: string) {
  const activeResponse = await api.get("/sessions/active", {
    params: {
      telegramId,
    },
  });

  if (activeResponse.data?.id) {
    return activeResponse.data.id;
  }

  const createResponse = await api.post("/sessions", {
    telegramId,
    name: displayName,
  });

  return createResponse.data.id;
}

/**
 * CHAT (RAG)
 */
bot.on("message:text", async (ctx) => {
  const text = ctx.message?.text;
  const chatId = ctx.chat?.id;

  if (!text || !chatId) return;

  // ignore commands
  if (isCommand(text)) return;

  try {
    const telegramId = String(chatId);
    const sessionId = await resolveSessionId(telegramId, getDisplayName(ctx));

    const response = await api.post("/ask", {
      question: text,
      session_id: sessionId,
      telegramId,
    });

    const answer = response.data.answer;
    const citations = response.data.citations || [];

    let citationText = "";

    if (citations.length > 0) {
      citationText = "\n\nSources:\n";

      for (const citation of citations) {
        citationText += `- ${citation.filename} (page ${citation.page})\n`;
      }
    }

    await ctx.reply(`${answer}${citationText}`);
  } catch (error) {
    console.error("ASK ERROR:", error);
    await ctx.reply("API Unavailable");
  }
});

/**
 * PDF UPLOAD
 */
bot.on("message:document", async (ctx) => {
  const document = ctx.message?.document;
  const chatId = ctx.chat?.id;

  if (!document || !chatId) return;

  try {
    if (document.mime_type !== "application/pdf") {
      return ctx.reply("Only PDF files are supported");
    }

    const file = await ctx.getFile();

    const fileUrl = `https://api.telegram.org/file/bot${token}/${file.file_path}`;

    const filename = document.file_name || `file-${Date.now()}.pdf`;

    const response = await axios.get(fileUrl, {
      responseType: "arraybuffer",
    });

    const telegramId = String(chatId);
    const sessionId = await resolveSessionId(telegramId, getDisplayName(ctx));

    const form = new FormData();

    form.append("file", Buffer.from(response.data), {
      filename,
    });
    form.append("telegramId", telegramId);
    form.append("session_id", sessionId);

    await api.post("/upload", form, {
      headers: form.getHeaders(),
      maxBodyLength: Infinity,
      maxContentLength: Infinity,
    });

    await ctx.reply("PDF uploaded and indexed.");
  } catch (error) {
    console.error("UPLOAD ERROR:", error);
    await ctx.reply("Failed to upload PDF.");
  }
});

/**
 * COMMAND 1 — /new
 */
bot.command("new", async (ctx) => {
  const text = ctx.message?.text;
  const chatId = ctx.chat?.id;

  if (!text || !chatId) return;

  const name = text.replace("/new", "").trim();

  if (!name) {
    return ctx.reply("Usage: /new <session-name>");
  }

  try {
    await api.post("/sessions", {
      telegramId: String(chatId),
      name,
    });

    await ctx.reply(`Session "${name}" created and activated.`);
  } catch (error) {
    console.error("NEW ERROR:", error);
    await ctx.reply("Failed to create session.");
  }
});

/**
 * COMMAND 2 — /list
 */
bot.command("list", async (ctx) => {
  const chatId = ctx.chat?.id;
  if (!chatId) return;

  try {
    const response = await api.get("/sessions", {
      params: {
        telegramId: String(chatId),
      },
    });

    const sessions = response.data;

    if (!sessions || sessions.length === 0) {
      return ctx.reply("No sessions found.");
    }

    let message = "Sessions:\n\n";

    sessions.forEach((session: any, index: number) => {
      message += `${index + 1}. ${session.name}`;
      if (session.isActive) message += " (active)";
      message += "\n";
    });

    await ctx.reply(message);
  } catch (error) {
    console.error("LIST ERROR:", error);
    await ctx.reply("Failed to fetch sessions.");
  }
});

/**
 * COMMAND 3 — /current
 */
bot.command("current", async (ctx) => {
  const chatId = ctx.chat?.id;
  if (!chatId) return;

  try {
    const response = await api.get("/sessions/active", {
      params: {
        telegramId: String(chatId),
      },
    });

    const session = response.data;

    if (!session) {
      return ctx.reply("No active session.");
    }

    await ctx.reply(`Current session: ${session.name}`);
  } catch (error) {
    console.error("CURRENT ERROR:", error);
    await ctx.reply("Failed to fetch active session.");
  }
});

/**
 * START BOT
 */
bot.start();

console.log("Telegram bot is running");
