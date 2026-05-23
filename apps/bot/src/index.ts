import { Bot } from "grammy";
import dotenv from "dotenv";
import axios from "axios";

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
  const message = ctx.message.text;
  console.log("Received telegram message:", message);

  try {
    const response = await axios.post("http://127.0.0.1:3000/ask", {
      message,
    });
    console.log("API response:", response.data);
    await ctx.reply(`You said: ${response.data.answer}`);
  } catch (error) {
    console.log(error);
    await ctx.reply("API Unavailable");
  }
});

bot.start();

console.log("Telegram bot is running");
