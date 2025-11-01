#!/usr/bin/env python3
"""
Kurdish Wikipedia Biography Scraper
Collects biographical text from Kurdish Wikipedia to diversify training corpus.
Target: 500+ high-quality biographical sentences with 6-10% ZWNJ density.
"""

import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path
import time
from urllib.parse import urljoin, quote
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WikipediaBioScraper:
    def __init__(self):
        self.base_url = "https://ckb.wikipedia.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def extract_sentences(self, text):
        """Extract sentences from Kurdish text"""
        if not text:
            return []
        
        # Split on Kurdish sentence boundaries
        # Kurdish uses: . (U+002E), ؟ (U+061F), ! (U+0021)
        sentences = re.split(r'[.؟!]+\s+', text)
        
        result = []
        for sent in sentences:
            sent = sent.strip()
            
            # Filter criteria:
            # - Must be at least 30 characters
            # - Must start with Kurdish character
            # - Must have mostly Kurdish script
            if len(sent) < 30:
                continue
                
            # Check if starts with Kurdish/Arabic script
            if not sent or not ('\u0600' <= sent[0] <= '\u06FF' or sent[0] == ' '):
                continue
            
            # Count Kurdish vs Latin characters
            kurdish_chars = sum(1 for c in sent if '\u0600' <= c <= '\u06FF')
            latin_chars = sum(1 for c in sent if c.isalpha() and c.isascii())
            
            if kurdish_chars < 10:  # Too short in Kurdish
                continue
                
            total_alpha = kurdish_chars + latin_chars
            if total_alpha > 0 and (kurdish_chars / total_alpha) < 0.8:
                continue  # Too much Latin
            
            # Clean up
            sent = re.sub(r'\s+', ' ', sent)  # Normalize whitespace
            sent = re.sub(r'^\s*[-•*]\s*', '', sent)  # Remove list markers
            
            if len(sent) >= 30:
                result.append(sent)
        
        return result
    
    def scrape_page(self, url):
        """Scrape a single Wikipedia page"""
        try:
            logging.info(f"Scraping: {url}")
            response = self.session.get(url, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                logging.warning(f"Failed to fetch {url}: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get main content
            content = soup.find('div', {'id': 'mw-content-text'})
            if not content:
                logging.warning(f"No content found in {url}")
                return []
            
            # Remove unwanted elements
            for element in content.find_all(['table', 'script', 'style', 'sup', 'ref']):
                element.decompose()
            
            # Extract paragraphs
            paragraphs = content.find_all('p')
            
            sentences = []
            for p in paragraphs:
                text = p.get_text()
                sents = self.extract_sentences(text)
                sentences.extend(sents)
            
            logging.info(f"  Extracted: {len(sentences)} sentences")
            return sentences
            
        except Exception as e:
            logging.error(f"Error scraping {url}: {e}")
            return []
    
    def get_category_pages(self, category_url, limit=50):
        """Get pages from a Wikipedia category"""
        try:
            logging.info(f"Fetching category: {category_url}")
            response = self.session.get(category_url, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                logging.warning(f"Failed to fetch category: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all page links in category
            pages = []
            mw_pages = soup.find('div', {'id': 'mw-pages'})
            if not mw_pages:
                logging.warning("No pages div found")
                return []
            
            links = mw_pages.find_all('a')
            for link in links[:limit]:
                href = link.get('href', '')
                if href.startswith('/wiki/') and ':' not in href:  # Avoid special pages
                    full_url = urljoin(self.base_url, href)
                    title = link.get_text()
                    pages.append((full_url, title))
            
            logging.info(f"  Found {len(pages)} pages in category")
            return pages
            
        except Exception as e:
            logging.error(f"Error fetching category: {e}")
            return []
    
    def scrape_biographies(self, max_pages=100, delay=1.0):
        """Scrape biographical content from Kurdish Wikipedia"""
        
        # Kurdish Wikipedia biography categories (URL-encoded)
        categories = [
            "/wiki/%D9%BE%DB%86%D9%84:%DA%A9%DB%95%D8%B3%D8%A7%DB%8C%DB%95%D8%AA%DB%8C%DB%8C%DB%95%DA%A9%D8%A7%D9%86%DB%8C_%DA%A9%D9%88%D8%B1%D8%AF%D8%B3%D8%AA%D8%A7%D9%86",  # Personalities of Kurdistan
            "/wiki/%D9%BE%DB%86%D9%84:%D9%86%D9%88%D9%88%D8%B3%DB%95%D8%B1%D8%A7%D9%86%DB%8C_%DA%A9%D9%88%D8%B1%D8%AF",  # Kurdish writers
            "/wiki/%D9%BE%DB%86%D9%84:%D8%B3%DB%8C%D8%A7%D8%B3%DB%95%D8%AA%D9%85%DB%95%D8%AF%D8%A7%D8%B1%D8%A7%D9%86%DB%8C_%DA%A9%D9%88%D8%B1%D8%AF",  # Kurdish politicians
            "/wiki/%D9%BE%DB%86%D9%84:%D8%B4%D8%A7%D8%B9%DB%8C%D8%B1%D8%A7%D9%86%DB%8C_%DA%A9%D9%88%D8%B1%D8%AF",  # Kurdish poets
            "/wiki/%D9%BE%DB%86%D9%84:%D9%85%DB%8E%DA%98%D9%88%D9%88%D9%86%D9%88%D9%88%D8%B3%D8%A7%D9%86%DB%8C_%DA%A9%D9%88%D8%B1%D8%AF",  # Kurdish historians
        ]
        
        all_sentences = []
        all_pages = []
        
        # Collect page URLs from categories
        for category in categories:
            category_url = urljoin(self.base_url, category)
            pages = self.get_category_pages(category_url, limit=max_pages // len(categories))
            all_pages.extend(pages)
            time.sleep(delay)
        
        logging.info(f"\nTotal pages to scrape: {len(all_pages)}")
        
        # Scrape each page
        for i, (url, title) in enumerate(all_pages[:max_pages], 1):
            logging.info(f"\n[{i}/{len(all_pages[:max_pages])}] {title}")
            
            sentences = self.scrape_page(url)
            all_sentences.extend(sentences)
            
            logging.info(f"  Total sentences so far: {len(all_sentences)}")
            
            # Be polite to Wikipedia servers
            time.sleep(delay)
        
        return all_sentences
    
    def save_corpus(self, sentences, output_file):
        """Save sentences to file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for sent in sentences:
                f.write(sent + '\n')
        
        logging.info(f"\nSaved {len(sentences)} sentences to: {output_path}")
        
        # Print statistics
        total_chars = sum(len(s) for s in sentences)
        total_words = sum(len(s.split()) for s in sentences)
        zwnj_count = sum(s.count('\u200c') for s in sentences)
        
        logging.info(f"\nCorpus Statistics:")
        logging.info(f"  Sentences: {len(sentences):,}")
        logging.info(f"  Total Characters: {total_chars:,}")
        logging.info(f"  Total Words: {total_words:,}")
        logging.info(f"  Avg Words/Sentence: {total_words/len(sentences):.2f}")
        logging.info(f"  ZWNJ Count: {zwnj_count:,}")
        logging.info(f"  ZWNJ Density: {(zwnj_count/total_chars)*100:.2f}%")

def main():
    scraper = WikipediaBioScraper()
    
    logging.info("=" * 60)
    logging.info("Kurdish Wikipedia Biography Scraper")
    logging.info("=" * 60)
    
    # Scrape biographies
    sentences = scraper.scrape_biographies(max_pages=100, delay=1.5)
    
    # Save raw corpus
    output_file = 'wikipedia_bio_raw.txt'
    scraper.save_corpus(sentences, output_file)
    
    logging.info("\n" + "=" * 60)
    logging.info("Scraping complete!")
    logging.info(f"Next step: Filter corpus with filter_corpus.py")
    logging.info("=" * 60)

if __name__ == '__main__':
    main()
