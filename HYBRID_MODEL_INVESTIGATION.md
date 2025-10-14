# Hybrid Arabic-Farsi Base Model Investigation

**Date**: October 13, 2024, 4:30 PM  
**Objective**: Investigate if combining Arabic and Farsi base models improves Kurdish OCR accuracy

---

## Background

### Problem with Single-Base Approach

**Phase 5 Training Results:**

- **Farsi base**: Training ran but produced identical model to Phase 3 (MD5: 9e7d9ee5e60ca0cc28f2c1e86f08e4e4)

  - Checkpoint: 25MB (created Oct 13, 13:55)
  - Finalized model: 3.1MB (identical to Phase 3)
  - BCER: 2.242 (from evaluation log)
  - **Accuracy**: 71.69% (no improvement)

- **Arabic base**: Training succeeded, new model created

  - BCER: 1.502 (better convergence than Farsi)
  - Model size: 11.7MB
  - **Accuracy**: 65.39% (-6.3% vs Phase 4)

- **English base**: Training succeeded
  - Model size: 11.7MB
  - **Accuracy**: 65.54% (-6.2% vs Phase 4)

**Key Insight**: Farsi training appears broken (produces Phase 3 model despite new checkpoint), while Arabic trains but performs worse.

---

## Linguistic Rationale for Hybrid Approach

### Kurdish Language Position

Kurdish sits **linguistically between** Farsi and Arabic:

**Similarities to Farsi:**

- Both are **Indo-European languages** (Iranian branch)
- Similar grammar structures
- Shared vocabulary (40-50% cognates)
- Similar word order (SOV)

**Similarities to Arabic:**

- Uses **Arabic script** (Perso-Arabic alphabet)
- Shares Arabic loanwords (religion, administration)
- Similar cursive writing style
- RTL (right-to-left) text direction

**Kurdish-Specific:**

- Uses additional letters: ێ, ۆ, ڕ, ڵ, ڤ, و (with 3 sounds)
- Unique ZWNJ usage patterns
- Mix of Arabic and Latin script (Hawar dialect)

### Hypothesis

A **hybrid model** combining Arabic (script/visual features) + Farsi (linguistic/grammatical features) might:

1. Leverage Arabic's script recognition
2. Use Farsi's linguistic patterns
3. Provide more robust character recognition

---

## Tesseract Training Architecture

### Current Training Flow (from `execute_ckb_training.sh`)

```bash
for START_BASE in "${BASE_LANGS[@]}"; do  # BASE_LANGS=(fas ara eng)
  # Extract LSTM from base model
  combine_tessdata -e "$MODEL_PATH" "$TMP_DIR/$START_BASE.lstm"

  # Train from single base
  lstmtraining \
    --continue_from "$TMP_DIR/$START_BASE.lstm" \
    --old_traineddata "$MODEL_PATH" \
    --traineddata "$TARGET_TRAINEDDATA" \
    --model_output "$MODEL_PREFIX" \
    ...

  # Finalize best/fast variants
  lstmtraining --stop_training --continue_from "$CHECKPOINT" ...
done

# Pick better model (fas vs ara based on CER)
pick_and_install()  # Chooses lowest CER model
```

**Key Points:**

1. **Sequential training**: Trains from each base separately
2. **No built-in hybrid**: lstmtraining doesn't support multiple `--continue_from`
3. **Selection, not combination**: Picks best single model, doesn't merge

### Hybrid Segmentation (Already Used)

The script **does** use hybrid segmentation for LSTMF generation:

```bash
SEG_LANGS=(fas ara eng ckb)  # Try all bases for segmentation
for B in "${SEG_LANGS[@]}"; do
  tesseract "$tif" "$base-$B" -l "$B" --oem 1 --psm 6 lstm.train
  if [ -f "$base-$B.lstmf" ]; then break; fi  # Use first success
done
```

**Result**: Each training image uses **whichever base** successfully segments it (Arabic, Farsi, English, or existing CKB).

