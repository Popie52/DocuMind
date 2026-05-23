import Fastify from "fastify";

const app = Fastify({
  logger: true,
});

app.get("/health", async () => {
  return {
    status: "ok",
  };
});

app.post("/ask", async (req) => {
    const body = req.body as {
        message: string;
    };
    return {
        answer: `Recieve: ${body.message}`,
    }
});

const start = async () => {
    try {
        await app.listen({
            port: 3000,
            host: "0.0.0.0",
        });
        console.log("API running on port 3000");
    } catch(error) {
        app.log.error(error);
        process.exit(1);
    }
}

start();