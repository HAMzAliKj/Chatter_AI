🌐 Chatter with Websites | Web Chatbot

A lightweight toolkit to chat with any website — ask questions, get summaries, and explore web content using an LLM + RAG pipeline powered by scraped text.

🔹 What It Does

🕸️ Scrapes website content (HTML/text).

🧹 Cleans & parses text (removes boilerplate, keeps relevant sections).

✂️ Splits & embeds content chunks into a vector store.

🤖 RAG-powered answers — user questions are answered with context from the website.

📝 Summarizes content (short, medium, long).

⚡ Easy to run locally or deploy (Procfile/Docker supported).

🌟 Key Features

✅ Ask anything about a webpage (topics, details, quotes, sections).

✅ Automatic summarization (short, medium, long).

✅ RAG-backed answers that cite scraped text.

✅ Extensible — swap scrapers, LLMs, embeddings, or vector DBs easily.

🏗️ High-Level Architecture

🌍 Web Scraper → fetch & clean website text.

📑 Text Splitter → chunk content (keep headings/sections).

🔢 Embeddings → convert chunks into vectors (OpenAI or other models).

📦 Vector Store → store & search (FAISS, Chroma, Pinecone, etc.).

🤝 Retriever + LLM → retrieve top-k chunks, feed into LLM (RAG).

💡 Output → concise answer + summary + quoted context.
