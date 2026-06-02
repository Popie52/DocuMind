import { Bot } from "grammy";
import dotenv from "dotenv";
import axios from "axios";
import FormData from "form-data";
import { api } from "./services/api.js";

dotenv.config();

const token = process.env.TELEGRAM_BOT_TOKEN;

if (!token) {
  throw new Error("Telegram_BOT_TOKEN missing");
}

const bot = new Bot(token);

bot.command("start", async (ctx) => {
  await ctx.reply("Telegram RAG Agent is running");
});

bot.on("message:text", async (ctx) => {
  const question = ctx.message.text;
  console.log("Received telegram message:", question);

  try {
    const response = await api.post("/ask", {
      question,
    });

    console.log("API response:", response);
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
    console.log(error);
    await ctx.reply("API Unavailable");
  }
});

bot.on("message:document", async (ctx) => {
  try {
    const document = ctx.message.document;

    if (document.mime_type !== "application/pdf") {
      await ctx.reply("Only PDF files are supported");
      return;
    }

    const file = await ctx.getFile();

    const fileUrl = `https://api.telegram.org/file/bot${token}/${file.file_path}`;

    const filename = document.file_name || `file-${Date.now()}.pdf`;

    const response = await axios.get(fileUrl, {
      responseType: "arraybuffer",
    });

    const form = new FormData();

    form.append("file", Buffer.from(response.data), {
      filename: filename,
    });

    await api.post("/upload", form, {
      headers: form.getHeaders(),
      maxBodyLength: Infinity,
      maxContentLength: Infinity,
    });

    await ctx.reply("PDF uploaded and indexed.");
  } catch (error) {
    console.error(error);

    await ctx.reply("Failed to upload PDF.");
  }
});

bot.start();

console.log("Telegram bot is running");
