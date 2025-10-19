#!/usr/bin/env python3
"""
Sample Kurdish News Extractor
Demonstrates how to extract sentences from Kurdish news articles
"""

import re

def extract_sentences_from_text(text):
    """
    Extract sentences from Kurdish text.
    Splits on common sentence terminators: . ! ? ، and newlines
    """
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Split on sentence terminators (Kurdish and Arabic punctuation)
    # . (period), ! (exclamation), ? (question), ، (Arabic comma as separator)
    sentences = re.split(r'[\.!?،]\s*', text)
    
    # Clean and filter sentences
    clean_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        
        # Skip if too short or too long
        word_count = len(sentence.split())
        if word_count < 10 or word_count > 25:
            continue
            
        # Skip if contains URLs, dates, English text
        if any(skip in sentence.lower() for skip in ['http', 'www.', '@', '#']):
            continue
        if re.search(r'[a-zA-Z]{3,}', sentence):  # 3+ consecutive Latin chars
            continue
        if re.search(r'\d{4}', sentence):  # Standalone years
            continue
            
        # Check ZWNJ presence (good indicator of Kurdish text)
        zwnj_count = sentence.count('\u200c')
        if zwnj_count > 0:
            clean_sentences.append(sentence)
    
    return clean_sentences

def calculate_zwnj_density(text):
    """Calculate ZWNJ density percentage"""
    if not text:
        return 0.0
    chars = len(text)
    zwnj_count = text.count('\u200c')
    return (zwnj_count / chars) * 100 if chars > 0 else 0.0

def main():
    print("=" * 70)
    print("🔍 Kurdish News Sentence Extractor - Example")
    print("=" * 70)
    print()
    
    # Example article text from Rudaw (you would copy this from the website)
    example_text = """
    حکومەتی هەرێمی کوردستان لە کۆبوونەوەیەکی ئاساییدا چەندین بڕیاری گرنگی 
    دەرکرد کە پەیوەندیی بە پێشخستنی پڕۆژە گشتییەکانەوە هەیە. بەپێی ڕاگەیاندنی 
    فەرمی، ئەم بڕیارانە لە چوارچێوەی پلانی حکومەتدا بۆ باشترکردنی خزمەتگوزاری 
    دەخرێنە بواری جێبەجێکردنەوە. سەرۆکی حکومەت لە کۆبوونەوەکەدا تیشکی خستە 
    سەر گرنگی هاوکاری نێوان وەزارەتەکان بۆ جێبەجێکردنی ئەم پڕۆژانە. وەزیری 
    دارایی باسی لە دابینکردنی بودجەی پێویست کرد بۆ ئەم مەبەستە.
    """
    
    print("📄 Example article text:")
    print("-" * 70)
    print(example_text.strip())
    print()
    print("=" * 70)
    print()
    
    # Extract sentences
    sentences = extract_sentences_from_text(example_text)
    
    print(f"✅ Extracted {len(sentences)} valid sentences:")
    print("=" * 70)
    print()
    
    for i, sentence in enumerate(sentences, 1):
        word_count = len(sentence.split())
        zwnj_density = calculate_zwnj_density(sentence)
        
        print(f"{i}. [{word_count} words, {zwnj_density:.1f}% ZWNJ]")
        print(f"   {sentence}")
        print()
    
    # Overall statistics
    if sentences:
        all_text = ' '.join(sentences)
        total_words = sum(len(s.split()) for s in sentences)
        avg_words = total_words / len(sentences)
        overall_zwnj = calculate_zwnj_density(all_text)
        
        print("=" * 70)
        print("📊 Statistics:")
        print(f"   Total sentences: {len(sentences)}")
        print(f"   Total words: {total_words}")
        print(f"   Avg words/sentence: {avg_words:.1f}")
        print(f"   Overall ZWNJ density: {overall_zwnj:.2f}%")
        print()
        
        if overall_zwnj >= 8 and overall_zwnj <= 12:
            print("   ✅ ZWNJ density in target range (8-12%)")
        elif overall_zwnj < 8:
            print("   ⚠️  ZWNJ density low, look for more formal articles")
        else:
            print("   ⚠️  ZWNJ density high (acceptable but unusual)")
    
    print()
    print("=" * 70)
    print("💡 How to use this for collection:")
    print("   1. Copy article text from Rudaw/BasNews/NRT")
    print("   2. Paste into this script as 'example_text'")
    print("   3. Run script to extract valid sentences")
    print("   4. Copy extracted sentences to kurdish_news_batch2.txt")
    print("=" * 70)

if __name__ == "__main__":
    main()
