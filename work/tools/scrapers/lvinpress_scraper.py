#!/usr/bin/env python3
"""
LvinPress Scraper - Kurdish news website
Website: https://lvinpress.com
"""

from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
import re
import time


class LvinpressScraper(BaseScraper):
    """Scraper for lvinpress.com - Kurdish news"""
    
    def __init__(self):
        super().__init__(name="lvinpress")
        self.source = "lvinpress"
        self.base_url = "https://lvinpress.com"
    
    def scrape_political(self, pages=5):
        """Scrape Kurdistan political/news"""
        category_url = f"{self.base_url}/category/news/kurdistan"
        return self._scrape_category("Kurdistan News", category_url, pages)
    
    def scrape_specialized(self, pages=3, articles_per_category=None, **kwargs):
        """Scrape specialized categories"""
        categories = [
            ('Social Media', f'{self.base_url}/category/socialmedia'),
            ('Opinion', f'{self.base_url}/category/birura'),
        ]
        
        all_sentences = []
        
        for cat_name, cat_url in categories:
            print(f"\n{'='*60}")
            print(f"📂 Category: {cat_name}")
            print(f"{'='*60}")
            
            sentences = self._scrape_category(cat_name, cat_url, pages)
            all_sentences.extend(sentences)
            
            print(f"✅ {cat_name}: {len(sentences)} sentences")
            
            # Brief pause between categories
            time.sleep(2)
        
        return all_sentences
    
    def _scrape_category(self, cat_name, base_url, pages):
        """Scrape articles from a category across multiple pages"""
        all_sentences = []
        
        try:
            self.init_driver()
            
            for page_num in range(1, pages + 1):
                print(f"\n📄 Page {page_num}/{pages}")
                
                # Construct page URL
                if page_num == 1:
                    page_url = base_url
                else:
                    page_url = f"{base_url}/page/{page_num}"
                
                # Load the page
                if not self.safe_get(page_url, delay=3):
                    print(f"⚠️  Failed to load page {page_num}, skipping...")
                    break
                
                # Find article links - Elementor posts
                try:
                    article_elements = self.driver.find_elements(
                        By.CSS_SELECTOR, 
                        "article.elementor-post h3.elementor-post__title a"
                    )
                    
                    article_urls = []
                    for elem in article_elements:
                        try:
                            url = elem.get_attribute('href')
                            # Skip video articles - they have minimal text content
                            if url and ('/news/' in url or '/birura/' in url) and '/video/' not in url:
                                article_urls.append(url)
                        except:
                            continue
                    
                    print(f"   Found {len(article_urls)} articles")
                    
                    # Scrape each article
                    for i, article_url in enumerate(article_urls, 1):
                        print(f"   [{i}/{len(article_urls)}] {article_url}")
                        
                        if not self.safe_get(article_url, delay=2):
                            print(f"      ⚠️  Failed to load article")
                            continue
                        
                        # Extract article content
                        try:
                            # Title - try h1 first, fall back to h2 for video articles
                            title = ""
                            try:
                                title_elem = self.driver.find_element(
                                    By.CSS_SELECTOR,
                                    "h1.elementor-heading-title"
                                )
                                title = title_elem.text.strip()
                            except:
                                try:
                                    title_elem = self.driver.find_element(
                                        By.CSS_SELECTOR,
                                        "h2.elementor-heading-title"
                                    )
                                    title = title_elem.text.strip()
                                except:
                                    pass
                            
                            # Content - theme-post-content widget
                            content_elem = self.driver.find_element(
                                By.CSS_SELECTOR,
                                "div.elementor-widget-theme-post-content div.elementor-widget-container"
                            )
                            content = content_elem.text.strip()
                            
                            # Combine title and content
                            full_text = f"{title}\n{content}"
                            
                            # Split into sentences
                            sentences = self.split_sentences(full_text)
                            valid_sentences = [s for s in sentences if self.is_valid_sentence(s)]
                            
                            all_sentences.extend(valid_sentences)
                            print(f"      ✅ {len(valid_sentences)} sentences")
                            
                        except Exception as e:
                            print(f"      ⚠️  {self.clean_error(e)} (skipped)")
                            continue
                        
                        # Small delay between articles
                        time.sleep(1)
                    
                except Exception as e:
                    print(f"   ⚠️  Failed to find articles: {e}")
                    break
                
                # Delay between pages
                time.sleep(2)
        
        except Exception as e:
            print(f"❌ Category error: {self.clean_error(e)}")
        
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
        
        return all_sentences
    
    def split_sentences(self, text):
        """Split Kurdish text into sentences"""
        # Remove "لڤین" prefix if present
        text = re.sub(r'^لڤین\s*', '', text, flags=re.MULTILINE)
        
        # Split on common Kurdish sentence endings
        sentences = re.split(r'[؟!۔\.\n]+', text)
        
        # Clean and filter
        cleaned = []
        for sent in sentences:
            sent = sent.strip()
            if sent:
                cleaned.append(sent)
        
        return cleaned
    
    def is_valid_sentence(self, sentence):
        """Check if sentence is valid for corpus"""
        # Length check
        word_count = len(sentence.split())
        if word_count < 10 or word_count > 30:
            return False
        
        # Kurdish character ratio check
        kurdish_chars = sum(1 for c in sentence if '\u0600' <= c <= '\u06FF')
        if len(sentence) > 0 and (kurdish_chars / len(sentence)) < 0.7:
            return False
        
        return True
