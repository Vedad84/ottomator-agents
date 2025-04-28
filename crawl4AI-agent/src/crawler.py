import asyncio
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Set, Dict

from .database import site_pages_db
from .embeddings import embedding_generator

class AsyncWebCrawler:
    def __init__(self, base_url: str, max_pages: int = 100, max_depth: int = 3):
        self.base_url = base_url
        self.max_pages = max_pages
        self.max_depth = max_depth
        
        self.visited_urls: Set[str] = set()
        self.to_visit_urls: List[Dict] = [{'url': base_url, 'depth': 0}]
        
        self.client = httpx.AsyncClient(
            follow_redirects=True, 
            timeout=10.0
        )

    async def _fetch_page(self, url: str) -> str:
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""

    def _extract_text(self, html: str) -> str:
        soup = BeautifulSoup(html, 'lxml')
        
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
        
        return soup.get_text(separator=' ', strip=True)

    def _extract_links(self, html: str, base_url: str) -> List[str]:
        soup = BeautifulSoup(html, 'lxml')
        base_domain = urlparse(base_url).netloc
        
        links = []
        for a in soup.find_all('a', href=True):
            link = urljoin(base_url, a['href'])
            parsed_link = urlparse(link)
            
            if (parsed_link.netloc == base_domain and 
                not parsed_link.fragment and 
                link not in self.visited_urls):
                links.append(link)
        
        return links

    async def crawl(self, source_name: str = 'web_crawl'):
        while self.to_visit_urls and len(self.visited_urls) < self.max_pages:
            current = self.to_visit_urls.pop(0)
            url, depth = current['url'], current['depth']
            
            if url in self.visited_urls or depth > self.max_depth:
                continue
            
            self.visited_urls.add(url)
            
            html = await self._fetch_page(url)
            if not html:
                continue
            
            text = self._extract_text(html)
            links = self._extract_links(html, self.base_url)
            
            embedding = embedding_generator.generate_embedding(text)
            
            site_pages_db.insert_page(
                url=url, 
                title=f"Crawled Page: {url}", 
                content=text, 
                embedding=embedding,
                source=source_name,
                metadata={'depth': depth}
            )
            
            new_links = [{'url': link, 'depth': depth + 1} for link in links]
            self.to_visit_urls.extend(new_links)
            
            print(f"Crawled: {url}, Depth: {depth}")
        
        await self.client.aclose()
        print(f"Crawling complete. Visited {len(self.visited_urls)} pages.")

def start_crawl(base_url: str, max_pages: int = 100, max_depth: int = 3):
    crawler = AsyncWebCrawler(base_url, max_pages, max_depth)
    asyncio.run(crawler.crawl())

if __name__ == '__main__':
    start_crawl('https://example.com')