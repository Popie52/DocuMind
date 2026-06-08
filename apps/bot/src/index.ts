import { Bot } from "grammy";
import dotenv from "dotenv";
import axios from "axios";
import FormData from "form-data";
import { api } from "./services/api.js";
import crypto from "node:crypto";

dotenv.config();

const token = process.env.TELEGRAM_BOT_TOKEN;

if (!token) {
  throw new Error("TELEGRAM_BOT_TOKEN missing");
}

const bot = new Bot(token);

// Axios Global Error Logging for API Client
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error(`[AXIOS ERROR] ${error.config?.method?.toUpperCase()} ${error.config?.url} failed:`, error.message);
    if (error.response) {
      console.error("[AXIOS ERROR DATA]:", error.response.data);
    }
    return Promise.reject(error);
  }
);

/**
 * helper → detect commands
 */
function isCommand(text?: string) {
  return !!text && text.startsWith("/");
}

/**
 * START
 */
bot.command("start", async (ctx) => {
  await ctx.reply("Telegram RAG Agent is running");
});

/**
 * helper → user name
 */
function getDisplayName(ctx: any) {
  return (
    [ctx.from?.first_name, ctx.from?.last_name]
      .filter(Boolean)
      .join(" ")
      .trim() || "Telegram user"
  );
}

/**
 * session resolver
 */
async function resolveSessionId(telegramId: string, displayName: string) {
  const activeResponse = await api.get("/sessions/active", {
    params: { telegramId },
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
bot.on("message:text", async (ctx, next) => {
  const text = ctx.message?.text;

  if (!text) return;
  if (text.startsWith("/")) return next();

  try {
    const telegramId = String(ctx.chat.id);
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
  if (!document) return;

  const reqId = crypto.randomUUID();
  const startTime = Date.now();

  try {
    console.log(`\n[BOT] [${reqId}] PDF received`);
    
    if (document.mime_type !== "application/pdf") {
      return ctx.reply("Only PDF files are supported");
    }

    const file = await ctx.getFile();
    const fileUrl = `https://api.telegram.org/file/bot${token}/${file.file_path}`;
    const filename = document.file_name || `file-${Date.now()}.pdf`;

    console.log(`[BOT] [${reqId}] Downloading file from Telegram...`);
    const response = await axios.get(fileUrl, {
      responseType: "arraybuffer",
      timeout: 60000,
    });

    const fileBuffer = Buffer.from(response.data);
    console.log(`[BOT] [${reqId}] Download complete. File size: ${fileBuffer.length} bytes`);

    const telegramId = String(ctx.chat.id);
    const sessionId = await resolveSessionId(telegramId, getDisplayName(ctx));

    const form = new FormData();
    form.append("file", fileBuffer, { filename });
    form.append("telegramId", telegramId);

    console.log(`[BOT] [${reqId}] Sending to API /upload`);
    const headers = form.getHeaders();
    headers["X-Request-ID"] = reqId;

    await api.post("/upload", form, {
      headers,
      maxBodyLength: Infinity,
      maxContentLength: Infinity,
      timeout: 10 * 60 * 1000, // 10 minutes timeout for the whole pipeline
    });

    console.log(`[BOT] [${reqId}] Upload completed. Time taken: ${Date.now() - startTime}ms\n`);
    await ctx.reply("PDF uploaded and indexed.");
  } catch (error: any) {
    console.error(`[BOT] [${reqId}] Request failed:`, error.message);
    await ctx.reply("Failed to upload PDF.");
  }
});

/**
 * COMMAND: /new
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
 * COMMAND: /list
 */
bot.command("list", async (ctx) => {
  try {
    const response = await api.get("/sessions", {
      params: { telegramId: String(ctx.chat.id) },
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
 * COMMAND: /current
 */
bot.command("current", async (ctx) => {
  try {
    const response = await api.get("/sessions/active", {
      params: { telegramId: String(ctx.chat.id) },
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
 * COMMAND: /clear
 */
bot.command("clear", async (ctx) => {
  try {
    await api.delete("/sessions/active/messages", {
      data: { telegramId: String(ctx.chat.id) },
    });

    await ctx.reply("Conversation memory cleared.");
  } catch (error) {
    console.error("CLEAR ERROR:", error);
    await ctx.reply("Failed to clear conversation memory.");
  }
});

/**
 * COMMAND: /status
 */
bot.command("status", async (ctx) => {
  try {
    const response = await api.get("/sessions/active/status", {
      params: { telegramId: String(ctx.chat.id) },
    });

    if (!response.data || response.data.length === 0) {
      return ctx.reply("No documents in current session.");
    }

    let message = "Documents Status\n\n";

    for (const doc of response.data) {
      message += `${doc.filename}\n${doc.status}\n\n`;
    }

    await ctx.reply(message);
  } catch (error) {
    console.error("STATUS ERROR:", error);
    await ctx.reply("Failed to fetch document status.");
  }
});

/**
 * COMMAND: /help
 */
bot.command("help", async (ctx) => {
  await ctx.reply(`
Available Commands

/new <name>
/list
/current
/clear
/status

Upload PDF and start chatting.
`);
});

/**
 * ERROR HANDLER
 */
bot.catch((err) => {
  console.error("GRAMMY ERROR:", err);
});

/**
 * START BOT
 */
bot.api.deleteWebhook({ drop_pending_updates: true })
  .then(() => {
    bot.start({
      onStart: (botInfo) => {
        console.log(`Telegram bot running as @${botInfo.username}`);
      },
    });
  })
  .catch((err) => {
    console.error("Failed to initialize bot:", err);
  });
