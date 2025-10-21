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
                    url = f'https://www.kurdistan24.net/ckb/list/country/%DA%A9%D9%88%D8%B1%D8%AF%D8%B3%D8%AA%D8%A7%D9%86?page={page}'
                    
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
            f.write(f"Kurdistan24: ~{self.stats['kurdistan24']}\n")
            f.write("#\n")
            
            for sent in sorted_sents:
                f.write(sent + '\n')
        
        print(f"\n✅ Saved {len(sorted_sents)} sentences to {output_file}")
    
    def cleanup(self):
        self.driver.quit()

def main():
    print("="*70)
    print("KURDISH CORPUS EXPANSION - BATCH 3 (6 SOURCES)")
    print("Proven sources + NEW: NRT TV, Awene, Kurdistan24")
    print("="*70)
    
    scraper = ReliableKurdishScraper()
    
    try:
        # Scrape from all 6 sources
        scraper.scrape_kurdsat_extended(clicks=30)      # 1. Batch 2 proven
        scraper.scrape_rudaw_extended(scrolls=20)       # 2. Batch 2 proven
        scraper.scrape_khak_extended(pages=10)          # 3. Batch 2 proven
        scraper.scrape_nrt_extended(clicks=15)          # 4. NEW! Major news
        scraper.scrape_awene_extended(pages=10)         # 5. NEW! Newspaper
        scraper.scrape_kurdistan24_flaresolverr(pages=10)  # 6. NEW! With FlareSolverr
        
        scraper.save()
        
        print("\n" + "="*70)
        print(f"✅ SUCCESS! Collected {len(scraper.sentences)} sentences")
        print(f"   Kurdsat: {scraper.stats['kurdsat']}")
        print(f"   Rudaw: {scraper.stats['rudaw']}")
        print(f"   Khak TV: {scraper.stats['khak']}")
        print(f"   NRT TV: {scraper.stats['nrt']}")
        print(f"   Awene: {scraper.stats['awene']}")
        print(f"   Kurdistan24: {scraper.stats['kurdistan24']}")
        print("="*70)
    
    finally:
        scraper.cleanup()

if __name__ == '__main__':
    main()
