#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 5 Wikipedia Corpus Expansion
Extract 4,000-5,000 high-quality lines from Kurdish Wikipedia

Goal: Expand corpus from 3,321 → 7,000-8,000 lines
Quality filters: ZWNJ presence, sentence length, Kurdish characters
"""

import bz2
import xml.etree.ElementTree as ET
import re
import sys
from pathlib import Path
from collections import Counter
import random

ZWNJ = '\u200c'

def clean_wikitext(text: str) -> list:
    """
    Clean Wikipedia markup and extract quality sentences.
    
    Returns:
        List of cleaned sentences
    """
    if not text:
        return []
    
    # Remove templates {{...}}
    text = re.sub(r'\{\{[^}]+\}\}', '', text)
    
    # Remove file/image links
    text = re.sub(r'\[\[(File|پەڕگە|Image|وێنە):[^\]]+\]\]', '', text, flags=re.IGNORECASE)
    
    # Convert [[Link|Text]] to Text
    text = re.sub(r'\[\[(?:[^|\]]+\|)?([^\]]+)\]\]', r'\1', text)
    
    # Remove section headers
    text = re.sub(r'==+\s*.*?\s*==+', '', text)
    
    # Remove HTML comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    
    # Remove references
    text = re.sub(r'<ref[^>]*>.*?</ref>', '', text, flags=re.DOTALL)
    text = re.sub(r'<ref[^>]*?/>', '', text)
    
    # Remove other HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove URLs
    text = re.sub(r'https?://[^\s]+', '', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Split into sentences
    sentences = []
    
    # Split on Kurdish sentence terminators
    for part in re.split(r'[.؟!،\n]+', text):
        line = part.strip()
        if not line:
            continue
        
        # Quality filters
        words = line.split()
        
        # Length filter: 5-25 words (reasonable sentence length)
        if len(words) < 5 or len(words) > 25:
            continue
        
        # Character count filter
        if len(line) < 30 or len(line) > 250:
            continue
        
        # Must be mostly Kurdish/Arabic script
        kurdish_chars = sum(1 for c in line if '\u0600' <= c <= '\u06FF' or c == ZWNJ)
        if kurdish_chars < len(line) * 0.6:
            continue
        
        # Prefer sentences with ZWNJ (but don't require it - we'll add later)
        # This allows us to get more content
        
        # Skip if it's mostly numbers or punctuation
        alpha_chars = sum(1 for c in line if c.isalpha() or '\u0600' <= c <= '\u06FF')
        if alpha_chars < len(line) * 0.5:
            continue
        
        sentences.append(line)
    
    return sentences


def extract_articles(dump_path: Path, max_articles: int = 1000):
    """
    Extract text from Wikipedia dump.
    
    Args:
        dump_path: Path to .xml.bz2 dump file
        max_articles: Maximum number of articles to process
        
    Yields:
        (title, sentences) tuples
    """
    print(f"Opening Wikipedia dump: {dump_path}")
    
    if dump_path.suffix == '.bz2':
        f = bz2.open(dump_path, 'rt', encoding='utf-8')
    else:
        f = open(dump_path, 'r', encoding='utf-8')
    
    article_count = 0
    namespace = '{http://www.mediawiki.org/xml/export-0.10/}'
    
    try:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag == f'{namespace}page':
                # Check if it's a main article (not a redirect, template, etc.)
                ns_elem = elem.find(f'{namespace}ns')
                if ns_elem is not None and ns_elem.text != '0':
                    elem.clear()
                    continue
                
                # Get title
                title_elem = elem.find(f'{namespace}title')
                title = title_elem.text if title_elem is not None else ''
                
                # Skip special pages
                if ':' in title:
                    elem.clear()
                    continue
                
                # Get article text
                revision = elem.find(f'{namespace}revision')
                if revision is not None:
                    text_elem = revision.find(f'{namespace}text')
                    if text_elem is not None and text_elem.text:
                        text = text_elem.text
                        
                        # Clean and extract sentences
                        sentences = clean_wikitext(text)
                        
                        if sentences:
                            yield (title, sentences)
                            article_count += 1
                            
                            if article_count % 100 == 0:
                                print(f"  Processed {article_count} articles...")
                            
                            if article_count >= max_articles:
                                print(f"Reached max articles ({max_articles})")
                                break
                
                elem.clear()
    
    finally:
        f.close()
    
    print(f"Total articles processed: {article_count}")


def main():
    """Extract Wikipedia text and save to corpus file"""
    
    # Paths
    work_dir = Path(__file__).parent.parent
    dump_path = work_dir / 'corpus' / 'ckbwiki-latest-pages-articles.xml.bz2'
    output_path = work_dir / 'corpus' / 'wikipedia_phase5.txt'
    
    if not dump_path.exists():
        print(f"Error: Wikipedia dump not found at {dump_path}")
        print("Please download from: https://dumps.wikimedia.org/ckbwiki/latest/")
        sys.exit(1)
    
    print("=" * 70)
    print("PHASE 5 WIKIPEDIA CORPUS EXPANSION")
    print("=" * 70)
    print()
    print(f"Dump file: {dump_path}")
    print(f"Output: {output_path}")
    print()
    print("Target: 4,000-5,000 quality lines")
    print()
    
    # Extract articles
    all_sentences = []
    sentence_counts = Counter()
    
    print("Extracting articles...")
    for title, sentences in extract_articles(dump_path, max_articles=1000):
        for sentence in sentences:
            # Deduplicate sentences
            if sentence not in sentence_counts:
                all_sentences.append(sentence)
            sentence_counts[sentence] += 1
    
    print()
    print(f"Total unique sentences extracted: {len(all_sentences)}")
    print(f"Duplicate sentences removed: {sum(sentence_counts.values()) - len(all_sentences)}")
    
    # Shuffle for better distribution
    random.seed(42)
    random.shuffle(all_sentences)
    
    # Take first 5,000 (or all if less)
    target_lines = min(5000, len(all_sentences))
    selected = all_sentences[:target_lines]
    
    # Calculate statistics
    total_chars = sum(len(s) for s in selected)
    total_zwnj = sum(s.count(ZWNJ) for s in selected)
    zwnj_density = (total_zwnj / total_chars * 100) if total_chars > 0 else 0
    
    # Count words
    total_words = sum(len(s.split()) for s in selected)
    
    print()
    print("=" * 70)
    print("EXTRACTION SUMMARY")
    print("=" * 70)
    print(f"Lines selected: {len(selected)}")
    print(f"Total words: {total_words:,}")
    print(f"Total characters: {total_chars:,}")
    print(f"ZWNJ count: {total_zwnj:,}")
    print(f"ZWNJ density: {zwnj_density:.2f}%")
    print(f"Avg line length: {total_chars / len(selected):.1f} chars")
    print(f"Avg words per line: {total_words / len(selected):.1f}")
    
    # Save to file
    print()
    print(f"Saving to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        for sentence in selected:
            f.write(sentence + '\n')
    
    print()
    print("✅ Wikipedia extraction complete!")
    print()
    print("Next steps:")
    print("  1. Review output file: corpus/wikipedia_phase5.txt")
    print("  2. Merge with existing corpus")
    print("  3. Run corpus audit")


if __name__ == '__main__':
    main()
