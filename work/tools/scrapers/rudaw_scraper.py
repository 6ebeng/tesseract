"""
Rudaw News Scraper
"""

from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
import time
import re


class RudawScraper(BaseScraper):
    """Scraper for Rudaw (rudaw.net)"""
    
    def __init__(self):
        super().__init__("Rudaw")
        self.base_url = "https://www.rudaw.net/sorani/kurdistan"
    
    def scrape_political(self, scrolls=20):
        """Scrape political news from main Kurdistan page"""
        print(f"\n📰 Scraping {self.name} Political ({scrolls} scrolls)...")
        
        try:
            self.init_driver()
            
            if not self.safe_get(self.base_url, delay=3):
                return 0
            
            # Scroll to load more articles
            for i in range(scrolls):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                if (i + 1) % 5 == 0:
                    print(f"   Scrolled {i+1}/{scrolls} times...")
            
            # Extract article links
            articles = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/sorani/']")
            
            # Filter for actual article URLs
            article_urls = []
            for article in articles:
                try:
                    link = article.get_attribute('href')
                    if link and '/sorani/' in link and re.search(r'/\d+$', link):
                        if link not in article_urls:
                            article_urls.append(link)
                except:
                    continue
            
            print(f"   Found {len(article_urls)} article URLs (filtered)")
            
            articles_found = 0
            
            # Visit articles and extract content
            for idx, link in enumerate(article_urls[:100], 1):  # Limit to first 100
                try:
                    if not self.safe_get(link, delay=1):
                        continue
                    
                    # Extract content from div elements
                    content_divs = self.driver.find_elements(By.CSS_SELECTOR, ".content div")
                    
                    for div in content_divs:
                        text = div.text.strip()
                        if len(text) < 30:
                            continue
                        
                        # Split into sentences
                        sents = re.split(r'[.؟!،]\s*', text)
                        for sent in sents:
                            if self.add_sentence(sent):
                                articles_found += 1
                    
                    if idx % 10 == 0:
                        print(f"   Processed {idx} articles, {articles_found} sentences so far...")
                
                except Exception as e:
                    continue
            
            self.stats['political'] = articles_found
            print(f"✅ {self.name} Political: {articles_found} sentences from {min(len(article_urls), 100)} articles")
            return articles_found
        
        except Exception as e:
            print(f"⚠️  {self.name} Political error: {e}")
            return 0
    
    def scrape_specialized(self, articles_per_category=50, **kwargs):
        """Scrape specialized categories: Economy, Health, Sport, Culture, Interview"""
        scrolls_per_category = articles_per_category // 10  # Convert articles to scrolls
        print(f"\n📚 Scraping {self.name} Specialized (5 categories, {scrolls_per_category} scrolls each)...")
        
        categories = [
            ('Economy', 'https://www.rudaw.net/sorani/business'),
            ('Health', 'https://www.rudaw.net/sorani/news?CategoryID=412631'),
            ('Sport', 'https://www.rudaw.net/sorani/news?CategoryID=412632'),
            ('Culture', 'https://www.rudaw.net/sorani/culture'),
            ('Interview', 'https://www.rudaw.net/sorani/news?CategoryID=412627')
        ]
        
        try:
            self.init_driver()
            total_found = 0
            
            for cat_name, url in categories:
                print(f"\n   📂 Category: {cat_name}")
                cat_found = 0
                
                try:
                    if not self.safe_get(url, delay=3):
                        continue
                    
                    # Scroll to load articles
                    for i in range(scrolls_per_category):
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)
                    
                    # Extract article links
                    articles = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/sorani/']")
                    
                    # Filter for actual article URLs (ending with numbers)
                    article_urls = []
                    for article in articles:
                        try:
                            link = article.get_attribute('href')
                            if link and '/sorani/' in link and re.search(r'/\d+$', link):
                                if link not in article_urls:
                                    article_urls.append(link)
                        except:
                            continue
                    
                    print(f"      Found {len(article_urls)} article URLs")
                    
                    visited = 0
                    for link in article_urls[:20]:  # Process up to 20 articles
                        try:
                            if not self.safe_get(link, delay=1):
                                continue
                            
                            visited += 1
                            
                            # Extract content from div elements
                            content_divs = self.driver.find_elements(By.CSS_SELECTOR, ".content div")
                            
                            article_sents = 0
                            for div in content_divs:
                                text = div.text.strip()
                                if len(text) < 30:
                                    continue
                                
                                # Split into sentences
                                sents = re.split(r'[.؟!،]\s*', text)
                                for sent in sents:
                                    if self.add_sentence(sent):
                                        cat_found += 1
                                        article_sents += 1
                            
                            if visited % 5 == 0:
                                print(f"      Processed {visited} articles, {cat_found} sentences so far...")
                        
                        except:
                            continue
                    
                    print(f"      ✅ {cat_name}: {cat_found} sentences from {visited} articles")
                    total_found += cat_found
                
                except Exception as e:
                    print(f"      ⚠️  {cat_name} error: {e}")
            
            self.stats['specialized'] = total_found
            print(f"\n✅ {self.name} Specialized: {total_found} total sentences")
            return total_found
        
        except Exception as e:
            print(f"⚠️  {self.name} Specialized error: {e}")
            return 0
