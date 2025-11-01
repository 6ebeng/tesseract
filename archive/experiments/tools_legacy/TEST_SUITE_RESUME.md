# Test Suite Resume Feature

The test suite now supports resuming from interrupted runs, so you never lose progress!

## Features

### 🔄 Auto-Resume

The test suite automatically saves progress after each website is tested. If interrupted, simply run again and it will continue where it left off.

### 💾 State Tracking

- Tracks which websites have been tested
- Tracks which categories within each website have been completed
- Saves state to `.test_suite_state.json`
- Auto-clears state when all tests complete successfully

### 🎯 Resume Modes

#### 1. **Automatic Resume** (Default for full test runs)

```bash
# Start testing all websites
python3 test_suite.py

# If interrupted (Ctrl+C), just run again
python3 test_suite.py
# Will automatically skip completed websites/categories
```

#### 2. **Explicit Resume**

```bash
# Force resume from previous state
python3 test_suite.py --resume
```

#### 3. **Fresh Start**

```bash
# Ignore previous state and start from scratch
python3 test_suite.py --fresh
```

## Usage Examples

### Example 1: Testing All Websites with Auto-Resume

```bash
# Start testing all websites
python3 test_suite.py --max-articles 10

# If this gets interrupted (timeout, Ctrl+C, crash), run again:
python3 test_suite.py --max-articles 10

# Output will show:
# 📌 Loaded previous state from 2025-10-26T14:30:00
#    3 website(s) already completed
#    ✓ yariga: Already completed (2/2 categories)
#    ✓ rudaw: Already completed (4/4 categories)
#    11 website(s) remaining to test
```

### Example 2: Resume After Interruption

```bash
# You're testing 5 websites, but interrupt after 2
python3 test_suite.py yariga rudaw avanews khak nrt --max-articles 5
# (Ctrl+C after rudaw completes)

# Resume - will skip yariga and rudaw
python3 test_suite.py --resume

# Or just run the same command again
python3 test_suite.py yariga rudaw avanews khak nrt --max-articles 5
```

### Example 3: Partial Category Completion

```bash
# Start testing AvaNews (6 categories)
python3 test_suite.py avanews --max-articles 10

# Gets interrupted after completing 3 categories
# Run again - will skip completed categories:
python3 test_suite.py avanews --max-articles 10

# Output:
# 📌 Resuming: 3 categories already completed
# ✓ Category: news (already completed)
# ✓ Category: economy (already completed)
# ✓ Category: culture (already completed)
# 📂 Category: environment
#    ✅ 10 sentences in 45.2s
# ...
```

### Example 4: Start Fresh

```bash
# Clear previous state and start over
python3 test_suite.py --fresh

# Or for specific test:
python3 test_suite.py avanews --fresh --max-articles 10
```

## State File

### Location

`.test_suite_state.json` in the same directory as `test_suite.py`

### Format

```json
{
	"timestamp": "2025-10-26T14:30:00.123456",
	"max_articles": 5,
	"completed": {
		"yariga": {
			"categories": ["news", "kurdistan"],
			"total_categories": 2,
			"timestamp": "2025-10-26T14:32:15.123456"
		},
		"avanews": {
			"categories": ["news", "economy", "culture"],
			"total_categories": 6,
			"timestamp": "2025-10-26T14:45:30.123456"
		}
	}
}
```

### State Management

- **Auto-saved**: After each website completes
- **Auto-cleared**: When all tests complete successfully
- **Manual clear**: Use `--fresh` flag or delete `.test_suite_state.json`

## Benefits

### ⏱️ Time Saving

- Don't re-run completed tests after interruptions
- Skip websites that already succeeded
- Resume exactly where you left off

### 🛡️ Interruption Recovery

- Safe to Ctrl+C at any time
- Power loss or crash recovery
- Network timeout recovery

### 📊 Progress Tracking

- See which websites are already done
- Know how many remain
- Track per-category completion

## Output Indicators

### When Resuming

```
📌 Loaded previous state from 2025-10-26T14:30:00
   3 website(s) already completed

✓ yariga: Already completed (2/2 categories)
✓ rudaw: Already completed (4/4 categories)

📋 11 website(s) remaining to test
```

### During Test

```
🧪 Testing avanews
   Categories: 6/6 enabled
   📌 Resuming: 3 categories already completed

   ✓ Category: news (already completed)
   ✓ Category: economy (already completed)
   ✓ Category: culture (already completed)

   📂 Category: environment
      ✅ 10 sentences in 45.2s
```

### After Interruption

```
⚠️  Test interrupted by user
💾 State saved - use --resume to continue from where you left off
```

### On Completion

```
✅ All tests completed successfully!
```

(State automatically cleared)

## Tips

1. **Long test runs**: Always use auto-resume for full test suite runs
2. **Interruptions**: Just re-run the same command - it will resume
3. **Retrying failures**: Use `--fresh` to retry everything from scratch
4. **Check state**: Look at `.test_suite_state.json` to see what's completed
5. **Clear state**: Use `--fresh` or delete the state file manually

## Command Quick Reference

```bash
# Auto-resume (default for all-sites runs)
python3 test_suite.py

# Explicit resume
python3 test_suite.py --resume

# Fresh start (clear state)
python3 test_suite.py --fresh

# Specific sites with auto-resume
python3 test_suite.py yariga avanews

# Fresh test of specific sites
python3 test_suite.py yariga avanews --fresh
```
