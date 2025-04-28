import os
from dotenv import load_dotenv
from src.crawler import start_crawl
from src.database import site_pages_db
from src.embeddings import embedding_generator

load_dotenv()

def main():
    BASE_URL = os.getenv('CRAWL_BASE_URL', 'https://example.com')
    MAX_PAGES = int(os.getenv('MAX_PAGES', 100))
    MAX_DEPTH = int(os.getenv('MAX_DEPTH', 3))

    try:
        start_crawl(BASE_URL, MAX_PAGES, MAX_DEPTH)
        
        # Optional: Perform a test search
        test_query = "example search"
        test_embedding = embedding_generator.generate_embedding(test_query)
        
        results = site_pages_db.search_by_embedding(test_embedding)
        
        print("\nTop Matching Pages:")
        for url, title, content, similarity in results:
            print(f"URL: {url}")
            print(f"Similarity: {similarity}")
            print(f"Title: {title[:100]}...")
            print("-" * 50)
    
    except Exception as e:
        print(f"Crawling error: {e}")
    finally:
        site_pages_db.close()

if __name__ == '__main__':
    main()