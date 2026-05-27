# 🔍 News Verifier — Autonomous AI Fact-Checking Agent

A production-grade multi-agent news verification system built with LangGraph, FastAPI, and Next.js.

## 🚀 Live Demo
[Add your deployment URL here]

## 🏗️ Architecture

User Claim → Cache Check → Evidence Retrieval → Bias Detection →
Source Diversity Analysis → LLM Analysis → Verification Report

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, LangGraph |
| LLM | Groq (llama-3.1-8b-instant) |
| Vector DB | ChromaDB |
| Database | MySQL |
| Search | Tavily + NewsAPI |
| Frontend | Next.js, TypeScript, TailwindCSS |
| Deployment | Docker, Docker Compose |

## 🤖 Multi-Agent Pipeline

1. **Cache Agent** — checks vector store for similar past claims
2. **Retrieval Agent** — fetches evidence from Tavily and NewsAPI
3. **Bias Detection Agent** — detects political/emotional bias
4. **Source Diversity Agent** — analyzes source breadth
5. **Analysis Agent** — LLM-powered verdict generation
6. **Report Agent** — structured report with confidence scoring
7. **Storage Agent** — persists to MySQL + ChromaDB

## 🛠️ Running Locally

### Prerequisites
- Docker Desktop
- API keys: Groq, Tavily, NewsAPI

### Setup

1. Clone the repo:
```bash
git clone https://github.com/YOUR_USERNAME/news-verifier.git
cd news-verifier
```

2. Create `.env` in root:
```env
GROQ_API_KEY=your_key
TAVILY_API_KEY=your_key
NEWS_API_KEY=your_key
```

3. Start everything:
```bash
docker compose up
```

4. Open http://localhost:3000

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /agent/verify | Full multi-agent verification |
| GET | /agent/history | Verification history |
| POST | /claims/extract | Extract claims from text |
| GET | /health | Health check |

## 📸 Screenshots
[Add screenshots here]