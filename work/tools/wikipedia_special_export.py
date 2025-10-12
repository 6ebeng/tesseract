#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract Kurdish Wikipedia articles using Special:Export.
More reliable than API for bulk extraction.
"""

import requests
import re
import time
from pathlib import Path
import sys


def get_article_list():
    """
    Get list of important Kurdish articles.
    Using categories and high-traffic pages.
    """
    # Common Kurdish topics that should have good content
    articles = [
        # Geography
        'سلێمانی', 'هەولێر', 'کەرکووک', 'دهۆک', 'هەڵەبجە',
        # History
        'کورد', 'کوردستان', 'شۆڕشی_ئەیلوول', 'کۆماری_مەهاباد',
        # Culture
        'زمانی_کوردی', 'ئەدەبیاتی_کوردی', 'مێژووی_کورد',
        # Science
        'ئاو', 'خۆر', 'زەوی', 'ڕووەک', 'درەخت',
        # Society
        'خوێندن', 'پەروەردە', 'زانکۆ', 'پزیشکی',
        # Politics
        'دیموکراسی', 'حکومەت', 'پەرلەمان',
        # Economics
        'ئابووری', 'سەرمایە', 'بازرگانی',
        # Technology
        'کۆمپیوتەر', 'ئینتەرنێت', 'تەکنەلۆجیا',
        # Literature
        'شێعر', 'چیرۆک', 'ڕۆمان', 'نووسەر',
        # Religion
        'ئیسلام', 'مسوڵمان', 'قورئان',
        # Nature
        'چیا', 'ڕووبار', 'دەریا', 'باران', 'هەور',
        # Animals
        'پشیلە', 'سەگ', 'ئەسپ', 'مەڕ', 'مانگا',
        # Food
        'نان', 'برنج', 'گۆشت', 'سەوزە', 'میوە',
        # Numbers and common words
        'یەک', 'دوو', 'سێ', 'چوار', 'پێنج', 'شەش', 'حەوت', 'هەشت', 'نۆ', 'دە',
    ]
    
    return articles


def fetch_article(title: str, session: requests.Session):
    """Fetch article content using Special:Export."""
    url = "https://ckb.wikipedia.org/wiki/Special:Export"
    
    params = {
        'pages': title,
        'action': 'submit',
    }
    
    try:
        response = session.post(url, data=params, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"  ⚠️ Error fetching {title}: {e}")
        return None


def clean_wikitext(xml_content: str):
    """Extract and clean text from Wikipedia XML export."""
    if not xml_content:
        return ""
    
    # Extract text content from XML
    text_match = re.search(r'<text[^>]*>(.*?)</text>', xml_content, re.DOTALL)
    if not text_match:
        return ""
    
    wikitext = text_match.group(1)
    
    # Remove wiki markup
    # Remove templates {{...}}
    wikitext = re.sub(r'\{\{[^}]+\}\}', '', wikitext)
    
    # Remove file/image links [[File:...]] or [[پەڕگە:...]]
    wikitext = re.sub(r'\[\[(File|پەڕگە|Image|وێنە):[^\]]+\]\]', '', wikitext, flags=re.IGNORECASE)
    
    # Convert [[Link|Text]] to Text
    wikitext = re.sub(r'\[\[(?:[^|\]]+\|)?([^\]]+)\]\]', r'\1', wikitext)
    
    # Remove section headers
    wikitext = re.sub(r'==+\s*.*?\s*==+', '', wikitext)
    
    # Remove HTML comments
    wikitext = re.sub(r'<!--.*?-->', '', wikitext, flags=re.DOTALL)
    
    # Remove references <ref>...</ref>
    wikitext = re.sub(r'<ref[^>]*>.*?</ref>', '', wikitext, flags=re.DOTALL)
    wikitext = re.sub(r'<ref[^>]*?/>', '', wikitext)
    
    # Remove other HTML tags
    wikitext = re.sub(r'<[^>]+>', '', wikitext)
    
    # Remove URLs
    wikitext = re.sub(r'https?://[^\s]+', '', wikitext)
    
    # Remove multiple spaces and empty lines
    wikitext = re.sub(r'\s+', ' ', wikitext)
    
    # Split into sentences and filter
    sentences = []
    for line in wikitext.split('.'):
        line = line.strip()
        if not line:
            continue
        
        # Quality filters
        words = line.split()
        if len(words) < 5 or len(words) > 30:
            continue
        
        # Must have ZWNJ
        if '\u200c' not in line:
            continue
        
        # Must be mostly Kurdish characters (Arabic script)
        kurdish_chars = sum(1 for c in line if '\u0600' <= c <= '\u06FF')
        if kurdish_chars < len(line) * 0.7:
            continue
        
        sentences.append(line)
    
    return sentences


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 wikipedia_special_export.py <output.txt> [target_words]")
        sys.exit(1)
    
    output_file = Path(sys.argv[1])
    target_words = int(sys.argv[2]) if len(sys.argv) > 2 else 50000
    
    print("="*70)
    print("📚 KURDISH WIKIPEDIA EXTRACTOR (Special:Export)")
    print("="*70)
    print(f"   Target: {target_words:,} words")
    print(f"   Output: {output_file}")
    print()
    
    # Setup session with User-Agent
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) TesseractBot/1.0'
    })
    
    articles = get_article_list()
    print(f"📋 Fetching {len(articles)} articles...")
    print()
    
    all_sentences = []
    total_words = 0
    articles_processed = 0
    
    for i, title in enumerate(articles, 1):
        if total_words >= target_words:
            break
        
        print(f"[{i}/{len(articles)}] Fetching: {title}...", end=' ')
        
        xml_content = fetch_article(title, session)
        sentences = clean_wikitext(xml_content)
        
        if sentences:
            all_sentences.extend(sentences)
            article_words = sum(len(s.split()) for s in sentences)
            total_words += article_words
            articles_processed += 1
            print(f"✅ ({len(sentences)} sentences, {article_words} words, total: {total_words:,})")
        else:
            print("⚠️ No content")
        
        # Be nice to the server
        time.sleep(0.5)
    
    # Write output
    print()
    print(f"💾 Writing to {output_file}...")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for sentence in all_sentences:
            f.write(sentence + '\n')
    
    # Statistics
    text = '\n'.join(all_sentences)
    zwnj_count = text.count('\u200c')
    
    print()
    print("="*70)
    print("📊 EXTRACTION COMPLETE")
    print("="*70)
    print(f"   Articles processed: {articles_processed}")
    print(f"   Sentences extracted: {len(all_sentences):,}")
    print(f"   Total words: {total_words:,}")
    print(f"   ZWNJ count: {zwnj_count:,} ({(zwnj_count/len(text)*100):.2f}%)")
    print(f"   File size: {output_file.stat().st_size / 1024:.1f} KB")
    print("="*70)
    
    if zwnj_count / len(text) < 0.05:
        print()
        print("⚠️ WARNING: ZWNJ percentage is low. Consider adding more articles.")
    else:
        print()
        print("✅ Quality looks good!")


if __name__ == '__main__':
    main()
