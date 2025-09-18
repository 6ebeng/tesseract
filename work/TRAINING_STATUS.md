# Kurdish OCR Training - Current Status

## ✅ TRAINING IN PROGRESS

### Current Activity:

- **Script Running**: `train_with_existing_data.sh`
- **Training Data**: 27 LSTMF files (from previous Arabic Typesetting font generation)
- **Status**: Successfully restored from checkpoint and continuing training
- **Target**: 2000 iterations with 0.01 target error rate

### Progress Summary:

#### ✅ Completed Steps:

1. **Scripts Created**:

   - `prepare_training_data.sh` - Original data preparation script
   - `prepare_training_data_v2.sh` - Improved version with font handling
   - `full_training_pipeline.sh` - Complete pipeline script
   - `simple_training.sh` - Simplified training script
   - `train_with_existing_data.sh` - Training with existing LSTMF files
   - `run_training.ps1` - Windows PowerShell launcher

2. **Training Data Found**:

   - Located 27 existing LSTMF files from previous training sessions
   - Files use Arabic Typesetting font with Kurdish corpus text
   - Successfully loaded for training

3. **Training Started**:
   - Restored from existing checkpoint
   - Training for 2000 iterations
   - Using English base model for transfer learning

#### 🔄 In Progress:

- Model training (2000 iterations)
- Error rate reduction from current checkpoint

#### ⏳ Upcoming:

1. Model finalization (creating ckb_custom.traineddata)
2. Installation to WSL and Windows directories
3. Testing with Kurdish text samples

### Files and Locations:

#### Training Data:

- LSTMF files: `/mnt/c/tesseract/work/training/*.lstmf`
- List file: `/mnt/c/tesseract/work/output/all-lstmf.txt`
- Checkpoint: `/mnt/c/tesseract/work/output/ckb_checkpoint`

#### Output Model (when complete):

- **Model Name**: `ckb_custom.traineddata`
- **WSL Location**: `/usr/share/tesseract-ocr/5/tessdata/ckb_custom.traineddata`
- **Windows Location**: `C:\tesseract\tessdata\ckb_custom.traineddata`

### How to Use (After Training):

```bash
# In WSL/Linux
tesseract image.tif output -l ckb_custom --psm 6

# In Windows
tesseract.exe image.tif output -l ckb_custom --psm 6
```

### Training Parameters:

- **Max Iterations**: 2000
- **Target Error Rate**: 0.01 (1%)
- **Base Model**: eng.traineddata
- **Training Samples**: 27 LSTMF files
- **Debug Interval**: Disabled for faster training

### Expected Duration:

- Training: ~20-40 minutes for 2000 iterations
- Finalization: ~1-2 minutes
- Total: ~30-45 minutes

### Notes:

- The training is using existing LSTMF files generated with Arabic Typesetting font
- These files contain Kurdish text from your corpus
- The model will be optimized for recognizing Kurdish text in various styles
- Once complete, the model will be automatically installed and tested

---

_Last Updated: Training actively running_
