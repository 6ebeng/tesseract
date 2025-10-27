# URL Filtering - Easy Maintenance Guide

## 🎯 Quick Start (5 Flexible Options)

### Option 1: Template Only (EASIEST ⭐)
```yaml
url_filtering:
  template: 'rudaw'  # One line - uses patterns from preset file
```
**When to use:** Site has pre-configured template  
**Maintenance:** Update template in presets file

### Option 2: Template + Website Patterns (FLEXIBLE ⭐⭐ RECOMMENDED)
```yaml
url_filtering:
  template: 'rudaw'    # Base patterns from preset file
  whitelist:            # Add site-specific patterns (MERGED)
    - 'https://www.rudaw.net/sorani/sports/*'  # New category
    - 'https://www.rudaw.net/sorani/tech/*'    # New category
```
**When to use:** Template covers most needs, but need site-specific additions  
**Maintenance:** Update template for common patterns, website config for unique ones

### Option 3: Preset Only (Balanced)
```yaml
url_filtering:
  preset: 'standard'  # Choose: minimal, standard, aggressive, maximum
```
**When to use:** Generic site, standard blocking levels  
**Maintenance:** Update preset in presets file

### Option 4: Preset + Website Patterns (Customized)
```yaml
url_filtering:
  preset: 'standard'     # Base blocking from preset
  blacklist:              # Add site-specific blocks (MERGED)
    - '*custom-tracker.com*'
    - '*/unwanted-ads/*'
```
**When to use:** Standard blocking + site-specific needs  
**Maintenance:** Update preset for common blocks, website config for unique ones

### Option 5: Manual (Full Control)
```yaml
url_filtering:
  whitelist:
    - 'https://example.com/*'
  blacklist:
    - '*.jpg'
    - '*tracking*'
```
**When to use:** Very specific needs, complete control  
**Maintenance:** Update individual config file

## 📚 All Configuration Examples

### Example 1: Template Only
```yaml
# configs/rudaw.yaml
url_filtering:
  template: 'rudaw'  # Uses all patterns from preset file
```

### Example 2: Template + Website Additions (RECOMMENDED)
```yaml
# configs/rudaw.yaml
url_filtering:
  template: 'rudaw'    # Base: 4 patterns from preset file
  whitelist:            # Add: 2 new categories (MERGED = 6 total)
    - 'https://www.rudaw.net/sorani/sports/*'
    - 'https://www.rudaw.net/sorani/tech/*'
```

### Example 3: Preset Only
```yaml
# configs/mysite.yaml
url_filtering:
  preset: 'standard'  # Blocks: media, tracking, ads
```

### Example 4: Preset + Website Blacklist
```yaml
# configs/mysite.yaml
url_filtering:
  preset: 'standard'      # Base blocking from preset
  blacklist:               # Add site-specific blocks (MERGED)
    - '*custom-tracker.com*'
    - '*/annoying-popup/*'
```

### Example 5: Maximum Speed - Whitelist Only
```yaml
# configs/fastsite.yaml
url_filtering:
  preset: 'maximum'      # Whitelist-only mode
  whitelist:              # Define allowed patterns
    - 'https://example.com/articles/*'
    - 'https://example.com/api/*'
```

### Example 6: Manual Configuration
```yaml
# configs/custom.yaml
url_filtering:
  whitelist:
    - 'https://mysite.com/*'
  blacklist:
    - '*.jpg'
    - '*.png'
    - '*facebook.com*'
```

## 🔧 How to Add New Template

Edit `configs/url_filtering_presets.yaml`:

```yaml
templates:
  mysite:
    preset: "maximum"
    whitelist:
      - 'https://mysite.com/*'
      - 'https://mysite.com/articles/*'
    blacklist: []
```

Then use in config:
```yaml
url_filtering:
  template: 'mysite'
```

## 🔍 How to Choose

### Use Template When:
- ✅ Site already has pre-configured template
- ✅ Want one-line configuration
- ✅ Don't want to maintain whitelist/blacklist manually

