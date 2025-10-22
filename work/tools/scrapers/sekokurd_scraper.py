"""
Sekokurd Academic/Cultural Platform Scraper
"""

from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
import time
import re


class SekokurdScraper(BaseScraper):
    """Scraper for Sekokurd (sekokurd.org)"""
    
    def __init__(self):
        super().__init__("Sekokurd")
        # Sekokurd is specialized only (no general political news)
        self.base_url = None
    
    def scrape_political(self, **kwargs):
        """Sekokurd does not have political news section"""
        raise NotImplementedError(f"{self.name} does not implement political scraping")
    
    def scrape_specialized(self, clicks=10, articles_per_category=None, **kwargs):
        """
        Scrape specialized categories:
        - Articles: page_id=874 (film, politics, feminism, nationalism)
        - Culture: page_id=1614 (art, music, poetry, literature)
        """
        # Support articles_per_category for compatibility
        if articles_per_category is not None:
            clicks = max(3, articles_per_category // 5)  # Convert articles to clicks
        
        print(f"\n📚 Scraping {self.name} Specialized (2 categories, {clicks} clicks each)...")
        
        categories = [
            ('Articles', 'https://sekokurd.org/?page_id=874'),
            ('Culture', 'https://sekokurd.org/?page_id=1614')
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
                        
                        if self.add_sentence(text):
                            cat_found += 1
                        
                        if href and href not in article_links:
                            article_links.append(href)
                    
                    print(f"      Found {len(article_links)} {cat_name.lower()} links")
                    
                    # Visit article detail pages (limit to 30 per category)
                    for article_url in article_links[:30]:
                        try:
                            if not self.safe_get(article_url, delay=2):
                                continue
                            
                            # Get article title
                            try:
                                title_elem = self.driver.find_element(By.CSS_SELECTOR, '.wpr-post-title')
                                title = title_elem.text.strip()
                                if self.add_sentence(title):
                                    cat_found += 1
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
                                        if self.add_sentence(s):
                                            cat_found += 1
                            except:
                                pass
                            
                            time.sleep(1.5)
                        
                        except:
                            continue
                    
                    print(f"      ✅ {cat_name}: {cat_found} sentences")
                    total_found += cat_found
                
                except Exception as e:
                    print(f"      ⚠️  {cat_name} error: {e}")
            
            self.stats['specialized'] = total_found
            print(f"\n✅ {self.name} Specialized: {total_found} total sentences")
            return total_found
        
        except Exception as e:
            print(f"⚠️  {self.name} Specialized error: {e}")
            return 0
