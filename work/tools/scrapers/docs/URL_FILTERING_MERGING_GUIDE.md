# URL Filtering - Website-Specific Patterns (NEW FLEXIBILITY)

## 🎉 What Changed

**BEFORE:** Patterns could only be in preset file OR website config (not both)

**NOW:** Patterns can be in BOTH places and are **MERGED**!

---

## 🔄 How Merging Works

### Template + Website Whitelist (MERGED)

**Preset File** (`url_filtering_presets.yaml`):
```yaml
templates:
  rudaw:
    whitelist:
      - 'https://www.rudaw.net/sorani/*'           # Base pattern 1
      - 'https://www.rudaw.net/sorani/kurdistan/*' # Base pattern 2
```

**Website Config** (`configs/rudaw.yaml`):
```yaml
url_filtering:
  template: 'rudaw'    # Load base patterns
  whitelist:            # Add MORE patterns (MERGED)
    - 'https://www.rudaw.net/sorani/sports/*'  # New pattern 3
    - 'https://www.rudaw.net/sorani/tech/*'    # New pattern 4
```

**Result:** 4 patterns total (2 from template + 2 from website = **MERGED**)

---

### Preset + Website Blacklist (MERGED)

**Preset File** (`url_filtering_presets.yaml`):
```yaml
presets:
  standard:
    blacklist_types:
      - images    # Blocks: *.jpg, *.png, *.gif, etc.
      - tracking  # Blocks: *analytics*, *tracking*, etc.
```

**Website Config** (`configs/mysite.yaml`):
```yaml
url_filtering:
  preset: 'standard'      # Load base blocking
  blacklist:               # Add MORE blocks (MERGED)
    - '*custom-tracker.com*'
    - '*/annoying-popup/*'
```

**Result:** Base blocks (images + tracking) + custom blocks = **MERGED**

---

## 📊 Configuration Examples

### Example 1: Template Only (Simplest)
```yaml
# configs/rudaw.yaml
url_filtering:
  template: 'rudaw'
```
**Result:** Uses 4 patterns from template

---

### Example 2: Template + Site-Specific Whitelist (FLEXIBLE)
```yaml
# configs/rudaw.yaml
url_filtering:
  template: 'rudaw'    # Base: 4 patterns from preset file
  whitelist:            # Add: 2 new patterns
    - 'https://www.rudaw.net/sorani/sports/*'
    - 'https://www.rudaw.net/sorani/tech/*'
```
**Result:** 6 patterns total (4 template + 2 website = **MERGED**)

**When to use:**
- ✅ Template covers common patterns
- ✅ Website has a few unique categories
- ✅ Want centralized maintenance for common patterns
- ✅ Want local control for unique patterns

---

### Example 3: Template + Site-Specific Blacklist
```yaml
# configs/rudaw.yaml
url_filtering:
  template: 'rudaw'    # Base whitelist from template
  blacklist:            # Add site-specific blocks
    - '*rudaw-specific-tracker.com*'
```
**Result:** Template whitelist + custom blacklist

---

### Example 4: Preset + Site-Specific Blacklist (FLEXIBLE)
```yaml
# configs/mysite.yaml
url_filtering:
  preset: 'standard'      # Base blocking from preset
  blacklist:               # Add site-specific blocks
    - '*custom-tracker.com*'
    - '*/unwanted-popup/*'
```
**Result:** Standard blocking + custom blocks = **MERGED**

**When to use:**
- ✅ Standard blocking is good base
- ✅ Site has specific trackers to block
- ✅ Want preset benefits + customization

---

### Example 5: Preset + Site-Specific Whitelist
```yaml
# configs/mysite.yaml
url_filtering:
  preset: 'standard'      # Apply standard blocking
  whitelist:               # Allow specific URLs
    - 'https://mysite.com/*'
    - 'https://cdn.mysite.com/*'
```
**Result:** Standard blocking + site-specific whitelist

---

### Example 6: No Preset - Pure Website Config
```yaml
# configs/custom.yaml
url_filtering:
  whitelist:
    - 'https://mysite.com/articles/*'
    - 'https://mysite.com/news/*'
  blacklist:
    - '*.jpg'
    - '*tracking*'
```
**Result:** Only website patterns (no preset/template)

**When to use:**
- ✅ Very specific needs
- ✅ Small site
- ✅ Want full control

---

## 🎯 Best Practices

