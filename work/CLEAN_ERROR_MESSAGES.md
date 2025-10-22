# Clean Error Message Implementation

## Summary

Fixed ugly Selenium stacktraces across LvinPress and Sharpress scrapers by implementing a `clean_error()` helper method in `BaseScraper`.

## Changes Made

### 1. **BaseScraper (`base_scraper.py`)**

Added `clean_error()` static method to extract concise error messages:

```python
@staticmethod
def clean_error(exception):
    """Extract clean, concise error message from exception"""
    error_str = str(exception)
    first_line = error_str.split('\n')[0]

    # Simplify common Selenium errors
    if 'no such element' in first_line.lower():
        return "Element not found"
    elif 'timeout' in first_line.lower():
        return "Page timeout"
    elif 'stale element' in first_line.lower():
        return "Element changed"
    elif 'session' in first_line.lower() and 'deleted' in first_line.lower():
        return "Browser session lost"
    elif len(first_line) > 100:
        return first_line[:100] + "..."
    else:
        return first_line
```

### 2. **LvinPress Scraper (`lvinpress_scraper.py`)**

**Before:**

```python
except Exception as e:
    print(f"      ⚠️  Content extraction failed: {e}")
    continue
```

**After:**

```python
except Exception as e:
    print(f"      ⚠️  {self.clean_error(e)} (skipped)")
    continue
```

### 3. **Sharpress Scraper (`sharpress_scraper.py`)**

**Before:**

```python
except Exception as e:
    print(f"      Error on page {page}: {e}")
    break
```

**After:**

```python
except Exception as e:
    print(f"      ⚠️  Page {page}: {self.clean_error(e)}")
    break
```

## Before vs After

### Before (Ugly):

```
   [1/5] https://lvinpress.com/video/7431
      ⚠️  Content extraction failed: Message: no such element: Unable to locate element: {"method":"css selector","selector":"h1.elementor-heading-title"}
  (Session info: chrome=141.0.7390.54); For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception
Stacktrace:
#0 0x562acbe3995a <unknown>
#1 0x562acb8da536 <unknown>
#2 0x562acb92b484 <unknown>
#3 0x562acb92b721 <unknown>
#4 0x562acb97a134 <unknown>
#5 0x562acb95174d <unknown>
... (18 more lines)
```

### After (Clean):

```
   [1/5] https://lvinpress.com/video/7431
      ⚠️  Element not found (skipped)
```

## Benefits

1. **Cleaner output** - No more 20+ line stacktraces
2. **Easier debugging** - Focus on the actual issue
3. **Better UX** - Less intimidating error messages
4. **Consistent** - All scrapers can use the same helper method

## Usage in Other Scrapers

Other scrapers can adopt this pattern:

```python
except Exception as e:
    print(f"⚠️  {self.clean_error(e)}")
```

Instead of:

```python
except Exception as e:
    print(f"⚠️  Error: {e}")
```

## Testing

Tested with:

- LvinPress scraper (video articles triggering element not found)
- Sharpress scraper (pagination errors)
- Manual error injection

All errors now display cleanly without stacktraces.
