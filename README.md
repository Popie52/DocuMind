# Telegram RAG Agent

[![Docker](https://img.shields.io/badge/docker-compose-blue?logo=docker)](./docker-compose.yml)
[![Fastify](https://img.shields.io/badge/Fastify-Node.js-green?logo=node.js)](https://www.fastify.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Python-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Qdrant](https://img.shields.io/badge/Qdrant-vector%20search-orange)](https://qdrant.ai/)

A production-oriented Telegram assistant that supports:

- PDF upload and document ingestion
- Retrieval-augmented conversational QA
- Session-based memory and document isolation
- Citation-aware responses
- Containerized deployment using Docker Compose

![Architecture diagram](diagram/telegram_bot_architecture.png)

## Project Summary

This repository demonstrates a polished microservice architecture for a document-centric conversational agent. The application is split into three core services:

- **Telegram bot** (`apps/bot`) — handles user interaction, command parsing, and file uploads
- **API gateway** (`apps/api`) — manages sessions, stores metadata, and proxies requests to the AI engine
- **AI service** (`apps/ai`) — ingests PDF content, generates embeddings, performs retrieval, and produces answers

The bot communicates only with the API gateway, which enforces session boundaries and forwards workload to the AI service. This design keeps the system maintainable, secure, and aligned with modern cloud-native deployment practices.

## Key Features

- Session-aware conversational memory with `/new`, `/list`, `/current`, `/switch`, `/clear`
- PDF ingestion and indexing with session-scoped document visibility
- Retrieval-augmented answers with citations for transparency
- Lightweight observability and stable upload lifecycle
- Docker Compose orchestration for local and production-ready deployment

## Technology Stack

- Node.js + Fastify for the API gateway
- TypeScript and `pnpm` for fast Node workflow
- Python + FastAPI for AI and ingestion services
- Qdrant for vector storage and semantic retrieval
- PostgreSQL for session and document metadata
- Telegram `grammy` for bot integration

## Architecture Overview

1. Telegram users send text, commands, or PDF documents to the bot.
2. The bot resolves the active session and forwards requests to the API gateway.
3. The API gateway persists session state and document metadata in PostgreSQL.
4. Uploaded PDFs are parsed, chunked, embedded, and stored in Qdrant by the AI service.
5. User questions are executed as retrieval-augmented queries with session-specific filters.
6. Answers and citations are returned through the API back to Telegram.

## Bot Commands

- `/new <session-name>` — Create and activate a new session
- `/list` — List all sessions for the current Telegram user
- `/current` — Display the currently active session
- `/switch <session-name>` — Switch the active session
- `/docs` — Show documents attached to the active session
- `/status` — Show document indexing status
- `/clear` — Clear conversation memory for the active session
- `/help` — Display available commands

## Setup Instructions

### Prerequisites

- Docker Desktop or Docker Engine
- Docker Compose v2+
- Optional: Node.js 24+, pnpm, Python 3.12+ (for local development)

### 1. Clone the repository

```bash
git clone https://github.com/<your-org>/telegram-rag-bot.git
cd telegram-rag-bot
```

### 2. Create environment variables

Copy `.env.example` or create `.env` in the repository root with the following values:

```env
TELEGRAM_BOT_TOKEN=<your telegram bot token>
GEMINI_API_KEY=<your Gemini / Google GenAI key>
LLAMA_PARSE_API_KEY=<your parser API key>
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ragdb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=ragdb
QDRANT_URL=http://qdrant:6333
```

### 3. Run the full stack with Docker

```bash
docker compose up --build
```

Open the Telegram bot and start a conversation once the services are running.

### 4. Stop the stack

```bash
docker compose down
```

## Local Development

### API Service

```bash
cd apps/api
pnpm install
pnpm build
pnpm start
```

### Bot Service

```bash
cd apps/bot
pnpm install
pnpm build
pnpm start
```

### AI Service

```bash
cd apps/ai
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

> If running locally, ensure the bot can reach `http://localhost:3000` and the API can reach `http://localhost:8000`.

## Docker Notes

- `docker-compose.yml` orchestrates:
  - `postgres`
  - `qdrant`
  - `api`
  - `ai`
  - `bot`
- `.dockerignore` is included to reduce build context size and exclude artifacts.
- The API service exposes port `3000`; the AI service exposes port `8000`.

## Repository Structure

- `apps/bot` — Telegram bot implementation and command router
- `apps/api` — Fastify API routes, session management, and upload handling
- `apps/ai` — FastAPI AI backend with parser, ingestion, retrieval, and generation
- `data` — persistent storage for Postgres and Qdrant volumes
- `diagram` — architecture illustration

## Why This Project Stands Out

- Strong service separation with clear ownership boundaries
- Production-ready container deployment
- Practical use case with real-world PDF ingestion and semantic search
- Designed for fast iteration and easy extension

## Next Steps

- Add automated tests for API and bot interactions
- Add CI/CD pipeline for Docker and deployment
- Harden environment configuration for production readiness

---