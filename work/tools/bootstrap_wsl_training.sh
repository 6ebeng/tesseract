#!/bin/bash
set -euo pipefail

# Bootstrap Tesseract training environment in WSL Ubuntu
# Installs core dependencies and verifies toolchain availability.

if ! command -v apt-get >/dev/null 2>&1; then
  echo "This script targets Ubuntu (apt-get required)." >&2
  exit 1
fi

sudo apt-get update
# Install core OCR and build deps; on Ubuntu 24.04 (noble), tesseract-ocr-dev is replaced by libtesseract-dev
sudo apt-get install -y \
  tesseract-ocr \
  libtesseract-dev \
  libleptonica-dev \
  build-essential \
  automake autoconf libtool \
  libpng-dev libjpeg-dev libtiff-dev zlib1g-dev \
  python3 python3-pip \
  fonts-dejavu-core fontconfig \
  imagemagick || true

# Fallback attempts for any missing packages
if ! command -v tesseract >/dev/null 2>&1; then
  sudo apt-get install -y tesseract-ocr || true
fi
if ! dpkg -s libtesseract-dev >/dev/null 2>&1; then
  sudo apt-get install -y libtesseract-dev || true
fi

# Optional: lstmeval ships with training tools in recent versions
# Verify tools
missing=()
for tool in tesseract text2image lstmtraining combine_tessdata lstmeval unicharset_extractor combine_lang_model set_unicharset_properties fc-scan; do
  command -v "$tool" >/dev/null 2>&1 || missing+=("$tool")
done

if [ ${#missing[@]} -gt 0 ]; then
  echo "WARNING: Missing tools: ${missing[*]}" >&2
  # Try to install extras via apt if available
  sudo apt-get install -y tesseract-ocr-all || true
  # Recheck
  re_missing=()
  for tool in "${missing[@]}"; do command -v "$tool" >/dev/null 2>&1 || re_missing+=("$tool"); done
  if [ ${#re_missing[@]} -gt 0 ]; then
    echo "Still missing: ${re_missing[*]}" >&2
  fi
else
  echo "All required training tools found."
fi

echo "Done."
