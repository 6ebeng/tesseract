#!/usr/bin/env python3
"""Filter Wikipedia biography corpus - very lenient for low-ZWNJ content"""

import hashlib
from collections import defaultdict
from pathlib import Path

def filter_wiki_corpus():
    seen_hashes = set()
    filtered = []
    stats = defaultdict(int)
    
    with open('wikipedia_bio_raw.txt', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            stats['total'] += 1
            
            # Dedup
            h = hashlib.md5(line.encode()).hexdigest()
            if h in seen_hashes:
                stats['duplicate'] += 1
                continue
            seen_hashes.add(h)
            
            # Length check (8-40 words)
            words = line.split()
            if len(words) < 8 or len(words) > 40:
                stats['bad_length'] += 1
                continue
            
            # Purity check (85%+ Kurdish)
            kurdish = sum(1 for c in line if '\u0600' <= c <= '\u06FF')
            latin = sum(1 for c in line if c.isalpha() and c.isascii())
            if latin + kurdish > 0 and (kurdish / (latin + kurdish)) < 0.85:
                stats['bad_purity'] += 1
                continue
            
            # Accept all (no ZWNJ filtering - Wikipedia has very low ZWNJ)
            stats['accepted'] += 1
            zwnj_density = (line.count('\u200c') / len(line)) * 100 if len(line) > 0 else 0
            filtered.append((line, len(words), zwnj_density))
    
    # Save
    output_path = Path('../../corpus/ckb_wikipedia_bio_filtered.training_text')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for sent, wc, zwnj in filtered:
            f.write(sent + '\n')
    
    print(f'Wikipedia Biography Filtering:')
    print(f'  Total: {stats["total"]:,}')
    print(f'  Duplicates: {stats["duplicate"]:,}')
    print(f'  Bad length: {stats["bad_length"]:,}')
    print(f'  Bad purity: {stats["bad_purity"]:,}')
    print(f'  ACCEPTED: {stats["accepted"]:,}')
    print(f'  Acceptance Rate: {(stats["accepted"]/stats["total"]*100):.1f}%')
    
    if filtered:
        avg_words = sum(x[1] for x in filtered) / len(filtered)
        avg_zwnj = sum(x[2] for x in filtered) / len(filtered)
        print(f'')
        print(f'Quality Metrics:')
        print(f'  Avg Words/Sentence: {avg_words:.2f}')
        print(f'  Avg ZWNJ Density: {avg_zwnj:.2f}%')
        print(f'')
        print(f'Output: {output_path}')

if __name__ == '__main__':
    filter_wiki_corpus()
