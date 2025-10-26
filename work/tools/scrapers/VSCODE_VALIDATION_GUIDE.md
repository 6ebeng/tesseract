# 🎨 VS Code Real-Time Validation Setup

**Status**: ✅ Configured  
**Extension**: Red Hat YAML (already installed)

---

## ✅ What's Now Active

I've configured VS Code to provide **real-time validation** as you type in config files.

### Settings Applied

Created `.vscode/settings.json` with:

- ✅ Schema validation enabled
- ✅ Auto-completion enabled (Ctrl+Space)
- ✅ Hover documentation enabled
- ✅ Format on save enabled

---

## 🎯 How to Use

### 1. **Open Any Config File**

```
work/tools/scrapers/configs/kurdsat.yaml  ← You're here now!
```

### 2. **Real-Time Features**

#### ✅ **Error Detection**

- Red squiggly lines appear instantly on errors
- Hover over them to see what's wrong

#### 💡 **Auto-Complete**

- Press `Ctrl+Space` to see available fields
- Start typing and suggestions appear automatically

#### 📖 **Hover Documentation**

- Hover over any field name to see its description
- Shows: type, required/optional, examples

#### 🎨 **Format on Save**

- Press `Ctrl+S` to save
- File automatically formats with proper indentation

---

## 🧪 Try It Now!

### Test 1: Auto-Complete

1. Open `kurdsat.yaml`
2. Under `selectors:`, type a new line
3. Press `Ctrl+Space`
4. You'll see: `article_list`, `article_title`, `article_body`

### Test 2: Error Detection

1. Try changing `enabled: true` to `enabled: "yes"`
2. You'll immediately see a red squiggle
3. Hover to see: "Expected boolean, got string"
4. Change it back to `true` - error disappears!

### Test 3: Forbidden Field Detection

1. Try adding `article_link: 'a'` under `selectors:`
2. You'll see a red squiggle
3. Hover to see: "Should NOT be valid (V3 field removed)"

### Test 4: Hover Documentation

1. Hover over `pagination:`
2. You'll see the schema description
3. Shows required fields and valid values

---

## 📋 What You'll See While Typing

### Creating a New Config

```yaml
name: 'My Site'
base_url: 'https://example.com'
enabled: true

pagination:
  type: |  ← Press Ctrl+Space here
  #      You'll see: pagination, infinite_scroll, click_load_more
```

### Auto-Complete After Selecting Type

```yaml
pagination:
  type: 'pagination'
  |  ← Press Ctrl+Space here
  #  You'll see: pages, delay
```

### Error Detection

```yaml
pagination:
  type: 'wrong_value'  ← Red squiggle appears
  #                     Hover: "Must be one of: pagination, infinite_scroll, click_load_more"
```

---

## 🎨 Visual Indicators

### Valid Code

```yaml
name: 'Kurdsat TV'  ✅ No underline
enabled: true       ✅ No underline
```

### Invalid Code

```yaml
name: 'Kurdsat TV'  ✅ No underline
enabled: "yes"      ❌ Red squiggle (should be boolean)
```

### Forbidden V3 Fields

```yaml
selectors:
  article_list: 'a'      ✅ Valid
  article_link: 'a'      ❌ Red squiggle (V3 field)
  article_content: '.p'  ❌ Red squiggle (V3 field)
```

---

## 🔧 Advanced Features

### 1. **Format Document**

- Right-click → "Format Document"
- Or: `Shift+Alt+F`
- Fixes indentation automatically

### 2. **Show All Errors**

- Press `Ctrl+Shift+M` to open Problems panel
- See all errors in current file
- Click to jump to error location

### 3. **IntelliSense**

- As you type, suggestions appear automatically
- Use ↑/↓ to select
- Press `Tab` to insert

### 4. **Schema Validation Status**

- Bottom right corner shows "YAML ✓" when valid
- Shows "YAML ✗" with error count when invalid

---

## 📖 Field Documentation

When you hover over fields, you'll see:

### Example: `pagination.type`

```
type: string (required)
enum: ["pagination", "infinite_scroll", "click_load_more"]

Description: Type of pagination used by the website.
- pagination: Page number in URL
- infinite_scroll: Scroll to load more
- click_load_more: Click button to load more
```

### Example: `wait.selector`

