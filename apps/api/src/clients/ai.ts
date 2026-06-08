import axios from "axios";

export const aiClient = axios.create({
  baseURL: process.env.AI_URL || "http://localhost:8080",
  timeout: 120000,
});
