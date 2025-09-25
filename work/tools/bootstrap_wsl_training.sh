#!/bin/bash
set -euo pipefail

# Bootstrap Tesseract training environment in WSL Ubuntu
# Installs core dependencies and verifies toolchain availability.

if ! command -v apt-get >/dev/null 2>&1; then
  echo "This script targets Ubuntu (apt-get required)." >&2
  exit 1
fi

sudo apt-get update
sudo apt-get install -y \
  tesseract-ocr \
  tesseract-ocr-dev \
  libtesseract-dev \
  libleptonica-dev \
  build-essential \
  automake autoconf libtool \
  libpng-dev libjpeg-dev libtiff-dev zlib1g-dev \
  python3 python3-pip \
  fonts-dejavu-core fontconfig \
  imagemagick

# Optional: lstmeval ships with training tools in recent versions
# Verify tools
missing=()
for tool in tesseract text2image lstmtraining combine_tessdata lstmeval unicharset_extractor combine_lang_model set_unicharset_properties fc-scan; do
  command -v "$tool" >/dev/null 2>&1 || missing+=("$tool")
done

if [ ${#missing[@]} -gt 0 ]; then
  echo "WARNING: Missing tools: ${missing[*]}" >&2
else
  echo "All required training tools found."
fi

echo "Done."
