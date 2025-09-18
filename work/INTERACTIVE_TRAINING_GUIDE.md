# 🎯 Interactive Kurdish OCR Training Guide

## Overview

The interactive training script provides a user-friendly menu system to choose between different training strategies based on your needs.

## 🚀 Quick Start

```bash
# Run the interactive trainer
wsl sh work/scripts/interactive_train.sh
```

## 📋 Training Modes

### 1. ⚡ **QUICK MODE** (5-10 minutes)

**Best for**: Testing, development, quick iterations

- **Fonts**: 10-20 fonts
- **Augmentation**: Basic
- **Accuracy**: ~80%
- **Use case**: Quick testing of corpus changes

### 2. 🚀 **FAST MODE** (30-60 minutes)

**Best for**: Good balance of speed and quality

- **Fonts**: 50-100 diverse fonts
- **Augmentation**: Moderate (shear, rotation)
- **Accuracy**: ~85-90%
- **Use case**: Development builds, CI/CD pipelines

### 3. ⭐ **STANDARD MODE** (1-2 hours)

**Best for**: Production deployments

- **Fonts**: 200-300 fonts
- **Augmentation**: Good (shear, rotation, exposure)
- **Accuracy**: ~90-93%
- **Use case**: Production systems with normal quality requirements

### 4. 🔥 **ROBUST MODE** (2-4 hours)

**Best for**: Maximum accuracy, handling poor quality images

- **Fonts**: ALL 670 Kurdish fonts
- **Augmentation**: Heavy (shear, rotation, noise, blur)
- **Accuracy**: ~95%+
- **Use case**: Critical applications, poor scan quality, varied fonts

### 5. 🎯 **CUSTOM MODE**

**Best for**: Specific requirements

- Choose your own:
  - Font count (1-670)
  - Iterations (1000-20000)
  - Target error rate (0.001-0.1)
  - Augmentation level (none/basic/moderate/heavy)
  - Model name

### 6. 📊 **COMPARE MODELS**

**Features**:

- Test single model performance
- Compare two models side-by-side
- Benchmark all available models
- Processing time measurements
- Accuracy comparisons

### 7. ℹ️ **VIEW STATUS**

**Shows**:

- Running training processes
- Disk usage
- Existing models and sizes
- Corpus information
- Available fonts count

## 🎨 Augmentation Levels Explained

### **None**

- Clean images only
- No distortions
- Fastest training
- Best for: High-quality scans only

### **Basic**

- Exposure variations (-2 to +2)
- Character spacing (0.0 to 0.2)
- Best for: Good quality documents

### **Moderate**

- Everything from Basic, plus:
- Shear transformation (-5° to +5°)
- Rotation (-2° to +2°)
- Best for: Normal document variations

### **Heavy**

- Everything from Moderate, plus:
- Gaussian noise
- Blur effects
- More aggressive shear (-7° to +7°)
- More rotation (-3° to +3°)
- Best for: Poor quality scans, phone photos

## 📊 Mode Comparison Table

| Mode     | Fonts   | Time      | Accuracy | Augmentation | Use Case    |
| -------- | ------- | --------- | -------- | ------------ | ----------- |
| Quick    | 10-20   | 5-10 min  | ~80%     | Basic        | Testing     |
| Fast     | 50-100  | 30-60 min | 85-90%   | Moderate     | Development |
| Standard | 200-300 | 1-2 hrs   | 90-93%   | Good         | Production  |
| Robust   | ALL 670 | 2-4 hrs   | 95%+     | Heavy        | Critical    |

## 💡 Choosing the Right Mode

### Choose **QUICK MODE** if:

- You're testing corpus changes
- You need rapid iteration
- Accuracy isn't critical
- You're debugging the pipeline

### Choose **FAST MODE** if:

- You need reasonable accuracy quickly
- You're building for development/staging
- You have standard document quality
- Time is a constraint

### Choose **STANDARD MODE** if:

- You're deploying to production
- You need reliable accuracy
- You have diverse font requirements
- You can wait 1-2 hours

### Choose **ROBUST MODE** if:

- Accuracy is critical
- You handle poor quality images
- You need to support ALL Kurdish fonts
- You process varied document types
- Time is not a constraint

