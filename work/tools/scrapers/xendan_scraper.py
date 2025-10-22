"""
Xendan News Portal Scraper
"""

from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
import time
import re


class XendanScraper(BaseScraper):
    """Scraper for Xendan (xendan.org)"""
    
    def __init__(self):
        super().__init__("Xendan")
        self.base_url = "https://www.xendan.org/babetakan?babet=1&title=%DA%A9%D9%88%D8%B1%D8%AF%D8%B3%D8%AA%D8%A7%D9%86"
    
    def scrape_political(self, pages=10):
        """Scrape political/Kurdistan news"""
        print(f"\n📰 Scraping {self.name} Political ({pages} pages)...")
        
        try:
            self.init_driver()
            articles_found = 0
            article_links = []
            
            # Scrape article list pages
            for page in range(1, pages + 1):
                try:
                    if not self.safe_get(self.base_url, delay=3):
                        continue
                    
                    # Find article cards
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
                            if self.add_sentence(title):
                                articles_found += 1
                            
                            # Store link for detail scraping
                            if link and link not in article_links:
                                article_links.append(link)
                        except:
                            continue
                    
                    # Try to click "دواتر" (next) button
                    try:
                        next_btn = self.driver.find_element(By.CSS_SELECTOR, 'a.nextbutton')
                        if next_btn.text == 'دواتر':
                            self.driver.execute_script("arguments[0].click();", next_btn)
                            time.sleep(2)
                    except:
                        print(f"   Stopped at page {page} (no next button)")
                        break
                
                except Exception as e:
                    print(f"   ⚠️  Page {page} failed: {e}")
            
            print(f"   Found {len(article_links)} articles, visiting top 50...")
            
            # Visit article detail pages
            for link in article_links[:50]:
                try:
                    if not self.safe_get(link, delay=2):
                        continue
                    
                    # Get article title
                    try:
                        title_elem = self.driver.find_element(By.CSS_SELECTOR, '.detail-top h1')
                        title = title_elem.text.strip()
                        if self.add_sentence(title):
                            articles_found += 1
                    except:
                        pass
                    
                    # Get article body paragraphs
                    paragraphs = self.driver.find_elements(By.CSS_SELECTOR, '.detail-big-text-p p')
                    
                    for p in paragraphs:
                        text = p.text.strip()
                        if len(text) < 20:
                            continue
                        
                        # Split into sentences
                        sents = re.split(r'[.؟!،]\s*', text)
                        for s in sents:
                            s = s.strip()
                            if self.add_sentence(s):
                                articles_found += 1
                
                except:
                    continue
            
            self.stats['political'] = articles_found
            print(f"✅ {self.name} Political: {articles_found} sentences")
            return articles_found
        
        except Exception as e:
            print(f"⚠️  {self.name} Political error: {e}")
            return 0
    
    def scrape_specialized(self, pages_per_category=5, articles_per_category=None, **kwargs):
        """Scrape specialized categories: Sport, Economy, Technology"""
        # Support both parameter names for compatibility
        if articles_per_category is not None:
            pages_per_category = max(1, articles_per_category // 10)  # Convert articles to pages
        
        print(f"\n📚 Scraping {self.name} Specialized (3 categories, {pages_per_category} pages each)...")
        
        categories = [
            ('Sport', 'https://www.xendan.org/Sport/babetakan?babet=20'),
            ('Economy', 'https://www.xendan.org/babetakan?babet=8'),
            ('Technology', 'https://www.xendan.org/babetakan?babet=7')
        ]
        
        try:
            self.init_driver()
            total_found = 0
            
            for cat_name, base_url in categories:
                print(f"\n   📂 Category: {cat_name}")
                cat_found = 0
                article_links = []
                
                try:
                    # Scrape category pages
                    for page in range(1, pages_per_category + 1):
                        if not self.safe_get(base_url, delay=3):
                            continue
                        
                        # Find article cards
                        cards = self.driver.find_elements(By.CSS_SELECTOR, '.card-small')
                        
                        for card in cards:
                            try:
                                link_elem = card.find_element(By.XPATH, '..')
                                link = link_elem.get_attribute('href')
                                
                                title_elem = card.find_element(By.CSS_SELECTOR, 'h2')
                                title = title_elem.text.strip()
                                
                                if self.add_sentence(title):
                                    cat_found += 1
                                
                                if link and link not in article_links:
                                    article_links.append(link)
                            except:
                                continue
                        
                        # Try next button
                        try:
                            next_btn = self.driver.find_element(By.CSS_SELECTOR, 'a.nextbutton')
                            if next_btn.text == 'دواتر':
                                self.driver.execute_script("arguments[0].click();", next_btn)
                                time.sleep(2)
                        except:
                            break
                    
                    # Visit article details
                    for link in article_links[:20]:  # Limit per category
                        try:
                            if not self.safe_get(link, delay=1.5):
                                continue
                            
                            # Get paragraphs
                            paragraphs = self.driver.find_elements(By.CSS_SELECTOR, '.detail-big-text-p p')
                            
                            for p in paragraphs:
                                text = p.text.strip()
                                if len(text) < 20:
                                    continue
                                
                                sents = re.split(r'[.؟!،]\s*', text)
                                for s in sents:
                                    s = s.strip()
                                    if self.add_sentence(s):
                                        cat_found += 1
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
