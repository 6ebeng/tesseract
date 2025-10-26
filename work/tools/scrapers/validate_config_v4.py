#!/usr/bin/env python3
"""
Test new config structure (V4.0)
Tests the simplified pagination/selectors/wait structure
"""

import yaml
from pathlib import Path

print("="*80)
print("CONFIG STRUCTURE V4.0 VALIDATION")
print("="*80)

configs_dir = Path('configs')
config_files = list(configs_dir.glob('*.yaml'))

# Exclude templates and examples
test_files = [f for f in config_files if f.stem not in ['TEMPLATE', 'MINIMAL_EXAMPLE', 'websites_backup']]

print(f"\nFound {len(test_files)} website configs to validate\n")

validation_results = {}

for config_file in sorted(test_files):
    print(f"{'='*80}")
    print(f"Validating: {config_file.name}")
    print(f"{'='*80}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        errors = []
        warnings = []
        
        # Check required top-level keys
        required_keys = ['name', 'base_url', 'enabled', 'pagination', 'selectors', 'wait', 'categories']
        for key in required_keys:
            if key not in config:
                errors.append(f"Missing required key: {key}")
        
        # Check pagination structure
        if 'pagination' in config:
            pag = config['pagination']
            if 'type' not in pag:
                errors.append("pagination: missing 'type'")
            if 'delay' not in pag:
                warnings.append("pagination: missing 'delay' (will use default)")
            
            # Check type-specific requirements
            if pag.get('type') == 'pagination' and 'pages' not in pag:
                warnings.append("pagination: type=pagination but no 'pages' specified")
            elif pag.get('type') == 'infinite_scroll' and 'scrolls' not in pag:
                warnings.append("pagination: type=infinite_scroll but no 'scrolls' specified")
            elif pag.get('type') == 'click_load_more' and 'clicks' not in pag:
                warnings.append("pagination: type=click_load_more but no 'clicks' specified")
        
        # Check selectors structure
        if 'selectors' in config:
            sel = config['selectors']
            
            # Check for old structure
            if 'article_link' in sel:
                errors.append("selectors: Has 'article_link' (should be removed in V4)")
            if 'article_content' in sel:
                errors.append("selectors: Has 'article_content' (should merge to 'article_body')")
            if 'article_paragraphs' in sel:
                errors.append("selectors: Has 'article_paragraphs' (should merge to 'article_body')")
            
            # Check for new structure
            if 'article_list' not in sel:
                errors.append("selectors: Missing 'article_list'")
            if 'article_body' not in sel:
                errors.append("selectors: Missing 'article_body' (should be merged from content+paragraphs)")
            if 'article_title' not in sel:
                warnings.append("selectors: Missing 'article_title'")
        
        # Check wait structure
        if 'wait' in config:
            wait = config['wait']
            
            # Check for old structure
            if 'type' in wait:
                errors.append("wait: Has 'type' (should use 'selector' in V4)")
            if 'seconds' in wait:
                errors.append("wait: Has 'seconds' (should use 'timeout' in V4)")
            
            # Check for new structure
            if 'selector' not in wait:
                errors.append("wait: Missing 'selector'")
            if 'timeout' not in wait:
                warnings.append("wait: Missing 'timeout'")
        
        # Check categories
        if 'categories' in config:
            cats = config['categories']
            
            for cat_name, cat_config in cats.items():
                # Check for old per-category settings
                if 'enabled' in cat_config:
                    warnings.append(f"category '{cat_name}': Has 'enabled' (implicit in V4)")
                if 'type' in cat_config:
                    warnings.append(f"category '{cat_name}': Has 'type' (should override in 'pagination')")
                if 'pages' in cat_config:
                    warnings.append(f"category '{cat_name}': Has 'pages' (should override in 'pagination')")
                if 'page_param' in cat_config:
                    warnings.append(f"category '{cat_name}': Has 'page_param' (not needed in V4)")
                
                # Check required
                if 'url' not in cat_config:
                    errors.append(f"category '{cat_name}': Missing 'url'")
        
        # Print results
        if errors:
            print("❌ ERRORS:")
            for err in errors:
                print(f"   - {err}")
        
        if warnings:
            print("⚠️  WARNINGS:")
            for warn in warnings:
                print(f"   - {warn}")
        
        if not errors and not warnings:
            print("✅ VALID - Perfect V4 structure!")
        
        validation_results[config_file.name] = {
            'errors': len(errors),
            'warnings': len(warnings),
            'valid': len(errors) == 0
        }
    
    except Exception as e:
        print(f"❌ ERROR loading config: {e}")
        validation_results[config_file.name] = {
            'errors': 1,
            'warnings': 0,
            'valid': False
        }
    
    print()

# Summary
print("="*80)
print("SUMMARY")
print("="*80)

total = len(validation_results)
valid = sum(1 for r in validation_results.values() if r['valid'])
total_errors = sum(r['errors'] for r in validation_results.values())
total_warnings = sum(r['warnings'] for r in validation_results.values())

print(f"\nTotal configs: {total}")
print(f"✅ Valid: {valid}/{total} ({valid/total*100:.0f}%)")
print(f"❌ Errors: {total_errors}")
print(f"⚠️  Warnings: {total_warnings}")

print("\n" + "="*80)
if valid == total and total_errors == 0:
    print("🎉 ALL CONFIGS UPDATED TO V4 STRUCTURE!")
else:
    print("⚠️  Some configs need fixes")
print("="*80)
