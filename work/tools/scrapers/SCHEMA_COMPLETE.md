# JSON Schema Validation - Complete! ✅

## What We Built

Created a comprehensive **JSON Schema** system for validating website scraper configurations.

## Files Created

### 1. config.schema.json

Full JSON Schema definition with:

- Required fields validation
- Type checking (string, number, boolean, array, object)
- Enum constraints (pagination types)
- Format validation (URLs)
- Pattern matching (category names)
- Conditional requirements (type-specific fields)
- Forbidden fields detection (old V3 fields)

**Size:** 200+ lines of schema rules

### 2. validate_schema.py

Python validator using jsonschema library:

- Loads and validates all YAML configs
- Reports errors with clear messages
- Provides summary statistics
- Exit code for CI/CD integration

**Size:** 150+ lines

### 3. SCHEMA_VALIDATION.md

Comprehensive documentation:

- Usage instructions
- Schema rules explained
- Error examples
- CI/CD integration
- VS Code integration
- Extension guidelines

**Size:** 300+ lines

### 4. INVALID_EXAMPLE.yaml

Test file with intentional errors for demonstration

## Validation Results

### Current Status (All Valid Configs)

```
Total configs: 12
✅ Valid: 12/12 (100%)
❌ Errors: 0
⚠️  Warnings: 0

🎉 ALL CONFIGS PASS SCHEMA VALIDATION!
```

### Test with Invalid Config

```
❌ ERRORS: (12 errors caught)
   ❌ base_url: 'invalid-url' does not match '^https?://'
   ❌ enabled: 'yes' is not of type 'boolean'
   ❌ pagination.type: 'scroll' is not one of ['pagination', 'infinite_scroll', 'click_load_more']
   ❌ pagination.pages: 'five' is not of type 'integer'
   ❌ selectors: 'article_body' is a required property
   ❌ selectors.article_link: should not be valid (V3 field)
   ❌ selectors.article_content: should not be valid (V3 field)
   ❌ selectors.article_paragraphs: should not be valid (V3 field)
   ❌ wait: 'selector' is a required property
   ❌ wait: 'timeout' is a required property
   ❌ wait.type: should not be valid (V3 field)
   ❌ wait.seconds: should not be valid (V3 field)
```

## What the Schema Validates

### ✅ Required Fields

- `name`, `base_url`, `enabled`
- `pagination`, `selectors`, `wait`, `categories`

### ✅ Data Types

- Strings, numbers, booleans, arrays, objects
- URLs (must start with http:// or https://)
- Integers with minimum values

### ✅ Enums & Patterns

- `pagination.type`: Only valid types
- Category names: `lowercase_with_underscores`
- Language codes: 2-3 lowercase letters

### ✅ Conditional Requirements

- `pagination='pagination'` → requires `pages`
- `pagination='infinite_scroll'` → requires `scrolls`
- `pagination='click_load_more'` → requires `clicks` + `load_more_button`

### ✅ Forbidden Fields (V3 Removal)

- `selectors.article_link` ❌
- `selectors.article_content` ❌
- `selectors.article_paragraphs` ❌
- `wait.type` ❌
- `wait.seconds` ❌
- `category.enabled` ❌
- `category.type` ❌
- `category.pages` ❌
- `category.page_param` ❌

### ✅ Structure Validation

- Selectors must have fallback arrays
- Categories must have URL
- Pagination must have type-specific fields

## Benefits

1. **Early Error Detection** 🔍

   - Catch config errors before runtime
   - Clear error messages
   - Prevents deployment of invalid configs

2. **Enforces Standards** 📐

   - All configs follow same structure
   - Prevents V3 fields from creeping back in
   - Ensures type consistency

3. **Documentation** 📚

   - Schema documents valid structure
   - Self-documenting through constraints
   - Examples in documentation

4. **IDE Integration** 💡

   - VS Code auto-completion
   - Real-time validation
   - Hover documentation
   - Inline errors

5. **CI/CD Ready** 🚀

   - Exit codes for automation
   - Clear pass/fail results
   - Easy to integrate in pipelines

6. **Version Control** 🔄
   - Detects old V3 fields automatically
   - Enforces V4 structure
   - Future-proof for V5+

## Usage

### Validate All Configs

```bash
cd /mnt/c/tesseract/work/tools/scrapers
source venv/bin/activate
python validate_schema.py
```

### Validate Single Config

Edit `validate_schema.py` to filter specific files.

### CI/CD Integration

```bash
python validate_schema.py
exit_code=$?
if [ $exit_code -eq 0 ]; then
  echo "✅ All configs valid"
else
  echo "❌ Validation failed"
  exit 1
fi
```

### VS Code Integration

Add to `.vscode/settings.json`:

```json
{
	"yaml.schemas": {
		"./work/tools/scrapers/configs/config.schema.json": ["./work/tools/scrapers/configs/*.yaml"]
	}
}
```

## Schema Evolution

The schema can be extended for new features:

1. **Add new pagination type:**

   - Update enum in schema
   - Add conditional validation
   - Test with example

2. **Add new required field:**

   - Add to `required` array
   - Update documentation
   - Validate all existing configs

3. **Add new optional field:**
   - Add to `properties`
   - Add constraints if needed
   - Document usage

## Testing

### Valid Config Test

All 12 production configs pass:

- ✅ kurdsat, rudaw, govkrd
- ✅ sekokurd, sharpress, awene
- ✅ khak, xendan, lvinpress
- ✅ balinde, kurdistan24, nrt

### Invalid Config Test

`INVALID_EXAMPLE.yaml` catches 12 errors:

- URL format errors
- Type mismatches
- Invalid enum values
- Missing required fields
- Forbidden V3 fields

## Next Steps

1. ✅ Schema created (DONE)
2. ✅ Validator implemented (DONE)
3. ✅ All configs validated (12/12 pass)
4. ✅ Documentation complete (DONE)
5. ⏳ Add to CI/CD pipeline
6. ⏳ Configure VS Code integration
7. ⏳ Update generic_scraper.py to use validated structure

## Files Summary

| File                   | Purpose                | Status        |
| ---------------------- | ---------------------- | ------------- |
| `config.schema.json`   | JSON Schema definition | ✅ Complete   |
| `validate_schema.py`   | Python validator       | ✅ Complete   |
| `SCHEMA_VALIDATION.md` | Documentation          | ✅ Complete   |
| `INVALID_EXAMPLE.yaml` | Test invalid config    | ✅ Complete   |
| All 12 website configs | Production configs     | ✅ 100% valid |

---

**Date:** 2025-10-24  
**Schema Version:** V4.0  
**Validation Status:** ✅ 12/12 configs pass (100%)  
**Coverage:** All required fields, types, enums, conditionals, and forbidden fields
