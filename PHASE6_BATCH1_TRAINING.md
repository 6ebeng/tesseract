# Phase 6 Batch 1 - Training Session

**Date**: October 15, 2025  
**Status**: 🟡 TRAINING IN PROGRESS

---

## 📊 Batch 1 Statistics

### Corpus Details

- **Total lines**: 3,637
- **Phase 4 base**: 3,278 lines
- **New sentences**: 480 lines (from Wikipedia quality extraction)
- **Duplicates removed**: 121 lines
- **ZWNJ density**: 8.25% (↑ from Phase 4's 8.15%)
- **Quality grade**: **B (85/100)** (↑ from Phase 4's 80/100)
- **Kurdish purity**: 97.6%
- **Avg words/line**: 17.5

### New Sentence Quality (480 lines)

- **Source**: Wikipedia corpus (Phase 5) - quality extracted
- **Individual grade**: **A (90/100)**
- **ZWNJ density**: 9.17%
- **Avg words**: 18.8
- **Selection method**: Quality scoring (ZWNJ + length + purity)

---

## 🎯 Expected Outcomes

### Baseline (Phase 4 Farsi checkpoint)

- **Accuracy**: 72.19%
- **CER**: 0.2781
- **Corpus**: 3,278 lines (B grade, 80/100)

### Target for Batch 1

- **Minimum improvement**: +0.3% → 72.5%
- **Realistic target**: 72.5-73.5%
- **Optimistic target**: 73.5-74.0%

### Decision Criteria

- ✅ **Keep if**: Accuracy ≥ 72.5% (+0.3% or better)
- ⚠️ **Review if**: Accuracy = 72.0-72.4% (marginal improvement)
- ❌ **Discard if**: Accuracy < 72.0% (no improvement or regression)

---

## ⏱️ Training Progress

### Started

- **Time**: October 15, 2025 (current session)
- **Command**: `.\run_training.ps1 -Mode GenerateTrain`
- **Terminal ID**: 70b7ca07-da8c-4a74-bf69-745f87ee30c8

### Current Stage

🔄 **Generating training images** (Font rendering with text2image)

- Fonts: 9 fonts detected
- Exposures: -1, 0, 1 (brightness variations)
- DPI: 300, Size: 18pt

### Remaining Stages

1. ⏳ Generate LSTMF files from images
2. ⏳ Train from Farsi base model
3. ⏳ Train from Arabic base model
4. ⏳ Train from English base model
5. ⏳ Select best checkpoint

### Expected Duration

- **Image generation**: 30-60 minutes
- **LSTMF creation**: 10-20 minutes
- **Training (3 bases)**: 2-4 hours
- **Total**: **3-5 hours**

---

## 📋 Next Steps After Training

### 1. Evaluate Accuracy

```bash
cd c:\tesseract\work
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work && python3 tools/eval_real_cer.py"
```

**Expected output**:

- Accuracy % for each base model (fas/ara/eng)
- CER (Character Error Rate)
- Comparison vs baseline (72.19%)

### 2. Record Results

```bash
# Example: If Farsi model achieved 72.8% (CER 0.272)
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work && python3 tools/incremental_training.py record 1 3637 72.8 0.272"
```

This will:

- Save to `work/output/phase6_results.json`
- Update `PHASE6_PROGRESS.md`
- Calculate improvement

### 3. Make Decision

- **If successful** (≥72.5%): Continue to Batch 2 (collect 500 more sentences)
- **If marginal** (72.0-72.4%): Review quality, possibly keep
- **If failed** (<72.0%): Try different source or quality threshold

---

## 📈 Phase 6 Strategy Context

### Why Batch 1 Should Improve

1. ✅ **Higher quality new sentences** (A grade vs Phase 4's B grade)
2. ✅ **Increased ZWNJ density** (8.25% from 8.15%)
3. ✅ **Better sentence selection** (quality scoring vs random Wikipedia)
4. ✅ **Diverse sources** (Wikipedia spans many topics)
5. ✅ **Proper length distribution** (89.8% in 10-25 word range)

### Why Batch 1 Might Not Improve Much

1. ⚠️ **Still from Wikipedia** (not professional news)
2. ⚠️ **Only +359 net new lines** (+11% corpus size)
3. ⚠️ **Similar to Phase 5 source** (but better filtering)
4. ⚠️ **Diminishing returns** (already at 72.19%)

### Backup Plan If Batch 1 Fails

- Try **manual news collection** from Rudaw/BasNews
- Use **official government documents** (higher ZWNJ)
- Extract from **published Kurdish literature**
- Consider **sentence augmentation** (RTL variation, punctuation)

---

## 🔍 Monitoring Commands

### Check Training Progress

```powershell
# Check if still running
Get-Process | Where-Object {$_.ProcessName -like "*tesseract*"}

# View training logs
Get-Content c:\tesseract\work\training_output\logs\training_*.log -Tail 50
```

### Monitor System Resources

```powershell
# Check CPU/Memory usage
Get-Process | Where-Object {$_.ProcessName -like "*wsl*"} | Select-Object ProcessName,CPU,WorkingSet
```

---

## 📝 Training Configuration

### Corpus

- **File**: `work/corpus/ckb.training_text`
- **Backup**: `work/corpus/ckb_phase6_batch1.training_text`

### Base Models

- Farsi: `tessdata/best/fas.traineddata`
- Arabic: `tessdata/best/ara.traineddata`
- English: `tessdata/best/eng.traineddata`

### Training Parameters

- **Mode**: LSTM fine-tuning
- **Target error**: 0.02 (2% BCER)
- **Max iterations**: 10,000
- **Debug interval**: 100
- **Net spec**: Layer1,Lfx256,Lrx256,Lfx256,O1(1D1),Ct5,5,64,C3,3,F64,Bn,D50

---

## 🎯 Success Metrics

### Immediate (Batch 1)

- ✅ Accuracy ≥ 72.5% (+0.3%)
- ✅ ZWNJ in output remains stable
- ✅ No character recognition regression

### Phase 6 Overall

- 🎯 Batch 1-3: Reach 73-75% (Wikipedia quality + news)
- 🎯 Batch 4-6: Reach 75-78% (news + official docs)
- 🎯 Batch 7-9: Reach 78-80% (official + literature)
- 🎯 Final: 80%+ accuracy for ZWNJ rules retry

---

**Status**: 🔄 Training started, waiting for completion...  
**ETA**: 3-5 hours from start  
**Next update**: After training completes
