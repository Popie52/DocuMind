# Telegram RAG Bot Architecture

This document describes the current project architecture, including service boundaries, data flows, and the key technologies used.

## Architecture Diagram

```mermaid
flowchart LR
  subgraph BotService[Telegram Bot Service]
    direction TB
    TelegramBot[Telegram Bot\n(grammy, axios)]
    TelegramBot -->|command/text/pdf| APIService
  end

  subgraph APIService[API Service]
    direction TB
    APIService[Fastify API\n(prisma, multipart, session routes)]
    APIService -->|POST /ask| AIService
    APIService -->|POST /upload| AIService
    APIService -->|session management| Postgres
  end

  subgraph AIService[AI Service]
    direction TB
    AIService[FastAPI service\n(parser, ingest, retrieve, RAG)]
    AIService -->|metadata + embeddings| Qdrant
    AIService -->|session-scoped retrieval| Qdrant
  end

  subgraph DataStores[Data Stores]
    direction TB
    Postgres[Postgres\n(session, document, message, user state)]
    Qdrant[Qdrant\n(vector store for chunks/embeddings)]
  end

  TelegramUser[Telegram User] --> TelegramBot
  APIService --> AIService
  APIService --> Postgres
  AIService --> Qdrant
  AIService --> APIService
  APIService --> TelegramBot
```

## Component Summary

- `apps/bot`
  - Telegram bot implementation using `grammy`
  - Sends `/ask` requests and `/upload` requests to the API service
  - Manages user commands such as session creation, list, and active session queries

- `apps/api`
  - Fastify-based HTTP API gateway and session manager
  - Uses Prisma to store session, document, message, and user state data in Postgres
  - Converts Telegram bot input into AI service requests
  - Persists uploaded PDF metadata and forwards files to the AI ingest route

- `apps/ai`
  - FastAPI-based AI microservice
  - Handles document parsing and vector ingestion
  - Executes retrieval-augmented generation (RAG) queries
  - Uses `session_id` to keep retrieval scoped to a user session
  - Stores embeddings and chunk payloads in Qdrant

- `data/postgres-data`
  - Persistent Postgres database storage for session state and document metadata

- `data/qdrant`
  - Persistent vector store for document embeddings and retrieval data

## Modern Design Principles

- **Service separation**: bot, API gateway, and AI engine are separate services with clean interfaces.
- **Session isolation**: each Telegram user session is tracked in Postgres and referenced by `session_id` for AI retrieval.
- **Vector search**: uses Qdrant for scalable similarity search over document chunks.
- **Containerization**: the project is composed with `docker-compose`, making services easy to run and deploy.
- **API-first bot integration**: the bot never talks directly to the AI service; it goes through the API layer.
- **Strong boundaries**: the API service owns session management, while the AI service owns ingestion and retrieval.
- **Modern frameworks**: `Fastify` for Node API, `FastAPI` for Python AI, and `grammy` for Telegram.
- **Async / streaming-friendly ingest**: PDF uploads are streamed, parsed, split into chunks, embedded, and indexed.

## Key Data Flow

1. User sends a message or document via Telegram.
2. `apps/bot` receives the update and sends a request to `apps/api`.
3. For text queries, the API resolves the active session and forwards the request to the AI service.
4. For PDF uploads, the API stores metadata, forwards the file to the AI service for parsing, and associates chunks with a session.
5. The AI service retrieves session-scoped chunks from Qdrant, answers the query, and returns citations.
6. The API returns the result to the bot, which replies in Telegram.

## File/Folder Mapping

- `apps/bot/src/index.ts`
  - Telegram handlers, session command support, upload forwarding
- `apps/api/src/routes/ask.ts`
  - `/ask` endpoint, forwards queries to AI service
- `apps/api/src/routes/upload.ts`
  - `/upload` endpoint, stores metadata and forwards PDF to AI service
- `apps/api/src/routes/session.ts`
  - session lifecycle endpoints (`/sessions`, `/sessions/active`, activation, delete)
- `apps/api/src/services/session.service.ts`
  - session and user state logic with Prisma
- `apps/ai/app/routes/query.py`
  - `/query` endpoint for RAG questions
- `apps/ai/app/routes/upload.py`
  - `/parse` endpoint for PDF ingestion
- `apps/ai/app/services/rag.py`
  - question-answer orchestration with citations
- `apps/ai/app/services/ingest.py`
  - document chunking, embedding, and Qdrant upsert
- `apps/ai/app/retrievers/qdrant.py`
  - vector retrieval filtered by session_id
