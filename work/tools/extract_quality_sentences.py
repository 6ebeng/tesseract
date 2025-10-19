#!/usr/bin/env python3
"""
Extract High-Quality Sentences from Existing Wikipedia Corpus

Takes the ckb_wikipedia.txt file and extracts the best 500 sentences
based on strict quality criteria.
"""

import re
from pathlib import Path
from typing import List, Tuple
import unicodedata


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
    def score_sentence(s: str) -> float:
        """Score sentence quality (0-100)."""
        words = KurdishQualityChecker.count_words(s)
        zwnj = KurdishQualityChecker.count_zwnj(s)
        purity = KurdishQualityChecker.kurdish_purity(s)
        
        # Score components
        word_score = 0
        if 12 <= words <= 22:
            word_score = 40  # Perfect range
        elif 10 <= words <= 25:
            word_score = 30  # Acceptable
        elif 8 <= words <= 30:
            word_score = 15  # Borderline
        
        zwnj_score = 0
        if 8.0 <= zwnj <= 12.0:
            zwnj_score = 40  # Perfect range (Phase 4 target)
        elif 6.0 <= zwnj <= 14.0:
            zwnj_score = 30  # Good
        elif 4.0 <= zwnj <= 16.0:
            zwnj_score = 15  # Acceptable
        
        purity_score = 0
        if purity >= 95.0:
            purity_score = 20  # Excellent
        elif purity >= 90.0:
            purity_score = 15  # Good
        elif purity >= 85.0:
            purity_score = 10  # Acceptable
        elif purity >= 75.0:
            purity_score = 5   # Marginal
        
        total = word_score + zwnj_score + purity_score
        return total


def main():
    print("=" * 70)
    print("🔍 High-Quality Sentence Extractor")
    print("=" * 70)
    
    # Load existing Wikipedia corpus
    wiki_file = Path("corpus/ckb_wikipedia.txt")
    
    if not wiki_file.exists():
        print(f"❌ File not found: {wiki_file}")
        return
    
    print(f"\n📖 Loading: {wiki_file}")
    
    with open(wiki_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    print(f"   Total lines: {len(lines):,}")
    
    # Score all sentences
    print("\n📊 Scoring sentences...")
    scored_sentences = []
    
    checker = KurdishQualityChecker()
    
    for line in lines:
        score = checker.score_sentence(line)
        if score > 0:  # Only include sentences with some quality
            scored_sentences.append((score, line))
    
    print(f"   Sentences with score > 0: {len(scored_sentences):,}")
    
    # Sort by score (descending)
    scored_sentences.sort(reverse=True, key=lambda x: x[0])
    
    # Show score distribution
    if scored_sentences:
        top_score = scored_sentences[0][0]
        print(f"   Top score: {top_score:.0f}/100")
        
        # Count by score ranges
        excellent = sum(1 for s, _ in scored_sentences if s >= 80)
        good = sum(1 for s, _ in scored_sentences if 60 <= s < 80)
        acceptable = sum(1 for s, _ in scored_sentences if 40 <= s < 60)
        marginal = sum(1 for s, _ in scored_sentences if 20 <= s < 40)
        poor = sum(1 for s, _ in scored_sentences if s < 20)
        
        print(f"\n   Score distribution:")
        print(f"      Excellent (80-100): {excellent}")
        print(f"      Good (60-79): {good}")
        print(f"      Acceptable (40-59): {acceptable}")
        print(f"      Marginal (20-39): {marginal}")
        print(f"      Poor (0-19): {poor}")
    
    # Take top 500 sentences
    target = 500
    top_sentences = scored_sentences[:target]
    
    print(f"\n✂️  Selecting top {len(top_sentences)} sentences")
    
    # Save to file
    output_file = Path("corpus/kurdish_news_batch1.txt")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for score, sentence in top_sentences:
            f.write(sentence + '\n')
    
    # Calculate statistics
    sentences_only = [s for _, s in top_sentences]
    total_words = sum(checker.count_words(s) for s in sentences_only)
    total_chars = sum(len(s) for s in sentences_only)
    total_zwnj = sum(s.count(checker.ZWNJ) for s in sentences_only)
    avg_zwnj = (total_zwnj / total_chars * 100) if total_chars > 0 else 0
    avg_score = sum(score for score, _ in top_sentences) / len(top_sentences) if top_sentences else 0
    
    print("\n" + "=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    print(f"✅ Saved to: {output_file}")
    print(f"📝 Sentences: {len(top_sentences)}")
    print(f"⭐ Average quality score: {avg_score:.1f}/100")
    print(f"📚 Total words: {total_words:,}")
    print(f"🔗 ZWNJ density: {avg_zwnj:.2f}%")
    print(f"📏 Avg words/sentence: {total_words / len(top_sentences):.1f}")
    
    # Show sample sentences
    print("\n📋 Sample sentences (top 3):")
    for i, (score, sentence) in enumerate(top_sentences[:3], 1):
        preview = sentence[:80] + "..." if len(sentence) > 80 else sentence
        print(f"   {i}. [{score:.0f}] {preview}")
    
    print("\n📋 Next steps:")
    print("   1. Review: cat corpus/kurdish_news_batch1.txt | head -20")
    print("   2. Quality check: python3 tools/corpus_quality_checker.py corpus/kurdish_news_batch1.txt")
    print("   3. Create batch: python3 tools/incremental_training.py create 1 corpus/kurdish_news_batch1.txt 500")
    print("   4. Train: cd c:\\tesseract && .\\run_training.ps1 -Mode GenerateTrain")
    print("=" * 70)


if __name__ == '__main__':
    main()
