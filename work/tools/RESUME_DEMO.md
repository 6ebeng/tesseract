# Test Suite Resume Feature - Demonstration

This document shows real examples of how the resume feature works.

## Scenario 1: Full Test Run Interrupted

### Initial Run (Gets Interrupted)

```bash
$ python3 test_suite.py --max-articles 5

🔧 Initializing Generic Scraper...
✅ Loaded 17 websites from 17 config files

📝 Testing all 14 website(s) (excluding examples)
   Max articles per website: 5

============================================================
Progress: 1/14
============================================================
🧪 Testing awene
   ✅ awene: SUCCESS
   Total sentences: 42

============================================================
Progress: 2/14
============================================================
🧪 Testing balinde
   ✅ balinde: SUCCESS
   Total sentences: 38

============================================================
Progress: 3/14
============================================================
🧪 Testing govkrd
   📂 Category: news

   ^C  # User presses Ctrl+C

⚠️  Test interrupted by user
💾 State saved - use --resume to continue from where you left off
```

### State File Created (`.test_suite_state.json`)

```json
{
	"timestamp": "2025-10-26T14:30:00.123456",
	"max_articles": 5,
	"completed": {
		"awene": {
			"categories": ["news", "kurdistan"],
			"total_categories": 2,
			"timestamp": "2025-10-26T14:32:15.123456"
		},
		"balinde": {
			"categories": ["news"],
			"total_categories": 1,
			"timestamp": "2025-10-26T14:35:45.123456"
		}
	}
}
```

### Resume Run (Continues Where Left Off)

```bash
$ python3 test_suite.py --max-articles 5

🔧 Initializing Generic Scraper...
✅ Loaded 17 websites from 17 config files

📌 Loaded previous state from 2025-10-26T14:30:00
   2 website(s) already completed

📝 Testing all 14 website(s) (excluding examples)

   ✓ awene: Already completed (2/2 categories)
   ✓ balinde: Already completed (1/1 categories)

   📋 12 website(s) remaining to test
   Max articles per website: 5

============================================================
Progress: 1/12
============================================================
🧪 Testing govkrd
   # Continues from govkrd...
```

## Scenario 2: Multi-Category Website Interrupted

### Testing AvaNews (6 Categories)

```bash
$ python3 test_suite.py avanews --max-articles 10

🔧 Initializing Generic Scraper...

📝 Testing 1 specific website(s)
   Max articles per website: 10

============================================================
🧪 Testing avanews
   Categories: 6/6 enabled
============================================================

   📂 Category: news
      ✅ 10 sentences in 45.2s

   📂 Category: economy
      ✅ 10 sentences in 42.8s

   📂 Category: culture
      ✅ 10 sentences in 48.1s

   📂 Category: environment

   ^C  # Interrupted after 3 categories

⚠️  Test interrupted by user
💾 State saved - use --resume to continue from where you left off
```

### Resume (Skips Completed Categories)

```bash
$ python3 test_suite.py avanews --max-articles 10

🔧 Initializing Generic Scraper...

📌 Loaded previous state from 2025-10-26T15:00:00
   0 website(s) already completed

📝 Testing 1 specific website(s)
   Max articles per website: 10

============================================================
🧪 Testing avanews
   Categories: 6/6 enabled
   📌 Resuming: 3 categories already completed
============================================================

   ✓ Category: news (already completed)
   ✓ Category: economy (already completed)
   ✓ Category: culture (already completed)

   📂 Category: environment
      ✅ 10 sentences in 46.5s

   📂 Category: health
      ✅ 10 sentences in 44.2s

   📂 Category: opinion
      ✅ 10 sentences in 43.8s

============================================================
✅ avanews: SUCCESS
   Categories tested: 3
   Successful: 3
   Total sentences: 30
   Total duration: 134.5s
============================================================

📊 TEST SUMMARY
============================================================
✅ Successful: 1
   - avanews

Success Rate: 100.0% (1/1)
============================================================

✅ All tests completed successfully!
🗑️  Cleared previous state
```

## Scenario 3: Fresh Start After Failed Attempt

### Initial Attempt (Had Issues)

```bash
$ python3 test_suite.py nrt --max-articles 10

# Network issues, timeouts, etc.
❌ nrt: FAILED
```

