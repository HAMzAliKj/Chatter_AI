Chatter with Websites | Web Chatbot

A lightweight toolkit to chat with any website — ask questions, get summaries, and explore web content using an LLM + RAG pipeline powered by scraped text.

What It Does

Fetches and scrapes website content (HTML/text).

Parses and cleans the scraped text (e.g., remove boilerplate, extract relevant sections).

Splits and embeds content chunks into a vector store.

Uses Retrieval-Augmented Generation (RAG) to answer user questions with context from the scraped content.

Produces short summaries, timestamps (or section markers), and direct quotes.

Designed for local execution or easy deployment (Procfile or Docker included).

Key Features

Ask anything about a webpage (topics, details, quotes, sections).

Automatic summarization (short, medium, long formats).

RAG-backed answers — responses cite the scraped context.

Extensible — switch scraping strategies, LLMs, embedding models, or vector stores easily.

High-Level Architecture

Web Scraper → fetch and clean HTML/text from given URL.

Text Parser → convert content into structured chunks (maintaining headings/timestamps).

Embeddings → convert chunks to vectors (via OpenAI or other embedding models).

Vector Store → store and index (e.g., FAISS, Chroma, Pinecone).

Retriever + LLM → retrieve top-k relevant chunks and feed them into LLM for RAG synthesis.

Output → answer, summary, and highlighted snippets with source context.
