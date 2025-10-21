#!/usr/bin/env python3
"""
Test Kurdish post-processor on real OCR outputs
Compare before/after accuracy on multi-image test set
"""

import sys
import os
from difflib import SequenceMatcher

# Add tools to path
sys.path.insert(0, os.path.dirname(__file__))
from kurdish_postprocessor import KurdishPostProcessor, evaluate_postprocessing

def calculate_accuracy(gt_text, ocr_text):
    """Calculate character accuracy using SequenceMatcher"""
    matcher = SequenceMatcher(None, gt_text, ocr_text)
    matches = sum(block.size for block in matcher.get_matching_blocks())
    cer = 1 - (matches / len(gt_text))
    return (1 - cer) * 100, cer

def test_image(image_name, gt_file, ocr_file, processor):
    """Test post-processing on a single image"""
    
    # Read ground truth
    with open(gt_file, 'r', encoding='utf-8') as f:
        gt_text = f.read().strip()
    
    # Read OCR output
    with open(ocr_file, 'r', encoding='utf-8') as f:
        ocr_text = f.read().strip()
    
    # Calculate before accuracy
    acc_before, cer_before = calculate_accuracy(gt_text, ocr_text)
    
    # Apply post-processing
    ocr_processed = processor.process(ocr_text)
    
    # Calculate after accuracy
    acc_after, cer_after = calculate_accuracy(gt_text, ocr_processed)
    
    improvement = acc_after - acc_before
    
    return {
        'name': image_name,
        'before': {
            'accuracy': acc_before,
            'cer': cer_before,
            'chars': len(ocr_text)
        },
        'after': {
            'accuracy': acc_after,
            'cer': cer_after,
            'chars': len(ocr_processed)
        },
        'improvement': improvement,
        'gt_chars': len(gt_text)
    }

def main():
    print("="*70)
    print("KURDISH OCR POST-PROCESSING TEST")
    print("="*70)
    print()
    
    # Initialize post-processor
    processor = KurdishPostProcessor()
    
    # Test images
    test_images = [
        ('kurdsat2', 'real_gt/eval_clean/kurdsat2.gt.txt', 'output/kurdsat2.txt'),
        ('kurdsat3', 'real_gt/eval_clean/kurdsat3.gt.txt', 'output/kurdsat3.txt'),
        ('rudaw1', 'real_gt/eval_clean/rudaw1.gt.txt', 'output/rudaw1.txt'),
        ('rudaw2', 'real_gt/eval_clean/rudaw2.gt.txt', 'output/rudaw2.txt'),
        ('mgk', 'real_gt/eval/mgk.gt.txt', 'output/mgk.txt'),
    ]
    
    results = []
    
    for name, gt_file, ocr_file in test_images:
        if not os.path.exists(gt_file):
            print(f"⚠️  Skipping {name}: GT file not found")
            continue
        if not os.path.exists(ocr_file):
            print(f"⚠️  Skipping {name}: OCR file not found")
            continue
        
        print(f"Testing {name}...")
        result = test_image(name, gt_file, ocr_file, processor)
        results.append(result)
    
    # Report results
    print("\n" + "="*70)
    print("INDIVIDUAL RESULTS")
    print("="*70)
    print()
    
    for r in results:
        print(f"{r['name']:12s}: {r['before']['accuracy']:5.2f}% → {r['after']['accuracy']:5.2f}% "
              f"({r['improvement']:+.2f}%)")
    
    # Summary statistics
    if results:
        avg_before = sum(r['before']['accuracy'] for r in results) / len(results)
        avg_after = sum(r['after']['accuracy'] for r in results) / len(results)
        avg_improvement = avg_after - avg_before
        
        print("\n" + "="*70)
        print("SUMMARY STATISTICS")
        print("="*70)
        print(f"Average before:  {avg_before:.2f}%")
        print(f"Average after:   {avg_after:.2f}%")
        print(f"Improvement:     {avg_improvement:+.2f}%")
        print()
        
        if avg_improvement > 0:
            print("✅ Post-processing IMPROVED accuracy!")
        elif avg_improvement < 0:
            print("⚠️  Post-processing REDUCED accuracy (rules need tuning)")
        else:
            print("➖ No change (need better rules)")
    
    else:
        print("\n⚠️  No test results (check file paths)")

if __name__ == '__main__':
    main()
