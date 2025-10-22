"""
Kurdsat TV Scraper
"""

from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
import time


class KurdsatScraper(BaseScraper):
    """Scraper for Kurdsat TV (kurdsat.tv)"""
    
    def __init__(self):
        super().__init__("Kurdsat")
        self.base_url = "https://kurdsat.tv/ckb/news"
    
    def scrape_political(self, clicks=30):
        """Scrape political news from main news page"""
        print(f"\n📰 Scraping {self.name} Political ({clicks} clicks)...")
        
        try:
            self.init_driver()
            
            if not self.safe_get(self.base_url, delay=3):
                return 0
            
            # Try to click "زیاتر ببینە" (Load More) button
            # Note: Button click often intercepted by header, but we can get articles without it
            for i in range(min(clicks, 5)):  # Limit to 5 attempts
                try:
                    button = self.driver.find_element(By.XPATH, "//button[contains(text(),'زیاتر ببینە')]")
                    
                    # Scroll past the button to avoid header interception
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                    time.sleep(1)
                    
                    # Use JavaScript click (more reliable)
                    self.driver.execute_script("arguments[0].click();", button)
                    time.sleep(2)
                    
                    if (i + 1) % 5 == 0:
                        print(f"   Clicked {i+1}/{clicks} times...")
                except Exception as e:
                    print(f"   Stopped at click {i+1} (button not available)")
                    break
            
            # Extract article links - store hrefs first to avoid stale elements
            articles = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/ckb/news/']")
            article_links = []
            
            for article in articles:
                try:
                    link = article.get_attribute('href')
                    if link and '/ckb/news/' in link and link not in article_links:
                        article_links.append(link)
                except:
                    continue
            
            print(f"   Found {len(article_links)} article links")
            
            articles_found = 0
            
            # Visit articles and extract content
            for link in article_links[:50]:  # Limit to 50 articles
                try:
                    if not self.safe_get(link, delay=1):
                        continue
                    
                    # Try multiple selectors for content
                    paragraphs = self.driver.find_elements(By.CSS_SELECTOR, ".article-body p")
                    if not paragraphs:
                        paragraphs = self.driver.find_elements(By.CSS_SELECTOR, ".content p")
                    if not paragraphs:
                        # Fallback to all p tags
                        paragraphs = self.driver.find_elements(By.TAG_NAME, "p")
                    
                    for p in paragraphs:
                        text = p.text.strip()
                        if self.add_sentence(text):
                            articles_found += 1
                
                except Exception:
                    continue
            
            self.stats['political'] = articles_found
            print(f"✅ {self.name} Political: {articles_found} sentences from {len(article_links[:50])} articles")
            return articles_found
        
        except Exception as e:
            print(f"⚠️  {self.name} Political error: {e}")
            return 0
    
    def scrape_specialized(self, articles_per_category=20):
        """
        Scrape specialized categories: Health, Science, Technology
        Note: May be slow due to page load times, but functional
        """
        print(f"\n📚 Scraping {self.name} Specialized (3 categories, {articles_per_category} articles each)...")
        
        categories = [
            ('Health', 'https://kurdsat.tv/ckb/categories/8'),
            ('Science', 'https://kurdsat.tv/ckb/categories/16'),
            ('Technology', 'https://kurdsat.tv/ckb/categories/9')
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
                    
                    # Find all article links (look for /articles/ pattern)
                    all_links = self.driver.find_elements(By.TAG_NAME, 'a')
                    article_links = []
                    
                    for link_elem in all_links:
                        href = link_elem.get_attribute('href')
                        if href and '/articles/' in href and href not in article_links:
                            article_links.append(href)
                    
                    print(f"      Found {len(article_links)} {cat_name.lower()} article links")
                    
                    # Visit articles
                    visited = 0
                    for link in article_links[:articles_per_category]:
                        if visited >= articles_per_category:
                            break
                        
                        try:
                            if not self.safe_get(link, delay=2):
                                continue
                            
                            visited += 1
                            
                            # Get title
                            try:
                                title_elem = self.driver.find_element(By.TAG_NAME, 'h1')
                                title = title_elem.text.strip()
                                if self.add_sentence(title):
                                    cat_found += 1
                            except:
                                pass
                            
                            # Extract paragraphs
                            paragraphs = self.driver.find_elements(By.TAG_NAME, 'p')
                            
                            for p in paragraphs:
                                text = p.text.strip()
                                if self.add_sentence(text):
                                    cat_found += 1
                        
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
