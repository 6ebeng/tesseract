# 🛡️ Config Validation Setup Guide

Complete guide to setting up all validation layers for scraper configurations.

## 📋 Table of Contents

1. [Python Validator Setup](#python-validator-setup)
2. [VS Code Integration](#vs-code-integration)
3. [GitHub Actions CI/CD](#github-actions-cicd)
4. [Pre-commit Hooks](#pre-commit-hooks)
5. [Command Reference](#command-reference)

---

## 🐍 Python Validator Setup

### Install Dependencies

```bash
# In WSL Ubuntu
cd /mnt/c/tesseract/work/tools/scrapers
pip install pyyaml jsonschema
```

### Run Validation

```bash
# Validate all configs
python validate_schema.py

# Validate specific configs
python validate_schema.py configs/kurdsat.yaml configs/rudaw.yaml

# Check exit code (for scripts)
python validate_schema.py && echo "All valid!" || echo "Errors found!"
```

### Expected Output

```
🔍 Validating scraper configurations...

Checking configs/kurdsat.yaml... ✅
Checking configs/rudaw.yaml... ✅
Checking configs/govkrd.yaml... ✅
...

Total configs: 12
✅ Valid: 12/12 (100%)
❌ Errors: 0
⚠️  Warnings: 0

🎉 ALL CONFIGS PASS SCHEMA VALIDATION!
```

---

## 🎨 VS Code Integration

### Enable Real-time Validation

1. **Install Extension**

   - Open VS Code
   - Install: "YAML" by Red Hat (`redhat.vscode-yaml`)

2. **Configure Workspace Settings**
   - Create/edit `.vscode/settings.json`:

```json
{
	"yaml.schemas": {
		"./work/tools/scrapers/configs/config.schema.json": ["./work/tools/scrapers/configs/*.yaml"]
	},
	"yaml.validate": true,
	"yaml.completion": true,
	"yaml.hover": true,
	"yaml.format.enable": true
}
```

3. **Verify It Works**
   - Open any config file in `configs/`
   - You should see:
     - ✅ Green checkmarks for valid fields
     - ❌ Red squiggles for errors
     - 💡 Auto-completion when typing
     - 📖 Hover docs on field names

### Features You Get

- **Real-time Validation**: Errors show as you type
- **Auto-completion**: Press `Ctrl+Space` for field suggestions
- **Hover Documentation**: Hover over fields to see descriptions
- **Format on Save**: Auto-format YAML files

---

## 🚀 GitHub Actions CI/CD

### Setup GitHub Actions

1. **Create Workflow Directory**

```bash
mkdir -p .github/workflows
```

2. **Copy Workflow File**

```bash
cp work/tools/scrapers/github-actions-workflow.yml .github/workflows/validate-scraper-configs.yml
```

3. **Commit and Push**

```bash
git add .github/workflows/validate-scraper-configs.yml
git commit -m "Add scraper config validation workflow"
git push
```

### What It Does

The workflow runs **3 jobs** on every push/PR:

#### Job 1: Schema Validation

- Validates all configs against `config.schema.json`
- Uses Python `validate_schema.py` script
- Fails if any config has errors

#### Job 2: Legacy Field Check

- Searches for removed V3 fields:
  - `article_link`
  - `article_content`
  - `article_paragraphs`
  - `wait.type` / `wait.seconds`
- Fails if any legacy fields found

#### Job 3: Structure Check

- Verifies all configs have required sections:
  - `pagination`
  - `selectors`
  - `wait`
  - `categories`
- Fails if any section missing

### Triggering the Workflow

Workflow triggers automatically when:

- You push changes to `configs/*.yaml`
- You push changes to `config.schema.json`
- You push changes to `validate_schema.py`
- You create a PR with config changes

### View Results

1. Go to GitHub repository
2. Click **Actions** tab
3. See workflow runs:
   - ✅ Green checkmark = All passed
   - ❌ Red X = Validation failed

---

## 🪝 Pre-commit Hooks

### Install pre-commit

```bash
# In WSL Ubuntu
pip install pre-commit
```

### Create `.pre-commit-config.yaml`

Create file in repo root:

```yaml
repos:
  - repo: local
    hooks:
      - id: validate-scraper-configs
        name: Validate Scraper Configs
        entry: python work/tools/scrapers/validate_schema.py
        language: system
        files: 'work/tools/scrapers/configs/.*\.yaml$'
        pass_filenames: false

      - id: check-legacy-fields
        name: Check for Legacy V3 Fields
        entry: bash -c 'grep -r "article_link:\|article_content:\|article_paragraphs:" work/tools/scrapers/configs/*.yaml --exclude="INVALID_EXAMPLE.yaml" && exit 1 || exit 0'
        language: system
        files: 'work/tools/scrapers/configs/.*\.yaml$'
        pass_filenames: false

      - id: yaml-lint
        name: YAML Lint
        entry: yamllint
        language: system
        types: [yaml]
        files: 'work/tools/scrapers/configs/.*\.yaml$'
```

### Install Hooks

```bash
# In repo root
pre-commit install
```

### Test Hooks

```bash
# Test on all files
pre-commit run --all-files

# Test on staged files only
pre-commit run
```

### What Happens

Now every time you `git commit`:

1. ✅ Validates all configs against schema
2. ✅ Checks for legacy V3 fields
3. ✅ Lints YAML syntax
4. ❌ Blocks commit if validation fails

---

## 📚 Command Reference

### Quick Commands

```bash
# Validate all configs
python validate_schema.py

# Validate and show details
python validate_schema.py --verbose

# Validate specific files
python validate_schema.py configs/kurdsat.yaml configs/rudaw.yaml

# Check for legacy fields
grep -r "article_link:\|article_content:" configs/*.yaml

# Format all YAML files
find configs -name "*.yaml" -exec yamllint {} \;

# Count valid configs
python validate_schema.py | grep "Valid:"
```

### Integration with Scripts

```bash
#!/bin/bash
# Example: Validate before running scrapers

echo "🔍 Validating configs..."
cd work/tools/scrapers

if python validate_schema.py; then
    echo "✅ Configs valid, starting scrapers..."
    python generic_scraper.py --config configs/kurdsat.yaml
else
    echo "❌ Config validation failed, aborting!"
    exit 1
fi
```

---

## 🎯 Validation Layers Summary

| Layer                     | Tool                 | When              | Coverage                                    |
| ------------------------- | -------------------- | ----------------- | ------------------------------------------- |
| **1. Schema Validation**  | `validate_schema.py` | Pre-commit, CI/CD | Required fields, types, enums, conditionals |
| **2. Legacy Field Check** | `grep` search        | CI/CD             | Removed V3 fields                           |
| **3. Structure Check**    | Custom script        | CI/CD             | Required sections present                   |
| **4. Real-time IDE**      | VS Code YAML         | As you type       | Syntax, schema, auto-complete               |
| **5. Manual Test**        | Python validator     | Before deploy     | Final verification                          |

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Python validator runs successfully: `python validate_schema.py`
- [ ] VS Code shows real-time validation (open any config file)
- [ ] GitHub Actions workflow runs on push (check Actions tab)
- [ ] Pre-commit hooks block invalid commits (test with intentional error)
- [ ] All 12 configs pass validation (100%)

---

## 🆘 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'jsonschema'"

```bash
pip install jsonschema pyyaml
```

### Error: "No such file or directory: config.schema.json"

```bash
# Make sure you're in the scrapers directory
cd work/tools/scrapers
python validate_schema.py
```

### VS Code not showing validation

1. Install "YAML" extension by Red Hat
2. Reload VS Code window: `Ctrl+Shift+P` → "Reload Window"
3. Check `.vscode/settings.json` exists and has correct schema path

### GitHub Actions failing

1. Check workflow file is in `.github/workflows/`
2. Verify Python version matches (3.12)
3. Check file paths are correct for your repo structure

---

## 📖 Related Documentation

- **[SCHEMA_VALIDATION.md](SCHEMA_VALIDATION.md)** - Complete schema documentation
- **[SCHEMA_COMPLETE.md](SCHEMA_COMPLETE.md)** - System summary and results
- **[CONFIG_V4_CHANGES.md](CONFIG_V4_CHANGES.md)** - V4.0 migration guide
- **[LEGACY_SELECTORS_REFERENCE.md](LEGACY_SELECTORS_REFERENCE.md)** - Proven selectors from legacy scrapers

---

## 🎉 Quick Start (TL;DR)

```bash
# 1. Install dependencies
pip install pyyaml jsonschema pre-commit

# 2. Run validation
cd work/tools/scrapers
python validate_schema.py

# 3. Setup VS Code (one-time)
# Install "YAML" extension by Red Hat
# Add schema path to .vscode/settings.json

# 4. Setup GitHub Actions (one-time)
cp github-actions-workflow.yml .github/workflows/validate-scraper-configs.yml
git add .github/workflows/validate-scraper-configs.yml
git commit -m "Add config validation"
git push

# 5. Setup pre-commit hooks (one-time)
pre-commit install

# Done! Now you have 4 layers of validation 🛡️
```

---

**Last Updated**: 2025-01-XX  
**Schema Version**: V4.0  
**Python**: 3.12+  
**Status**: ✅ All 12 configs validated (100%)
