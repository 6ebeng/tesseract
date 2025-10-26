#!/usr/bin/env python3
"""
Minimal pilot test for the new scraper system
Tests just the basic functionality without all advanced features
"""

import yaml
import sys
from pathlib import Path

print("=" * 60)
print("  Minimal Pilot Test - YAML Configuration")
print("=" * 60)
print()

# Test 1: Load YAML
print("[1/3] Loading websites.yaml...")
try:
    with open('websites.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    print(f"✅ YAML loaded successfully")
    print(f"   Websites found: {len(config)}")
    for name in config:
        if isinstance(config[name], dict):
            print(f"   - {name}: {config[name].get('name', 'N/A')}")
except Exception as e:
    print(f"❌ Error loading YAML: {e}")
    sys.exit(1)

print()

# Test 2: Validate structure
print("[2/3] Validating configuration structure...")
try:
    websites = config
    
    for name, site_config in websites.items():
        if not isinstance(site_config, dict):
            continue  # Skip non-website entries
        
        if site_config.get('enabled', True):
            # Check required fields
            assert 'name' in site_config, f"{name}: missing 'name'"
            assert 'base_url' in site_config, f"{name}: missing 'base_url'"
            assert 'categories' in site_config, f"{name}: missing 'categories'"
            
            # Check categories
            for cat_name, cat_config in site_config['categories'].items():
                assert 'url' in cat_config, f"{name}.{cat_name}: missing 'url'"
                assert 'type' in cat_config, f"{name}.{cat_name}: missing 'type'"
            
            print(f"✅ {name}: {len(site_config['categories'])} categories")
    
except AssertionError as e:
    print(f"❌ Validation error: {e}")
    sys.exit(1)

print()

# Test 3: Check Python environment
print("[3/3] Checking Python environment...")
try:
    import selenium
    print(f"✅ Selenium: {selenium.__version__}")
except ImportError:
    print("❌ Selenium not installed")
    sys.exit(1)

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    print("✅ Selenium WebDriver imports OK")
except ImportError as e:
    print(f"❌ Selenium import error: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("✅ All basic tests passed!")
print("=" * 60)
print()
print("Next step: Run full pilot migration with:")
print("  wsl -d Ubuntu -- bash -lc 'cd /mnt/c/tesseract/work/tools/scrapers && source venv/bin/activate && ./migrate_pilot.sh'")
print()
