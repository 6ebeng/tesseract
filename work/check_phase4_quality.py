import sys

with open('corpus/ckb_phase4.training_text', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]
    total_chars = sum(len(l) for l in lines)
    zwnj_count = sum(l.count('\u200c') for l in lines)
    total_words = sum(len(l.split()) for l in lines)
    print(f'Phase 4 Baseline:')
    print(f'  Sentences: {len(lines):,}')
    print(f'  Avg Words/Sentence: {total_words/len(lines):.2f}')
    print(f'  ZWNJ Density: {(zwnj_count/total_chars)*100:.2f}%')
