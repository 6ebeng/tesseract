#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Wikipedia extraction via API (no dump download needed).
Faster alternative for initial testing.
"""

import requests
import time
import sys
import re
from pathlib import Path

class QuickWikipediaExtractor:
    def __init__(self, output_file: str, target_words: int = 50000):
        self.output_file = Path(output_file)
        self.target_words = target_words
        self.api_url = "https://ckb.wikipedia.org/w/api.php"
        
    def get_random_articles(self, count: int = 50):
        """Get list of random article IDs."""
        params = {
            'action': 'query',
            'list': 'random',
            'rnnamespace': 0,  # Main namespace only (articles)
            'rnlimit': min(count, 50),  # API limit is 50
            'format': 'json'
        }
        
        try:
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return [page['id'] for page in data['query']['random']]
        except Exception as e:
            print(f"⚠️ Error fetching random articles: {e}")
            return []
    
    def get_article_content(self, page_id: int):
        """Get clean text content for an article."""
        params = {
            'action': 'query',
            'pageids': page_id,
            'prop': 'extracts',
            'explaintext': True,  # Get plain text without HTML
            'exsectionformat': 'plain',
            'format': 'json'
        }
        
        try:
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            page_data = data['query']['pages'].get(str(page_id), {})
            return page_data.get('extract', '')
        except Exception as e:
            print(f"⚠️ Error fetching article {page_id}: {e}")
            return ''
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Remove URLs
        text = re.sub(r'http\S+', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove section headers (=== text ===)
        text = re.sub(r'={2,}[^=]+={2,}', '', text)
        
        return text.strip()
    
    def extract_sentences(self, text: str, min_words: int = 5, max_words: int = 30):
        """Extract sentences within word count range."""
        # Split on sentence boundaries (Arabic and Latin)
        sentences = re.split(r'[.!?؟۔]\s+', text)
        
        valid_sentences = []
        for sent in sentences:
            sent = sent.strip()
            
            # Skip empty or very short
            if len(sent) < 20:
                continue
            
            word_count = len(sent.split())
            
            # Check word count range
            if not (min_words <= word_count <= max_words):
                continue
            
            # Must contain Kurdish characters
            kurdish_chars = set('ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنوۆهھەیێ')
            if not any(c in kurdish_chars for c in sent):
                continue
            
            # Not too much Latin
            latin_count = sum(1 for c in sent if ('A' <= c <= 'Z') or ('a' <= c <= 'z'))
            if latin_count > len(sent) * 0.3:
                continue
            
            # Check for ZWNJ (important for Kurdish!)
            zwnj_count = sent.count('\u200c')
            zwnj_pct = (zwnj_count / len(sent)) * 100 if sent else 0
            
            # Kurdish should have 5-12% ZWNJ typically
            if zwnj_pct < 3.0:  # Too low, might not be proper Kurdish
                continue
            
            valid_sentences.append(sent)
        
        return valid_sentences
    
    def extract(self):
        """Main extraction process."""
        print("🚀 Quick Wikipedia Extractor (API Method)")
        print(f"   Target: {self.target_words:,} words")
        print(f"   Output: {self.output_file}")
        print()
        
        all_sentences = []
        total_words = 0
        articles_processed = 0
        batch_count = 0
        
        # Open output file
        with open(self.output_file, 'w', encoding='utf-8') as out:
            while total_words < self.target_words:
                batch_count += 1
                print(f"📚 Batch {batch_count}: Fetching articles...", end='\r')
                
                # Get random article IDs
                page_ids = self.get_random_articles(50)
                
                if not page_ids:
                    print("⚠️ No more articles available")
                    break
                
                # Process each article
                for page_id in page_ids:
                    # Get content
                    content = self.get_article_content(page_id)
                    
                    if not content:
                        continue
                    
                    # Clean text
                    clean_content = self.clean_text(content)
                    
                    # Extract sentences
                    sentences = self.extract_sentences(clean_content)
                    
                    if not sentences:
                        continue
                    
                    articles_processed += 1
                    
                    # Write sentences
                    for sent in sentences:
                        out.write(sent + '\n')
                        words_in_sent = len(sent.split())
                        total_words += words_in_sent
                        
                        if total_words >= self.target_words:
                            break
                    
                    # Progress update
                    if articles_processed % 10 == 0:
                        print(f"📚 Articles: {articles_processed:,} | Words: {total_words:,}/{self.target_words:,} ({total_words/self.target_words*100:.1f}%)", end='\r')
                    
                    # Rate limiting
                    time.sleep(0.2)
                    
                    if total_words >= self.target_words:
                        break
                
                if total_words >= self.target_words:
                    break
        
        # Summary
        print()
        print()
        print("="*70)
        print("📊 EXTRACTION SUMMARY")
        print("="*70)
        print(f"Articles processed: {articles_processed:,}")
        print(f"Total words: {total_words:,}")
        print(f"Output file: {self.output_file}")
        print(f"File size: {self.output_file.stat().st_size / 1024:.1f} KB")
        
        # Analyze ZWNJ
        text = self.output_file.read_text(encoding='utf-8')
        zwnj_count = text.count('\u200c')
        print(f"\nQuality Metrics:")
        print(f"  ZWNJ count: {zwnj_count:,}")
        print(f"  ZWNJ percentage: {(zwnj_count/len(text)*100):.2f}%")
        print("="*70)
        print("✅ Extraction complete!")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 quick_wikipedia_extract.py <output.txt> [target_words]")
        print()
        print("Example:")
        print("  python3 quick_wikipedia_extract.py ckb_wikipedia.txt 50000")
        sys.exit(1)
    
    output_file = sys.argv[1]
    target_words = int(sys.argv[2]) if len(sys.argv) > 2 else 50000
    
    extractor = QuickWikipediaExtractor(output_file, target_words)
    extractor.extract()


if __name__ == '__main__':
    main()
