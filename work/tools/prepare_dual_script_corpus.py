#!/usr/bin/env python3
"""
Prepare corpus for dual-script (Arabic + Latin) training.
Handles mixed-script lines by keeping them but ensuring proper balance.
"""
import re
import sys

def analyze_script(line):
    """Analyze script composition."""
    line = line.strip()
    arabic = len(re.findall(r'[\u0600-\u06FF]', line))
    latin = len(re.findall(r'[A-Za-z]', line))
    return arabic, latin

def is_problematic_mixed(line):
    """Check if mixed line will cause encoding issues."""
    arabic, latin = analyze_script(line)
    
    # Allow lines with embedded Latin words in Arabic context
    if arabic > 0 and latin > 0:
        # If Latin is just small technical terms/names (< 30% of letters)
        total = arabic + latin
        if total > 0 and (latin / total) < 0.3:
            return False  # Safe mixed line
        else:
            return True  # Too much Latin, will cause issues
    return False

def main():
    input_file = '../corpus/ckb.training_text'
    output_file = '../corpus/ckb_dual_script.training_text'
    rejected_file = '../corpus/ckb_rejected_mixed.txt'
    
    # Read corpus
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Filter lines
    accepted = []
    rejected = []
    
    stats = {
        'arabic_only': 0,
        'safe_mixed': 0,
        'rejected_mixed': 0,
        'total': len(lines)
    }
    
    for line in lines:
        arabic, latin = analyze_script(line)
        
        if arabic > 0 and latin == 0:
            # Pure Arabic - always accept
            accepted.append(line)
            stats['arabic_only'] += 1
        elif is_problematic_mixed(line):
            # Too much Latin - reject
            rejected.append(line)
            stats['rejected_mixed'] += 1
        else:
            # Safe mixed (small Latin terms in Arabic context) - accept
            accepted.append(line)
            stats['safe_mixed'] += 1
    
    # Write outputs
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(accepted)
    
    with open(rejected_file, 'w', encoding='utf-8') as f:
        f.writelines(rejected)
    
    # Report
    print('Dual-Script Corpus Preparation')
    print('=' * 50)
    print(f'Total lines: {stats["total"]}')
    print(f'Arabic-only: {stats["arabic_only"]} ({100*stats["arabic_only"]/stats["total"]:.1f}%)')
    print(f'Safe mixed: {stats["safe_mixed"]} ({100*stats["safe_mixed"]/stats["total"]:.1f}%)')
    print(f'Rejected: {stats["rejected_mixed"]} ({100*stats["rejected_mixed"]/stats["total"]:.1f}%)')
    print()
    print(f'✓ Accepted: {len(accepted)} lines → {output_file}')
    print(f'✗ Rejected: {len(rejected)} lines → {rejected_file}')
    print()
    
    # Calculate ZWNJ percentage
    accepted_text = ''.join(accepted)
    zwnj_count = accepted_text.count('\u200c')
    total_chars = len([c for c in accepted_text if c.strip()])
    zwnj_pct = 100 * zwnj_count / total_chars if total_chars > 0 else 0
    
    print(f'ZWNJ in accepted corpus: {zwnj_count:,} ({zwnj_pct:.2f}%)')
    print(f'Ready for training with -LatinDigits flag!')

if __name__ == '__main__':
    main()
