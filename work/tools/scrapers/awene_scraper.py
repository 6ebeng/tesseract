"""
Awene Newspaper Scraper
"""

from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
import time


class AweneScraper(BaseScraper):
    """Scraper for Awene (awene.com)"""
    
    def __init__(self):
        super().__init__("Awene")
        self.base_url = "https://www.awene.com/part?section=2"
    
    def scrape_political(self, pages=10):
        """Scrape political news from main section"""
        print(f"\n📰 Scraping {self.name} Political ({pages} pages)...")
        
        try:
            self.init_driver()
            articles_found = 0
            article_links = []
            
            # Scrape list pages
            for page in range(1, pages + 1):
                url = f'https://www.awene.com/part?section=2&page={page}'
                
                if not self.safe_get(url, delay=2):
                    continue
                
                # Extract titles from list
                titles = self.driver.find_elements(By.CSS_SELECTOR, ".newstopsumbtitle a")
                
                for title in titles:
                    text = title.get_attribute('title')
                    if not text:
                        text = title.text.strip()
                    
                    if self.add_sentence(text):
                        articles_found += 1
                    
                    # Collect article links
                    href = title.get_attribute('href')
                    if href and 'detail?article=' in href:
                        article_links.append(href)
                
                print(f"   Page {page}/{pages}: {articles_found} sentences")
            
            # Visit article detail pages (limit based on pages parameter for testing)
            max_articles = min(50, pages * 5)  # 5 articles per page in test mode
            print(f"   Visiting top {max_articles} articles...")
            for link in article_links[:max_articles]:
                try:
                    if not self.safe_get(link, delay=1):
                        continue
                    
                    # Extract article content
                    paragraphs = self.driver.find_elements(By.CSS_SELECTOR, ".viewdesc p")
                    
                    for p in paragraphs:
                        text = p.text.strip()
                        if self.add_sentence(text):
                            articles_found += 1
                except:
                    continue
            
            self.stats['political'] = articles_found
            print(f"✅ {self.name} Political: {articles_found} sentences")
            return articles_found
        
        except Exception as e:
            print(f"⚠️  {self.name} Political error: {e}")
            return 0
    
    def scrape_specialized(self, articles_per_category=30):
        """Scrape specialized categories: Articles, Culture, Economy, Health, Multimedia"""
        print(f"\n📚 Scraping {self.name} Specialized (5 categories, {articles_per_category} articles each)...")
        
        categories = [
            ('Articles', 'https://www.awene.com/articles'),
            ('Culture', 'https://www.awene.com/culture'),
            ('Economy', 'https://www.awene.com/aburi'),
            ('Health', 'https://www.awene.com/health'),
            ('Multimedia', 'https://www.awene.com/multimedia')
        ]
        
        try:
            self.init_driver()
            total_found = 0
            
            for cat_name, url in categories:
                print(f"\n   📂 Category: {cat_name}")
                cat_found = 0
                
                try:
                    if not self.safe_get(url, delay=4):
                        continue
                    
                    # Find all article links on category page
                    all_links = self.driver.find_elements(By.TAG_NAME, 'a')
                    
                    article_links = []
                    for link in all_links:
                        href = link.get_attribute('href')
                        text = link.text.strip()
                        
                        # Filter for article links with titles
                        # Articles category uses 'article?no=' while others use 'detail?article='
                        is_article = href and (('detail?article=' in href) or ('article?no=' in href))
                        
                        if is_article and text and len(text) > 10:
                            # Skip "درێژەی بابەت" (Read more) links
                            if text != "درێژەی بابەت":
                                article_links.append((text, href))
                    
                    # Deduplicate by URL
                    seen_urls = set()
                    unique_articles = []
                    for text, href in article_links:
                        if href not in seen_urls:
                            seen_urls.add(href)
                            unique_articles.append((text, href))
                    
                    print(f"      Found {len(unique_articles)} unique articles")
                    
                    # Collect titles first
                    for text, _ in unique_articles[:articles_per_category]:
                        if self.add_sentence(text):
                            cat_found += 1
                    
                    # Visit article detail pages
                    print(f"      Visiting top {min(articles_per_category, len(unique_articles))} articles...")
                    for _, article_url in unique_articles[:articles_per_category]:
                        try:
                            if not self.safe_get(article_url, delay=2):
                                continue
                            
                            # Extract article content
                            paragraphs = self.driver.find_elements(By.CSS_SELECTOR, ".viewdesc p")
                            
                            for p in paragraphs:
                                text = p.text.strip()
                                if self.add_sentence(text):
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
