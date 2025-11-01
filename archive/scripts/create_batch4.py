#!/usr/bin/env python3
"""Create Phase 6 Batch 4 corpus - hybrid approach"""

print("Creating Phase 6 Batch 4...")
print("=" * 60)

# Read Batch 3
with open('ckb_phase6_batch3.training_text', 'r', encoding='utf-8') as f:
    batch3_lines = [l.strip() for l in f if l.strip()]

# Read Wikipedia bio (300 sentences)
with open('ckb_wikipedia_bio_filtered.training_text', 'r', encoding='utf-8') as f:
    wiki_lines = [l.strip() for l in f if l.strip()][:300]

# Read high-ZWNJ news (200 sentences from end - highest ZWNJ)
with open('ckb_scraped_filtered.training_text', 'r', encoding='utf-8') as f:
    news_lines = [l.strip() for l in f if l.strip()][-200:]

# Combine
batch4_lines = batch3_lines + wiki_lines + news_lines

# Save
with open('ckb_phase6_batch4.training_text', 'w', encoding='utf-8') as f:
    for line in batch4_lines:
        f.write(line + '\n')

# Statistics
total_chars = sum(len(l) for l in batch4_lines)
zwnj_count = sum(l.count('\u200c') for l in batch4_lines)
total_words = sum(len(l.split()) for l in batch4_lines)

print(f"\nBatch 4 Composition:")
print(f"  Batch 3 (baseline): {len(batch3_lines):,} sentences")
print(f"  Wikipedia biography: {len(wiki_lines):,} sentences (0.08% ZWNJ)")
print(f"  High-ZWNJ news: {len(news_lines):,} sentences (9.15% ZWNJ)")
print(f"  Total: {len(batch4_lines):,} sentences")

print(f"\nBatch 4 Quality:")
print(f"  Avg Words/Sentence: {total_words/len(batch4_lines):.2f}")
print(f"  ZWNJ Density: {(zwnj_count/total_chars)*100:.2f}%")
print(f"  Delta from Batch 3: +{len(batch4_lines) - len(batch3_lines)} sentences")

print(f"\nOutput: ckb_phase6_batch4.training_text")
print("=" * 60)
