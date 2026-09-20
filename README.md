# 📰 NewsSense

### AI-powered news, summarized and organized for you.

> **Too much news. Too little time.**

NewsSense is an AI-powered news application built to solve a simple problem: keeping up with the news shouldn't require opening dozens of articles.

NewsSense automatically fetches current news, uses **GPT-OSS-120B** to generate concise summaries, categorizes stories, and presents everything in a simple interface.

### 🚀 [Try NewsSense Live](https://web-production-6aaa3.up.railway.app)

---

## 💡 The Idea

Instead of:

News → Open article → Read 5–10 minutes → Repeat

NewsSense turns it into:

News → AI Summary → Understand the story → Move on

The goal was to build more than an LLM demo.

**The LLM is one component. The system is the product.**

---

## 🧠 How It Works

```text
📰 NewsAPI
     │
     ▼
Validation & Filtering
     │
     ▼
🤖 GPT-OSS-120B
     │
     ▼
AI Summarization
     │
     ▼
🏷️ Deterministic Categorization
     │
     ▼
💾 SQLite
     │
     ▼
⚡ FastAPI
     │
     ▼
🌐 NewsSense
