"""
NRT TV Scraper
"""

from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
import time


class NRTScraper(BaseScraper):
    """Scraper for NRT TV (nrttv.com)"""
    
    def __init__(self):
        super().__init__("NRT")
        self.base_url = "https://nrttv.com/kurd"
    
    def scrape_political(self, clicks=15):
        """Scrape political news from main page"""
        print(f"\n📰 Scraping {self.name} Political ({clicks} clicks)...")
        
        try:
            self.init_driver()
            
            if not self.safe_get(self.base_url, delay=3):
                return 0
            
            # Click "زیاتر..." (Load More) button multiple times
            for i in range(clicks):
                try:
                    button = self.driver.find_element(By.ID, "loadMore")
                    self.driver.execute_script("arguments[0].scrollIntoView();", button)
                    time.sleep(1)
                    button.click()
                    time.sleep(2)
                    
                    if (i + 1) % 5 == 0:
                        print(f"   Clicked {i+1}/{clicks} times...")
                except:
                    print(f"   Stopped at click {i+1} (button not available)")
                    break
            
            articles_found = 0
            
            # Get titles (h2.Name)
            titles = self.driver.find_elements(By.CSS_SELECTOR, "h2.Name")
            for title in titles:
                text = title.text.strip()
                if self.add_sentence(text):
                    articles_found += 1
            
            # Get descriptions (p.de)
            descriptions = self.driver.find_elements(By.CSS_SELECTOR, "p.de")
            for desc in descriptions:
                text = desc.text.strip()
                if self.add_sentence(text):
                    articles_found += 1
            
            # Visit article detail pages for full content
            article_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='detail/']")
            print(f"   Found {len(article_links)} article links, visiting top 50...")
            
            visited_links = set()
            for link_elem in article_links[:50]:
                try:
                    link = link_elem.get_attribute('href')
                    if not link or 'detail/' not in link or link in visited_links:
                        continue
                    
                    visited_links.add(link)
                    
                    if not self.safe_get(link, delay=1):
                        continue
                    
                    # Get full article content
                    content_divs = self.driver.find_elements(By.CSS_SELECTOR, "div[style*='font-size:16px']")
                    
                    for div in content_divs:
                        # Try paragraphs first
                        paragraphs = div.find_elements(By.TAG_NAME, "p")
                        if paragraphs:
                            for p in paragraphs:
                                text = p.text.strip()
                                if self.add_sentence(text):
                                    articles_found += 1
                        else:
                            # Try direct text split by newlines
                            text = div.text.strip()
                            for line in text.split('\n'):
                                line = line.strip()
                                if self.add_sentence(line):
                                    articles_found += 1
                    
                    if len(visited_links) % 10 == 0:
                        print(f"   Visited {len(visited_links)} articles, {articles_found} sentences...")
                
                except:
                    continue
            
            self.stats['political'] = articles_found
            print(f"✅ {self.name} Political: {articles_found} sentences from {len(visited_links)} articles")
            return articles_found
        
        except Exception as e:
            print(f"⚠️  {self.name} Political error: {e}")
            return 0
    
    def scrape_specialized(self, clicks=3, articles_per_category=None, **kwargs):
        """
        Scrape specialized categories:
        - Economy: https://nrttv.com/abury
        - Social: https://nrttv.com/komalayaty
        - Culture: https://nrttv.com/kltwr
        - Science: https://nrttv.com/zanst
        - Technology: https://nrttv.com/teknology
        """
        # Support articles_per_category for compatibility
        if articles_per_category is not None:
            clicks = max(2, articles_per_category // 5)  # Convert articles to clicks
        
        print(f"\n📚 Scraping {self.name} Specialized (5 categories, {clicks} clicks each)...")
        
        categories = [
            ('Economy', 'https://nrttv.com/abury'),
            ('Social', 'https://nrttv.com/komalayaty'),
            ('Culture', 'https://nrttv.com/kltwr'),
            ('Science', 'https://nrttv.com/zanst'),
            ('Technology', 'https://nrttv.com/teknology')
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
                    
                    # Click "Load More" button to load more articles
                    for i in range(clicks):
                        try:
                            button = self.driver.find_element(By.ID, "loadMore")
                            self.driver.execute_script("arguments[0].scrollIntoView();", button)
                            time.sleep(1)
                            button.click()
                            time.sleep(2)
                        except:
                            break
                    
                    # Get article links
                    article_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='detail/']")
                    
                    visited = set()
                    for link_elem in article_links[:20]:  # Limit per category
                        try:
                            link = link_elem.get_attribute('href')
                            if not link or 'detail/' not in link or link in visited:
                                continue
                            
                            visited.add(link)
                            
                            if not self.safe_get(link, delay=1):
                                continue
                            
                            # Get full article content
                            content_divs = self.driver.find_elements(By.CSS_SELECTOR, "div[style*='font-size:16px']")
                            
                            for div in content_divs:
                                # Try paragraphs first
                                paragraphs = div.find_elements(By.TAG_NAME, "p")
                                if paragraphs:
                                    for p in paragraphs:
                                        text = p.text.strip()
                                        if self.add_sentence(text):
                                            cat_found += 1
                                else:
                                    # Try direct text split by newlines
                                    text = div.text.strip()
                                    for line in text.split('\n'):
                                        line = line.strip()
                                        if self.add_sentence(line):
                                            cat_found += 1
                        
                        except:
                            continue
                    
                    print(f"      ✅ {cat_name}: {cat_found} sentences from {len(visited)} articles")
                    total_found += cat_found
                
                except Exception as e:
                    print(f"      ⚠️  {cat_name} error: {e}")
            
            self.stats['specialized'] = total_found
            print(f"\n✅ {self.name} Specialized: {total_found} total sentences")
            return total_found
        
        except Exception as e:
            print(f"⚠️  {self.name} Specialized error: {e}")
            return 0
