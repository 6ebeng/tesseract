# WSL Training Script Solutions - Summary

## Problem

When running `wsl sh work/scripts/robust_train_all_fonts.sh`, the process quits unexpectedly after starting to process.

## Solutions Provided

### 1. Diagnostic Scripts

#### A. WSL Environment Test (`work/scripts/wsl_test.sh`)

Quick test to check if WSL environment is working correctly:

```bash
wsl sh work/scripts/wsl_test.sh
```

This will check:

- Shell configuration
- Line endings
- Memory status
- Disk space
- Tesseract installation
- Font availability

#### B. Debug Training Script (`work/scripts/robust_train_debug.sh`)

Minimal training with extensive logging:

```bash
wsl sh work/scripts/robust_train_debug.sh
```

Features:

- Only processes 5 fonts
- Creates detailed log at `work/robust_train_debug.log`
- Shows exactly where the script fails
- Includes system resource monitoring

#### C. WSL-Optimized Script (`work/scripts/robust_train_wsl_fixed.sh`)

Full training script optimized for WSL:

```bash
wsl sh work/scripts/robust_train_wsl_fixed.sh
```

Improvements:

- Processes 50 fonts (configurable)
- Includes timeouts to prevent hanging
- Better memory management
- WSL-specific optimizations

### 2. Most Common Fixes

#### Fix #1: Line Endings (Most Likely Issue)

```bash
# Check if script has Windows line endings
file work/scripts/robust_train_all_fonts.sh

# Fix line endings
dos2unix work/scripts/robust_train_all_fonts.sh

# Alternative if dos2unix not available
sed -i 's/\r$//' work/scripts/robust_train_all_fonts.sh
```

#### Fix #2: Memory Limitations

Create `.wslconfig` in your Windows user directory (e.g., `C:\Users\YourName\.wslconfig`):

```ini
[wsl2]
memory=8GB
processors=4
swap=2GB
```

Then restart WSL:

```bash
wsl --shutdown
wsl
```

#### Fix #3: Make Scripts Executable

```bash
chmod +x work/scripts/*.sh
```

### 3. Quick Test Sequence

Run these commands in order to diagnose and fix:

```bash
# Step 1: Test WSL environment
wsl sh work/scripts/wsl_test.sh

# Step 2: Fix line endings on all scripts
wsl dos2unix work/scripts/*.sh

# Step 3: Make scripts executable
wsl chmod +x work/scripts/*.sh

# Step 4: Try debug version first
wsl sh work/scripts/robust_train_debug.sh

# Step 5: Check the log
wsl cat work/robust_train_debug.log

# Step 6: If debug works, try WSL-optimized version
wsl sh work/scripts/robust_train_wsl_fixed.sh
```

### 4. Alternative Running Methods

If the above doesn't work, try these alternatives:

#### Option A: Run with bash instead of sh

```bash
wsl bash work/scripts/robust_train_all_fonts.sh
```

#### Option B: Run from within WSL

```bash
# Enter WSL first
wsl

# Navigate to directory
cd /mnt/c/tesseract

# Run script
sh work/scripts/robust_train_all_fonts.sh
```

#### Option C: Use the WSL-optimized version

```bash
wsl sh work/scripts/robust_train_wsl_fixed.sh
```

### 5. Emergency Workaround

If nothing else works, use the minimal training script:

```bash
# This will only train with 5 fonts but should complete successfully
wsl sh work/scripts/robust_train_debug.sh
```

## Verification

After running any fix, verify success by checking:

1. **Model file created:**

   ```bash
   wsl ls -la work/output/*.traineddata
   ```

2. **Checkpoint files exist:**

   ```bash
   wsl ls -la work/output/*.checkpoint
   ```

3. **Training data generated:**
   ```bash
   wsl ls work/ground-truth-robust/*.tif | wc -l
   ```

## Most Likely Solution

Based on the symptom (script quits after starting), the most likely issue is **Windows line endings (CRLF)**.

**Quick fix:**

```bash
wsl dos2unix work/scripts/robust_train_all_fonts.sh
wsl sh work/scripts/robust_train_all_fonts.sh
```

If this doesn't work, use the debug script to get more information:

```bash
wsl sh work/scripts/robust_train_debug.sh
wsl cat work/robust_train_debug.log
```

## Support Files Created

1. **`work/scripts/wsl_test.sh`** - Environment tester
2. **`work/scripts/robust_train_debug.sh`** - Debug version with logging
3. **`work/scripts/robust_train_wsl_fixed.sh`** - WSL-optimized version
4. **`work/WSL_TROUBLESHOOTING_GUIDE.md`** - Comprehensive troubleshooting guide
5. **`work/WSL_SOLUTION_SUMMARY.md`** - This summary document

## Next Steps

1. Try the line endings fix first (most common issue)
2. If that fails, run the debug script and check the log
3. Share the debug log output if you need further assistance
4. Use the WSL-optimized script for better compatibility

The debug log will tell us exactly where and why the script is failing.
