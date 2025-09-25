# Kurdish Sorani (ckb) OCR – Improvement Plan

This document tracks concrete improvements to achieve a high‑quality `ckb` model.

## Priorities (P0–P2)

P0 – Data & Pipeline correctness

- Ensure WSL has training tools: tesseract-ocr, tesseract-ocr-dev, training tools (lstmtraining, text2image, combine_tessdata, lstmeval). Add a bootstrap script to install these.
- Verify `work/corpus/ckb.training_text` quality: balanced coverage of letters (ەێۆڤڕڵگچژ…), punctuation (، ؛ ؟ « » ٪), digits (٠١٢٣٤٥٦٧٨٩), diacritics if needed. Deduplicate and normalize to NFC.
- Expand fonts set: include Serif/Sans/Mono styles; add Naskh/Nastaliq/modern Kurdish fonts to improve generalization. At least 12–20 distinct families.
- Ground‑truth variety: generate multiple exposures, point sizes (14–28pt), DPI (300/400), margins, char spacing. Introduce page shaping variety (long/short lines, RTL punctuation cases).
- LSTM fine‑tune from the best Arabic/Persian bases (ara, fas) only when they are LSTM (not fast). Skip fast models automatically (already handled).
- Use eval split and lstmeval to monitor CER per checkpoint (partially implemented). Persist metrics to a CSV/JSON.

P1 – Coverage & accuracy

- Add language‑specific punctuation and symbols to minimal traineddata builder (puncs.txt) and numbers.txt (Arabic‑Indic and optionally Latin digits 0–9 if target).
- Expand verify script to check: punctuation coverage, digits, bidi marks, common ligatures’ base chars present.
- Add distortion/augmentation in synthetic rendering: slight noise/blur/contrast, baseline shift, character spacing variations.
- Add real‑world ground truth (scanned PDFs/photos) with hand‑corrected boxes/text to reduce synthetic bias.

P2 – Automation & reproducibility

- Create `work/bootstrap.sh` to install deps in WSL and verify versions.
- Add `work/Makefile` or a single `train.ckb` task orchestrating: generate -> train -> eval -> package.
- Cache downloaded langdata assets and base models deterministically (already partially cached to work/charsets and tessdata/best). Pin URLs/commits for reproducibility.

## Gaps / What’s Missing

- Real data: Only synthetic GT is present. Add a `work/real_gt/` with curated images + .gt.txt for at least 200–500 lines. Use `work/tools/eval_real_cer.py` on `work/real_gt/eval` to track real CER.
- Corpus breadth: The corpus appears single‑file. Add domain corpora (news, literature, social, government) and mix them; ensure balanced rare characters (ڕ ڵ ڤ ێ ۆ ژ چ گ پ).
- Fonts diversity: Current fonts are from one provider series. Add system‑popular fonts used in Kurdish publications.
- Augmentations: text2image supports exposures; add blur/noise via ImageMagick (convert -blur, -attenuate noise, -contrast-stretch) between render and box.
- Evaluation: Save CER per checkpoint (already `metrics.csv`) and also evaluate on the real eval split to pick best by real CER.
- Packaging: Provide `tessdata/best/ckb.traineddata` alongside `tessdata/ckb.traineddata` (and `tessdata/fast/ckb.traineddata`) so consumers can default to the best model.

## Concrete next steps

1. Bootstrap script (WSL): install deps, verify tools, set TESSDATA_PREFIX; pin training tools versions.
2. Corpus upgrade: add `work/corpus/ckb.training_text.extra` and a script to compile a balanced `ckb.training_text.final` with stats (char freq histogram).
3. Fonts upgrade: add at least 10 more high‑quality Kurdish/Arabic fonts, plus italics/bold variants where available.
4. Rendering matrix: vary ptsize=[16,18,22,26], dpi=[300,400], exposures=[-1,0,1], char_spacing=[0,0.5,1], leading=[18,22,26].
5. Augment pipeline: optional `ENABLE_AUG=1` to run ImageMagick transforms per generated image.
6. Metrics: write `work/training_output/model/metrics.json` and `metrics.csv` recording checkpoint, CER, params.
7. Verification+: enhance `verify_ckb_traineddata.py` to validate punctuation and digits; add `--require-latin-digits` option.
8. Add smoke/regression test: run OCR over small eval set and assert CER < target threshold.

## Targets

- Synthetic‑only baseline: CER ≤ 8–12% on held‑out synthetic; ≤ 20–25% on small real set.
- With real data + augments: CER ≤ 10–15% on real set depending on domain.

## Troubleshooting hints

- If .lstmf not generated: ensure base models are LSTM (not fast). The script skips fast; consider fetching from tessdata/best.
- If fonts not found: confirm fontconfig uses repo `fonts.conf`; run `fc-cache -f ./work/fonts`.
- If missing Kurdish letters: run verifier and extend `puncs.txt`/`numbers.txt` and rebuild minimal traineddata.

---

Maintain this file as you iterate. Save experiment configs and outcomes with timestamps under `work/training_output/model/`.
