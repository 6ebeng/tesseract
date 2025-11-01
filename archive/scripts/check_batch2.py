lines = [l.strip() for l in open("ckb_phase6_batch2.training_text", "r", encoding="utf-8") if l.strip()]
total_chars = sum(len(l) for l in lines)
zwnj = sum(l.count("\u200c") for l in lines)
words = sum(len(l.split()) for l in lines)
print(f"Phase 6 Batch 2:")
print(f"  Sentences: {len(lines):,}")
print(f"  Avg Words/Sentence: {words/len(lines):.2f}")
print(f"  ZWNJ Density: {(zwnj/total_chars)*100:.2f}%")
