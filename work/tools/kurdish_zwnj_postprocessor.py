#!/usr/bin/env python3
"""
Kurdish ZWNJ Post-Processor
Applies ZWNJ insertion rules to OCR output text
"""

import sys
import argparse
from pathlib import Path
from kurdish_zwnj_rules import KurdishZWNJRules

def process_file(input_path: str, output_path: str = None, ground_truth_path: str = None) -> dict:
    """
    Process OCR output file and insert ZWNJs using Kurdish grammar rules
    
    Args:
        input_path: Path to OCR output text file
        output_path: Path to save processed text (optional)
        ground_truth_path: Path to ground truth for comparison (optional)
        
    Returns:
        Dictionary with processing statistics
    """
    # Read input file
    input_file = Path(input_path)
    if not input_file.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        input_text = f.read()
    
    print(f"Input file: {input_path}")
    print(f"Input length: {len(input_text)} characters")
    print(f"Original ZWNJs: {input_text.count(chr(0x200c))}")
    print()
    
    # Apply ZWNJ rules
    rules = KurdishZWNJRules()
    processed_text, stats = rules.apply_all_rules(input_text)
    
    # Print statistics
    print("=" * 60)
    print("ZWNJ INSERTION STATISTICS")
    print("=" * 60)
    print(f"Original ZWNJs:     {stats['original_zwnj']}")
    print(f"Ezafe insertions:   {stats['ezafe']}")
    print(f"Compound words:     {stats['compound_words']}")
    print(f"Suffixes:           {stats['suffixes']}")
    print(f"Prepositions:       {stats['prepositions']}")
    print(f"Total inserted:     {stats['total_inserted']}")
    print(f"Final ZWNJ count:   {stats['final_zwnj']}")
    print("=" * 60)
    print()
    
    # Save output if path provided
    if output_path:
        output_file = Path(output_path)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(processed_text)
        print(f"Processed text saved to: {output_path}")
        print()
    
    # Compare with ground truth if provided
    if ground_truth_path:
        gt_file = Path(ground_truth_path)
        if not gt_file.exists():
            print(f"Warning: Ground truth file not found: {ground_truth_path}")
        else:
            with open(gt_file, 'r', encoding='utf-8') as f:
                ground_truth = f.read()
            
            metrics = rules.compare_with_ground_truth(processed_text, ground_truth)
            
            print("=" * 60)
            print("COMPARISON WITH GROUND TRUTH")
            print("=" * 60)
            print(f"Ground truth ZWNJs:  {metrics['ground_truth_count']}")
            print(f"Predicted ZWNJs:     {metrics['predicted_count']}")
            print(f"True positives:      {metrics['true_positives']}")
            print(f"False positives:     {metrics['false_positives']}")
            print(f"False negatives:     {metrics['false_negatives']}")
            print()
            print(f"Precision:           {metrics['precision']:.2%}")
            print(f"Recall:              {metrics['recall']:.2%}")
            print(f"F1 Score:            {metrics['f1_score']:.2%}")
            print("=" * 60)
            
            # Calculate recovery rate
            recovery_rate = metrics['recall'] * 100
            print()
            print(f"ZWNJ Recovery Rate: {recovery_rate:.1f}%")
            print()
            
            if recovery_rate >= 80:
                print("✅ SUCCESS: Recovery rate meets target (≥80%)")
            elif recovery_rate >= 70:
                print("⚠️  ACCEPTABLE: Recovery rate acceptable (70-79%)")
            else:
                print("❌ NEEDS IMPROVEMENT: Recovery rate below target (<70%)")
    
    return stats


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Apply ZWNJ insertion rules to Kurdish OCR output',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process OCR output
  python3 kurdish_zwnj_postprocessor.py mgk_phase4.txt -o mgk_processed.txt
  
  # Process and compare with ground truth
  python3 kurdish_zwnj_postprocessor.py mgk_phase4.txt -o mgk_processed.txt -g mgk.gt.txt
        """
    )
    
    parser.add_argument('input', help='Input OCR text file')
    parser.add_argument('-o', '--output', help='Output file path (optional)')
    parser.add_argument('-g', '--ground-truth', help='Ground truth file for comparison (optional)')
    
    args = parser.parse_args()
    
    # Default output path if not provided
    output_path = args.output
    if not output_path:
        input_file = Path(args.input)
        output_path = str(input_file.parent / f"{input_file.stem}_processed{input_file.suffix}")
    
    # Process file
    process_file(args.input, output_path, args.ground_truth)


if __name__ == "__main__":
    main()
