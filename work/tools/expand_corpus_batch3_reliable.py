#!/usr/bin/env python3
"""
Simple and reliable Kurdish corpus expander
Focus on sources we know work: Kurdsat, Rudaw, Khak TV (proven in Batch 2)
Plus add more pages/articles from each
"""

import sys
sys.path.insert(0, '/mnt/c/tesseract/work/tools')

# Use the working scraper from Batch 2 as base
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
from collections import Counter

class SimpleQC:
    """Simple quality checker - same as Batch 2"""
    min_words = 10
    max_words = 30
    min_purity = 70.0
    
    def check(self, text):
        words = text.split()
        if len(words) < self.min_words or len(words) > self.max_words:
            return False
        
        # Count Kurdish characters
        kurdish = sum(1 for c in text if c in 'ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهەوۆیێ')
        total = len([c for c in text if c.isalpha()])
        
        if total == 0:
            return False
        
        purity = 100 * kurdish / total
        return purity >= self.min_purity

class ReliableKurdishScraper:
    """Use proven methods from Batch 2, just scrape MORE"""
    
    def __init__(self):
        self.qc = SimpleQC()
        self.sentences = set()
        self.stats = Counter()
        
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        
        self.driver = webdriver.Chrome(
            service=Service('/usr/bin/chromedriver'),
            options=opts
        )
        print("✅ Browser initialized")
    
    def scrape_kurdsat_extended(self, clicks=30):
        """Kurdsat - proven to work, just click MORE times"""
        print(f"\n📰 Scraping Kurdsat (clicking {clicks} times)...")
        
        try:
            self.driver.get('https://kurdsat.tv/ckb/news')
            time.sleep(3)
            
            articles_found = 0
            for i in range(clicks):
                try:
                    button = self.driver.find_element(By.XPATH, "//button[contains(text(),'زیاتر ببینە')]")
                    self.driver.execute_script("arguments[0].scrollIntoView();", button)
                    time.sleep(1)
                    button.click()
                    time.sleep(2)
                    
                    if (i + 1) % 5 == 0:
                        print(f"   Clicked {i+1} times...")
                except:
                    print(f"   Stopped at click {i+1} (button not found)")
                    break
            
            articles = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/ckb/news/']")
            print(f"   Found {len(articles)} article links")
            
            for article in articles:
                try:
                    link = article.get_attribute('href')
                    if not link or '/ckb/news/' not in link:
                        continue
                    
                    self.driver.get(link)
                    time.sleep(1)
                    
                    paragraphs = self.driver.find_elements(By.CSS_SELECTOR, ".article-body p, .content p")
                    
                    for p in paragraphs:
                        text = p.text.strip()
                        if text and self.qc.check(text):
                            self.sentences.add(text)
                            articles_found += 1
                            break
                except:
                    continue
            
            self.stats['kurdsat'] = len([s for s in self.sentences if 'kurdsat' in str(hash(s))])
            print(f"✅ Kurdsat: {articles_found} articles processed")
        
        except Exception as e:
            print(f"⚠️  Kurdsat error: {e}")
    
    def scrape_rudaw_extended(self, scrolls=20):
        """Rudaw - proven to work, just scroll MORE"""
        print(f"\n📰 Scraping Rudaw (scrolling {scrolls} times)...")
        
        try:
            self.driver.get('https://www.rudaw.net/sorani/kurdistan')
            time.sleep(3)
            
            for i in range(scrolls):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                if (i + 1) % 5 == 0:
                    print(f"   Scrolled {i+1} times...")
            
            articles = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/sorani/']")
            print(f"   Found {len(articles)} article links")
            
            articles_found = 0
            for article in articles[:300]:  # Process more articles
                try:
                    link = article.get_attribute('href')
                    if not link or '/sorani/' not in link:
                        continue
                    
                    self.driver.get(link)
                    time.sleep(1)
                    
                    paragraphs = self.driver.find_elements(By.CSS_SELECTOR, ".detail-body p, .bodyContentMainParent p")
                    
                    for p in paragraphs:
                        text = p.text.strip()
                        if text and self.qc.check(text):
                            self.sentences.add(text)
                            articles_found += 1
                            break
                except:
                    continue
            
            self.stats['rudaw'] = articles_found
            print(f"✅ Rudaw: {articles_found} articles processed")
        
        except Exception as e:
            print(f"⚠️  Rudaw error: {e}")
    
    def scrape_khak_extended(self, pages=10):
        """Khak TV - proven to work, scrape MORE pages"""
        print(f"\n📰 Scraping Khak TV ({pages} pages)...")
        
        try:
            articles_found = 0
            for page in range(1, pages + 1):
                url = f'https://www.khaktv.net/article?group=5&page={page}'
                self.driver.get(url)
                time.sleep(2)
                
                links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/article/']")
                
                for link_elem in links[:15]:  # 15 per page
                    try:
                        link = link_elem.get_attribute('href')
                        if not link:
                            continue
                        
                        self.driver.get(link)
                        time.sleep(1)
                        
                        paragraphs = self.driver.find_elements(By.CSS_SELECTOR, ".html-content p, .content p")
                        
                        for p in paragraphs:
                            text = p.text.strip()
                            if text and self.qc.check(text):
                                self.sentences.add(text)
                                articles_found += 1
                                break
                    except:
                        continue
                
                print(f"   Page {page}: {articles_found} total sentences")
            
            self.stats['khak'] = articles_found
            print(f"✅ Khak TV: {articles_found} articles processed")
        
        except Exception as e:
            print(f"⚠️  Khak TV error: {e}")
    
    def scrape_nrt_extended(self, clicks=15):
        """NRT TV - major Kurdish news source with high-quality content"""
        print(f"\n📰 Scraping NRT TV (clicking {clicks} times)...")
        
        try:
            self.driver.get('https://nrttv.com/kurd')
            time.sleep(3)
            
            # Click "Load More" button multiple times
            for i in range(clicks):
                try:
                    # Button text is "زیاتر..."
                    button = self.driver.find_element(By.ID, "loadMore")
                    self.driver.execute_script("arguments[0].scrollIntoView();", button)
                    time.sleep(1)
                    button.click()
                    time.sleep(2)
                    
                    if (i + 1) % 5 == 0:
                        print(f"   Clicked {i+1} times...")
                except:
                    print(f"   Stopped at click {i+1} (button not found)")
                    break
            
            # Extract article titles and descriptions from list
            articles_found = 0
            
            # Get titles (h2.Name inside links)
            titles = self.driver.find_elements(By.CSS_SELECTOR, "h2.Name")
            for title in titles:
                text = title.text.strip()
                if text and self.qc.check(text):
                    self.sentences.add(text)
                    articles_found += 1
            
            # Get descriptions (p.de - article summaries)
            descriptions = self.driver.find_elements(By.CSS_SELECTOR, "p.de")
            for desc in descriptions:
                text = desc.text.strip()
                if text and self.qc.check(text):
                    self.sentences.add(text)
                    articles_found += 1
            
            # Also visit article detail pages for full content
            article_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='detail/']")
            print(f"   Found {len(article_links)} article links, visiting top 50...")
            
            visited = 0
            for link_elem in article_links[:50]:  # Visit top 50 articles
                try:
                    link = link_elem.get_attribute('href')
                    if not link or 'detail/' not in link:
                        continue
                    
                    self.driver.get(link)
                    time.sleep(1)
                    
                    # Get full article content
                    content_divs = self.driver.find_elements(By.CSS_SELECTOR, "div[style*='font-size:16px']")
                    
                    for div in content_divs:
                        # Split by paragraphs
                        paragraphs = div.find_elements(By.TAG_NAME, "p")
                        for p in paragraphs:
                            text = p.text.strip()
                            if text and self.qc.check(text):
                                self.sentences.add(text)
                                articles_found += 1
                        
                        # Also try direct text if no paragraphs
                        if not paragraphs:
                            text = div.text.strip()
                            # Split by newlines and check each
                            for line in text.split('\n'):
                                line = line.strip()
                                if line and self.qc.check(line):
                                    self.sentences.add(line)
                                    articles_found += 1
                    
                    visited += 1
                    if visited % 10 == 0:
                        print(f"   Visited {visited} articles, {articles_found} sentences so far...")
                        
                except:
                    continue
            
            self.stats['nrt'] = articles_found
            print(f"✅ NRT TV: {articles_found} sentences collected")
        
        except Exception as e:
            print(f"⚠️  NRT TV error: {e}")
    
    def scrape_awene_extended(self, pages=10):
        """Awene - Kurdish newspaper with quality content"""
        print(f"\n📰 Scraping Awene ({pages} pages)...")
        
        try:
            articles_found = 0
            article_links = []
            
            # Scrape list pages
            for page in range(1, pages + 1):
                url = f'https://www.awene.com/part?section=2&page={page}'
                self.driver.get(url)
                time.sleep(2)
                
                # Extract titles from list
                titles = self.driver.find_elements(By.CSS_SELECTOR, ".newstopsumbtitle a")
                
                for title in titles:
                    text = title.get_attribute('title')
                    if not text:
                        text = title.text.strip()
                    
                    if text and self.qc.check(text):
                        self.sentences.add(text)
                        articles_found += 1
                    
                    # Collect article links
                    href = title.get_attribute('href')
                    if href and 'detail?article=' in href:
                        article_links.append(href)
                
                print(f"   Page {page}: {articles_found} total sentences")
            
            # Visit article detail pages
            print(f"   Visiting top 50 articles...")
            for link in article_links[:50]:
                try:
                    self.driver.get(link)
                    time.sleep(1)
                    
                    # Extract article content
                    paragraphs = self.driver.find_elements(By.CSS_SELECTOR, ".viewdesc p")
                    
                    for p in paragraphs:
                        text = p.text.strip()
                        if text and self.qc.check(text):
                            self.sentences.add(text)
                            articles_found += 1
                except:
                    continue
            
            self.stats['awene'] = articles_found
            print(f"✅ Awene: {articles_found} sentences collected")
        
        except Exception as e:
            print(f"⚠️  Awene error: {e}")
    
    def scrape_awene_specialized(self, articles_per_category=30):
        """
        Scrape Awene specialized categories
        - Articles: General articles
        - Culture: Literature, art, music
        - Economy: Economic news and analysis
        - Health: Health and medicine
        - Multimedia: Multimedia content
        """
        categories = [
            ('Articles', 'https://www.awene.com/articles'),
            ('Culture', 'https://www.awene.com/culture'),
            ('Economy', 'https://www.awene.com/aburi'),
            ('Health', 'https://www.awene.com/health'),
            ('Multimedia', 'https://www.awene.com/multimedia')
        ]
        
        print(f"\n📚 Scraping Awene Specialized ({len(categories)} categories, {articles_per_category} articles each)...")
        
        try:
            total_articles = 0
            
            for cat_name, url in categories:
                print(f"\n   📂 Category: {cat_name}")
                articles_found = 0
                
                try:
                    self.driver.get(url)
                    time.sleep(4)
                    
                    # Find all article links on category page
                    all_links = self.driver.find_elements(By.TAG_NAME, 'a')
                    
                    article_links = []
                    for link in all_links:
                        href = link.get_attribute('href')
                        text = link.text.strip()
                        
                        # Filter for article detail links with titles
                        if href and 'detail?article=' in href and text and len(text) > 10:
                            # Skip "درێژەی بابەت" (Read more) links
                            if text != "درێژەی بابەت":
                                article_links.append((text, href))
                    
                    # Deduplicate by URL
                    seen_urls = set()
                    unique_articles = []
                    for text, href in article_links:
                        if href not in seen_urls:
                            seen_urls.add(href)
                            unique_articles.append((text, href))
                    
                    print(f"      Found {len(unique_articles)} unique articles on category page")
                    
                    # Collect titles first
                    for text, _ in unique_articles[:articles_per_category]:
                        if self.qc.check(text):
                            self.sentences.add(text)
                            articles_found += 1
                    
                    # Visit article detail pages
                    print(f"      Visiting top {min(articles_per_category, len(unique_articles))} articles...")
                    for _, article_url in unique_articles[:articles_per_category]:
                        try:
                            self.driver.get(article_url)
                            time.sleep(2)
                            
                            # Extract article content
                            paragraphs = self.driver.find_elements(By.CSS_SELECTOR, ".viewdesc p")
                            
                            for p in paragraphs:
                                text = p.text.strip()
                                if text and self.qc.check(text):
                                    self.sentences.add(text)
                                    articles_found += 1
                        except Exception as e:
                            print(f"         Error visiting article: {e}")
                            continue
                    
                    print(f"      ✅ {cat_name}: {articles_found} sentences")
                    total_articles += articles_found
                    
                except Exception as e:
                    print(f"      ⚠️  {cat_name} error: {e}")
                    continue
            
            self.stats['awene_specialized'] = total_articles
            print(f"\n✅ Awene Specialized: {total_articles} total sentences collected")
        
        except Exception as e:
            print(f"⚠️  Awene Specialized error: {e}")
    
    def scrape_kurdistan24_flaresolverr(self, pages=10):
        """Kurdistan24 - using FlareSolverr to bypass Cloudflare"""
        print(f"\n📰 Scraping Kurdistan24 ({pages} pages with FlareSolverr)...")
        
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Check if FlareSolverr is running
            try:
                requests.get('http://localhost:8191/', timeout=5)
            except:
                print("   ⚠️  FlareSolverr not running! Skipping Kurdistan24")
                print("   To enable: sudo docker start flaresolverr")
                self.stats['kurdistan24'] = 0
                return
            
            # Create FlareSolverr session
            session_response = requests.post('http://localhost:8191/v1', json={
                "cmd": "sessions.create"
            })
            
            if session_response.status_code != 200:
                print("   ⚠️  Failed to create FlareSolverr session")
                self.stats['kurdistan24'] = 0
                return
            
            session_id = session_response.json().get('session')
            print(f"   ✅ FlareSolverr session: {session_id}")
            
            articles_found = 0
            article_links = []
            
            try:
                # Scrape list pages
                for page in range(1, pages + 1):
                    url = f'https://www.kurdistan24.net/ckb/list/category/9/%D8%B3%DB%8C%D8%A7%D8%B3%DB%8C?page={page}'
                    
                    # Get page through FlareSolverr
                    response = requests.post('http://localhost:8191/v1', json={
                        "cmd": "request.get",
                        "url": url,
                        "session": session_id,
                        "maxTimeout": 60000
                    })
                    
                    if response.status_code == 200 and response.json().get('status') == 'ok':
                        html = response.json()['solution']['response']
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract article titles
                        articles = soup.find_all('article')
                        
                        for article in articles:
                            h3 = article.find('h3')
                            if h3:
                                text = h3.get_text(strip=True)
                                if text and self.qc.check(text):
                                    self.sentences.add(text)
                                    articles_found += 1
                                
                                # Collect article links
                                link = article.find('a', href=lambda x: x and '/story/' in x)
                                if link:
                                    href = link.get('href')
                                    if href and href.startswith('http'):
                                        article_links.append(href)
                        
                        print(f"   Page {page}: {articles_found} total sentences")
                        time.sleep(2)
                    else:
                        print(f"   ⚠️  Page {page} failed")
                
                # Visit article detail pages
                print(f"   Visiting top 50 articles...")
                for link in article_links[:50]:
                    try:
                        response = requests.post('http://localhost:8191/v1', json={
                            "cmd": "request.get",
                            "url": link,
                            "session": session_id,
                            "maxTimeout": 60000
                        })
                        
                        if response.status_code == 200 and response.json().get('status') == 'ok':
                            html = response.json()['solution']['response']
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Extract content
                            content_div = soup.find('div', class_='reader-content')
                            if content_div:
                                paragraphs = content_div.find_all('p')
                                
                                for p in paragraphs:
                                    text = p.get_text(strip=True)
                                    if text and self.qc.check(text):
                                        self.sentences.add(text)
                                        articles_found += 1
                        
                        time.sleep(2)
                    except:
                        continue
            
            finally:
                # Destroy FlareSolverr session
                requests.post('http://localhost:8191/v1', json={
                    "cmd": "sessions.destroy",
                    "session": session_id
                })
            
            self.stats['kurdistan24'] = articles_found
            print(f"✅ Kurdistan24: {articles_found} sentences collected")
        
        except Exception as e:
            print(f"⚠️  Kurdistan24 error: {e}")
            self.stats['kurdistan24'] = 0
    
    def scrape_xendan_extended(self, pages=10):
        """
        Scrape xendan.org Kurdish news
        Uses Selenium (no Cloudflare protection)
        Source: https://www.xendan.org/babetakan?babet=1&title=کوردستان
        """
        print("\n🔍 Xendan.org (NEW! Kurdish news portal)...")
        
        try:
            articles_found = 0
            article_links = []
            
            # Category page with Kurdistan news
            base_url = "https://www.xendan.org/babetakan?babet=1&title=%DA%A9%D9%88%D8%B1%D8%AF%D8%B3%D8%AA%D8%A7%D9%86"
            
            # Scrape article list pages
            for page in range(1, pages + 1):
                try:
                    print(f"   Page {page}...")
                    self.driver.get(base_url)
                    time.sleep(3)
                    
                    # Find article titles and links
                    # HTML: <li><a href="..."><div class="card-small"><h2>TITLE</h2>
                    cards = self.driver.find_elements(By.CSS_SELECTOR, '.card-small')
                    
                    for card in cards:
                        try:
                            # Get link from parent <a>
                            link_elem = card.find_element(By.XPATH, '..')
                            link = link_elem.get_attribute('href')
                            
                            # Get title
                            title_elem = card.find_element(By.CSS_SELECTOR, 'h2')
                            title = title_elem.text.strip()
                            
                            # Add title if quality
                            if title and self.qc.check(title):
                                self.sentences.add(title)
                                articles_found += 1
                            
                            # Store link for detail scraping
                            if link and link not in article_links:
                                article_links.append(link)
                        except:
                            continue
                    
                    # Try to click "دواتر" (next) button
                    # HTML: <a class="nextbutton" href="javascript:__doPostBack(...)">دواتر</a>
                    try:
                        next_btn = self.driver.find_element(By.CSS_SELECTOR, 'a.nextbutton')
                        if next_btn.text == 'دواتر':  # "Next" in Kurdish
                            self.driver.execute_script("arguments[0].click();", next_btn)
                            time.sleep(2)
                    except:
                        print(f"   ⚠️  No next button found, stopping at page {page}")
                        break
                
                except Exception as e:
                    print(f"   ⚠️  Page {page} failed: {e}")
            
            print(f"   Found {len(article_links)} articles, visiting top 50...")
            
            # Visit article detail pages
            for link in article_links[:50]:
                try:
                    self.driver.get(link)
                    time.sleep(2)
                    
                    # Get article title
                    # HTML: <div class="detail-top"><h1>TITLE</h1>
                    try:
                        title_elem = self.driver.find_element(By.CSS_SELECTOR, '.detail-top h1')
                        title = title_elem.text.strip()
                        if title and self.qc.check(title):
                            self.sentences.add(title)
                            articles_found += 1
                    except:
                        pass
                    
                    # Get article body paragraphs
                    # HTML: <div class="detail-big-text-p"><p>...</p>
                    paragraphs = self.driver.find_elements(By.CSS_SELECTOR, '.detail-big-text-p p')
                    
                    for p in paragraphs:
                        text = p.text.strip()
                        
                        # Skip very short or metadata lines
                        if len(text) < 20:
                            continue
                        
                        # Split into sentences
                        sents = re.split(r'[.؟!،]\s*', text)
                        for s in sents:
                            s = s.strip()
                            if s and self.qc.check(s):
                                self.sentences.add(s)
                                articles_found += 1
                    
                    time.sleep(1.5)
                
                except Exception as e:
                    continue
            
            self.stats['xendan'] = articles_found
            print(f"✅ Xendan: {articles_found} sentences collected")
        
        except Exception as e:
            print(f"⚠️  Xendan error: {e}")
            self.stats['xendan'] = 0
    
    def scrape_xendan_specialized(self, pages_per_category=5):
        """
        Scrape Xendan specialized categories
        - Sport: /Sport/babetakan?babet=20
        - Economy: /babetakan?babet=8
        - Technology: /babetakan?babet=7
        """
        print("\n🔍 Xendan Specialized (Sport, Economy, Tech)...")
        
        categories = [
            ('Sport', 'https://www.xendan.org/Sport/babetakan?babet=20'),
            ('Economy', 'https://www.xendan.org/babetakan?babet=8'),
            ('Technology', 'https://www.xendan.org/babetakan?babet=7')
        ]
        
        try:
            total_found = 0
            
            for cat_name, base_url in categories:
                print(f"   {cat_name}...")
                
                try:
                    article_links = []
                    
                    # Scrape pages
                    for page in range(1, pages_per_category + 1):
                        try:
                            self.driver.get(base_url)
                            time.sleep(2)
                            
                            # Find titles and links
                            cards = self.driver.find_elements(By.CSS_SELECTOR, '.card-small')
                            
                            for card in cards:
                                try:
                                    # Get link
                                    link_elem = card.find_element(By.XPATH, '..')
                                    link = link_elem.get_attribute('href')
                                    
                                    # Get title
                                    title_elem = card.find_element(By.CSS_SELECTOR, 'h2')
                                    title = title_elem.text.strip()
                                    
                                    # Add title if quality
                                    if title and self.qc.check(title):
                                        self.sentences.add(title)
                                        total_found += 1
                                    
                                    # Store link
                                    if link and link not in article_links:
                                        article_links.append(link)
                                except:
                                    continue
                            
                            # Try next page button
                            try:
                                next_btn = self.driver.find_element(By.CSS_SELECTOR, 'a.nextbutton')
                                if next_btn.text == 'دواتر':
                                    self.driver.execute_script("arguments[0].click();", next_btn)
                                    time.sleep(2)
                            except:
                                break
                        
                        except Exception as e:
                            break
                    
                    print(f"      Found {len(article_links)} {cat_name.lower()} articles")
                    
                    # Visit article detail pages (limit to 20 per category)
                    for link in article_links[:20]:
                        try:
                            self.driver.get(link)
                            time.sleep(2)
                            
                            # Get title
                            try:
                                title_elem = self.driver.find_element(By.CSS_SELECTOR, '.detail-top h1')
                                title = title_elem.text.strip()
                                if title and self.qc.check(title):
                                    self.sentences.add(title)
                                    total_found += 1
                            except:
                                pass
                            
                            # Get paragraphs
                            paragraphs = self.driver.find_elements(By.CSS_SELECTOR, '.detail-big-text-p p')
                            
                            for p in paragraphs:
                                text = p.text.strip()
                                if len(text) < 20:
                                    continue
                                
                                # Split into sentences
                                sents = re.split(r'[.؟!،]\s*', text)
                                for s in sents:
                                    s = s.strip()
                                    if s and self.qc.check(s):
                                        self.sentences.add(s)
                                        total_found += 1
                            
                            time.sleep(1.5)
                        
                        except:
                            continue
                
                except Exception as e:
                    print(f"      ⚠️  {cat_name} category error: {e}")
                    continue
            
            self.stats['xendan_specialized'] = total_found
            print(f"✅ Xendan Specialized: {total_found} sentences collected")
        
        except Exception as e:
            print(f"⚠️  Xendan Specialized error: {e}")
            self.stats['xendan_specialized'] = 0
    
    def scrape_sekokurd(self, clicks=10):
        """
        Scrape Sekokurd.org categories
        - Articles: page_id=874 (film, politics, feminism, nationalism)
        - Culture: page_id=1614 (art, music, poetry, literature)
        """
        print(f"\n📚 Scraping Sekokurd (Articles + Culture, {clicks} clicks each)...")
        
        categories = [
            ('Articles', 'https://sekokurd.org/?page_id=874'),
            ('Culture', 'https://sekokurd.org/?page_id=1614')
        ]
        
        try:
            articles_found = 0
            
            for cat_name, url in categories:
                print(f"\n   {cat_name}...")
                
                try:
                    self.driver.get(url)
                    time.sleep(3)
                    
                    article_links = []
                    
                    # Click "Load More" button multiple times to load more articles
                    for click in range(clicks):
                        try:
                            # Find and click "Load More" button
                            load_more = self.driver.find_elements(By.CSS_SELECTOR, '.anwp-pg-load-more__btn')
                            
                            if load_more and len(load_more) > 0:
                                self.driver.execute_script("arguments[0].scrollIntoView();", load_more[0])
                                time.sleep(1)
                                load_more[0].click()
                                time.sleep(3)
                            else:
                                break
                        
                        except:
                            break
                    
                    # Collect article titles and links
                    titles = self.driver.find_elements(By.CSS_SELECTOR, '.anwp-pg-post-teaser__title a')
                    
                    for title in titles:
                        text = title.text.strip()
                        href = title.get_attribute('href')
                        
                        if text and self.qc.check(text):
                            self.sentences.add(text)
                            articles_found += 1
                        
                        if href and href not in article_links:
                            article_links.append(href)
                    
                    print(f"      Found {len(article_links)} {cat_name.lower()} links")
                    
                    # Visit article detail pages (limit to 30 per category)
                    for article_url in article_links[:30]:
                        try:
                            self.driver.get(article_url)
                            time.sleep(2)
                            
                            # Get article title
                            try:
                                title_elem = self.driver.find_element(By.CSS_SELECTOR, '.wpr-post-title')
                                title = title_elem.text.strip()
                                if title and self.qc.check(title):
                                    self.sentences.add(title)
                                    articles_found += 1
                            except:
                                pass
                            
                            # Get article content
                            try:
                                content = self.driver.find_element(By.CSS_SELECTOR, '.wpr-post-content')
                                paragraphs = content.find_elements(By.TAG_NAME, 'p')
                                
                                for p in paragraphs:
                                    text = p.text.strip()
                                    if len(text) < 20:
                                        continue
                                    
                                    # Split into sentences
                                    sents = re.split(r'[.؟!،]\s*', text)
                                    for s in sents:
                                        s = s.strip()
                                        if s and self.qc.check(s):
                                            self.sentences.add(s)
                                            articles_found += 1
                            except:
                                pass
                            
                            time.sleep(1.5)
                        
                        except:
                            continue
                
                except Exception as e:
                    print(f"      ⚠️  {cat_name} error: {e}")
                    continue
            
            self.stats['sekokurd'] = articles_found
            print(f"✅ Sekokurd: {articles_found} sentences collected")
        
        except Exception as e:
            print(f"⚠️  Sekokurd error: {e}")
            self.stats['sekokurd'] = 0
    
    def scrape_kurdsat_specialized(self, articles_per_category=20):
        """
        Scrape Kurdsat specialized categories
        - Health: categories/8
        - Science: categories/16
        - Technology: categories/9
        """
        print("\n🔍 Kurdsat Specialized (Health, Science, Tech)...")
        
        categories = [
            ('Health', 'https://kurdsat.tv/ckb/categories/8'),
            ('Science', 'https://kurdsat.tv/ckb/categories/16'),
            ('Technology', 'https://kurdsat.tv/ckb/categories/9')
        ]
        
        try:
            total_found = 0
            
            for cat_name, url in categories:
                print(f"   {cat_name}...")
                
                try:
                    self.driver.get(url)
                    time.sleep(3)
                    
                    # Find all article links
                    all_links = self.driver.find_elements(By.TAG_NAME, 'a')
                    article_links = []
                    
                    for link in all_links:
                        href = link.get_attribute('href')
                        if href and '/articles/' in href and href not in article_links:
                            article_links.append(href)
                    
                    print(f"      Found {len(article_links)} {cat_name.lower()} articles")
                    
                    # Visit article pages
                    for article_url in article_links[:articles_per_category]:
                        try:
                            self.driver.get(article_url)
                            time.sleep(2)
                            
                            # Get title
                            try:
                                title_elem = self.driver.find_element(By.TAG_NAME, 'h1')
                                title = title_elem.text.strip()
                                if title and self.qc.check(title):
                                    self.sentences.add(title)
                                    total_found += 1
                            except:
                                pass
                            
                            # Get paragraphs
                            try:
                                paragraphs = self.driver.find_elements(By.TAG_NAME, 'p')
                                for p in paragraphs:
                                    text = p.text.strip()
                                    if len(text) < 20:
                                        continue
                                    
                                    # Split into sentences
                                    sents = re.split(r'[.؟!،]\s*', text)
                                    for s in sents:
                                        s = s.strip()
                                        if s and self.qc.check(s):
                                            self.sentences.add(s)
                                            total_found += 1
                            except:
                                pass
                            
                            time.sleep(1)
                        
                        except:
                            continue
                
                except Exception as e:
                    print(f"      ⚠️  {cat_name} category error: {e}")
                    continue
            
            self.stats['kurdsat_specialized'] = total_found
            print(f"✅ Kurdsat Specialized: {total_found} sentences collected")
        
        except Exception as e:
            print(f"⚠️  Kurdsat Specialized error: {e}")
            self.stats['kurdsat_specialized'] = 0
    
    def scrape_rudaw_specialized(self, scrolls_per_category=10):
        """
        Scrape Rudaw specialized categories
        - Economy: CategoryID=412626
        - Health: CategoryID=412631
        - Sport: CategoryID=412632
        - Culture: CategoryID=414583
        """
        print("\n🔍 Rudaw Specialized (Economy, Health, Sport, Culture)...")
        
        categories = [
            ('Economy', 'https://www.rudaw.net/sorani/news?CategoryID=412626'),
            ('Health', 'https://www.rudaw.net/sorani/news?CategoryID=412631'),
            ('Sport', 'https://www.rudaw.net/sorani/news?CategoryID=412632'),
            ('Culture', 'https://www.rudaw.net/sorani/news?CategoryID=414583')
        ]
        
        try:
            total_found = 0
            
            for cat_name, url in categories:
                print(f"   {cat_name}...")
                
                try:
                    self.driver.get(url)
                    time.sleep(3)
                    
                    # Scroll to load more articles (same as main Rudaw)
                    for scroll in range(scrolls_per_category):
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)
                    
                    # Find article titles (h3 elements)
                    titles = self.driver.find_elements(By.TAG_NAME, 'h3')
                    
                    for title in titles:
                        text = title.text.strip()
                        if text and self.qc.check(text):
                            self.sentences.add(text)
                            total_found += 1
                    
                    # Try to get article links for detail scraping
                    links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/sorani/"]')
                    article_links = []
                    
                    for link in links:
                        href = link.get_attribute('href')
                        if href and '/sorani/' in href and 'CategoryID' not in href:
                            if href not in article_links:
                                article_links.append(href)
                    
                    print(f"      Found {len(article_links)} {cat_name.lower()} articles")
                    
                    # Visit article detail pages (limit to 15 per category)
                    for article_url in article_links[:15]:
                        try:
                            self.driver.get(article_url)
                            time.sleep(2)
                            
                            # Get article title
                            try:
                                title_elem = self.driver.find_element(By.TAG_NAME, 'h1')
                                title = title_elem.text.strip()
                                if title and self.qc.check(title):
                                    self.sentences.add(title)
                                    total_found += 1
                            except:
                                pass
                            
                            # Get paragraphs
                            paragraphs = self.driver.find_elements(By.TAG_NAME, 'p')
                            
                            for p in paragraphs:
                                text = p.text.strip()
                                if len(text) < 20:
                                    continue
                                
                                # Split into sentences
                                sents = re.split(r'[.؟!،]\s*', text)
                                for s in sents:
                                    s = s.strip()
                                    if s and self.qc.check(s):
                                        self.sentences.add(s)
                                        total_found += 1
                            
                            time.sleep(1)
                        
                        except:
                            continue
                
                except Exception as e:
                    print(f"      ⚠️  {cat_name} category error: {e}")
                    continue
            
            self.stats['rudaw_specialized'] = total_found
            print(f"✅ Rudaw Specialized: {total_found} sentences collected")
        
        except Exception as e:
            print(f"⚠️  Rudaw Specialized error: {e}")
            self.stats['rudaw_specialized'] = 0
    
    def scrape_kurdistan24_specialized(self, pages_per_category=5):
        """
        Scrape Kurdistan24 specialized categories with FlareSolverr
        - Economy: category/1
        - Health: category/4
        - Sport: category/14
        - Culture: category/10
        - Artistic: category/13
        - Technology: category/7
        - Social: category/11
        """
        print("\n🔍 Kurdistan24 Specialized (7 categories via FlareSolverr)...")
        
        categories = [
            ('Economy', 'https://www.kurdistan24.net/ckb/list/category/1'),
            ('Health', 'https://www.kurdistan24.net/ckb/list/category/4'),
            ('Sport', 'https://www.kurdistan24.net/ckb/list/category/14'),
            ('Culture', 'https://www.kurdistan24.net/ckb/list/category/10'),
            ('Artistic', 'https://www.kurdistan24.net/ckb/list/category/13'),
            ('Technology', 'https://www.kurdistan24.net/ckb/list/category/7'),
            ('Social', 'https://www.kurdistan24.net/ckb/list/category/11')
        ]
        
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Check if FlareSolverr is running
            try:
                requests.get('http://localhost:8191/', timeout=5)
            except:
                print("   ⚠️  FlareSolverr not running! Skipping K24 specialized")
                self.stats['kurdistan24_specialized'] = 0
                return
            
            # Create FlareSolverr session
            session_response = requests.post('http://localhost:8191/v1', json={
                "cmd": "sessions.create"
            })
            
            if session_response.status_code != 200:
                print("   ⚠️  Failed to create FlareSolverr session")
                self.stats['kurdistan24_specialized'] = 0
                return
            
            session_id = session_response.json().get('session')
            print(f"   ✅ FlareSolverr session: {session_id}")
            
            total_found = 0
            
            try:
                for cat_name, base_url in categories:
                    print(f"   {cat_name}...")
                    
                    try:
                        article_links = []
                        
                        # Scrape category list pages
                        for page in range(1, pages_per_category + 1):
                            url = f"{base_url}?page={page}" if page > 1 else base_url
                            
                            response = requests.post('http://localhost:8191/v1', json={
                                "cmd": "request.get",
                                "url": url,
                                "session": session_id,
                                "maxTimeout": 60000
                            }, timeout=90)
                            
                            if response.status_code == 200 and response.json().get('status') == 'ok':
                                html = response.json()['solution']['response']
                                soup = BeautifulSoup(html, 'html.parser')
                                
                                # Extract h3 titles
                                h3_titles = soup.find_all('h3')
                                for h3 in h3_titles:
                                    text = h3.get_text(strip=True)
                                    if text and self.qc.check(text):
                                        self.sentences.add(text)
                                        total_found += 1
                                
                                # Collect article links
                                links = soup.find_all('a', href=lambda x: x and '/ckb/story/' in x)
                                for link in links:
                                    href = link.get('href')
                                    if href and href.startswith('http') and href not in article_links:
                                        article_links.append(href)
                                
                                time.sleep(2)
                            else:
                                print(f"      ⚠️  Page {page} failed")
                        
                        print(f"      Found {len(article_links)} {cat_name.lower()} article links")
                        
                        # Visit article detail pages (limit to 10 per category)
                        for article_url in article_links[:10]:
                            try:
                                response = requests.post('http://localhost:8191/v1', json={
                                    "cmd": "request.get",
                                    "url": article_url,
                                    "session": session_id,
                                    "maxTimeout": 60000
                                }, timeout=90)
                                
                                if response.status_code == 200 and response.json().get('status') == 'ok':
                                    html = response.json()['solution']['response']
                                    soup = BeautifulSoup(html, 'html.parser')
                                    
                                    # Get article title
                                    title = soup.find('h1')
                                    if title:
                                        text = title.get_text(strip=True)
                                        if text and self.qc.check(text):
                                            self.sentences.add(text)
                                            total_found += 1
                                    
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
                                                if s and self.qc.check(s):
                                                    self.sentences.add(s)
                                                    total_found += 1
                                    
                                    time.sleep(2)
                            
                            except Exception as e:
                                continue
                    
                    except Exception as e:
                        print(f"      ⚠️  {cat_name} category error: {e}")
                        continue
            
            finally:
                # Destroy FlareSolverr session
                try:
                    requests.post('http://localhost:8191/v1', json={
                        "cmd": "sessions.destroy",
                        "session": session_id
                    })
                except:
                    pass
            
            self.stats['kurdistan24_specialized'] = total_found
            print(f"✅ Kurdistan24 Specialized: {total_found} sentences collected")
        
        except Exception as e:
            print(f"⚠️  Kurdistan24 Specialized error: {e}")
            self.stats['kurdistan24_specialized'] = 0
    
    def save(self, output_file='corpus/kurdish_expanded_batch3.txt'):
        """Save results"""
        sorted_sents = sorted(self.sentences)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Kurdish Expanded Corpus - Batch 3\n")
            f.write(f"# Total: {len(sorted_sents)} unique sentences\n")
            f.write(f"# Kurdsat: ~{self.stats['kurdsat']} | ")
            f.write(f"Rudaw: ~{self.stats['rudaw']} | ")
            f.write(f"Khak TV: ~{self.stats['khak']} | ")
            f.write(f"NRT TV: ~{self.stats['nrt']} | ")
            f.write(f"Awene: ~{self.stats['awene']} | ")
            f.write(f"Kurdistan24: ~{self.stats['kurdistan24']} | ")
            f.write(f"Xendan: ~{self.stats['xendan']} | ")
            f.write(f"Sekokurd: ~{self.stats['sekokurd']} | ")
            f.write(f"Kurdsat Spec: ~{self.stats['kurdsat_specialized']} | ")
            f.write(f"Xendan Spec: ~{self.stats['xendan_specialized']} | ")
            f.write(f"Rudaw Spec: ~{self.stats['rudaw_specialized']} | ")
            f.write(f"K24 Spec: ~{self.stats['kurdistan24_specialized']} | ")
            f.write(f"Awene Spec: ~{self.stats['awene_specialized']}\n")
            f.write("#\n")
            
            for sent in sorted_sents:
                f.write(sent + '\n')
        
        print(f"\n✅ Saved {len(sorted_sents)} sentences to {output_file}")
    
    def cleanup(self):
        self.driver.quit()

