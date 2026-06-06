import Fastify from "fastify";
import multipart from "@fastify/multipart";
import { uploadRoutes } from "./routes/upload.js";
import { askRoutes } from "./routes/ask.js";
import { sessionRoutes } from "./routes/session.js";

const app = Fastify({
  logger: true,
});


await app.register(sessionRoutes);
await app.register(multipart, {
  limits: {
    fileSize: 20*1024*1024,
  }
});
await app.register(uploadRoutes);
await app.register(askRoutes);

app.get("/health", async () => {
  return {
    status: "ok",
  };
});

const start = async () => {
  try {
    await app.listen({
      port: 3000,
      host: "0.0.0.0",
    });
    console.log("API running on port 3000");
  } catch (error) {
    app.log.error(error);
    process.exit(1);
  }
};

start();