This means training data **already has mixed segmentation**, but final training still uses a single base model.

---

## Possible Hybrid Approaches

### Approach 1: Model Averaging (Tesseract doesn't support)

**Concept**: Average LSTM weights from Arabic + Farsi models

**Requirements:**

- Extract LSTM networks from both models
- Average weight matrices
- Combine into single model

**Status**: ❌ **Not supported**

- `lstmtraining` has no `--average` or `--ensemble` option
- Would require custom C++ code or Python manipulation of LSTM weights
- Tesseract's LSTM format is proprietary (TTComp archive)

### Approach 2: Checkpoint Ensemble (Not feasible)

**Concept**: Use both Arabic and Farsi checkpoints during inference

**Status**: ❌ **Not supported**

- Tesseract OCR uses single model at runtime
- No built-in ensemble prediction
- Would require modifying Tesseract core code

### Approach 3: Sequential Fine-Tuning ✅ (Feasible)

**Concept**: Train from Farsi, then continue from that result using Arabic

**Method:**

```bash
# Stage 1: Train from Farsi
lstmtraining --continue_from fas.lstm --traineddata ckb.traineddata \
  --model_output ckb_from_fas ...

# Stage 2: Continue from Farsi result using Arabic recoder
lstmtraining --continue_from ckb_from_fas_checkpoint \
  --old_traineddata ara.traineddata \
  --traineddata ckb.traineddata \
  --model_output ckb_fas_then_ara ...
```

**Status**: ⚠️ **Theoretically possible but problematic**

- May confuse recoder (Farsi chars → Arabic chars)
- Risk of catastrophic forgetting
- No clear linguistic benefit

### Approach 4: Mixed Training Data (Already Implemented) ✅

**Concept**: Use training data segmented by both bases

**Current implementation:**

- LSTMF files created using whichever base succeeds (hybrid segmentation)
- Single base model used for final training
- **Result**: Already happening!

**Status**: ✅ **Already in use**

- Phase 5 training used mixed Arabic/Farsi/CKB segmentation
- This IS a form of hybrid approach at the data level

### Approach 5: Pre-training + Transfer Learning (Complex)

**Concept**: Create intermediate model trained on Arabic+Farsi+Kurdish corpus

**Method:**

1. Create multilingual corpus (Arabic + Farsi + Kurdish)
2. Train from scratch on combined data
3. Fine-tune on Kurdish-only data

**Status**: ⏳ **Possible but time-intensive**

- Requires Arabic and Farsi training data
- Long training time (from scratch)
- May not converge well (3 languages with different scripts)

### Approach 6: Curriculum Learning ✅ (Most Promising)

**Concept**: Train using easier examples first, then harder ones

**Method:**

```bash
# Stage 1: Train on Phase 4 high-quality corpus (3,321 lines)
# Result: Stable base model with good convergence

# Stage 2: Add Phase 5 Wikipedia data incrementally
# Add 500 lines → train → evaluate → repeat
```

**Status**: ✅ **Feasible and research-backed**

- Prevents corpus quality dilution
- Allows evaluation at each step
- Can stop when accuracy plateaus
- Similar to "incremental fine-tuning"

---

## Experimental Test: Try Best Farsi Checkpoint

The Farsi Phase 5 checkpoint exists (25MB, Oct 13) but finalizes to Phase 3 model. Let me try using an older, better Farsi checkpoint:

### Best Historical Farsi Checkpoints

```bash
ckb_from_fas_0.195_8226_85300.checkpoint  # Oct 11, BCER 0.195 (Phase 4's best)
ckb_from_fas_0.253_7369_66000.checkpoint  # Oct 11, BCER 0.253
```

**Hypothesis**: Phase 5 Farsi checkpoint might have **overfit** or **diverged**, while Phase 4 checkpoint (BCER 0.195) was better.

### Test Plan

1. **Test Phase 4 Farsi checkpoint** (BCER 0.195):

   ```bash
   lstmtraining --stop_training \
     --continue_from ckb_from_fas_0.195_8226_85300.checkpoint \
     --traineddata ckb.traineddata \
     --model_output ckb_phase4_fas.traineddata
   ```

