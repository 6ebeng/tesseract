#!/bin/bash

# Auto-run training with default parameters
cd /mnt/c/tesseract/work/scripts

# Run full pipeline with default parameters
echo -e "2000\n0.01\ny" | bash full_training_pipeline.sh