### State File Shows Partial Completion

```json
{
	"completed": {
		"nrt": {
			"categories": ["news"],
			"total_categories": 2,
			"timestamp": "2025-10-26T16:00:00"
		}
	}
}
```

### Start Fresh (Ignore Previous State)

```bash
$ python3 test_suite.py nrt --max-articles 10 --fresh

🗑️  Cleared previous state

🔧 Initializing Generic Scraper...

📝 Testing 1 specific website(s)
   Max articles per website: 10

============================================================
🧪 Testing nrt
   Categories: 2/2 enabled
   # No "resuming" message - starts fresh
============================================================

   📂 Category: news
      ✅ 16 sentences in 95.2s

   📂 Category: economy
      ✅ 14 sentences in 88.4s

# Fresh run, all categories tested again
```

## Scenario 4: Multiple Specific Websites

### Testing Multiple Sites (Interrupted)

```bash
$ python3 test_suite.py yariga rudaw avanews khak nrt

============================================================
Progress: 1/5
============================================================
🧪 Testing yariga
   ✅ SUCCESS

============================================================
Progress: 2/5
============================================================
🧪 Testing rudaw
   ✅ SUCCESS

^C  # Interrupted after 2 websites

⚠️  Test interrupted by user
💾 State saved - use --resume to continue from where you left off
```

### Resume (Auto-Skips Completed Sites)

```bash
$ python3 test_suite.py yariga rudaw avanews khak nrt

📌 Loaded previous state from 2025-10-26T17:00:00
   2 website(s) already completed

   ✓ yariga: Already completed
   ✓ rudaw: Already completed

   📋 3 website(s) remaining to test

============================================================
Progress: 1/3
============================================================
🧪 Testing avanews
   # Continues with avanews...
```

## Command Patterns

### Pattern 1: Long Test Run

```bash
# Start
python3 test_suite.py

# If interrupted, just run same command
python3 test_suite.py
# Automatically resumes
```

### Pattern 2: Specific Sites

```bash
# Start
python3 test_suite.py site1 site2 site3

# If interrupted, same command
python3 test_suite.py site1 site2 site3
# Skips completed sites
```

### Pattern 3: Explicit Control

```bash
# Force resume
python3 test_suite.py --resume

# Force fresh
python3 test_suite.py --fresh
```

### Pattern 4: Retry After Fixes

```bash
# First attempt failed
python3 test_suite.py problematic_site
# Fix configuration

# Retry with fresh start
python3 test_suite.py problematic_site --fresh
```

## Benefits Demonstrated

### ⏱️ Time Saving

- **Before**: Re-run entire test suite after interruption
- **After**: Continue exactly where you left off
- **Example**: If 10 sites done out of 14, only test remaining 4

### 🎯 Category-Level Precision

- **Before**: Re-test entire website if interrupted mid-category
- **After**: Skip completed categories, only test remaining ones
- **Example**: AvaNews has 6 categories - if 3 done, only test remaining 3

### 🛡️ Interruption Safety

- **Ctrl+C**: Safe anytime, state saved
- **Network timeout**: Just re-run, continues
- **Power loss**: State file persists, resume when back

### 🧹 Auto-Cleanup

- **Success**: State automatically cleared
- **No clutter**: Only keeps state when needed
- **Fresh runs**: Easy with `--fresh` flag

## State File Details

### Location

```
work/tools/.test_suite_state.json
```

### Format

```json
{
	"timestamp": "ISO 8601 timestamp of test run start",
	"max_articles": 5,
	"completed": {
		"website_name": {
			"categories": ["cat1", "cat2"],
			"total_categories": 4,
			"timestamp": "ISO 8601 timestamp of completion"
		}
	}
}
```

### Lifecycle

1. **Created**: After first website completes
2. **Updated**: After each website completes
3. **Read**: On next test run (if exists)
4. **Cleared**: On successful completion OR with `--fresh` flag

## Tips for Best Experience

1. **Long runs**: Just re-run same command if interrupted
2. **Check progress**: Look at state file to see what's done
3. **Retry failures**: Use `--fresh` to start over
4. **Manual clean**: Delete `.test_suite_state.json` if needed
5. **Specific sites**: Resume works with specific site lists too
