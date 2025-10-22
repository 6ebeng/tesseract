"""
Khak TV Scraper
"""

from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
import time


class KhakScraper(BaseScraper):
    """Scraper for Khak TV (khaktv.net)"""
    
    def __init__(self):
        super().__init__("Khak")
        self.base_url = "https://www.khaktv.net/article?group=5"
    
    def scrape_political(self, pages=10):
        """Scrape political news"""
        print(f"\n📰 Scraping {self.name} Political ({pages} pages)...")
        
        try:
            self.init_driver()
            articles_found = 0
            
            for page in range(1, pages + 1):
                url = f'https://www.khaktv.net/article?group=5&page={page}'
                
                if not self.safe_get(url, delay=2):
                    continue
                
                # Extract article links
                links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/article/']")
                
                visited = 0
                for link_elem in links:
                    if visited >= 15:  # 15 articles per page
                        break
                    
                    try:
                        link = link_elem.get_attribute('href')
                        if not link or '/article/' not in link:
                            continue
                        
                        if not self.safe_get(link, delay=1):
                            continue
                        
                        visited += 1
                        
                        # Extract content from main element (Khak uses modern structure without <p> tags)
                        try:
                            main_content = self.driver.find_element(By.TAG_NAME, "main")
                            text = main_content.text.strip()
                            
                            # Split into sentences and add
                            import re
                            sentences = re.split(r'[.؟!]\s+', text)
                            for sent in sentences:
                                sent = sent.strip()
                                if self.add_sentence(sent):
                                    articles_found += 1
                        except:
                            # Fallback to paragraphs
                            paragraphs = self.driver.find_elements(By.CSS_SELECTOR, ".html-content p, .content p, p")
                            for p in paragraphs:
                                text = p.text.strip()
                                if self.add_sentence(text):
                                    articles_found += 1
                    
                    except:
                        continue
                
                print(f"   Page {page}/{pages}: {articles_found} total sentences")
            
            self.stats['political'] = articles_found
            print(f"✅ {self.name} Political: {articles_found} sentences")
            return articles_found
        
        except Exception as e:
            print(f"⚠️  {self.name} Political error: {e}")
            return 0
    
    def scrape_specialized(self, **kwargs):
        """Khak TV does not have specialized categories"""
        raise NotImplementedError(f"{self.name} does not implement specialized scraping")