2. **Test Arabic Phase 5 model** (already tested): 65.39% accuracy

3. **Compare:**
   - Phase 4 Farsi checkpoint: ? accuracy
   - Phase 5 Arabic: 65.39%
   - Phase 4 baseline: 71.69%

---

## Recommendation

### Short Answer: **Hybrid approach is NOT worth it**

**Reasons:**

1. **Already using hybrid segmentation**: Training data is already created using mixed Arabic/Farsi/CKB segmentation, so we're getting the benefit of hybrid data preparation.

2. **No built-in hybrid training**: Tesseract doesn't support:

   - Model averaging
   - Ensemble prediction
   - Multi-base simultaneous training

3. **Arabic performs worse**: Despite better BCER (1.502), Arabic produces 65.39% accuracy vs 71.69% baseline. Combining with Farsi unlikely to help.

4. **Farsi training issue**: The core problem is that Farsi training isn't producing new models (Phase 4 and Phase 5 both result in Phase 3 model).

### Real Problem: **Corpus Quality**, Not Base Model Choice

The Phase 5 failure is due to:

- ❌ Wikipedia corpus is lower quality (informal, varied)
- ❌ ZWNJ density dropped from 9.46% → 6.79%
- ❌ Dilution effect (55% of corpus is now lower-quality Wikipedia)

**Not due to**:

- ✅ Base model choice (Farsi vs Arabic)
- ✅ Training approach (hybrid vs single-base)

---

## Better Alternatives

### Option 1: **Fix Corpus Quality** ⭐ (Highest ROI)

**Action**: Replace Wikipedia with high-quality sources

- Kurdish news (Rudaw, BasNews, NRT)
- Official documents
- Published literature

**Expected improvement**: +5-10% accuracy (75-80%)

### Option 2: **Debug Farsi Training Issue** 🔧 (Technical)

**Action**: Investigate why Farsi checkpoint finalizes to Phase 3 model

- Check if Phase 5 checkpoint actually trained on Phase 5 corpus
- Verify checkpoint isn't restored from old Phase 3/4 checkpoint
- Test Phase 4's best checkpoint (BCER 0.195) on Phase 5 corpus

**Expected improvement**: Unknown, but may reveal training bug

### Option 3: **Curriculum Learning** 📚 (Incremental)

**Action**: Keep Phase 4 base, add quality data gradually

- Add 500 lines at a time
- Train and evaluate after each addition
- Stop when accuracy plateaus

**Expected improvement**: +3-7% accuracy (74-78%)

### Option 4: **Accept 71.69%, Focus on ZWNJ Rules** 🎯 (Pragmatic)

**Action**: Improve post-processing instead of base accuracy

- Better ZWNJ insertion rules
- Character confusion dictionary
- Context-aware corrections

**Expected improvement**: 71.69% base + 60-70% ZWNJ recovery

---

## Conclusion

**Hybrid base model approach is NOT worthwhile because:**

1. ✅ Already using hybrid data preparation (mixed segmentation)
2. ❌ Tesseract doesn't support model-level hybridization
3. ❌ Arabic performs worse than Farsi despite better BCER
4. ❌ Real problem is corpus quality, not base model choice
5. ⚠️ Farsi training has systematic issues (produces Phase 3 model)

**Recommended next steps:**

1. **Immediate**: Debug why Farsi training produces Phase 3 model

   - Test Phase 4 Farsi checkpoint (BCER 0.195)
   - Verify Phase 5 corpus was actually used

2. **Short-term**: Improve corpus quality (Option 1)

   - Replace Wikipedia with professional sources
   - Maintain 8-12% ZWNJ density

3. **Long-term**: If accuracy reaches 80%+, retry ZWNJ rules
   - Expected 60-75% ZWNJ recovery with better base model

**Bottom line**: Focus on **corpus quality** and **debugging Farsi training**, not hybrid models.
