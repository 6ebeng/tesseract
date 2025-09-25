Real ground-truth for Kurdish Sorani (ckb)
=========================================

Structure:

- images/        # Optional: store your source images here
- eval/          # Small held-out set for evaluation with pairs: <name>.(tif|png|jpg) + <name>.gt.txt

Guidelines:
- One image per .gt.txt file; .gt.txt must contain exactly the text in the image.
- Prefer 300+ DPI scans or clear photos; include variety (fonts, sizes, noise, skew).
- Keep 20–50 lines in eval/ initially to measure CER quickly.

Evaluate:
- After training, run in WSL:
  cd /mnt/c/tesseract/work
  python3 tools/eval_real_cer.py

The script writes CSV to work/output/real_metrics.csv and prints an average CER.
