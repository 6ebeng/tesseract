#!/usr/bin/env python3
"""Analyze ZWNJ and Tatweel usage in mgk.tif ground truth."""

def main():
    gt_file = '/mnt/c/tesseract/work/real_gt/mgk.gt.txt'
    
    try:
        with open(gt_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        total_chars = len(text)
        zwnj_count = text.count('\u200c')  # Zero Width Non-Joiner
        tatweel_count = text.count('\u0640')  # Arabic Tatweel (kashida)
        
        zwnj_pct = (zwnj_count / total_chars * 100) if total_chars > 0 else 0
        tatweel_pct = (tatweel_count / total_chars * 100) if total_chars > 0 else 0
        
        print('='*60)
        print('MGK.TIF GROUND TRUTH UNICODE ANALYSIS')
        print('='*60)
        print(f'Total characters: {total_chars:,}')
        print()
        print(f'ZWNJ (U+200C):')
        print(f'  Count: {zwnj_count:,}')
        print(f'  Percentage: {zwnj_pct:.3f}%')
        print()
        print(f'Tatweel (U+0640):')
        print(f'  Count: {tatweel_count:,}')
        print(f'  Percentage: {tatweel_pct:.3f}%')
        print('='*60)
        
        # Show examples if they exist
        if tatweel_count > 0:
            print('\nTatweel examples (first 5):')
            lines_with_tatweel = [line for line in text.split('\n') if '\u0640' in line]
            for i, line in enumerate(lines_with_tatweel[:5], 1):
                # Show position of tatweel
                pos = line.find('\u0640')
                excerpt = line[max(0, pos-10):pos+11]
                print(f'  {i}. ...{excerpt}...')
        
    except FileNotFoundError:
        print(f'❌ File not found: {gt_file}')
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == '__main__':
    main()
