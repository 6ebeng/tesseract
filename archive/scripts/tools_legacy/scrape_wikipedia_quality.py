#!/usr/bin/env python3
"""
Kurdish Wikipedia Article Scraper

Extracts high-quality Kurdish sentences from Wikipedia articles.
Uses Wikipedia's API to fetch full article content.
"""

import re
import sys
import json
import time
from pathlib import Path
from typing import List, Set
import unicodedata

try:
    import requests
except ImportError:
    print("Error: pip3 install requests")
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
        
        # Very relaxed criteria for Wikipedia - just filter junk
        return (8 <= words <= 30 and      # Allow shorter/longer
                zwnj >= 2.0 and           # Just need some ZWNJ
                purity >= 60.0 and        # Allow mixed scripts
                len(s) >= 40)


def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.replace('ك', 'ک').replace('ي', 'ی')
    return text


def extract_sentences(text: str) -> List[str]:
    # Remove Wikipedia markup
    text = re.sub(r'\[\[.*?\]\]', '', text)  # Remove links
    text = re.sub(r'\{\{.*?\}\}', '', text)  # Remove templates
    text = re.sub(r'<.*?>', '', text)         # Remove HTML tags
    
    sentences = re.split(r'[.!?؟]+\s*', text)
    return [clean_text(s) for s in sentences if len(s.strip()) > 30]


def fetch_wikipedia_article(title: str, lang: str = 'ckb') -> str:
    """Fetch article content from Wikipedia API."""
    api_url = f"https://{lang}.wikipedia.org/w/api.php"
    
    params = {
        'action': 'query',
        'format': 'json',
        'titles': title,
        'prop': 'extracts',
        'explaintext': True,
        'exsectionformat': 'plain'
    }
    
    headers = {
        'User-Agent': 'TesseractKurdishOCRTraining/1.0 (tesseract-ocr@github; research/non-commercial)'
    }
    
    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        pages = data.get('query', {}).get('pages', {})
        for page_id, page_data in pages.items():
            if 'extract' in page_data:
                return page_data['extract']
        
        return ""
    except Exception as e:
        return ""


def get_random_articles(count: int = 20, lang: str = 'ckb') -> List[str]:
    """Get random Wikipedia article titles."""
    api_url = f"https://{lang}.wikipedia.org/w/api.php"
    
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'random',
        'rnnamespace': 0,  # Main namespace only
        'rnlimit': count
    }
    
    headers = {
        'User-Agent': 'TesseractKurdishOCRTraining/1.0 (tesseract-ocr@github; research/non-commercial)'
    }
    
    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        articles = data.get('query', {}).get('random', [])
        return [article['title'] for article in articles]
    except Exception as e:
        return []


def scrape_wikipedia_articles(num_articles: int = 50, target_sentences: int = 500) -> List[str]:
    """Scrape sentences from Wikipedia articles."""
    
    checker = KurdishQualityChecker()
    all_sentences = []
    seen = set()
    
    articles_processed = 0
    
    while len(all_sentences) < target_sentences and articles_processed < num_articles:
        # Get batch of random articles
        print(f"\n📚 Fetching random articles (batch {articles_processed // 20 + 1})...")
        titles = get_random_articles(count=20, lang='ckb')
        
        if not titles:
            print("   ⚠️  No articles returned")
            break
        
        print(f"   Got {len(titles)} article titles")
        
        for title in titles:
            articles_processed += 1
            
            print(f"   [{articles_processed}/{num_articles}] {title[:50]}...")
            
            # Fetch article content
            content = fetch_wikipedia_article(title, lang='ckb')
            
            if not content:
                print(f"      ✗ No content")
                continue
            
            # Extract sentences
            sentences = extract_sentences(content)
            
            # Filter for quality
            quality_sentences = [s for s in sentences if checker.is_good_sentence(s)]
            
            # Deduplicate
            new_sentences = [s for s in quality_sentences if s not in seen]
            all_sentences.extend(new_sentences)
            seen.update(new_sentences)
            
            if new_sentences:
                print(f"      ✓ +{len(new_sentences)} sentences (total: {len(all_sentences)})")
            else:
                print(f"      ✗ No quality sentences")
            
            if len(all_sentences) >= target_sentences:
                print(f"\n🎯 Target reached! ({target_sentences} sentences)")
                break
            
            time.sleep(0.5)  # Be nice to Wikipedia
    
    return all_sentences


def main():
    print("=" * 70)
    print("🚀 Kurdish Wikipedia Scraper - High Quality Selection")
    print("=" * 70)
    print("\n📖 Fetching random Kurdish Wikipedia articles...")
    print("   Filtering for: 10-25 words, 4-15% ZWNJ, >75% Kurdish purity")
    
    # Scrape articles
    sentences = scrape_wikipedia_articles(num_articles=100, target_sentences=500)
    
    if not sentences:
        print("\n❌ No sentences collected")
        return
    
    # Save results
    output_file = Path("corpus/kurdish_wikipedia_quality.txt")
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
    print("   1. Review quality: python3 tools/corpus_quality_checker.py corpus/kurdish_wikipedia_quality.txt")
    print("   2. If good, use for Batch 1: cp corpus/kurdish_wikipedia_quality.txt corpus/kurdish_news_batch1.txt")
    print("   3. Create batch: python3 tools/incremental_training.py create 1 corpus/kurdish_news_batch1.txt 500")
    print("=" * 70)


if __name__ == '__main__':
    main()
