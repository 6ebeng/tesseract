#!/usr/bin/env python3
"""
Live Kurdish News Scraper - Rudaw Edition

Fetches real articles from Rudaw.net Sorani section and extracts
high-quality Kurdish sentences for Phase 6 corpus expansion.
"""

import re
import sys
import time
import random
from pathlib import Path
from typing import List, Set, Tuple
import unicodedata

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: Required packages not installed.")
    print("Install: pip3 install requests beautifulsoup4")
    sys.exit(1)


class KurdishTextQualityChecker:
    """Check quality of Kurdish text."""
    
    KURDISH_CHARS = set('ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهھوۆەیێ')
    ZWNJ = '\u200c'
    
    @staticmethod
    def count_zwnj(text: str) -> Tuple[int, float]:
        zwnj_count = text.count(KurdishTextQualityChecker.ZWNJ)
        total_chars = len(text)
        density = (zwnj_count / total_chars * 100) if total_chars > 0 else 0
        return zwnj_count, density
    
    @staticmethod
    def count_kurdish_chars(text: str) -> Tuple[int, float]:
        kurdish_count = sum(1 for c in text if c in KurdishTextQualityChecker.KURDISH_CHARS)
        total_letters = sum(1 for c in text if unicodedata.category(c).startswith('L'))
        purity = (kurdish_count / total_letters * 100) if total_letters > 0 else 0
        return kurdish_count, purity
    
    @staticmethod
    def count_words(text: str) -> int:
        words = re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+', text)
        return len(words)
    
    @staticmethod
    def is_quality_sentence(sentence: str) -> bool:
        """Check if sentence meets quality criteria."""
        # Check word count (10-25 words)
        word_count = KurdishTextQualityChecker.count_words(sentence)
        if word_count < 10 or word_count > 25:
            return False
        
        # Check ZWNJ density (relaxed: 5-15%)
        _, zwnj_density = KurdishTextQualityChecker.count_zwnj(sentence)
        if zwnj_density < 5.0 or zwnj_density > 15.0:
            return False
        
        # Check Kurdish script purity (>80%)
        _, kurdish_purity = KurdishTextQualityChecker.count_kurdish_chars(sentence)
        if kurdish_purity < 80.0:
            return False
        
        # Check for unwanted patterns
        if re.search(r'https?://|www\.|@|#', sentence):
            return False
        
        # Minimum length
        if len(sentence) < 50:
            return False
        
        return True