### 1. Common Patterns → Preset File
Put patterns shared by multiple sites in `url_filtering_presets.yaml`:
```yaml
templates:
  news_sites:
    whitelist:
      - '*/articles/*'
      - '*/news/*'
```

### 2. Unique Patterns → Website Config
Put site-specific patterns in individual config files:
```yaml
url_filtering:
  template: 'news_sites'   # Common patterns
  whitelist:                # Site-specific patterns
    - 'https://thissite.com/special/*'
```

### 3. Start with Template/Preset, Add as Needed
```yaml
# Start simple
url_filtering:
  template: 'rudaw'

# Add site-specific later if needed
url_filtering:
  template: 'rudaw'
  whitelist:
    - 'https://www.rudaw.net/sorani/NEW_CATEGORY/*'
```

---

## 🔍 Comparison: Before vs After

### BEFORE (Inflexible)
```yaml
# Option 1: Use template (ALL patterns from preset file)
url_filtering:
  template: 'rudaw'
# Can't add site-specific patterns!

# Option 2: Manual (NO template benefits)
url_filtering:
  whitelist:
    - 'https://www.rudaw.net/sorani/*'
    - 'https://www.rudaw.net/sorani/kurdistan/*'
    - 'https://www.rudaw.net/sorani/sports/*'  # Can't share with template
```

### AFTER (Flexible)
```yaml
# Best of both worlds!
url_filtering:
  template: 'rudaw'    # Get common patterns from template
  whitelist:            # Add site-specific patterns
    - 'https://www.rudaw.net/sorani/sports/*'  # Merged with template
```

---

## 🚀 Migration Examples

### Scenario 1: Add New Category to Rudaw

**Old Way (Manual - Update every file):**
```yaml
# configs/rudaw.yaml (must edit this file)
url_filtering:
  whitelist:
    - 'https://www.rudaw.net/sorani/*'
    - 'https://www.rudaw.net/sorani/kurdistan/*'
    - 'https://www.rudaw.net/sorani/business/*'
    - 'https://www.rudaw.net/sorani/sports/*'  # ← Add here
```

**New Way (Flexible - Use template + site-specific):**

*Option A: Add to template (if used by other sites)*
```yaml
# url_filtering_presets.yaml
templates:
  rudaw:
    whitelist:
      - 'https://www.rudaw.net/sorani/sports/*'  # ← Add once
# All sites using template auto-update!
```

*Option B: Add to website config (if site-specific)*
```yaml
# configs/rudaw.yaml
url_filtering:
  template: 'rudaw'    # Keep base patterns
  whitelist:            # Add site-specific
    - 'https://www.rudaw.net/sorani/sports/*'  # ← Add here only
```

---

### Scenario 2: Block Site-Specific Tracker

**Problem:** Site uses a custom tracker not in standard preset

**Solution:** Use preset + site-specific blacklist
```yaml
url_filtering:
  preset: 'standard'         # Get standard blocking
  blacklist:                  # Add site-specific
    - '*custom-tracker.com*'  # ← Blocks this site's tracker
```

---

## 📈 Benefits

### 1. Flexibility
- ✅ Use preset/template as base
- ✅ Add site-specific patterns as needed
- ✅ No need to choose between centralized or local

### 2. Maintainability
- ✅ Common patterns in one place (preset file)
- ✅ Unique patterns in website config
- ✅ Update once, many benefit (preset)
- ✅ Update locally for unique needs (website)

### 3. Scalability
- ✅ 100 sites can share 1 template
- ✅ Each site can add unique patterns
- ✅ Best of both worlds

### 4. Migration Path
- ✅ Start with manual config (all patterns in website)
- ✅ Move common patterns to preset file gradually
- ✅ Keep unique patterns in website config
- ✅ No breaking changes

---

## ✅ Summary

**Key Features:**
1. **Merging:** Preset/template + website patterns = combined result
2. **Flexibility:** Choose what goes where (centralized vs local)
3. **No Duplication:** Duplicate patterns are automatically filtered out
4. **Backward Compatible:** Old configs still work

**When to Use Each Approach:**
- **Template only:** Simple sites, all patterns in template
- **Template + website:** Most flexible, recommended for most cases
- **Preset only:** Standard blocking without whitelist
- **Preset + website:** Standard blocking + site-specific needs
- **Manual only:** Full control, unique requirements

**Recommendation:** Start with template/preset, add site-specific patterns as needed! 🎯

---

**Last Updated:** October 27, 2025  
**Status:** Production Ready
