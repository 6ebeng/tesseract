"""
GovKrd (Kurdistan Regional Government) Official Website Scraper
"""

from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
import time


class GovKrdScraper(BaseScraper):
    """Scraper for gov.krd official government website"""
    
    def __init__(self):
        super().__init__("GovKrd")
        self.base_url = "https://gov.krd/ka/activities/"
    
    def scrape_political(self, pages=5):
        """Scrape news and press releases from government activities"""
        print(f"\n📰 Scraping {self.name} Political ({pages} pages)...")
        
        try:
            self.init_driver()
            articles_found = 0
            visited_links = set()
            
            # Scrape multiple pages
            for page in range(1, pages + 1):
                url = f"{self.base_url}?page={page}"
                
                if not self.safe_get(url, delay=3):
                    continue
                
                print(f"   Page {page}/{pages}")
                
                # Find all article links
                article_items = self.driver.find_elements(By.CSS_SELECTOR, "div.item a[href*='/ka/activities/']")
                
                page_links = []
                for item in article_items:
                    try:
                        link = item.get_attribute('href')
                        if link and '/ka/activities/' in link and link not in visited_links:
                            visited_links.add(link)
                            page_links.append(link)
                    except:
                        continue
                
                print(f"      Found {len(page_links)} articles on page {page}")
                
                # Visit each article
                for link in page_links[:20]:  # Limit per page
                    try:
                        if not self.safe_get(link, delay=1):
                            continue
                        
                        # Extract title
                        try:
                            title_elem = self.driver.find_element(By.CSS_SELECTOR, "h1.heading.main")
                            title = title_elem.text.strip()
                            if self.add_sentence(title):
                                articles_found += 1
                        except:
                            pass
                        
                        # Extract content paragraphs
                        paragraphs = self.driver.find_elements(By.CSS_SELECTOR, "div.right-col p")
                        
                        for p in paragraphs:
                            text = p.text.strip()
                            if len(text) < 20:
                                continue
                            
                            # Split long paragraphs into sentences
                            import re
                            sentences = re.split(r'[.؟!]\s+', text)
                            
                            for sent in sentences:
                                sent = sent.strip()
                                if self.add_sentence(sent):
                                    articles_found += 1
                    
                    except:
                        continue
                
                print(f"      Processed page {page}: {articles_found} total sentences")
            
            self.stats['political'] = articles_found
            print(f"✅ {self.name} Political: {articles_found} sentences from {len(visited_links)} articles")
            return articles_found
        
        except Exception as e:
            print(f"⚠️  {self.name} Political error: {e}")
            return 0
    
    def scrape_specialized(self, **kwargs):
        """GovKrd is political/government news only"""
        raise NotImplementedError(f"{self.name} does not implement specialized scraping")
