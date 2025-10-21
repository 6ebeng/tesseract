#!/usr/bin/env python3
"""
Intelligent Kurdish Corpus Expander
Collect more high-quality Kurdish sentences from diverse sources
Target: 10,000+ sentences for better model generalization
"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
from collections import Counter
import unicodedata

class QualityChecker:
    """Enhanced quality checking for Kurdish text"""
    
    def __init__(self):
        # Kurdish characters (including Arabic base)
        self.kurdish_chars = set('ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهەوۆیێ')
        self.arabic_chars = set('اأإآبتثجحخدذرزسشصضطظعغفقكلمنهوي')
        self.latin_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        self.digits = set('0123456789٠١٢٣٤٥٦٧٨٩')
        self.zwnj = '\u200c'
    
    def check_quality(self, text, min_words=10, max_words=30, min_purity=70.0):
        """
        Check if text meets quality standards
        
        Returns:
            (is_valid, score, reason)
        """
        
        # Clean text
        text = text.strip()
        if not text:
            return False, 0, "Empty text"
        
        # Word count
        words = text.split()
        word_count = len(words)
        if word_count < min_words:
            return False, 0, f"Too short ({word_count} words)"
        if word_count > max_words:
            return False, 0, f"Too long ({word_count} words)"
        
        # Character composition
        total_chars = 0
        kurdish_count = 0
        arabic_count = 0
        latin_count = 0
        
        for char in text:
            if char in [' ', '\n', '\t', self.zwnj] or char in '.,!?;:()[]{}«»"\'-':
                continue
            
            total_chars += 1
            if char in self.kurdish_chars:
                kurdish_count += 1
            elif char in self.arabic_chars:
                arabic_count += 1
            elif char in self.latin_chars:
                latin_count += 1
            elif char in self.digits:
                pass  # Digits are OK
        
        if total_chars == 0:
            return False, 0, "No valid characters"
        
        # Calculate purity
        kurdish_purity = 100 * kurdish_count / total_chars
        
        if kurdish_purity < min_purity:
            return False, kurdish_purity, f"Low Kurdish purity ({kurdish_purity:.1f}%)"
        
        # Check for repeated content (spam detection)
        if len(set(words)) < len(words) * 0.5:
            return False, 0, "Too much repetition"
        
        # Calculate score (0-100)
        score = kurdish_purity
        
        # Bonus for optimal length
        if 12 <= word_count <= 20:
            score += 5
        
        # Bonus for some ZWNJ (traditional Kurdish)
        zwnj_count = text.count(self.zwnj)
        if zwnj_count > 0:
            score += min(5, zwnj_count)
        
        return True, min(100, score), "OK"

class ExpandedKurdishScraper:
    """Multi-source Kurdish text scraper with quality filtering"""
    
    def __init__(self):
        self.qc = QualityChecker()
        self.sentences = set()
        self.stats = Counter()
        
        # Selenium setup
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument('--disable-gpu')
        opts.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        try:
            self.driver = webdriver.Chrome(
                service=Service('/usr/bin/chromedriver'),
                options=opts
            )
            print("✅ Selenium initialized")
        except Exception as e:
            print(f"⚠️  Selenium failed: {e}")
            self.driver = None
    
    def extract_sentences(self, text):
        """Extract sentences from text"""
        # Split by common Kurdish sentence endings
        sentences = re.split(r'[.!?؟]+\s+', text)
        
        for sent in sentences:
            sent = sent.strip()
            if sent:
                is_valid, score, reason = self.qc.check_quality(sent)
                if is_valid:
                    self.sentences.add(sent)
                    yield sent
    
    def scrape_nrt_news(self, max_articles=200):
        """Scrape NRT News (nrttv.com) - Major Kurdish news source"""
        if not self.driver:
            return
        
        print("\n📰 Scraping NRT News...")
        base_url = "https://www.nrttv.com/ku/cat/News.aspx"
        
        try:
            self.driver.get(base_url)
            time.sleep(3)
            
            # Scroll to load more articles
            for i in range(10):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Find article links
            articles = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='birura']")
            print(f"   Found {len(articles)} articles")
            
            count = 0
            for article in articles[:max_articles]:
                if count >= max_articles:
                    break
                
                try:
                    link = article.get_attribute('href')
                    self.driver.get(link)
                    time.sleep(1)
                    
                    # Extract article body
                    body = self.driver.find_elements(By.CSS_SELECTOR, ".article-content, .news-body, p")
                    text = " ".join([p.text for p in body if p.text])
                    
                    extracted = list(self.extract_sentences(text))
                    if extracted:
                        count += 1
                        self.stats['nrt'] += len(extracted)
                
                except Exception as e:
                    continue
            
            print(f"✅ NRT: {self.stats['nrt']} sentences from {count} articles")
        
        except Exception as e:
            print(f"⚠️  NRT error: {e}")
    
    def scrape_awene_news(self, max_pages=20):
        """Scrape Awene News (awene.com) - Kurdish newspaper"""
        if not self.driver:
            return
        
        print("\n📰 Scraping Awene News...")
        
        try:
            for page in range(1, max_pages + 1):
                url = f"https://www.awene.com/category/news/page/{page}/"
                self.driver.get(url)
                time.sleep(2)
                
                # Get article links
                articles = self.driver.find_elements(By.CSS_SELECTOR, "article a")
                
                for article in articles[:10]:  # 10 per page
                    try:
                        link = article.get_attribute('href')
                        if not link or 'awene.com/page' not in link:
                            continue
                        
                        self.driver.get(link)
                        time.sleep(1)
                        
                        body = self.driver.find_elements(By.CSS_SELECTOR, ".entry-content p, .post-content p")
                        text = " ".join([p.text for p in body if p.text])
                        
                        extracted = list(self.extract_sentences(text))
                        if extracted:
                            self.stats['awene'] += len(extracted)
                    
                    except:
                        continue
                
                print(f"   Page {page}: {self.stats['awene']} total sentences")
        
        except Exception as e:
            print(f"⚠️  Awene error: {e}")
        
        print(f"✅ Awene: {self.stats['awene']} sentences")
    
    def scrape_bassnews(self, max_articles=150):
        """Scrape BasNews (basnews.com/ku) - Kurdish news agency"""
        if not self.driver:
            return
        
        print("\n📰 Scraping BasNews...")
        
        try:
            # Multiple categories
            categories = ['news', 'politics', 'economy', 'culture']
            
            for cat in categories:
                url = f"https://basnews.com/ku/{cat}"
                self.driver.get(url)
                time.sleep(3)
                
                # Scroll to load more
                for _ in range(5):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                
                articles = self.driver.find_elements(By.CSS_SELECTOR, "article a, .article-item a")
                
                for article in articles[:40]:
                    try:
                        link = article.get_attribute('href')
                        if not link or 'basnews.com/ku' not in link:
                            continue
                        
                        self.driver.get(link)
                        time.sleep(1)
                        
                        body = self.driver.find_elements(By.CSS_SELECTOR, ".article-body p, .content p")
                        text = " ".join([p.text for p in body if p.text])
                        
                        extracted = list(self.extract_sentences(text))
                        if extracted:
                            self.stats['basnews'] += len(extracted)
                    
                    except:
                        continue
                
                print(f"   {cat}: {self.stats['basnews']} total sentences")
        
        except Exception as e:
            print(f"⚠️  BasNews error: {e}")
        
        print(f"✅ BasNews: {self.stats['basnews']} sentences")
    
    def save_results(self, output_file='corpus/kurdish_expanded_batch3.txt'):
        """Save collected sentences"""
        if not self.sentences:
            print("⚠️  No sentences collected!")
            return
        
        sorted_sentences = sorted(self.sentences)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Kurdish Expanded Corpus - Batch 3\n")
            f.write(f"# Total: {len(sorted_sentences)} unique sentences\n")
            f.write(f"# Sources: NRT ({self.stats['nrt']}), ")
            f.write(f"Awene ({self.stats['awene']}), ")
            f.write(f"BasNews ({self.stats['basnews']})\n")
            f.write("#\n")
            
            for sent in sorted_sentences:
                f.write(sent + '\n')
        
        print(f"\n✅ Saved {len(sorted_sentences)} sentences to {output_file}")
        print(f"   NRT: {self.stats['nrt']}")
        print(f"   Awene: {self.stats['awene']}")
        print(f"   BasNews: {self.stats['basnews']}")
    
    def cleanup(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()

def main():
    print("="*70)
    print("KURDISH CORPUS EXPANDER - BATCH 3")
    print("Target: 3,000+ new sentences from diverse news sources")
    print("="*70)
    
    scraper = ExpandedKurdishScraper()
    
    try:
        # Scrape multiple sources
        scraper.scrape_nrt_news(max_articles=200)
        scraper.scrape_awene_news(max_pages=20)
        scraper.scrape_bassnews(max_articles=150)
        
        # Save results
        scraper.save_results()
        
        print("\n" + "="*70)
        print("✅ Batch 3 corpus collection complete!")
        print("="*70)
    
    finally:
        scraper.cleanup()

if __name__ == '__main__':
    main()
