#!/usr/bin/env python3
"""
Kurdish Corpus Quality Checker for Phase 6

Analyzes corpus quality metrics:
- ZWNJ density
- Sentence length distribution
- Kurdish script purity
- Duplicate detection
- Overall quality grading
"""

import re
import sys
import json
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter


class CorpusQualityAnalyzer:
    """Analyze quality of Kurdish training corpus."""
    
    KURDISH_CHARS = set('ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهھوۆەیێ')
    ARABIC_DIGITS = '٠١٢٣٤٥٦٧٨٩'
    ASCII_DIGITS = '0123456789'
    ZWNJ = '\u200c'
    
    def __init__(self, corpus_file: str):
        self.corpus_file = Path(corpus_file)
        self.lines = []
        self.load_corpus()
    
    def load_corpus(self):
        """Load corpus from file."""
        if not self.corpus_file.exists():
            print(f"❌ File not found: {self.corpus_file}")
            sys.exit(1)
        
        with open(self.corpus_file, 'r', encoding='utf-8') as f:
            self.lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        print(f"📂 Loaded: {self.corpus_file}")
        print(f"   Lines: {len(self.lines):,}\n")
    
    def analyze_zwnj(self) -> Dict:
        """Analyze ZWNJ usage."""
        total_chars = sum(len(line) for line in self.lines)
        total_zwnj = sum(line.count(self.ZWNJ) for line in self.lines)
        
        # Lines with ZWNJ
        lines_with_zwnj = sum(1 for line in self.lines if self.ZWNJ in line)
        
        # ZWNJ density per line
        densities = []
        for line in self.lines:
            if len(line) > 0:
                density = (line.count(self.ZWNJ) / len(line)) * 100
                densities.append(density)
        
        # Count lines in target range (8-12%)
        in_range = sum(1 for d in densities if 8.0 <= d <= 12.0)
        
        return {
            'total_zwnj': total_zwnj,
            'total_chars': total_chars,
            'overall_density': (total_zwnj / total_chars * 100) if total_chars > 0 else 0,
            'lines_with_zwnj': lines_with_zwnj,
            'lines_with_zwnj_pct': (lines_with_zwnj / len(self.lines) * 100) if self.lines else 0,
            'in_target_range': in_range,
            'in_target_range_pct': (in_range / len(self.lines) * 100) if self.lines else 0,
            'min_density': min(densities) if densities else 0,
            'max_density': max(densities) if densities else 0,
            'avg_density': sum(densities) / len(densities) if densities else 0,
        }
    
    def analyze_length(self) -> Dict:
        """Analyze sentence/line length."""
        word_counts = []
        char_counts = []
        
        for line in self.lines:
            # Count Kurdish/Arabic words
            words = re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+', line)
            word_counts.append(len(words))
            char_counts.append(len(line))
        
        # Count lines in target range (10-25 words)
        in_range = sum(1 for wc in word_counts if 10 <= wc <= 25)
        
        return {
            'total_words': sum(word_counts),
            'avg_words_per_line': sum(word_counts) / len(word_counts) if word_counts else 0,
            'min_words': min(word_counts) if word_counts else 0,
            'max_words': max(word_counts) if word_counts else 0,
            'in_target_range': in_range,
            'in_target_range_pct': (in_range / len(self.lines) * 100) if self.lines else 0,
            'avg_chars_per_line': sum(char_counts) / len(char_counts) if char_counts else 0,
        }
    
    def analyze_script_purity(self) -> Dict:
        """Analyze Kurdish script purity."""
        kurdish_purities = []
        
        for line in self.lines:
            kurdish_count = sum(1 for c in line if c in self.KURDISH_CHARS)
            letter_count = sum(1 for c in line if unicodedata.category(c).startswith('L'))
            
            if letter_count > 0:
                purity = (kurdish_count / letter_count) * 100
                kurdish_purities.append(purity)
        
        # Count lines with >85% Kurdish
        high_purity = sum(1 for p in kurdish_purities if p >= 85.0)
        
        return {
            'avg_kurdish_purity': sum(kurdish_purities) / len(kurdish_purities) if kurdish_purities else 0,
            'min_purity': min(kurdish_purities) if kurdish_purities else 0,
            'max_purity': max(kurdish_purities) if kurdish_purities else 0,
            'high_purity_lines': high_purity,
            'high_purity_pct': (high_purity / len(self.lines) * 100) if self.lines else 0,
        }
    
    def analyze_duplicates(self) -> Dict:
        """Detect duplicate lines."""
        line_counts = Counter(self.lines)
        duplicates = {line: count for line, count in line_counts.items() if count > 1}
        
        return {
            'unique_lines': len(line_counts),
            'duplicate_lines': len(duplicates),
            'duplicate_count': sum(count - 1 for count in duplicates.values()),
            'most_common': line_counts.most_common(5),
        }
    
    def analyze_character_distribution(self) -> Dict:
        """Analyze character frequency distribution."""
        char_counts = Counter()
        for line in self.lines:
            char_counts.update(line)
        
        # Kurdish letters
        kurdish_letter_counts = {char: char_counts[char] for char in self.KURDISH_CHARS if char in char_counts}
        
        return {
            'total_chars': sum(char_counts.values()),
            'unique_chars': len(char_counts),
            'kurdish_letters': dict(sorted(kurdish_letter_counts.items(), key=lambda x: x[1], reverse=True)[:20]),
            'zwnj_count': char_counts.get(self.ZWNJ, 0),
        }
    
    def grade_quality(self, zwnj_stats: Dict, length_stats: Dict, purity_stats: Dict) -> Tuple[str, float]:
        """
        Grade overall corpus quality.
        
        Returns:
            Tuple of (grade letter, score 0-100)
        """
        score = 0.0
        max_score = 100.0
        
        # ZWNJ density (30 points)
        # Target: 8-12% overall, 80%+ lines in range
        zwnj_density = zwnj_stats['overall_density']
        if 8.0 <= zwnj_density <= 12.0:
            score += 20
        elif 6.0 <= zwnj_density <= 14.0:
            score += 10
        
        zwnj_range_pct = zwnj_stats['in_target_range_pct']
        if zwnj_range_pct >= 80:
            score += 10
        elif zwnj_range_pct >= 60:
            score += 5
        
        # Length distribution (25 points)
        # Target: 10-25 words, 80%+ lines in range
        avg_words = length_stats['avg_words_per_line']
        if 12 <= avg_words <= 22:
            score += 15
        elif 10 <= avg_words <= 25:
            score += 10
        
        length_range_pct = length_stats['in_target_range_pct']
        if length_range_pct >= 80:
            score += 10
        elif length_range_pct >= 60:
            score += 5
        
        # Script purity (25 points)
        # Target: >85% Kurdish
        avg_purity = purity_stats['avg_kurdish_purity']
        if avg_purity >= 90:
            score += 15
        elif avg_purity >= 85:
            score += 10
        elif avg_purity >= 80:
            score += 5
        
        high_purity_pct = purity_stats['high_purity_pct']
        if high_purity_pct >= 85:
            score += 10
        elif high_purity_pct >= 70:
            score += 5
        
        # Uniqueness (20 points)
        # Target: <5% duplicates
        unique_lines = len(self.lines)
        if unique_lines == len(set(self.lines)):
            score += 20
        else:
            dup_pct = (len(self.lines) - unique_lines) / len(self.lines) * 100
            if dup_pct < 5:
                score += 15
            elif dup_pct < 10:
                score += 10
            elif dup_pct < 20:
                score += 5
        
        # Convert to grade
        percentage = (score / max_score) * 100
        if percentage >= 90:
            grade = 'A'
        elif percentage >= 80:
            grade = 'B'
        elif percentage >= 70:
            grade = 'C'
        elif percentage >= 60:
            grade = 'D'
        else:
            grade = 'F'
        
        return grade, percentage
    
    def generate_report(self, output_file: str = None):
        """Generate comprehensive quality report."""
        print("=" * 70)
        print("📊 KURDISH CORPUS QUALITY REPORT")
        print("=" * 70)
        
        # Basic stats
        print(f"\n📁 Corpus: {self.corpus_file.name}")
        print(f"   Total lines: {len(self.lines):,}")
        
        # ZWNJ analysis
        print("\n🔤 ZWNJ Analysis:")
        zwnj_stats = self.analyze_zwnj()
        print(f"   Overall density: {zwnj_stats['overall_density']:.2f}% (target: 8-12%)")
        print(f"   Lines with ZWNJ: {zwnj_stats['lines_with_zwnj']:,} ({zwnj_stats['lines_with_zwnj_pct']:.1f}%)")
        print(f"   Lines in target range: {zwnj_stats['in_target_range']:,} ({zwnj_stats['in_target_range_pct']:.1f}%)")
        print(f"   Range: {zwnj_stats['min_density']:.2f}% - {zwnj_stats['max_density']:.2f}%")
        
        # Length analysis
        print("\n📏 Length Analysis:")
        length_stats = self.analyze_length()
        print(f"   Total words: {length_stats['total_words']:,}")
        print(f"   Avg words/line: {length_stats['avg_words_per_line']:.1f} (target: 10-25)")
        print(f"   Range: {length_stats['min_words']}-{length_stats['max_words']} words")
        print(f"   Lines in target range: {length_stats['in_target_range']:,} ({length_stats['in_target_range_pct']:.1f}%)")
        print(f"   Avg chars/line: {length_stats['avg_chars_per_line']:.1f}")
        
        # Script purity
        print("\n🔠 Script Purity:")
        purity_stats = self.analyze_script_purity()
        print(f"   Avg Kurdish purity: {purity_stats['avg_kurdish_purity']:.1f}% (target: >85%)")
        print(f"   Range: {purity_stats['min_purity']:.1f}% - {purity_stats['max_purity']:.1f}%")
        print(f"   High purity lines (>85%): {purity_stats['high_purity_lines']:,} ({purity_stats['high_purity_pct']:.1f}%)")
        
        # Duplicates
        print("\n🔄 Duplicate Analysis:")
        dup_stats = self.analyze_duplicates()
        print(f"   Unique lines: {dup_stats['unique_lines']:,}")
        print(f"   Duplicate lines: {dup_stats['duplicate_lines']:,}")
        print(f"   Total duplicates: {dup_stats['duplicate_count']:,}")
        
        # Overall grade
        print("\n🎯 Overall Quality Grade:")
        grade, score = self.grade_quality(zwnj_stats, length_stats, purity_stats)
        print(f"   Grade: {grade} ({score:.1f}/100)")
        
        # Recommendations
        print("\n💡 Recommendations:")
        if zwnj_stats['overall_density'] < 8.0:
            print(f"   ⚠️  ZWNJ density too low ({zwnj_stats['overall_density']:.2f}%) - add more formal text")
        elif zwnj_stats['overall_density'] > 12.0:
            print(f"   ⚠️  ZWNJ density too high ({zwnj_stats['overall_density']:.2f}%) - may have artificial inflation")
        else:
            print(f"   ✅ ZWNJ density in target range ({zwnj_stats['overall_density']:.2f}%)")
        
        if length_stats['avg_words_per_line'] < 10:
            print(f"   ⚠️  Sentences too short (avg {length_stats['avg_words_per_line']:.1f} words)")
        elif length_stats['avg_words_per_line'] > 25:
            print(f"   ⚠️  Sentences too long (avg {length_stats['avg_words_per_line']:.1f} words)")
        else:
            print(f"   ✅ Sentence length in target range")
        
        if purity_stats['avg_kurdish_purity'] < 85:
            print(f"   ⚠️  Kurdish purity low ({purity_stats['avg_kurdish_purity']:.1f}%) - too much Latin/other scripts")
        else:
            print(f"   ✅ Kurdish script purity good ({purity_stats['avg_kurdish_purity']:.1f}%)")
        
        if dup_stats['duplicate_count'] > 0:
            print(f"   ⚠️  Found {dup_stats['duplicate_count']:,} duplicate lines - consider deduplication")
        else:
            print(f"   ✅ No duplicates found")
        
        print("\n" + "=" * 70)
        
        # Save JSON report if requested
        if output_file:
            report_data = {
                'corpus_file': str(self.corpus_file),
                'total_lines': len(self.lines),
                'zwnj': zwnj_stats,
                'length': length_stats,
                'purity': purity_stats,
                'duplicates': {k: v for k, v in dup_stats.items() if k != 'most_common'},
                'grade': grade,
                'score': score,
            }
            
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Report saved: {output_path}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 corpus_quality_checker.py <corpus_file> [output_json]")
        print("\nExample:")
        print("  python3 corpus_quality_checker.py corpus/ckb_phase6_batch1.txt")
        print("  python3 corpus_quality_checker.py corpus/ckb.training_text corpus_quality.json")
        sys.exit(1)
    
    corpus_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    analyzer = CorpusQualityAnalyzer(corpus_file)
    analyzer.generate_report(output_file)


if __name__ == '__main__':
    main()
