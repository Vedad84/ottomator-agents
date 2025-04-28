import sqlite3
import os
from typing import List, Dict, Any

class SitePagesDatabase:
    def __init__(self, db_path='database/site_pages.db'):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS site_pages (
            id INTEGER PRIMARY KEY,
            url TEXT UNIQUE,
            title TEXT,
            content TEXT,
            embedding BLOB,
            source TEXT,
            chunk_number INTEGER,
            metadata TEXT
        )''')
        
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_url ON site_pages(url)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON site_pages(source)')
        
        self.conn.commit()

    def insert_page(self, url, title, content, embedding, source, chunk_number=0, metadata=None):
        metadata_str = str(metadata) if metadata else '{}'
        
        try:
            self.cursor.execute('''
            INSERT OR REPLACE INTO site_pages 
            (url, title, content, embedding, source, chunk_number, metadata) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (url, title, content, sqlite3.Binary(bytes(embedding)), source, chunk_number, metadata_str))
            self.conn.commit()
        except Exception as e:
            print(f"Error inserting page: {e}")
            self.conn.rollback()

    def search_by_embedding(self, query_embedding, source=None, top_k=5):
        embedding_bytes = bytes(query_embedding)
        
        query = '''
        SELECT url, title, content, 
               (embedding.dot(?) / (norm(embedding) * norm(?))) as similarity 
        FROM site_pages
        '''
        params = [embedding_bytes, embedding_bytes]
        
        if source:
            query += ' WHERE source = ?'
            params.append(source)
        
        query += ' ORDER BY similarity DESC LIMIT ?'
        params.append(top_k)
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

site_pages_db = SitePagesDatabase()