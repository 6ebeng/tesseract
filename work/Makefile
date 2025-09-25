# Simple orchestrator for Kurdish OCR training in WSL
# Targets:
#   make bootstrap   - install deps in WSL
#   make buildcorpus - build balanced corpus -> corpus/ckb.training_text.final
#   make generate    - render synthetic ground truth
#   make train       - fine-tune and export traineddata (also installs to tessdata/best & tessdata/fast)
#   make eval        - evaluate real-world CER on work/real_gt/eval
#   make all         - buildcorpus -> generate -> train -> eval

.PHONY: bootstrap buildcorpus generate train eval all

bootstrap:
	wsl -d Ubuntu -- bash -lc "cd '/mnt/c/tesseract/work'; chmod +x tools/bootstrap_wsl_training.sh || true; tools/bootstrap_wsl_training.sh"

buildcorpus:
	wsl -d Ubuntu -- bash -lc "cd '/mnt/c/tesseract/work'; python3 tools/corpus_build.py --fixer"

# You can override params, e.g.:
# make generate DPI=400 FONT_SIZE=20 ENABLE_AUG=1

generate:
	wsl -d Ubuntu -- bash -lc "cd '/mnt/c/tesseract/work'; \
	  export DPI='${DPI}'; export FONT_SIZE='${FONT_SIZE}'; export ENABLE_AUG='${ENABLE_AUG}'; \
	  sed -i 's/\r$$//' generate_ckb_training_data.sh 2>/dev/null || true; \
	  chmod +x generate_ckb_training_data.sh; \
	  ./generate_ckb_training_data.sh"

train:
	wsl -d Ubuntu -- bash -lc "cd '/mnt/c/tesseract/work'; \
	  sed -i 's/\r$$//' execute_ckb_training.sh 2>/dev/null || true; \
	  chmod +x execute_ckb_training.sh; \
	  ./execute_ckb_training.sh"

eval:
	wsl -d Ubuntu -- bash -lc "cd '/mnt/c/tesseract/work'; python3 tools/eval_real_cer.py"

all: buildcorpus generate train eval
