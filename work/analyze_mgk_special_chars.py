#!/usr/bin/env python3
"""Analyze ZWNJ and Tatweel in mgk.tif ground truth."""

def main():
    # Analyze mgk.tif ground truth
    with open('real_gt/eval/mgk.gt.txt', 'r', encoding='utf-8') as f:
        gt_text = f.read()
    
    total_chars = len(gt_text)
    zwnj_count = gt_text.count('\u200c')
    tatweel_count = gt_text.count('\u0640')
    
    print("\n" + "="*60)
    print("mgk.tif Ground Truth Analysis")
    print("="*60)
    print(f"Total characters: {total_chars:,}")
    print(f"ZWNJ (U+200C) count: {zwnj_count:,}")
    print(f"ZWNJ density: {zwnj_count/total_chars*100:.4f}%")
    print(f"Tatweel (U+0640) count: {tatweel_count:,}")
    print(f"Tatweel density: {tatweel_count/total_chars*100:.4f}%")
    
    # Find examples of ZWNJ usage
    print("\n" + "="*60)
    print("ZWNJ Usage Examples from mgk.tif")
    print("="*60)
    
    lines = gt_text.split('\n')
    zwnj_examples = []
    
    for i, line in enumerate(lines):
        if '\u200c' in line:
            # Count ZWNJ in this line
            line_zwnj = line.count('\u200c')
            # Show with markers
            marked = line.replace('\u200c', '‌[ZWNJ]')
            zwnj_examples.append((i+1, line_zwnj, marked[:120]))
            if len(zwnj_examples) >= 10:
                break
    
    for line_num, count, example in zwnj_examples:
        print(f"\nLine {line_num} ({count} ZWNJ):")
        print(f"  {example}")
    
    # Find Tatweel examples if any
    if tatweel_count > 0:
        print("\n" + "="*60)
        print("Tatweel Usage Examples from mgk.tif")
        print("="*60)
        
        tatweel_examples = []
        for i, line in enumerate(lines):
            if '\u0640' in line:
                marked = line.replace('\u0640', '[TATWEEL]')
                tatweel_examples.append((i+1, marked[:120]))
                if len(tatweel_examples) >= 5:
                    break
        
        for line_num, example in tatweel_examples:
            print(f"\nLine {line_num}:")
            print(f"  {example}")
    
    # Compare with training corpus
    print("\n" + "="*60)
    print("COMPARISON: Test Image vs Training Corpus")
    print("="*60)
    
    with open('corpus/ckb_phase6_batch4.training_text', 'r', encoding='utf-8') as f:
        corpus_text = f.read()
    
    corpus_zwnj = corpus_text.count('\u200c') / len(corpus_text) * 100
    
    print(f"\n{'Source':<30} {'ZWNJ %':>10} {'Tatweel %':>12}")
    print("-" * 60)
    print(f"{'mgk.tif (Test Image)':<30} {zwnj_count/total_chars*100:>9.4f}% {tatweel_count/total_chars*100:>11.4f}%")
    print(f"{'Batch 4 Training Corpus':<30} {corpus_zwnj:>9.4f}% {corpus_text.count('\u0640')/len(corpus_text)*100:>11.4f}%")
    
    # Calculate the mismatch
    zwnj_diff = abs((zwnj_count/total_chars*100) - corpus_zwnj)
    print(f"\nZWNJ Density Mismatch: {zwnj_diff:.4f}%")
    
    if zwnj_diff < 1.0:
        print("✅ Good match - Similar ZWNJ usage patterns")
    elif zwnj_diff < 3.0:
        print("⚠️  Moderate mismatch - May affect accuracy")
    else:
        print("❌ Large mismatch - Significant impact on accuracy")

if __name__ == '__main__':
    main()
