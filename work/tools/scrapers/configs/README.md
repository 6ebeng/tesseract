# Scraper Configuration Files

This directory contains all configuration files for the Kurdish news scraper.

## Directory Structure

```
configs/
├── websites/           # Active website configurations (14 configs)
│   ├── avanews.yaml
│   ├── awene.yaml
│   ├── balinde.yaml
│   ├── govkrd.yaml
│   ├── khak.yaml
│   ├── kurdistan24.yaml
│   ├── kurdsat.yaml
│   ├── lvinpress.yaml
│   ├── nrt.yaml
│   ├── rudaw.yaml
│   ├── sekokurd.yaml
│   ├── sharpress.yaml
│   ├── xendan.yaml
│   └── yariga.yaml
│
└── templates/          # Templates, examples, and presets (4 configs)
    ├── TEMPLATE.yaml            # Template for creating new configs
    ├── MINIMAL_EXAMPLE.yaml     # Minimal working example
    ├── INVALID_EXAMPLE.yaml     # Example of invalid config (for testing)
    └── url_filtering_presets.yaml  # URL filtering presets library

```

## Usage

The scraper automatically loads all `.yaml` files from the `websites/` subdirectory when pointed to the `configs/` directory:

```python
scraper = GenericScraper('configs/')  # Loads all configs from configs/websites/
```

## Adding New Websites

1. Copy `templates/TEMPLATE.yaml` to `websites/yoursite.yaml`
2. Edit the configuration following the template structure
3. Test with: `python3 test_suite.py yoursite --category <category_name>`

## Configuration Categories

### Website Configs (`websites/`)

- **Purpose**: Production-ready website scraper configurations
- **Loaded by**: GenericScraper automatically
- **Tested by**: test_suite.py

### Templates (`templates/`)

- **Purpose**: Reference files, examples, and shared presets
- **Not loaded by**: GenericScraper (excluded from loading)
- **Use for**: Creating new configs or reference

## File Naming Convention

- Website configs: `{website_name}.yaml` (lowercase, no spaces)
- Templates: `{PURPOSE}.yaml` or `{NAME}_EXAMPLE.yaml` (uppercase for visibility)
- The scraper uses the filename (without `.yaml`) as the website identifier

## Notes

- The scraper will skip `index.yaml` files automatically
- Templates and examples are kept separate to avoid confusion
- URL filtering presets are shared across all website configs
