#!/usr/bin/env python3
"""
Kurdish Sentence Collection Assistant

Helps validate and clean sentences as you collect them.
Run this periodically to check your progress and quality.
"""

import sys
from pathlib import Path


def clean_sentence(text: str) -> str:
    """Clean and normalize a sentence."""
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    # Normalize Arabic to Kurdish
    text = text.replace('ك', 'ک').replace('ي', 'ی')
    return text.strip()


def count_words(text: str) -> int:
    """Count Kurdish/Arabic words."""
    import re
    words = re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+', text)
    return len(words)


def check_sentence_quality(text: str) -> dict:
    """Quick quality check for a sentence."""
    ZWNJ = '\u200c'
    
    word_count = count_words(text)
    zwnj_count = text.count(ZWNJ)
    zwnj_density = (zwnj_count / len(text) * 100) if text else 0
    
    issues = []
    
    if word_count < 10:
        issues.append(f"Too short ({word_count} words, need 10+)")
    elif word_count > 25:
        issues.append(f"Too long ({word_count} words, max 25)")
    
    if zwnj_density < 6:
        issues.append(f"Low ZWNJ density ({zwnj_density:.1f}%, need 8-12%)")
    elif zwnj_density > 15:
        issues.append(f"High ZWNJ density ({zwnj_density:.1f}%, need 8-12%)")
    
    # Check for unwanted patterns
    if any(x in text for x in ['http', 'www.', '@', '٢٠٢', '٢٠٢٤', '2024', '2023']):
        issues.append("Contains URLs/dates/emails")
    
    return {
        'words': word_count,
        'zwnj_density': zwnj_density,
        'zwnj_count': zwnj_count,
        'length': len(text),
        'issues': issues,
        'ok': len(issues) == 0
    }


def process_file(filepath: str):
    """Process collection file and show progress."""
    path = Path(filepath)
    
    if not path.exists():
        print(f"❌ File not found: {filepath}")
        print(f"   Create it at: {path.absolute()}")
        return
    
    with open(path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not lines:
        print("📝 File is empty. Start adding sentences!")
        print("\nSources to visit:")
        print("  1. https://www.rudaw.net/sorani")
        print("  2. https://www.basnews.com")
        print("  3. https://www.nrttv.com")
        return
    
    print("=" * 70)
    print(f"📊 Collection Progress: {filepath}")
    print("=" * 70)
    
    good_count = 0
    total_words = 0
    total_zwnj = 0
    total_chars = 0
    
    print(f"\n✅ Current count: {len(lines)} / 500 sentences")
    print(f"   Progress: {'█' * (len(lines) // 10)}{'░' * (50 - len(lines) // 10)} {len(lines) / 5:.0f}%")
    
    print("\n🔍 Checking quality...")
    problem_lines = []
    
    for i, line in enumerate(lines, 1):
        cleaned = clean_sentence(line)
        quality = check_sentence_quality(cleaned)
        
        total_words += quality['words']
        total_zwnj += quality['zwnj_count']
        total_chars += quality['length']
        
        if quality['ok']:
            good_count += 1
        else:
            problem_lines.append((i, cleaned[:50] + '...', quality['issues']))
            if len(problem_lines) <= 5:  # Show first 5 problems
                print(f"\n⚠️  Line {i}: {cleaned[:60]}...")
                for issue in quality['issues']:
                    print(f"     - {issue}")
    
    avg_zwnj = (total_zwnj / total_chars * 100) if total_chars > 0 else 0
    avg_words = total_words / len(lines) if lines else 0
    
    print("\n" + "=" * 70)
    print("📈 Overall Statistics:")
    print(f"   Total sentences: {len(lines)}")
    print(f"   Good quality: {good_count} ({good_count / len(lines) * 100:.1f}%)")
    print(f"   Problem sentences: {len(problem_lines)} ({len(problem_lines) / len(lines) * 100:.1f}%)")
    print(f"   Average ZWNJ density: {avg_zwnj:.2f}% (target: 8-12%)")
    print(f"   Average words/sentence: {avg_words:.1f} (target: 10-25)")
    print(f"   Total words: {total_words:,}")
    
    print("\n💡 Next Steps:")
    if len(lines) < 500:
        needed = 500 - len(lines)
        print(f"   ✅ Keep collecting! Need {needed} more sentences.")
        print(f"   📍 Target breakdown:")
        print(f"      - Rudaw: {max(0, 200 - int(len(lines) * 0.4))} more")
        print(f"      - BasNews: {max(0, 150 - int(len(lines) * 0.3))} more")
        print(f"      - NRT: {max(0, 150 - int(len(lines) * 0.3))} more")
    else:
        print(f"   ✅ Collection complete! ({len(lines)} sentences)")
        
        if len(problem_lines) > 25:
            print(f"   ⚠️  Many problem sentences ({len(problem_lines)})")
            print(f"      Consider reviewing and fixing or removing them")
        
        if avg_zwnj < 8:
            print(f"   ⚠️  ZWNJ density low ({avg_zwnj:.2f}%)")
            print(f"      Add more sentences with proper ZWNJ usage")
        elif avg_zwnj > 12:
            print(f"   ⚠️  ZWNJ density high ({avg_zwnj:.2f}%)")
            print(f"      May have artificial inflation, review sentences")
        else:
            print(f"   ✅ ZWNJ density good ({avg_zwnj:.2f}%)")
        
        if 10 <= avg_words <= 25:
            print(f"   ✅ Sentence length good ({avg_words:.1f} words)")
        else:
            print(f"   ⚠️  Sentence length off target ({avg_words:.1f} words)")
        
        print("\n   🚀 Ready for next step:")
        print("      1. Clean up any problem sentences")
        print("      2. Remove comment lines (#)")
        print("      3. Run: python3 tools/incremental_training.py create 1 corpus/kurdish_news_batch1.txt 500")
    
    print("=" * 70)


def main():
    """Main entry point."""
    filepath = "corpus/kurdish_news_batch1.txt"
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    
    process_file(filepath)
    
    print("\n💾 To check again, run:")
    print(f"   python3 tools/collection_assistant.py {filepath}")


if __name__ == '__main__':
    main()
