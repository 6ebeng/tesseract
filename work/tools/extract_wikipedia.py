#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract and clean Kurdish Wikipedia text from XML dump.
Filters for quality (ZWNJ presence, Kurdish characters, sentence length).
"""

import xml.etree.ElementTree as ET
import re
import sys
from pathlib import Path


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
    
    # Split into lines (periods and newlines)
    sentences = []
    for part in re.split(r'[.\n]+', text):
        line = part.strip()
        if not line:
            continue
        
        # Quality filters
        words = line.split()
        
        # Length filter: 5-30 words
        if len(words) < 5 or len(words) > 30:
            continue
        
        # Character count filter: reasonable length
        if len(line) < 20 or len(line) > 200:
            continue
        
        # Must have ZWNJ (critical for Kurdish)
        if '\u200c' not in line:
            continue
        
        # Must be mostly Kurdish/Arabic script
        kurdish_chars = sum(1 for c in line if '\u0600' <= c <= '\u06FF' or c == '\u200c')
        if kurdish_chars < len(line) * 0.6:
            continue
        
        # ZWNJ percentage check (should be 5-15%)
        zwnj_pct = line.count('\u200c') / len(line) * 100
        if zwnj_pct < 2.0 or zwnj_pct > 20.0:
            continue
        
        sentences.append(line)
    
    return sentences


def extract_wikipedia(xml_file: str, output_file: str, target_words: int = 50000):
    """
    Extract text from Wikipedia XML dump.
    
    Args:
        xml_file: Path to ckbwiki-latest-pages-articles.xml
        output_file: Path to output text file
        target_words: Stop after reaching this many words
    """
    
    print("="*70)
    print("📚 KURDISH WIKIPEDIA EXTRACTOR")
    print("="*70)
    print(f"   Input: {xml_file}")
    print(f"   Output: {output_file}")
    print(f"   Target: {target_words:,} words")
    print()
    
    # Namespace for MediaWiki XML
    ns = {'mw': 'http://www.mediawiki.org/xml/export-0.11/'}
    
    all_sentences = set()  # Use set to avoid duplicates
    total_words = 0
    pages_processed = 0
    pages_with_content = 0
    
    print("🔄 Processing articles (this may take 5-10 minutes)...")
    print()
    
    # Parse XML iteratively (memory-efficient for large files)
    context = ET.iterparse(xml_file, events=('end',))
    
    for event, elem in context:
        if elem.tag == '{http://www.mediawiki.org/xml/export-0.11/}page':
            pages_processed += 1
            
            # Get title
            title_elem = elem.find('mw:title', ns)
            title = title_elem.text if title_elem is not None else "Unknown"
            
            # Get text content
            revision = elem.find('mw:revision', ns)
            if revision is not None:
                text_elem = revision.find('mw:text', ns)
                if text_elem is not None and text_elem.text:
                    # Clean and extract sentences
                    sentences = clean_wikitext(text_elem.text)
                    
                    if sentences:
                        pages_with_content += 1
                        all_sentences.update(sentences)
                        
                        # Calculate words
                        total_words = sum(len(s.split()) for s in all_sentences)
                        
                        if pages_with_content % 50 == 0:
                            print(f"   📄 Processed {pages_with_content} articles, {total_words:,} words...")
                        
                        # Stop if we've reached target
                        if total_words >= target_words:
                            print(f"\n✅ Target reached: {total_words:,} words from {pages_with_content} articles")
                            break
            
            # Clear element to save memory
            elem.clear()
    
    print()
    print(f"📊 Extraction complete:")
    print(f"   Pages scanned: {pages_processed:,}")
    print(f"   Pages with content: {pages_with_content:,}")
    print(f"   Unique sentences: {len(all_sentences):,}")
    print(f"   Total words: {total_words:,}")
    
    # Write to file
    print()
    print(f"💾 Writing to {output_file}...")
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for sentence in sorted(all_sentences):  # Sort for consistency
            f.write(sentence + '\n')
    
    # Final statistics
    text = '\n'.join(all_sentences)
    zwnj_count = text.count('\u200c')
    file_size = output_path.stat().st_size
    
    print()
    print("="*70)
    print("✅ EXTRACTION COMPLETE")
    print("="*70)
    print(f"   Sentences: {len(all_sentences):,}")
    print(f"   Words: {total_words:,}")
    print(f"   Characters: {len(text):,}")
    print(f"   ZWNJ count: {zwnj_count:,}")
    print(f"   ZWNJ percentage: {(zwnj_count/len(text)*100):.2f}%")
    print(f"   File size: {file_size / 1024:.1f} KB")
    print("="*70)
    
    # Quality check
    zwnj_pct = zwnj_count / len(text) * 100
    if zwnj_pct < 5.0:
        print()
        print(f"⚠️ WARNING: ZWNJ percentage ({zwnj_pct:.2f}%) is below target (6-10%)")
        print("   Consider adjusting quality filters")
    elif 6.0 <= zwnj_pct <= 10.0:
        print()
        print(f"✅ ZWNJ percentage is excellent ({zwnj_pct:.2f}%)")
    else:
        print()
        print(f"✅ ZWNJ percentage is good ({zwnj_pct:.2f}%)")


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 extract_wikipedia.py <input.xml> <output.txt> [target_words]")
        print()
        print("Example:")
        print("  python3 extract_wikipedia.py ckbwiki-latest-pages-articles.xml ckb_wikipedia.txt 50000")
        sys.exit(1)
    
    xml_file = sys.argv[1]
    output_file = sys.argv[2]
    target_words = int(sys.argv[3]) if len(sys.argv) > 3 else 50000
    
    if not Path(xml_file).exists():
        print(f"❌ Error: Input file not found: {xml_file}")
        sys.exit(1)
    
    try:
        extract_wikipedia(xml_file, output_file, target_words)
    except Exception as e:
        print(f"\n❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