class RudawScraper:
    """Scrape Rudaw.net for Kurdish articles."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ku,en-US,en;q=0.5',
        })
        self.seen_sentences: Set[str] = set()
        self.quality_checker = KurdishTextQualityChecker()
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        # Normalize to Kurdish characters
        text = text.replace('ك', 'ک').replace('ي', 'ی')
        return text
    
    def extract_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Split on sentence terminators
        sentences = re.split(r'[.!?؟]+\s*', text)
        cleaned = []
        for s in sentences:
            s = self.clean_text(s)
            if len(s) > 30:  # Minimum length
                cleaned.append(s)
        return cleaned
    
    def get_article_links(self, category_url: str, max_links: int = 20) -> List[str]:
        """Get article URLs from category page."""
        try:
            print(f"   Fetching: {category_url}")
            response = self.session.get(category_url, timeout=15)
            
            if response.status_code != 200:
                print(f"   ⚠️  Status {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all article links
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                # Rudaw articles typically have /sorani/[section]/[date]/[article]
                if '/sorani/' in href and href.count('/') >= 5:
                    # Make absolute URL
                    if href.startswith('http'):
                        full_url = href
                    else:
                        full_url = f"https://www.rudaw.net{href}" if href.startswith('/') else f"https://www.rudaw.net/{href}"
                    
                    if full_url not in links:
                        links.append(full_url)
            
            print(f"   Found {len(links)} article links")
            return links[:max_links]
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []
    
    def scrape_article(self, url: str) -> List[str]:
        """Scrape single article and extract sentences."""
        try:
            time.sleep(random.uniform(1.5, 3.0))  # Respectful rate limiting
            
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract article body - Rudaw uses various structures
            # Try multiple selectors
            paragraphs = []
            
            # Method 1: Find article content div
            article = soup.find(['article', 'div'], class_=re.compile(r'article|content|body|detail', re.I))
            if article:
                paragraphs.extend(article.find_all('p'))
            
            # Method 2: Find all p tags in main content area
            if not paragraphs:
                main = soup.find(['main', 'div'], id=re.compile(r'main|content', re.I))
                if main:
                    paragraphs.extend(main.find_all('p'))
            
            # Method 3: Just get all paragraphs
            if not paragraphs:
                paragraphs = soup.find_all('p')
            
            # Extract text from paragraphs
            text_parts = []
            for p in paragraphs:
                text = p.get_text()
                text = self.clean_text(text)
                # Filter out short paragraphs (likely ads, captions, etc.)
                if len(text) > 50 and self.quality_checker.count_words(text) >= 8:
                    text_parts.append(text)
            
            # Combine and split into sentences
            full_text = ' '.join(text_parts)
            sentences = self.extract_sentences(full_text)
            
            # Filter for quality and deduplicate
            quality_sentences = []
            for s in sentences:
                if s not in self.seen_sentences and self.quality_checker.is_quality_sentence(s):
                    quality_sentences.append(s)
                    self.seen_sentences.add(s)
            
            return quality_sentences
            
        except Exception as e:
            return []
    
    def scrape_category(self, category_url: str, target_sentences: int = 200) -> List[str]:
        """Scrape a category until target sentences collected."""
        print(f"\n📰 Scraping category...")
        
        all_sentences = []
        article_links = self.get_article_links(category_url, max_links=50)
        
        print(f"   Processing {len(article_links)} articles...")
        
        for i, url in enumerate(article_links, 1):
            if len(all_sentences) >= target_sentences:
                break
            
            print(f"   [{i}/{len(article_links)}] {url[:60]}...")
            sentences = self.scrape_article(url)
            
            if sentences:
                all_sentences.extend(sentences)
                print(f"      ✓ +{len(sentences)} sentences (total: {len(all_sentences)})")
            else:
                print(f"      ✗ No quality sentences")
        
        return all_sentences


def main():
    """Main scraping workflow."""
    print("=" * 70)
    print("🚀 Rudaw Live Scraper - Phase 6 Corpus Collection")
    print("=" * 70)
    
    scraper = RudawScraper()
    
    # Target: 500 sentences total
    # Rudaw categories to scrape
    categories = [
        ("https://www.rudaw.net/sorani/kurdistan", 200, "Kurdistan"),
        ("https://www.rudaw.net/sorani/middleeast", 150, "Middle East"),
        ("https://www.rudaw.net/sorani/business", 150, "Business"),
    ]
    
    all_sentences = []
    
    for url, target, name in categories:
        print(f"\n{'=' * 70}")
        print(f"📂 Category: {name} (target: {target} sentences)")
        print(f"{'=' * 70}")
        
        sentences = scraper.scrape_category(url, target_sentences=target)
        all_sentences.extend(sentences)
        
        print(f"\n✅ Collected {len(sentences)} sentences from {name}")
        print(f"📊 Running total: {len(all_sentences)} sentences")
        
        if len(all_sentences) >= 500:
            print("\n🎯 Target reached! (500 sentences)")
            break
    
    # Save results
    output_file = Path("corpus/kurdish_news_batch1_scraped.txt")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for sentence in all_sentences:
            f.write(sentence + '\n')
    
    # Statistics
    total_words = sum(scraper.quality_checker.count_words(s) for s in all_sentences)
    total_chars = sum(len(s) for s in all_sentences)
    total_zwnj = sum(s.count(scraper.quality_checker.ZWNJ) for s in all_sentences)
    avg_zwnj = (total_zwnj / total_chars * 100) if total_chars > 0 else 0
    
    print("\n" + "=" * 70)
    print("📊 FINAL RESULTS")
    print("=" * 70)
    print(f"✅ Saved to: {output_file}")
    print(f"📝 Total sentences: {len(all_sentences)}")
    print(f"📚 Total words: {total_words:,}")
    print(f"🔤 Total characters: {total_chars:,}")
    print(f"🔗 ZWNJ density: {avg_zwnj:.2f}%")
    print(f"📏 Avg words/sentence: {total_words / len(all_sentences):.1f}")
    print()
    print("Next steps:")
    print("1. Review the scraped file")
    print("2. Run quality checker: python3 tools/corpus_quality_checker.py corpus/kurdish_news_batch1_scraped.txt")
    print("3. If quality is good, copy to kurdish_news_batch1.txt")
    print("4. Create batch: python3 tools/incremental_training.py create 1 corpus/kurdish_news_batch1.txt 500")
    print("=" * 70)


if __name__ == '__main__':
    main()
