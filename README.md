# 📰 NewsSense – An AI News Summarization Agent

## 1. What this project does (and why it is built)

**NewsSense** is an AI-based news summarization agent that automatically reads the latest news articles and generates short, easy-to-read summaries.

The main goal of this project is to:
- Pull real news from RSS feeds,
- Clean and extract the actual article content,
- And summarize long articles into short summaries (around 60–120 words).

This project is built to **simulate a real-world AI pipeline**, not just a notebook demo.  
It focuses on handling messy data, unreliable news sources, and deciding **when NOT to summarize**, which is a real challenge in production systems.

---

## 2. What is used in this project

This project uses simple and widely used tools, so the pipeline is easy to understand.

### Data Ingestion
- **RSS feeds** to get the latest news articles
- This avoids scraping homepages and keeps the system stable

### Article Extraction
- **newspaper3k** to extract readable text from news URLs
- Works well for long-form articles

### Summarization Model
- **Pegasus-XSUM** (Hugging Face Transformers)
- This model is designed for short, abstractive summaries from long articles

### Core Technologies
- Python
- Hugging Face Transformers
- sentencepiece (required for Pegasus)
- feedparser
- torch

### Architecture Style
- Agent-based design
- Clear separation between:
  - fetching data
  - cleaning data
  - summarizing text
  - decision-making

---

## 3. Challenges faced and how they were handled

This project intentionally deals with **real-world problems**, not ideal data.

### Challenge 1: Short or incomplete articles
Some news sources provide:
- very short articles,
- live updates,
- or partial content.

**Problem:**  
Summarizing short articles causes hallucinations and bad summaries.

**Solution:**  
The agent checks article length and **skips articles that are too short** instead of forcing a summary.

---

### Challenge 2: Unreliable article extraction
Not all websites expose full content in static HTML.

**Problem:**  
Extractors sometimes return only headlines or intro paragraphs.

**Solution:**  
The pipeline treats extraction as a best-effort step and relies on the agent to decide whether the content is usable.

---

### Challenge 3: Model limitations
Summarization models require enough context to work well.

**Problem:**  
Feeding very small inputs produces incorrect or unrelated summaries.

**Solution:**  
Input validation is done **before** calling the model.  
The model is treated as a tool, not a decision-maker.

---

### Challenge 4: Dependency and environment issues
Different models have different tokenizer requirements.

**Problem:**  
Pegasus requires `sentencepiece`, which is not installed by default.

**Solution:**  
Explicit dependency management using `requirements.txt` and environment setup.

---

## Summary

This project is not just about generating summaries.  
It is about building a **reliable AI pipeline** that:
- works with real data,
- handles failures gracefully,
- and avoids producing misleading results.

The focus is on **engineering decisions**, not just model output.

---

THIS PROJECT IS UNDER CONSTRUCTION 🚧 ⚠ 

## How to run

```bash
pip install -r requirements.txt
python run_agent.py
```
---

## Author

Built by **Rohan**, 
AI / Data Science enthusiast



