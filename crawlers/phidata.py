from typing import List, Dict, Any, Optional
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import logging
from newspaper import Article
import nltk
from urllib.parse import urljoin

class PhiDataCrawler:
    """Crawler for collecting and analyzing phidata"""
    
    def __init__(self, base_url: str = "https://bitcoin.org"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.data: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize NLTK for text analysis
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except Exception as e:
            self.logger.warning(f"NLTK download failed: {e}")

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def crawl(self, max_pages: int = 10) -> List[Dict[str, Any]]:
        """Crawl phidata sources and collect information"""
        try:
            urls = await self._discover_urls(max_pages)
            tasks = [self._process_url(url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out errors and None results
            self.data = [r for r in results if isinstance(r, dict)]
            return self.data
            
        except Exception as e:
            self.logger.error(f"Crawl failed: {e}")
            return []

    async def _discover_urls(self, max_pages: int) -> List[str]:
        """Discover relevant URLs to crawl"""
        urls = set()
        try:
            async with self.session.get(self.base_url) as response:
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')
                
                for link in soup.find_all('a', href=True):
                    url = urljoin(self.base_url, link['href'])
                    if self._is_relevant_url(url):
                        urls.add(url)
                        if len(urls) >= max_pages:
                            break
                            
        except Exception as e:
            self.logger.error(f"URL discovery failed: {e}")
            
        return list(urls)

    def _is_relevant_url(self, url: str) -> bool:
        """Check if URL is relevant for phidata collection"""
        relevant_terms = ['bitcoin', 'crypto', 'blockchain', 'defi']
        return any(term in url.lower() for term in relevant_terms)

    async def _process_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Process a single URL and extract phidata"""
        try:
            article = Article(url)
            await asyncio.to_thread(article.download)
            await asyncio.to_thread(article.parse)
            await asyncio.to_thread(article.nlp)
            
            return {
                'url': url,
                'title': article.title,
                'text': article.text,
                'summary': article.summary,
                'keywords': article.keywords,
                'publish_date': article.publish_date,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process URL {url}: {e}")
            return None

    def analyze(self) -> Dict[str, Any]:
        """Analyze collected phidata"""
        if not self.data:
            return {}
            
        df = pd.DataFrame(self.data)
        
        analysis = {
            'total_articles': len(df),
            'avg_keywords': df['keywords'].apply(len).mean(),
            'common_keywords': self._get_common_keywords(df),
            'timeline': self._analyze_timeline(df),
            'sentiment': self._analyze_sentiment(df)
        }
        
        return analysis

    def _get_common_keywords(self, df: pd.DataFrame) -> Dict[str, int]:
        """Get most common keywords across all articles"""
        keywords = {}
        for kw_list in df['keywords']:
            for kw in kw_list:
                keywords[kw] = keywords.get(kw, 0) + 1
        return dict(sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10])

    def _analyze_timeline(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze publication timeline"""
        df['publish_date'] = pd.to_datetime(df['publish_date'])
        timeline = df.groupby(df['publish_date'].dt.date).size()
        return {
            'dates': timeline.index.tolist(),
            'counts': timeline.values.tolist()
        }

    def _analyze_sentiment(self, df: pd.DataFrame) -> Dict[str, float]:
        """Basic sentiment analysis of article text"""
        try:
            from textblob import TextBlob
            sentiments = df['text'].apply(lambda x: TextBlob(x).sentiment.polarity)
            return {
                'average': sentiments.mean(),
                'positive': (sentiments > 0).sum() / len(sentiments),
                'negative': (sentiments < 0).sum() / len(sentiments),
                'neutral': (sentiments == 0).sum() / len(sentiments)
            }
        except ImportError:
            self.logger.warning("TextBlob not available for sentiment analysis")
            return {} 