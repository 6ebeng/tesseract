#!/usr/bin/env python3
"""
Balinde Scraper - Kurdish poetry and literature website
Website: https://balinde.com
"""

from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
import re
import time


class BalindeScraper(BaseScraper):
    """Scraper for balinde.com - Kurdish poetry and literature"""
    
    def __init__(self):
        super().__init__(name="balinde")
        self.source = "balinde"
        self.base_url = "https://balinde.com"
    
    def scrape_political(self, pages=5):
        """
        Balinde is a poetry/literature site, not political news.
        Use scrape_specialized instead for Kurdish Poetry category.
        """
        print(f"\n⚠️  {self.name} does not have political content")
        print(f"   Use scrape_specialized() for poetry/literature")
        return 0
    
    def scrape_specialized(self, pages=5, articles_per_category=None, **kwargs):
        """Scrape Kurdish Poetry and Article categories"""
        categories = [
            ('Kurdish Poetry', f'{self.base_url}/category/kurdishpoem'),
            ('Articles', f'{self.base_url}/category/wtar'),
        ]
        
        all_sentences = []
        
        for cat_name, cat_url in categories:
            print(f"\n{'='*60}")
            print(f"📂 Category: {cat_name}")
            print(f"{'='*60}")
            
            sentences = self._scrape_category(cat_name, cat_url, pages)
            all_sentences.extend(sentences)
            
            print(f"✅ {cat_name}: {len(sentences)} lines")
            
            # Brief pause between categories
            time.sleep(2)
        
        return all_sentences
    
    def _scrape_category(self, cat_name, base_url, pages):
        """Scrape poetry articles from category across multiple pages"""
        all_sentences = []
        
        try:
            self.init_driver()
            
            for page_num in range(1, pages + 1):
                print(f"\n📄 Page {page_num}/{pages}")
                
                # Construct page URL
                page_url = f"{base_url}/page/{page_num}/"
                
                # Load the page
                if not self.safe_get(page_url, delay=3):
                    print(f"⚠️  Failed to load page {page_num}, skipping...")
                    break
                
                # Find article links - cards with href
                try:
                    article_elements = self.driver.find_elements(
                        By.CSS_SELECTOR, 
                        "div.cards a.card"
                    )
                    
                    article_urls = []
                    for elem in article_elements:
                        try:
                            url = elem.get_attribute('href')
                            if url and self.base_url in url:
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
                            # Content is in div.poet-timeline
                            content_div = self.driver.find_element(
                                By.CSS_SELECTOR,
                                "div.poet-timeline"
                            )
                            
                            # Get all text content
                            full_text = content_div.text.strip()
                            
                            # Split into sentences/lines
                            # Poetry uses line breaks as natural separators
                            lines = full_text.split('\n')
                            
                            valid_sentences = []
                            for line in lines:
                                line = line.strip()
                                
                                # Skip empty lines, dates, and very short lines
                                if not line or len(line) < 15:
                                    continue
                                
                                # Skip lines that are just dates or metadata
                                if re.match(r'^(January|February|March|April|May|June|July|August|September|October|November|December)', line):
                                    continue
                                
                                # Check if line is valid sentence
                                if self.is_valid_sentence(line):
                                    valid_sentences.append(line)
                            
                            all_sentences.extend(valid_sentences)
                            print(f"      ✅ {len(valid_sentences)} lines")
                            
                        except Exception as e:
                            print(f"      ⚠️  {self.clean_error(e)} (skipped)")
                            continue
                        
                        # Small delay between articles
                        time.sleep(1)
                    
                except Exception as e:
                    print(f"   ⚠️  Failed to find articles: {self.clean_error(e)}")
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
    
    def is_valid_sentence(self, sentence):
        """
        Check if sentence/line is valid for corpus.
        Poetry has different requirements than news.
        """
        # Length check - poetry lines can be shorter
        word_count = len(sentence.split())
        if word_count < 5 or word_count > 40:  # More flexible for poetry
            return False
        
        # Kurdish character ratio check
        kurdish_chars = sum(1 for c in sentence if '\u0600' <= c <= '\u06FF')
        if len(sentence) > 0 and (kurdish_chars / len(sentence)) < 0.6:  # Slightly lower threshold
            return False
        
        # Skip lines that are purely metadata
        metadata_patterns = [
            r'^\d{4}$',  # Just a year
            r'^[\d\s\-/]+$',  # Just dates/numbers
            r'^[۰-۹]+$',  # Just Arabic-Indic numerals
        ]
        
        for pattern in metadata_patterns:
            if re.match(pattern, sentence.strip()):
                return False
        
        return True
