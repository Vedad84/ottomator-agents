# Local AI Crawler and Embedding System

## Overview
This project provides a flexible web crawling and local AI embedding system.

## Requirements
- Python 3.8+
- LM Studio
- Local embedding model

## Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure `.env`:
- `CRAWL_BASE_URL`: Starting URL for crawling
- `MAX_PAGES`: Maximum pages to crawl
- `MAX_DEPTH`: Maximum crawl depth

## Usage
```bash
python main.py
```

## Components
- `src/database.py`: SQLite database management
- `src/crawler.py`: Async web crawler
- `src/embeddings.py`: Local embedding generation