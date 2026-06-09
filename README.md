<div align="center">

# 🤖 Telegram RAG Assistant

A production-ready Telegram bot powered by Retrieval-Augmented Generation (RAG). Upload PDFs, switch context sessions, and get fast, citation-aware answers powered by a modern microservice architecture.

[![Docker Compose](https://img.shields.io/badge/Docker%20Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](./docker-compose.yml)
[![Fastify](https://img.shields.io/badge/Fastify-000000?style=for-the-badge&logo=fastify&logoColor=white)](https://www.fastify.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Qdrant](https://img.shields.io/badge/Qdrant-EF2658?style=for-the-badge&logo=qdrant&logoColor=white)](https://qdrant.ai/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

<br />

![Service Map](diagram/docubot_service_map.svg)

![Request Flows](diagram/docubot_request_flows.svg)

</div>

---

## 📖 Overview

This repository provides a highly scalable, containerized conversational agent tailored for document-heavy workflows. 
Rather than a monolithic approach, the application is divided into three purpose-built microservices:

1. **Telegram Bot (`apps/bot`)** — The user interface. Handles Telegram updates, command parsing, and file ingestion.
2. **API Gateway (`apps/api`)** — The orchestrator. Manages user states, conversation memory, and proxies complex tasks.
3. **AI Engine (`apps/ai`)** — The brain. Parses PDFs, generates embeddings, performs vector searches, and synthesizes answers via LLMs.

This separation of concerns ensures horizontal scalability, robust security, and an incredibly fast local development workflow.

---

## ✨ Key Features

- **📂 Document Ingestion:** Upload PDF files directly in the Telegram chat. Documents are parsed, chunked, and embedded instantly.
- **🧠 Contextual RAG:** Answers are generated purely based on the uploaded documents with precise page-level citations.
- **🔄 Session Management:** Create isolated conversational memory sessions. Switch between tasks seamlessly without cross-contamination of context.
- **🐳 Cloud-Native Deployment:** Fully orchestrated via Docker Compose for zero-headache local setup and production deployments.
- **📊 Robust Vector Search:** Powered by Qdrant for blazing-fast semantic retrieval.

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
| --- | --- | --- |
| **Bot Framework** | [grammY](https://grammy.dev/) | Telegram Bot API integration |
| **API Backend** | Node.js + [Fastify](https://fastify.dev/) | High-performance HTTP server |
| **Database ORM** | [Prisma](https://www.prisma.io/) | Type-safe PostgreSQL interactions |
| **AI Backend** | Python + [FastAPI](https://fastapi.tiangolo.com/) | AI model serving & ingestion logic |
| **Vector DB** | [Qdrant](https://qdrant.tech/) | Semantic vector storage and retrieval |
| **LLM & Parsing** | Gemini & LlamaParse | Document parsing and answer generation |

---

## 🚀 Getting Started

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine
- A Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- API Keys for Google Gemini and LlamaParse

### 1. Clone the Repository
```bash
git clone https://github.com/<your-org>/telegram-rag-bot.git
cd telegram-rag-bot
```

### 2. Configure Environment
Create a `.env` file in the root of the project with your credentials:

```env
# API Keys
TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
GEMINI_API_KEY="your_gemini_api_key"
LLAMA_PARSE_API_KEY="your_llamaparse_api_key"

# Database Configuration (Docker Internal)
DATABASE_URL=postgresql://postgres:kali@postgres:5432/ragdb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=kali
POSTGRES_DB=ragdb

# Services
QDRANT_URL=http://qdrant:6333
```

### 3. Launch the Stack
Fire up the entire microservice architecture with a single command:

```bash
docker compose up --build
```
*Docker will build the Node.js and Python containers, spin up PostgreSQL and Qdrant, and establish internal networking automatically.*

---

## 💬 Bot Commands

Interact with your bot on Telegram using the following commands:

| Command | Description |
| :--- | :--- |
| `/start` | Verify the bot is online and auto-create a "General" session |
| `/new <name>` | Create and activate a new conversation session |
| `/list` | View all your saved sessions |
| `/current` | View the currently active session |
| `/switch <number>`| Switch context to a different session by its number |
| `/delete <number>`| Delete a session by its number |
| `/status` | Check the parsing and indexing status of uploads |
| `/clear` | Wipe conversation memory for the current session |
| `/help` | Display the help menu |

---

## 📁 Repository Structure

```text
telegram-rag-bot/
├── apps/
│   ├── ai/          # Python FastAPI service (Retrieval, Embeddings, LLM)
│   ├── api/         # Node.js Fastify service (Gateway, Sessions, DB)
│   └── bot/         # Node.js grammY service (Telegram Webhooks/Polling)
├── data/            # Local Docker volumes for PostgreSQL & Qdrant
├── diagram/         # Architecture diagrams and assets
├── docker-compose.yml
└── .env             # Global configuration
```

---

## 💡 Local Development (Without Docker)

If you wish to run the services individually for active development:

**1. API Service (Node 24+)**
```bash
cd apps/api
pnpm install
npx prisma db push
pnpm dev
```

**2. Bot Service (Node 24+)**
```bash
cd apps/bot
pnpm install
pnpm dev
```

**3. AI Service (Python 3.12+)**
```bash
cd apps/ai
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*(Ensure PostgreSQL and Qdrant are running locally and update the `.env` URLs to point to `localhost` instead of Docker hostnames).*

---
<div align="center">
<i>Built with modern tools for modern document intelligence.</i>
</div>