# JSON Schema Validation for Scraper Configs

## Overview

We use **JSON Schema** to validate all website scraper configuration files. This ensures:

✅ All required fields are present  
✅ Field types are correct (string, number, array, etc.)  
✅ Values follow constraints (URLs, enums, minimums)  
✅ Old V3 fields are detected and rejected  
✅ Type-specific requirements are validated

## Files

1. **`config.schema.json`** - The JSON Schema definition
2. **`validate_schema.py`** - Python validator using the schema

## Usage

### Validate All Configs

```bash
cd /mnt/c/tesseract/work/tools/scrapers
source venv/bin/activate
python validate_schema.py
```

### Output

```
================================================================================
JSON SCHEMA VALIDATION - Config V4.0
================================================================================

✅ Loaded schema: configs/config.schema.json

📁 Found 12 configs to validate

================================================================================
Validating: kurdsat.yaml
================================================================================

✅ VALID - Passes all schema requirements!

...

================================================================================
SUMMARY
================================================================================

Total configs: 12
✅ Valid: 12/12 (100%)
❌ Errors: 0
⚠️  Warnings: 0

🎉 ALL CONFIGS PASS SCHEMA VALIDATION!
```

## Schema Rules

### Required Top-Level Fields

- `name` (string): Website name
- `base_url` (string, URI): Base URL starting with http:// or https://
- `enabled` (boolean): Whether scraper is enabled
- `pagination` (object): Universal pagination settings
- `selectors` (object): CSS selectors for finding content
- `wait` (object): Wait strategy
- `categories` (object): Categories to scrape

### Pagination Rules

**Required:**

- `type`: Must be `pagination`, `infinite_scroll`, or `click_load_more`
- `delay`: Number (seconds)

**Type-Specific Requirements:**

| Type              | Required Fields                                     |
| ----------------- | --------------------------------------------------- |
| `pagination`      | `pages` (integer ≥ 1)                               |
| `infinite_scroll` | `scrolls` (integer ≥ 1)                             |
| `click_load_more` | `clicks` (integer ≥ 1), `load_more_button` (string) |

**Example:**

```yaml
pagination:
  type: 'pagination'
  pages: 5
  delay: 2
```

### Selectors Rules

**Required:**

- `article_list`: String or array of strings
- `article_title`: Array of strings (fallback chain)
- `article_body`: Array of strings (fallback chain)

**Forbidden (Old V3 fields):**

- ❌ `article_link` - Removed in V4
- ❌ `article_content` - Merged into `article_body`
- ❌ `article_paragraphs` - Merged into `article_body`

**Example:**

```yaml
selectors:
  article_list: 'a[href*="/articles/"]'
  article_title: ['h1', 'h2']
  article_body: ['.content p', 'p']
```

### Wait Rules

**Required:**

- `selector`: String (CSS selector) or `null`
- `timeout`: Number (seconds, ≥ 0)

**Forbidden (Old V3 fields):**

- ❌ `type` - Use `selector` instead
- ❌ `seconds` - Use `timeout` instead

**Example:**

```yaml
wait:
  selector: null # or '.article-list'
  timeout: 3
```

### Categories Rules

**Required:**

- At least one category
- Category names must be lowercase with underscores only: `^[a-z_]+$`
- Each category must have `url` field

**Optional Overrides:**

- `pagination`: Override universal pagination
- `selectors`: Override universal selectors

**Forbidden (Old V3 fields):**

- ❌ `enabled` - Implicit in V4
- ❌ `type` - Override in `pagination.type`
- ❌ `pages` - Override in `pagination.pages`
- ❌ `page_param` - Not needed in V4

**Example:**

```yaml
categories:
  politics:
    url: 'https://example.com/politics'
    # Inherits everything

  economy:
    url: 'https://example.com/economy'
    pagination:
      pages: 10 # Override
```

## Error Detection

The schema catches these common errors:

### 1. Missing Required Fields

```
❌ root: 'pagination' is a required property
```

### 2. Wrong Type

```
❌ pagination.pages: 'five' is not of type 'integer'
```

### 3. Invalid Enum Value

```
❌ pagination.type: 'scroll' is not one of ['pagination', 'infinite_scroll', 'click_load_more']
```

### 4. Old V3 Fields

```
❌ selectors.article_link: Additional properties are not allowed
```

### 5. Missing Type-Specific Fields

```
❌ pagination: 'pages' is a required property when type is 'pagination'
```

### 6. Invalid URL Format

```
❌ base_url: 'example.com' does not match '^https?://'
```

### 7. Invalid Category Name

```
❌ categories: 'Politics-News' does not match '^[a-z_]+$'
```

## Integration with CI/CD

Add to your CI pipeline:

```yaml
# .github/workflows/validate-configs.yml
name: Validate Configs

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install pyyaml jsonschema

      - name: Validate configs
        run: |
          cd work/tools/scrapers
          python validate_schema.py
```

## VS Code Integration

Add to `.vscode/settings.json`:

```json
{
	"yaml.schemas": {
		"./work/tools/scrapers/configs/config.schema.json": ["./work/tools/scrapers/configs/*.yaml"]
	}
}
```

This enables:

- ✅ Real-time validation in VS Code
- ✅ Auto-completion for fields
- ✅ Hover documentation
- ✅ Inline error highlighting

## Schema Version

Current schema version: **V4.0**  
Schema ID: `https://github.com/6ebeng/tesseract/scrapers/config.schema.json`

## Extending the Schema

To add new validation rules:

1. Edit `config.schema.json`
2. Add new properties or constraints
3. Update documentation
4. Run `validate_schema.py` to test
5. Commit both schema and updated configs

### Example: Add New Pagination Type

```json
{
	"pagination": {
		"properties": {
			"type": {
				"enum": [
					"pagination",
					"infinite_scroll",
					"click_load_more",
					"ajax_load" // New type
				]
			}
		}
	}
}
```

Then add conditional validation for the new type.

## Benefits

1. **Catches Errors Early** - Before runtime
2. **Enforces Standards** - All configs follow same structure
3. **Documents Structure** - Schema is self-documenting
4. **IDE Support** - Auto-completion and validation
5. **Version Control** - Detects old V3 fields automatically
6. **Type Safety** - Ensures correct data types

## Validation Results (Current)

```
Total configs: 12
✅ Valid: 12/12 (100%)
❌ Errors: 0
⚠️  Warnings: 0

🎉 ALL CONFIGS PASS SCHEMA VALIDATION!
```

## See Also

- **config.schema.json** - The JSON Schema definition
- **validate_schema.py** - Python validator script
- **V4_QUICK_REFERENCE.md** - Config structure reference
- **CONFIG_V4_CHANGES.md** - Migration guide from V3 to V4
