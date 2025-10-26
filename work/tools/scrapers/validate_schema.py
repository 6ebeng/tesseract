#!/usr/bin/env python3
"""
JSON Schema Validator for Website Scraper Configs
Uses the config.schema.json to validate YAML config files
"""

import json
import yaml
from pathlib import Path
from jsonschema import validate, ValidationError, Draft7Validator
from jsonschema.exceptions import best_match

def load_schema():
    """Load the JSON schema"""
    schema_path = Path('configs/config.schema.json')
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_config(config_path):
    """Load a YAML config file"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def validate_config(config, schema):
    """
    Validate a config against the schema
    Returns: (is_valid, errors, warnings)
    """
    validator = Draft7Validator(schema)
    errors = []
    warnings = []
    
    # Collect all validation errors
    for error in validator.iter_errors(config):
        # Format error message
        path = '.'.join(str(p) for p in error.path) if error.path else 'root'
        
        # Check if it's a "not" schema (removed fields)
        if 'not' in str(error.schema_path):
            msg = f"❌ {path}: {error.message}"
            errors.append(msg)
        else:
            msg = f"❌ {path}: {error.message}"
            errors.append(msg)
    
    # Additional custom validations
    if 'pagination' in config:
        pag = config['pagination']
        pag_type = pag.get('type')
        
        # Check type-specific requirements
        if pag_type == 'pagination' and 'pages' not in pag:
            warnings.append("⚠️  pagination: type='pagination' but 'pages' not specified")
        elif pag_type == 'infinite_scroll' and 'scrolls' not in pag:
            warnings.append("⚠️  pagination: type='infinite_scroll' but 'scrolls' not specified")
        elif pag_type == 'click_load_more':
            if 'clicks' not in pag:
                warnings.append("⚠️  pagination: type='click_load_more' but 'clicks' not specified")
            if 'load_more_button' not in pag:
                warnings.append("⚠️  pagination: type='click_load_more' but 'load_more_button' not specified")
    
    is_valid = len(errors) == 0
    return is_valid, errors, warnings

def main():
    print("="*80)
    print("JSON SCHEMA VALIDATION - Config V4.0")
    print("="*80)
    
    # Load schema
    try:
        schema = load_schema()
        print(f"\n✅ Loaded schema: configs/config.schema.json")
        print(f"   Schema version: {schema.get('$id', 'unknown')}")
    except Exception as e:
        print(f"\n❌ Error loading schema: {e}")
        return
    
    # Find all config files
    configs_dir = Path('configs')
    config_files = list(configs_dir.glob('*.yaml'))
    
    # Exclude templates and examples
    test_files = [f for f in config_files if f.stem not in ['TEMPLATE', 'MINIMAL_EXAMPLE', 'websites_backup']]
    
    print(f"\n📁 Found {len(test_files)} configs to validate\n")
    
    # Validate each config
    results = {}
    
    for config_file in sorted(test_files):
        print(f"{'='*80}")
        print(f"Validating: {config_file.name}")
        print(f"{'='*80}")
        
        try:
            config = load_config(config_file)
            is_valid, errors, warnings = validate_config(config, schema)
            
            if errors:
                print("\n❌ ERRORS:")
                for error in errors:
                    print(f"   {error}")
            
            if warnings:
                print("\n⚠️  WARNINGS:")
                for warning in warnings:
                    print(f"   {warning}")
            
            if not errors and not warnings:
                print("\n✅ VALID - Passes all schema requirements!")
            
            results[config_file.name] = {
                'valid': is_valid,
                'errors': len(errors),
                'warnings': len(warnings)
            }
            
        except yaml.YAMLError as e:
            print(f"\n❌ YAML Parse Error: {e}")
            results[config_file.name] = {
                'valid': False,
                'errors': 1,
                'warnings': 0
            }
        except Exception as e:
            print(f"\n❌ Error: {e}")
            results[config_file.name] = {
                'valid': False,
                'errors': 1,
                'warnings': 0
            }
        
        print()
    
    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    
    total = len(results)
    valid = sum(1 for r in results.values() if r['valid'])
    total_errors = sum(r['errors'] for r in results.values())
    total_warnings = sum(r['warnings'] for r in results.values())
    
    print(f"\nTotal configs: {total}")
    print(f"✅ Valid: {valid}/{total} ({valid/total*100:.0f}%)")
    print(f"❌ Errors: {total_errors}")
    print(f"⚠️  Warnings: {total_warnings}")
    
    if valid == total and total_errors == 0:
        print("\n" + "="*80)
        print("🎉 ALL CONFIGS PASS SCHEMA VALIDATION!")
        print("="*80)
        return 0
    else:
        print("\n" + "="*80)
        print("⚠️  Some configs have validation issues")
        print("="*80)
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