def main():
    print("="*70)
    print("KURDISH CORPUS EXPANSION - BATCH 3 (14 SOURCE GROUPS)")
    print("Political + Sport + Economy + Health + Science + Tech + Culture + Art + Social + Academic + Multimedia")
    print("="*70)
    
    scraper = ReliableKurdishScraper()
    
    try:
        # Scrape from all 14 source groups
        scraper.scrape_kurdsat_extended(clicks=30)      # 1. Batch 2 proven (political)
        scraper.scrape_rudaw_extended(scrolls=20)       # 2. Batch 2 proven (political)
        scraper.scrape_khak_extended(pages=10)          # 3. Batch 2 proven (political)
        scraper.scrape_nrt_extended(clicks=15)          # 4. Major news (political)
        scraper.scrape_awene_extended(pages=10)         # 5. Newspaper (political)
        scraper.scrape_kurdistan24_flaresolverr(pages=10)  # 6. With FlareSolverr (political)
        scraper.scrape_xendan_extended(pages=10)        # 7. News portal (political)
        scraper.scrape_sekokurd(clicks=10)              # 8. Articles + Culture (academic)
        scraper.scrape_xendan_specialized(pages_per_category=5)  # 9. Sport+Economy+Tech
        scraper.scrape_kurdsat_specialized(articles_per_category=20)  # 10. Health+Science+Tech
        scraper.scrape_rudaw_specialized(scrolls_per_category=10)  # 11. Economy+Health+Sport+Culture
        scraper.scrape_kurdistan24_specialized(pages_per_category=5)  # 12. 7 categories via FlareSolverr
        scraper.scrape_awene_specialized(articles_per_category=30)  # 13. NEW! 5 categories (Articles+Culture+Economy+Health+Multimedia)
        
        scraper.save()
        
        print("\n" + "="*70)
        print(f"✅ SUCCESS! Collected {len(scraper.sentences)} sentences")
        print(f"   Kurdsat (political): ~{scraper.stats['kurdsat']}")
        print(f"   Rudaw (political): ~{scraper.stats['rudaw']}")
        print(f"   Khak TV: ~{scraper.stats['khak']}")
        print(f"   NRT TV: ~{scraper.stats['nrt']}")
        print(f"   Awene (political): ~{scraper.stats['awene']}")
        print(f"   Kurdistan24 (political): ~{scraper.stats['kurdistan24']}")
        print(f"   Xendan (political): ~{scraper.stats['xendan']}")
        print(f"   Sekokurd (articles+culture): ~{scraper.stats['sekokurd']}")
        print(f"   Xendan Specialized (S+E+T): ~{scraper.stats['xendan_specialized']}")
        print(f"   Kurdsat Specialized (H+S+T): ~{scraper.stats['kurdsat_specialized']}")
        print(f"   Rudaw Specialized (E+H+S+C): ~{scraper.stats['rudaw_specialized']}")
        print(f"   K24 Specialized (Ec+H+S+C+A+T+Soc): ~{scraper.stats['kurdistan24_specialized']}")
        print(f"   Awene Specialized (Art+Cult+Eco+Health+MM): ~{scraper.stats['awene_specialized']}")
        print("="*70)
    
    finally:
        scraper.cleanup()

if __name__ == '__main__':
    main()
