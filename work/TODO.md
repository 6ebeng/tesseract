# Kurdish OCR Training - TODO List

## Training Pipeline Setup ✅

### Completed:

- [x] Created `prepare_training_data.sh` - Script to generate training data from fonts and corpus
- [x] Created `full_training_pipeline.sh` - Complete training pipeline script
- [x] Created `run_training.ps1` - PowerShell launcher for Windows

### Training Steps:

#### Phase 1: Data Preparation

- [ ] Generate training text files from corpus
- [ ] Create training images using all 200+ fonts
- [ ] Generate box files for character positions
- [ ] Extract unicharset
- [ ] Generate LSTMF files for training
- [ ] Create training file list

#### Phase 2: Model Training

- [ ] Run initial training (2000 iterations default)
- [ ] Monitor error rate reduction
- [ ] Create checkpoint files

#### Phase 3: Model Finalization

- [ ] Stop training at checkpoint
- [ ] Create final traineddata file
- [ ] Name: `ckb_custom.traineddata`

#### Phase 4: Installation

- [ ] Install to WSL: `/usr/share/tesseract-ocr/5/tessdata/`
- [ ] Install to Windows: `C:\tesseract\tessdata\`

#### Phase 5: Testing

- [ ] Generate test images
- [ ] Run OCR with new model
- [ ] Verify accuracy

## Resources:

### Corpus:

- Location: `work/corpus/ckb.training_text`
- Content: Kurdish text with various characters and combinations

### Fonts:

- Location: `work/fonts/`
- Count: 200+ Kurdish fonts (Sarchia and others)

### Scripts:

1. **Full Pipeline**: `work/scripts/full_training_pipeline.sh`
2. **Data Prep**: `work/scripts/prepare_training_data.sh`
3. **Master Training**: `work/scripts/master_training.sh`
4. **Windows Launcher**: `work/run_training.ps1`

## How to Run:

### From Windows PowerShell:

```powershell
cd C:\tesseract\work
.\run_training.ps1
```

### From WSL directly:

```bash
cd /mnt/c/tesseract/work/scripts
bash full_training_pipeline.sh
```

## Expected Output:

- Custom trained model: `ckb_custom.traineddata`
- Training data in: `work/ground-truth-custom/`
- LSTMF files list: `work/output/all-lstmf.txt`
- Checkpoints in: `work/output/`

## Notes:

- Training time depends on number of iterations and fonts
- Default: 2000 iterations, 0.01 target error rate
- Can be customized when running the pipeline
