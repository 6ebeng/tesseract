"""
Sharpress News Scraper
"""

from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
import time
import re


class SharpressScraper(BaseScraper):
    """Scraper for Sharpress (sharpress.net)"""
    
    def __init__(self):
        super().__init__("Sharpress")
        self.base_url = "https://www.sharpress.net"
    
    def scrape_political(self, pages=5):
        """Scrape Kurdistan political news"""
        print(f"\n📰 Scraping {self.name} Political ({pages} pages)...")
        
        # Kurdistan political news category
        category_url = "https://www.sharpress.net/all-hawal.aspx?Cor=Herem&Nawnishan=%DA%A9%D9%88%D8%B1%D8%AF%D8%B3%D8%AA%D8%A7%D9%86"
        
        return self._scrape_category("Kurdistan", category_url, pages)
    
    def scrape_specialized(self, pages=3, articles_per_category=None, **kwargs):
        """
        Scrape specialized categories:
        - Economy: Business and economy
        - Sport: Sports news
        - Culture: Arts and culture
        - Health: Health and medical news
        - Opinion: Opinion pieces and editorials
        - Research and Analysis: Research articles and analysis
        """
        # Support articles_per_category for compatibility
        if articles_per_category is not None:
            pages = max(2, articles_per_category // 10)  # Convert articles to pages
        
        print(f"\n📚 Scraping {self.name} Specialized (6 categories, {pages} pages each)...")
        
        categories = [
            ('Economy', 'https://www.sharpress.net/all-hawal.aspx?Cor=abwri&Nawnishan=%D8%A6%D8%A7%D8%A8%D9%88%D8%B1%DB%8C'),
            ('Sport', 'https://www.sharpress.net/all-hawal.aspx?Cor=Werziş&Nawnishan=%D9%88%DB%95%D8%B1%D8%B2%D8%B4'),
            ('Culture', 'https://www.sharpress.net/all-hawal.aspx?Cor=Kültür&Nawnishan=%DA%A9%D9%88%D9%84%D8%AA%D9%88%D9%88%D8%B1'),
            ('Health', 'https://www.sharpress.net/all-hawal.aspx?Cor=tandrwsti&Nawnishan=%D8%AA%DB%95%D9%86%D8%AF%D8%B1%D9%88%D8%B3%D8%AA%DB%8C'),
            ('Opinion', 'https://www.sharpress.net/opinion.aspx?Cor=Birura&Nawnishan=%D8%A8%DB%8C%D8%B1%D9%88%DA%95%D8%A7'),
            ('Research and Analysis', 'https://www.sharpress.net/all-hawal.aspx?Cor=Dose&Nawnishan=%D8%AA%D9%88%DB%8E%DA%98%DB%8C%D9%86%DB%95%D9%88%DB%95%20%D9%88%20%D8%B4%DB%8C%DA%A9%D8%A7%D8%B1%DB%8C%DB%8C')
        ]
        
        try:
            self.init_driver()
            total_found = 0
            
            for cat_name, url in categories:
                print(f"\n   📂 Category: {cat_name}")
                cat_found = self._scrape_category(cat_name, url, pages)
                total_found += cat_found
                print(f"      ✅ {cat_name}: {cat_found} sentences")
            
            self.stats['specialized'] = total_found
            print(f"\n✅ {self.name} Specialized: {total_found} total sentences")
            return total_found
        
        except Exception as e:
            print(f"⚠️  {self.name} Specialized error: {e}")
            return 0
    
    def _scrape_category(self, cat_name, base_url, pages):
        """Helper method to scrape a category with pagination - uses fresh browser for each page"""
        articles_found = 0
        visited_links = set()
        
        # Process each page with a fresh browser session
        for page in range(1, pages + 1):
            try:
                # Initialize fresh browser for each page (option 3: stability over speed)
                if hasattr(self, 'driver') and self.driver is not None:
                    try:
                        self.driver.quit()
                    except:
                        pass
                
                self.init_driver()
                print(f"   Page {page}/{pages}")
                
                # Build the page URL
                if page == 1:
                    page_url = base_url
                else:
                    # Navigate directly to the page URL by clicking pagination would be complex
                    # So we load the category page and click the page number
                    page_url = base_url
                
                # Load the page
                if not self.safe_get(page_url, delay=3):
                    print(f"      Failed to load page {page}")
                    break
                
                # If not page 1, click on the page number
                if page > 1:
                    time.sleep(2)
                    try:
                        pagination = self.driver.find_element(By.ID, "ctl00_Main_PeopleDataPager")
                        page_buttons = pagination.find_elements(By.CSS_SELECTOR, "a.numericbutton")
                        
                        clicked = False
                        for button in page_buttons:
                            button_text = button.text.strip()
                            if button_text == str(page):
                                self.driver.execute_script("arguments[0].scrollIntoView();", button)
                                time.sleep(1)
                                button.click()
                                time.sleep(3)
                                clicked = True
                                break
                        
                        if not clicked:
                            print(f"      Page {page} button not found")
                            break
                    except Exception as e:
                        print(f"      Pagination error on page {page}: {e}")
                        break
                
                # Find all article links on current page
                # Try both regular articles and opinion articles
                article_links = self.driver.find_elements(By.CSS_SELECTOR, "div.more-news-page ul li a, div.birura-page ul li a")
                
                page_links = []
                for link_elem in article_links:
                    try:
                        link = link_elem.get_attribute('href')
                        # Accept both all-detail.aspx and op-detail.aspx
                        if link and ('all-detail.aspx' in link or 'op-detail.aspx' in link) and link not in visited_links:
                            visited_links.add(link)
                            page_links.append(link)
                    except:
                        continue
                
                print(f"      Found {len(page_links)} articles on page {page}")
                
                # Visit each article
                for link in page_links[:15]:  # Limit per page
                    try:
                        if not self.safe_get(link, delay=1):
                            continue
                        
                        # Extract title
                        try:
                            title_elem = self.driver.find_element(By.CSS_SELECTOR, "h1.detail-title")
                            title = title_elem.text.strip()
                            if self.add_sentence(title):
                                articles_found += 1
                        except:
                            pass
                        
                        # Extract content paragraphs
                        try:
                            # Try both regular content and opinion content
                            try:
                                content_div = self.driver.find_element(By.CSS_SELECTOR, "div.detail-content")
                            except:
                                content_div = self.driver.find_element(By.CSS_SELECTOR, "div.detail-big div.detail-content")
                            
                            paragraphs = content_div.find_elements(By.TAG_NAME, "p")
                            
                            for p in paragraphs:
                                text = p.text.strip()
                                if len(text) < 20:
                                    continue
                                
                                # Split long paragraphs into sentences
                                sentences = re.split(r'[.؟!]\s+', text)
                                
                                for sent in sentences:
                                    sent = sent.strip()
                                    if self.add_sentence(sent):
                                        articles_found += 1
                        except:
                            pass
                    
                    except:
                        continue
                
                print(f"      Processed page {page}: {articles_found} total sentences")
                
            except Exception as e:
                print(f"      ⚠️  Page {page}: {self.clean_error(e)}")
                break
        
        # Store results
        if cat_name == "Kurdistan":
            self.stats['political'] = articles_found
            print(f"✅ {self.name} Political: {articles_found} sentences from {len(visited_links)} articles")
        
        return articles_found

