🌐 Chatter with Websites, Videos & PDFs | Your All-in-One Web Chatbot

A lightweight, powerful toolkit to chat with any website, YouTube video, or PDF — ask questions, get summaries, and explore content with an LLM + RAG pipeline powered by smart scraping and embeddings.

🔹 What It Does
🕸️ Scrape Websites — fetch and clean HTML/text.
🧹 Parse & Clean Content — remove boilerplate, keep relevant sections.
✂️ Chunk & Embed — split content into sections, embed into a vector store.
🤖 RAG-Powered Answers — user questions are answered with contextual citations.
📝 Summarization — generate short, medium, or long summaries.

🎥 YouTube Summarization — process transcripts for Q&A and summaries.
📄 PDF Chat — upload PDFs, query sections, and summarize content.
⚡ Easy to Run — works locally, supports Procfile/Docker for deployment.

🌟 Key Features
✅ Ask anything about a webpage, YouTube video, or PDF (topics, details, quotes, sections).
✅ Automatic summarization (short, medium, long).
✅ RAG-backed answers with citations from scraped/transcribed text.
✅ Fully extensible — swap scrapers, LLMs, embeddings, or vector DBs easily.

🏗️ High-Level Architecture
🌍 Web Scraper / PDF Loader / YouTube Transcript → fetch & clean text.
📑 Text Splitter → chunk content (preserve headings/sections).
🔢 Embeddings → convert chunks into vectors (OpenAI or other models).
📦 Vector Store → store & search (FAISS, Chroma, Pinecone, etc.).
🤝 Retriever + LLM → retrieve top-k chunks, feed into LLM (RAG pipeline).
💡 Output → concise answer + summary + cited context.

⚡ One Toolkit — Websites, YouTube, PDFs. Chat, Summarize, Explore.
