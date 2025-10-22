"""
Kurdistan24 Scraper with FlareSolverr support
"""

from .base_scraper import BaseScraper
import requests
from bs4 import BeautifulSoup
import time
import re


class Kurdistan24Scraper(BaseScraper):
    """Scraper for Kurdistan24 (kurdistan24.net) using FlareSolverr to bypass Cloudflare"""
    
    def __init__(self):
        super().__init__("Kurdistan24")
        self.base_url = "https://www.kurdistan24.net/ckb/list/category/9"
        self.flaresolverr_url = "http://localhost:8191"
        self.session_id = None
    
    def _create_session(self):
        """Create FlareSolverr session"""
        try:
            response = requests.post(f'{self.flaresolverr_url}/v1', json={
                "cmd": "sessions.create",
                "session": f"k24_session_{int(time.time())}"
            }, timeout=30)
            
            if response.status_code == 200:
                self.session_id = response.json().get('session')
                print(f"   ✅ FlareSolverr session: {self.session_id}")
                return True
            return False
        except Exception as e:
            print(f"   ❌ FlareSolverr not available: {e}")
            return False
    
    def _destroy_session(self):
        """Destroy FlareSolverr session"""
        if self.session_id:
            try:
                requests.post(f'{self.flaresolverr_url}/v1', json={
                    "cmd": "sessions.destroy",
                    "session": self.session_id
                }, timeout=10)
            except:
                pass
    
    def _get_page(self, url):
        """Get page through FlareSolverr"""
        try:
            response = requests.post(f'{self.flaresolverr_url}/v1', json={
                "cmd": "request.get",
                "url": url,
                "session": self.session_id,
                "maxTimeout": 60000
            }, timeout=90)
            
            if response.status_code == 200 and response.json().get('status') == 'ok':
                return response.json()['solution']['response']
        except:
            pass
        return None
    
    def scrape_political(self, pages=10):
        """Scrape political news"""
        print(f"\n📰 Scraping {self.name} Political ({pages} pages with FlareSolverr)...")
        
        try:
            # Check FlareSolverr availability (with retry for startup delay)
            flare_ready = False
            for attempt in range(3):
                try:
                    response = requests.get(self.flaresolverr_url, timeout=5)
                    if response.status_code == 200:
                        flare_ready = True
                        break
                    time.sleep(2)
                except Exception as e:
                    if attempt < 2:
                        time.sleep(3)  # Wait longer for FlareSolverr to be ready
                    else:
                        print(f"   ❌ FlareSolverr not available after 3 attempts: {e}")
                        return 0
            
            if not flare_ready:
                print(f"   ❌ FlareSolverr not responding on {self.flaresolverr_url}")
                return 0
            
            if not self._create_session():
                return 0
            
            articles_found = 0
            article_links = []
            
            try:
                # Scrape list pages
                for page in range(1, pages + 1):
                    url = f'https://www.kurdistan24.net/ckb/list/category/9/%D8%B3%DB%8C%D8%A7%D8%B3%DB%8C?page={page}'
                    
                    html = self._get_page(url)
                    if not html:
                        print(f"   ⚠️  Page {page} failed")
                        continue
                    
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract article titles
                    articles = soup.find_all('article')
                    
                    for article in articles:
                        h3 = article.find('h3')
                        if h3:
                            text = h3.get_text(strip=True)
                            if self.add_sentence(text):
                                articles_found += 1
                            
                            # Collect article links
                            link = article.find('a', href=lambda x: x and '/story/' in x)
                            if link:
                                href = link.get('href')
                                if href and href.startswith('http') and href not in article_links:
                                    article_links.append(href)
                    
                    print(f"   Page {page}/{pages}: {articles_found} sentences")
                    time.sleep(2)
                
                # Visit article detail pages
                print(f"   Visiting top 50 articles...")
                for link in article_links[:50]:
                    try:
                        html = self._get_page(link)
                        if not html:
                            continue
                        
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract content
                        content_div = soup.find('div', class_='reader-content')
                        if content_div:
                            paragraphs = content_div.find_all('p')
                            
                            for p in paragraphs:
                                text = p.get_text(strip=True)
                                if self.add_sentence(text):
                                    articles_found += 1
                        
                        time.sleep(2)
                    except:
                        continue
            
            finally:
                self._destroy_session()
            
            self.stats['political'] = articles_found
            print(f"✅ {self.name} Political: {articles_found} sentences")
            return articles_found
        
        except Exception as e:
            print(f"⚠️  {self.name} Political error: {e}")
            self._destroy_session()
            return 0
    
    def scrape_specialized(self, pages_per_category=5, articles_per_category=None):
        """Scrape specialized categories"""
        # Support both parameter names for compatibility
        if articles_per_category is not None:
            pages_per_category = max(1, articles_per_category // 10)  # Convert articles to pages
        
        print(f"\n📚 Scraping {self.name} Specialized (6 categories, {pages_per_category} pages each with FlareSolverr)...")
        
        categories = [
            ('Economy', 'https://www.kurdistan24.net/ckb/list/category/12'),
            ('Culture', 'https://www.kurdistan24.net/ckb/list/category/10'),
            ('Artistic', 'https://www.kurdistan24.net/ckb/list/category/13'),
            ('Social', 'https://www.kurdistan24.net/ckb/list/category/11'),
            ('Health', 'https://www.kurdistan24.net/ckb/category/4/%D8%AA%DB%95%D9%86%D8%AF%D8%B1%D9%88%D8%B3%D8%AA%DB%8C'),
            ('Science-Technology', 'https://www.kurdistan24.net/ckb/category/7/%D8%B2%D8%A7%D9%86%D8%B3%D8%AA%20%D9%88%20%D8%AA%DB%95%DA%A9%D9%86%DB%95%D9%84%DB%86%DA%98%DB%8C%D8%A7')
        ]
        
        try:
            # Check FlareSolverr availability (with retry for startup delay)
            flare_ready = False
            for attempt in range(3):
                try:
                    response = requests.get(self.flaresolverr_url, timeout=5)
                    if response.status_code == 200:
                        flare_ready = True
                        break
                    time.sleep(2)
                except Exception as e:
                    if attempt < 2:
                        time.sleep(3)  # Wait longer for FlareSolverr to be ready
                    else:
                        print(f"   ❌ FlareSolverr not available after 3 attempts: {e}")
                        return 0
            
            if not flare_ready:
                print(f"   ❌ FlareSolverr not responding on {self.flaresolverr_url}")
                return 0
            
            if not self._create_session():
                return 0
            
            total_found = 0
            
            try:
                for cat_name, base_url in categories:
                    print(f"\n   📂 Category: {cat_name}")
                    cat_found = 0
                    article_links = []
                    
                    try:
                        # Scrape category pages
                        for page in range(1, pages_per_category + 1):
                            url = f"{base_url}?page={page}" if page > 1 else base_url
                            
                            html = self._get_page(url)
                            if not html:
                                print(f"      ⚠️  Page {page} failed")
                                continue
                            
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Extract h3 titles
                            h3_titles = soup.find_all('h3')
                            for h3 in h3_titles:
                                text = h3.get_text(strip=True)
                                if self.add_sentence(text):
                                    cat_found += 1
                            
                            # Collect article links
                            links = soup.find_all('a', href=lambda x: x and '/ckb/story/' in x)
                            for link in links:
                                href = link.get('href')
                                if href and href.startswith('http') and href not in article_links:
                                    article_links.append(href)
                            
                            time.sleep(2)
                        
                        print(f"      Found {len(article_links)} {cat_name.lower()} article links")
                        
                        # Visit article detail pages (limit to 10 per category)
                        for article_url in article_links[:10]:
                            try:
                                html = self._get_page(article_url)
                                if not html:
                                    continue
                                
                                soup = BeautifulSoup(html, 'html.parser')
                                
                                # Get article title
                                title = soup.find('h1')
                                if title:
                                    text = title.get_text(strip=True)
                                    if self.add_sentence(text):
                                        cat_found += 1
                                
                                # Get article content
                                content_div = soup.find('div', class_='reader-content')
                                if content_div:
                                    paragraphs = content_div.find_all('p')
                                    
                                    for p in paragraphs:
                                        text = p.get_text(strip=True)
                                        if len(text) < 20:
                                            continue
                                        
                                        # Split into sentences
                                        sents = re.split(r'[.؟!،]\s*', text)
                                        for s in sents:
                                            s = s.strip()
                                            if self.add_sentence(s):
                                                cat_found += 1
                                
                                time.sleep(2)
                            
                            except:
                                continue
                    
                    except Exception as e:
                        print(f"      ⚠️  {cat_name} category error: {e}")
                    
                    print(f"      ✅ {cat_name}: {cat_found} sentences")
                    total_found += cat_found
            
            finally:
                self._destroy_session()
            
            self.stats['specialized'] = total_found
            print(f"\n✅ {self.name} Specialized: {total_found} total sentences")
            return total_found
        
        except Exception as e:
            print(f"⚠️  {self.name} Specialized error: {e}")
            self._destroy_session()
            return 0
    
    def cleanup(self):
        """Cleanup resources"""
        self._destroy_session()
        super().cleanup()