```
selector: string or null (required)

Description: CSS selector to wait for before scraping.
Set to null for manual timeout without selector.
```

---

## 🎯 Common Scenarios

### Scenario 1: Adding a New Category

```yaml
categories:
  news:
    url: 'https://...'
  health:
    ← Start typing here
    |      ← Press Ctrl+Space
    #      Shows: url (required)
```

### Scenario 2: Changing Pagination Type

```yaml
pagination:
  type: 'pagination'  ← Change to 'click_load_more'
  pages: 3            ← Red squiggle appears
  #                   ← Hover: "pages not needed for click_load_more"
  delay: 2
```

After changing:

```yaml
pagination:
  type: 'click_load_more'
  clicks: |           ← Press Ctrl+Space
  #       ← Shows: integer type expected
  load_more_button: | ← Press Ctrl+Space
  #                 ← Shows: string (CSS/XPath selector)
  delay: 2
```

### Scenario 3: Overriding Category Settings

```yaml
categories:
  news:
    url: 'https://...'
    pagination:
      ← Override here
      |               ← Press Ctrl+Space
      #               ← Shows: type, pages, scrolls, clicks, etc.
```

---

## 🚫 What VS Code Catches

### ✅ Instant Detection

- ❌ Wrong type (string instead of boolean)
- ❌ Invalid enum value
- ❌ Missing required field
- ❌ V3 forbidden fields
- ❌ Invalid URL format
- ❌ Wrong category name pattern
- ❌ Missing conditional fields

### Example Errors You'll See

```yaml
enabled: 'yes'
# ❌ Error: Incorrect type. Expected "boolean".

pagination:
  type: 'scroll'
# ❌ Error: Value is not accepted. Valid values: "pagination", "infinite_scroll", "click_load_more".

selectors:
  article_link: 'a'
# ❌ Error: Matches a schema that it should not validate against (V3 field removed).

wait:
  type: 'manual'
# ❌ Error: Matches a schema that it should not validate against (use wait.selector instead).
```

---

## 🎉 Benefits

### Before (No Validation)

- ❌ Find errors at runtime
- ❌ Manual checking
- ❌ No suggestions
- ❌ Trial and error

### After (Real-Time Validation)

- ✅ Find errors as you type
- ✅ Automatic checking
- ✅ Auto-complete suggestions
- ✅ Instant feedback

---

## 🔍 Troubleshooting

### VS Code Not Showing Validation?

1. **Check Extension**

   ```vscode-extensions
   redhat.vscode-yaml
   ```

   ✅ Should be installed (you have it!)

2. **Reload Window**

   - Press `Ctrl+Shift+P`
   - Type "Reload Window"
   - Press Enter

3. **Check File Type**

   - Bottom right corner should show "YAML"
   - If not, click and select "YAML"

4. **Check Schema Status**
   - Open any config file
   - Look at bottom status bar
   - Should show: "Schema: config.schema.json"

### Not Seeing Auto-Complete?

- Make sure cursor is at correct indentation level
- Press `Ctrl+Space` explicitly
- Wait 1-2 seconds for suggestions to load

---

## 📚 Related Files

- **Schema**: `work/tools/scrapers/configs/config.schema.json`
- **Settings**: `.vscode/settings.json`
- **Configs**: `work/tools/scrapers/configs/*.yaml`

---

## 🎯 Quick Reference

| Action           | Shortcut       |
| ---------------- | -------------- |
| Auto-complete    | `Ctrl+Space`   |
| Format document  | `Shift+Alt+F`  |
| Show problems    | `Ctrl+Shift+M` |
| Go to definition | `F12`          |
| Peek definition  | `Alt+F12`      |
| Save             | `Ctrl+S`       |
| Command palette  | `Ctrl+Shift+P` |

---

## ✅ You're All Set!

**What works now:**

- ✅ Real-time error detection
- ✅ Auto-completion (Ctrl+Space)
- ✅ Hover documentation
- ✅ Format on save
- ✅ V3 field rejection
- ✅ Type checking
- ✅ Enum validation

**Try it:**

1. Open `kurdsat.yaml` (you're already there!)
2. Make a change
3. See instant validation!

---

**Last Updated**: October 24, 2025  
**Schema Version**: V4.0  
**Extension**: Red Hat YAML ✅ Installed
