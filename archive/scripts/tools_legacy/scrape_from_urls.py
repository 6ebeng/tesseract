#!/usr/bin/env python3
"""
Kurdish Sentence Collector - Semi-Automated Approach

Since Rudaw uses JavaScript rendering, this script helps you collect
sentences from manually provided article URLs.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple
import unicodedata

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: pip3 install requests beautifulsoup4")
    sys.exit(1)


class KurdishQualityChecker:
    KURDISH_CHARS = set('ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهھوۆەیێ')
    ZWNJ = '\u200c'
    
    @staticmethod
    def count_words(text: str) -> int:
        words = re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+', text)
        return len(words)
    
    @staticmethod
    def count_zwnj(text: str) -> float:
        if not text:
            return 0.0
        return (text.count(KurdishQualityChecker.ZWNJ) / len(text) * 100)
    
    @staticmethod
    def kurdish_purity(text: str) -> float:
        letters = [c for c in text if unicodedata.category(c).startswith('L')]
        if not letters:
            return 0.0
        kurdish = sum(1 for c in letters if c in KurdishQualityChecker.KURDISH_CHARS)
        return (kurdish / len(letters) * 100)
    
    @staticmethod
    def is_good_sentence(s: str) -> bool:
        words = KurdishQualityChecker.count_words(s)
        zwnj = KurdishQualityChecker.count_zwnj(s)
        purity = KurdishQualityChecker.kurdish_purity(s)
        
        return (10 <= words <= 25 and 
                5.0 <= zwnj <= 15.0 and 
                purity >= 80.0 and
                len(s) >= 50 and
                not re.search(r'https?://|www\.|@|#', s))


def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.replace('ك', 'ک').replace('ي', 'ی')
    return text


def extract_sentences(text: str) -> List[str]:
    sentences = re.split(r'[.!?؟]+\s*', text)
    return [clean_text(s) for s in sentences if len(s.strip()) > 30]


def scrape_article(url: str) -> List[str]:
    """Try to scrape an article and extract sentences."""
    try:
        print(f"   Fetching: {url[:70]}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, timeout=15, headers=headers)
        if response.status_code != 200:
            print(f"   ⚠️  Status: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style tags
        for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()
        
        # Try to find article content
        paragraphs = []
        
        # Try common article selectors
        for selector in [
            ('article', {}),
            ('div', {'class': re.compile(r'article|content|body|text|detail', re.I)}),
            ('div', {'id': re.compile(r'article|content|body|text', re.I)}),
        ]:
            container = soup.find(selector[0], selector[1])
            if container:
                paragraphs = container.find_all('p')
                if len(paragraphs) >= 3:
                    break
        
        # Fallback: just get all paragraphs
        if not paragraphs:
            paragraphs = soup.find_all('p')
        
        # Extract text
        all_text = []
        for p in paragraphs:
            text = p.get_text()
            text = clean_text(text)
            if len(text) > 50:
                all_text.append(text)
        
        # Split into sentences
        sentences = []
        for text in all_text:
            sentences.extend(extract_sentences(text))
        
        # Filter for quality
        checker = KurdishQualityChecker()
        quality = [s for s in sentences if checker.is_good_sentence(s)]
        
        print(f"   ✓ Extracted {len(quality)} quality sentences")
        return quality
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return []


def scrape_from_urls_file(urls_file: Path) -> List[str]:
    """Scrape sentences from URLs listed in a file."""
    
    if not urls_file.exists():
        print(f"❌ File not found: {urls_file}")
        return []
    
    urls = []
    with open(urls_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and line.startswith('http'):
                urls.append(line)
    
    print(f"📋 Found {len(urls)} URLs to scrape\n")
    
    all_sentences = []
    seen = set()
    
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}]")
        sentences = scrape_article(url)
        
        # Deduplicate
        for s in sentences:
            if s not in seen:
                all_sentences.append(s)
                seen.add(s)
        
        print(f"   Running total: {len(all_sentences)} unique sentences\n")
    
    return all_sentences


def create_sample_urls_file():
    """Create a sample URLs file for user to fill in."""
    sample_file = Path("corpus/kurdish_article_urls.txt")
    
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write("# Kurdish Article URLs for Scraping\n")
        f.write("# Add article URLs below (one per line)\n")
        f.write("# Remove these comment lines before running\n")
        f.write("#\n")
        f.write("# Example:\n")
        f.write("# https://www.rudaw.net/sorani/kurdistan/1410202501\n")
        f.write("# https://www.basnews.com/ku/news/...\n")
        f.write("#\n")
        f.write("# To scrape, run:\n")
        f.write("#   python3 tools/scrape_from_urls.py\n")
        f.write("#\n\n")
    
    print(f"✅ Created: {sample_file}")
    print(f"\n📋 Next steps:")
    print(f"   1. Open {sample_file}")
    print(f"   2. Visit Rudaw/BasNews/NRT and copy article URLs")
    print(f"   3. Paste URLs into the file (one per line)")
    print(f"   4. Run: python3 tools/scrape_from_urls.py")


def main():
    print("=" * 70)
    print("🚀 Kurdish Article Scraper - URL-based Collection")
    print("=" * 70)
    
    urls_file = Path("corpus/kurdish_article_urls.txt")
    
    # Check if URLs file exists
    if not urls_file.exists() or urls_file.stat().st_size < 100:
        print("\n⚠️  URLs file not found or empty")
        create_sample_urls_file()
        print("\n💡 TIP: Find articles by browsing:")
        print("   - https://www.rudaw.net/sorani/kurdistan")
        print("   - https://www.basnews.com")
        print("   - https://www.nrttv.com")
        return
    
    # Scrape from URLs
    print("\n🔍 Scraping articles...\n")
    sentences = scrape_from_urls_file(urls_file)
    
    if not sentences:
        print("\n⚠️  No sentences collected. Check your URLs.")
        return
    
    # Save results
    output_file = Path("corpus/kurdish_news_batch1_scraped.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        for s in sentences:
            f.write(s + '\n')
    
    # Statistics
    checker = KurdishQualityChecker()
    total_words = sum(checker.count_words(s) for s in sentences)
    total_chars = sum(len(s) for s in sentences)
    total_zwnj = sum(s.count(checker.ZWNJ) for s in sentences)
    avg_zwnj = (total_zwnj / total_chars * 100) if total_chars > 0 else 0
    
    print("\n" + "=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    print(f"✅ Saved to: {output_file}")
    print(f"📝 Sentences: {len(sentences)}")
    print(f"📚 Words: {total_words:,}")
    print(f"🔗 ZWNJ density: {avg_zwnj:.2f}%")
    print(f"📏 Avg words/sentence: {total_words / len(sentences):.1f}")
    print("\n📋 Next steps:")
    print("   1. Run quality check: python3 tools/corpus_quality_checker.py corpus/kurdish_news_batch1_scraped.txt")
    print("   2. If good, copy to: corpus/kurdish_news_batch1.txt")
    print("   3. Create batch: python3 tools/incremental_training.py create 1 corpus/kurdish_news_batch1.txt 500")
    print("=" * 70)


if __name__ == '__main__':
    main()