### Choose **CUSTOM MODE** if:

- You have specific requirements
- You want to experiment with parameters
- You need a specific model name
- You want fine control

## 🔧 Advanced Features

### Model Comparison

The compare feature allows you to:

1. **Test Single Model**: Run OCR on test image
2. **Compare Two Models**: Side-by-side comparison
3. **Benchmark All**: Test all models systematically

### Custom Parameters

In Custom Mode, you can set:

- **Font Count**: 1-670 (more = better coverage)
- **Iterations**: 1000-20000 (more = better accuracy)
- **Error Rate**: 0.001-0.1 (lower = more accurate)
- **Augmentation**: none/basic/moderate/heavy
- **Model Name**: Custom identifier

## 📁 Output Files

Each training mode creates:

```
work/output/
├── ckb_[mode].traineddata     # Final model
├── ckb_[mode]*.checkpoint      # Training checkpoints
├── [mode]-lstmf.txt           # Training file list
└── custom_train_[name].sh     # Custom mode scripts

tessdata/
├── ckb.traineddata            # Default model
├── ckb_quick.traineddata      # Quick mode output
├── ckb_fast_robust.traineddata # Fast mode output
├── ckb_robust.traineddata     # Robust mode output
└── ckb_[custom].traineddata   # Custom mode outputs
```

## 🚦 Status Indicators

The script uses color coding:

- 🟢 **Green**: Success, completed
- 🔵 **Blue**: Information, processing
- 🟡 **Yellow**: Warning, attention needed
- 🔴 **Red**: Error, action required
- 🟣 **Magenta**: Section headers
- 🔷 **Cyan**: Interactive prompts

## 📈 Expected Results

| Mode     | Clean Text | Skewed | Noisy | Blurred | Phone Photo |
| -------- | ---------- | ------ | ----- | ------- | ----------- |
| Quick    | 80%        | 60%    | 50%   | 55%     | 45%         |
| Fast     | 90%        | 75%    | 70%   | 70%     | 65%         |
| Standard | 93%        | 85%    | 80%   | 80%     | 75%         |
| Robust   | 95%+       | 90%    | 85%   | 85%     | 80%         |

## 🛠️ Troubleshooting

### If training fails:

1. Check disk space (need 5-10 GB free)
2. Verify corpus file exists
3. Ensure fonts are in `work/fonts/`
4. Check WSL memory allocation

### If accuracy is low:

1. Use more fonts (increase count)
2. Add more iterations
3. Lower target error rate
4. Increase augmentation level

### If training is too slow:

1. Reduce font count
2. Decrease iterations
3. Increase target error rate
4. Use less augmentation

## 💻 System Requirements

- **Minimum**: 4GB RAM, 5GB disk space
- **Recommended**: 8GB RAM, 10GB disk space
- **Optimal**: 16GB RAM, 20GB disk space
- **WSL**: Version 2 recommended

## 🎯 Best Practices

1. **Start with Fast Mode** to validate your setup
2. **Use Custom Mode** to fine-tune parameters
3. **Run Robust Mode** overnight for best results
4. **Compare models** before deployment
5. **Keep backups** of good models
6. **Document** which mode/parameters you used

## 📝 Example Workflow

```bash
# 1. Start interactive trainer
wsl sh work/scripts/interactive_train.sh

# 2. Choose mode based on needs:
#    - Press 2 for Fast Mode (development)
#    - Press 3 for Standard Mode (production)
#    - Press 4 for Robust Mode (maximum accuracy)

# 3. Monitor progress
#    - Press 7 to view status

# 4. Compare results
#    - Press 6 to compare models

# 5. Deploy best model
cp tessdata/ckb_robust.traineddata /production/tessdata/
```

## 🔄 Continuous Improvement

1. **Collect problem images** that fail OCR
2. **Add to corpus** for better coverage
3. **Retrain with Robust Mode** periodically
4. **Compare new vs old** models
5. **Deploy improvements** incrementally

---

**Pro Tip**: For production systems, train multiple models (Fast, Standard, Robust) and compare them on your actual data to find the best balance of speed and accuracy for your use case.
