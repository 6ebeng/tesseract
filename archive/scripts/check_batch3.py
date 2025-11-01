lines = [l.strip() for l in open("ckb_phase6_batch3.training_text", "r", encoding="utf-8") if l.strip()]
total_chars = sum(len(l) for l in lines)
zwnj = sum(l.count("\u200c") for l in lines)
words = sum(len(l.split()) for l in lines)
print(f"Phase 6 Batch 3:")
print(f"  Sentences: {len(lines):,}")
print(f"  Avg Words/Sentence: {words/len(lines):.2f}")
print(f"  ZWNJ Density: {(zwnj/total_chars)*100:.2f}%")
print(f"  Delta from Batch 2: +{len(lines)-4686} sentences")