### Use Preset When:
- ✅ Generic site without template
- ✅ Want standard blocking levels
- ✅ May need to add custom blocks later

### Use Manual When:
- ✅ Very specific blocking needs
- ✅ Small site with few patterns
- ✅ Want full control

## 📊 Performance Comparison

| Configuration | Requests/Article | Speed Gain | Maintenance |
|--------------|------------------|------------|-------------|
| **No filtering** | 30-50 | 1x (baseline) | None needed |
| **preset: minimal** | 10-20 | 2-3x | Very easy |
| **preset: standard** | 5-10 | 5-8x | Easy |
| **preset: aggressive** | 2-5 | 10-15x | Easy |
| **template: rudaw** | 1 | 15-20x | Easiest |
| **Manual whitelist** | 1-3 | 15-20x | Complex |

## ⚙️ Maintenance Tasks

### Update Template (Centralized)
Edit once in `url_filtering_presets.yaml`, all sites using template auto-update:

```yaml
templates:
  rudaw:
    whitelist:
      - 'https://www.rudaw.net/sorani/*'
      - 'https://www.rudaw.net/sorani/NEW_CATEGORY/*'  # Add here
```

### Update Individual Site
Edit specific config file:

```yaml
# configs/rudaw.yaml
url_filtering:
  preset: 'maximum'
  whitelist:
    - 'https://www.rudaw.net/sorani/*'
    - 'https://www.rudaw.net/sorani/NEW_CATEGORY/*'  # Add here
```

### Switch Blocking Level
Change preset in config:

```yaml
# Before
url_filtering:
  preset: 'minimal'

# After (more aggressive)
url_filtering:
  preset: 'aggressive'
```

## 🐛 Troubleshooting

### No Content Extracted
**Cause**: Whitelist too restrictive  
**Fix**: Use preset instead, or add more patterns:

```yaml
url_filtering:
  preset: 'standard'  # Instead of whitelist
```

### Still Too Slow
**Cause**: Not blocking enough  
**Fix**: Use more aggressive preset:

```yaml
url_filtering:
  preset: 'aggressive'  # or 'maximum'
```

### Template Not Found
**Cause**: Template not defined in presets file  
**Fix**: Check `url_filtering_presets.yaml` or use preset:

```yaml
url_filtering:
  preset: 'standard'  # Fallback to preset
```

## 📝 Migration from Old Format

### Old Format (Before)
```yaml
url_filtering:
  whitelist:
    - 'https://www.rudaw.net/sorani/*'
    - 'https://www.rudaw.net/sorani/kurdistan/*'
    - 'https://www.rudaw.net/sorani/business/*'
    - 'https://www.rudaw.net/sorani/culture/*'
  blacklist: []
```

### New Format (After) - 3 Options

**Option 1: Template (EASIEST)**
```yaml
url_filtering:
  template: 'rudaw'
```

**Option 2: Preset + Whitelist**
```yaml
url_filtering:
  preset: 'maximum'
  whitelist:
    - 'https://www.rudaw.net/sorani/*'
```

**Option 3: Keep Old Format (Still Works)**
```yaml
url_filtering:
  whitelist:
    - 'https://www.rudaw.net/sorani/*'
  # Old format still supported
```

## ✅ Best Practices

1. **Start with template** if available
2. **Use preset** for new sites (start with 'standard')
3. **Add extra_blacklist** for site-specific needs
4. **Centralize** common patterns in presets file
5. **Test** with `--max-articles 2` before full run

## 🚀 Current Status

**Rudaw Configuration:**
- ✅ Template-based (one line: `template: 'rudaw'`)
- ✅ Centralized in `url_filtering_presets.yaml`
- ✅ Easy to update
- ✅ Maximum performance (whitelist-only)

**Other Sites:**
- ✅ Can use presets for quick setup
- ✅ Can create custom templates
- ✅ Manual config still supported

---

**Last Updated**: October 27, 2025  
**Config File**: `configs/url_filtering_presets.yaml`  
**Status**: Production Ready
