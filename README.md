# 📰 NewsSense

### **Stay informed without reading everything.**

> **Too much news. Too little time.**

Every day, thousands of news stories are published. Keeping up usually means opening article after article, scrolling through long pages, and trying to figure out what is actually worth your attention.

**NewsSense was built to make that simpler.**

It automatically collects current news, uses an LLM to turn articles into concise summaries, organizes stories by topic, and presents everything in one clean interface.

### 🚀 [Try NewsSense Live →](https://web-production-6aaa3.up.railway.app)

### 💻 [View the GitHub Repository →](https://github.com/RohanPujari/NEWS-Summarization-Agent)

---

## 💡 The Idea

The goal wasn't to build another chatbot that answers questions about the news.

The goal was to build something that works **before you even ask a question**.

Instead of:

**Find news → Open article → Read → Repeat**

NewsSense turns it into:

**Find news → AI summarizes → Understand → Move on**

You can search for stories, filter them by category, and quickly understand what is happening without opening dozens of articles.

---

## 🤖 What Makes It an AI Engineering Project?

The interesting part of NewsSense isn't simply calling an LLM.

The LLM is one component inside a larger system.

The application handles the complete journey:

**News ingestion → validation → AI summarization → categorization → database → API → frontend → deployment**

This meant solving practical engineering problems around:

- API integration
- Data validation
- Duplicate detection
- Prompt design
- LLM response handling
- Classification
- Database persistence
- Scheduled processing
- Backend APIs
- Frontend integration
- Cloud deployment

> **The model is a component. The system is the product.**

---

## 🧠 How It Works

```text
             📰 NewsAPI
                 │
                 ▼
        Validate & Filter
                 │
                 ▼
          🤖 Groq + LLM
        GPT-OSS-120B
                 │
                 ▼
        AI Summarization
                 │
                 ▼
      🏷️ Categorization
                 │
                 ▼
            💾 SQLite
                 │
                 ▼
           ⚡ FastAPI
                 │
                 ▼
            🌐 UI

NewsSense processes articles in the background and stores the results so the frontend can serve already-processed stories instead of triggering an LLM request every time someone opens the application.
Process first. Serve second.
✨ What You Can Do
📰 Discover Current News
NewsSense automatically retrieves current stories and brings them into one place.
🤖 Understand Articles Faster
GPT-OSS-120B generates concise summaries from the available article content so you can quickly understand the main story.
🏷️ Browse by Topic
Articles are organized into categories such as:
- Technology
- Finance
- Politics
- Sports
- Health
- Entertainment
- General
🔎 Search & Filter
Search for topics you're interested in or filter the feed by category.
⏰ Automatic Processing
The ingestion pipeline runs automatically on a scheduled interval, keeping the application continuously updated.
🤔 Why Not Use an LLM for Everything?
One of the design decisions in NewsSense was intentionally not using an LLM for every task.
The summaries are generated using GPT-OSS-120B through Groq.
However, article categorization uses a lightweight deterministic classifier.
Why?
Because categorization doesn't always require an expensive generative model.
A deterministic approach is:
- ⚡ Faster
- 💰 Lower cost
- 🔍 Explainable
- 🐛 Easier to debug
- 🔁 More predictable
This was an important engineering lesson from the project:
Use AI where it adds value — not simply because you can.

🏗️ Architecture
┌─────────────────┐
│    NewsAPI      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Validation &    │
│ Duplicate Check │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Groq API      │
│ GPT-OSS-120B    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Summarization & │
│ Categorization  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ SQLite Database │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    FastAPI      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Web Frontend  │
└─────────────────┘
⚙️ Tech Stack
Layer	Technology
Language	Python
LLM	GPT-OSS-120B
LLM Provider	Groq
News Source	NewsAPI
Backend	FastAPI
Database	SQLite
ORM	SQLAlchemy
Scheduling	APScheduler
Frontend	HTML, CSS, JavaScript
Deployment	Railway


🚀 Try It Yourself
🌐 Open NewsSense →
Try:
- 🔎 Searching for a topic
- 🏷️ Filtering by category
- 📰 Reading AI-generated summaries
- ⏱️ Checking when stories were published
The application is designed to be useful within seconds of opening it.
🔐 AI Processing Pipeline
An LLM response should not automatically become application data.
NewsSense separates ingestion, processing, and serving:
Raw Article
     ↓
Validation
     ↓
Duplicate Check
     ↓
LLM Processing
     ↓
Summary Validation
     ↓
Categorization
     ↓
Database
     ↓
API
     ↓
User
This structure creates clear points where additional validation, evaluation, monitoring, and model improvements can be introduced.
⏰ Automated News Pipeline
NewsSense uses APScheduler to periodically run the ingestion pipeline.
The application:
1. Fetches current news
2. Validates incoming articles
3. Checks for duplicates
4. Generates summaries
5. Categorizes stories
6. Stores processed results
7. Makes them available through the FastAPI backend
This means the application isn't dependent on manually refreshing or processing individual articles.
🎯 Engineering Decisions
LLM for Summarization
Summarization is where generative AI provides clear value: transforming longer article content into a concise explanation.
Deterministic Categorization
Categorization uses keyword-based scoring rather than another LLM request.
This reduces unnecessary model calls and makes classification easier to understand and debug.
Background Processing
Articles are processed before they reach the frontend.
This keeps the user experience separate from the expensive processing step.
API-First Backend
FastAPI provides a clean interface between the processed data and the frontend, while also making the application easier to extend in future versions.
🔮 What's Next?
NewsSense v1 focuses on building the complete pipeline from data ingestion to a deployed AI application.
Potential improvements for future versions include:
- 🔗 Original article click-through
- 🗄️ PostgreSQL for production-scale storage
- 📰 Additional news providers
- 🧠 Semantic / embedding-based categorization
- 📊 Usage and application analytics
- 🧪 Automated LLM evaluation
- 📈 Monitoring and observability
- 🎯 Personalized news feeds
The goal is to continue improving the application based on how people actually use it.
🎯 Why I Built NewsSense
I wanted to build a project where I could work on more than just a model.
Building NewsSense meant thinking about the entire AI application:
Where does the data come from?
How should it be processed?
Where does the LLM actually add value?
How should its output be handled?
How do we store and serve the results?
How does the application continue running after deployment?
Those questions are what make AI engineering interesting to me.
The project is ultimately about building the system around the model — not just making a model call.
The model is a component. The system is the product.

🌐 Explore the Application
🚀 Open NewsSense Live
If you have a few seconds, try searching for a topic you're interested in and explore the categories.
👨‍💻 Built by Rohan Pujari
Data Scientist | AI/ML | Generative AI | NLP
GitHub
```
