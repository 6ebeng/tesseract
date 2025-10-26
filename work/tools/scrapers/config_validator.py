"""
Configuration Validator for Scraper YAML Configs

Validates websites.yaml against JSON schema to catch errors early.
Provides clear, actionable error messages for misconfigurations.

Usage:
    # In code
    from config_validator import validate_config_file, ConfigValidator
    
    if not validate_config_file('websites.yaml'):
        sys.exit(1)
    
    # CLI
    python config_validator.py config/websites.yaml
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
import re


class ConfigValidator:
    """Validates scraper configuration files"""
    
    # Valid pagination types
    VALID_PAGINATION_TYPES = ['pagination', 'scroll', 'infinite_scroll', 'load_more', 'numbered_pages']
    
    # Valid wait conditions
    VALID_WAIT_CONDITIONS = ['visible', 'invisible', 'present', 'clickable', 'count', 'text_present']
    
    # Valid selector types
    VALID_SELECTOR_TYPES = ['css', 'xpath']
    
    # Required fields per level
    REQUIRED_WEBSITE_FIELDS = ['name', 'base_url', 'categories']
    REQUIRED_CATEGORY_FIELDS = ['url', 'type']
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_config(self, config: Dict) -> Tuple[bool, List[str], List[str]]:
        """
        Validate entire configuration dictionary
        
        Returns:
            (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        if not isinstance(config, dict):
            self.errors.append("Config must be a dictionary")
            return False, self.errors, self.warnings
        
        # Validate each website
        for website_key, website_config in config.items():
            self._validate_website(website_key, website_config)
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def _validate_website(self, key: str, config: Dict):
        """Validate website-level configuration"""
        prefix = f"[{key}]"
        
        if not isinstance(config, dict):
            self.errors.append(f"{prefix} Website config must be a dictionary")
            return
        
        # Check required fields
        for field in self.REQUIRED_WEBSITE_FIELDS:
            if field not in config:
                self.errors.append(f"{prefix} Missing required field: '{field}'")
        
        # Validate name
        if 'name' in config:
            if not isinstance(config['name'], str) or not config['name'].strip():
                self.errors.append(f"{prefix} 'name' must be a non-empty string")
        
        # Validate base_url
        if 'base_url' in config:
            if not self._is_valid_url(config['base_url']):
                self.errors.append(f"{prefix} 'base_url' must be a valid URL starting with http:// or https://")
        
        # Validate enabled flag
        if 'enabled' in config and not isinstance(config['enabled'], bool):
            self.errors.append(f"{prefix} 'enabled' must be boolean (true/false)")
        
        # Validate scraper_class
        if 'scraper_class' in config:
            if not isinstance(config['scraper_class'], str):
                self.errors.append(f"{prefix} 'scraper_class' must be a string")
            elif not config['scraper_class'].strip():
                self.errors.append(f"{prefix} 'scraper_class' cannot be empty")
        
        # Validate wait_times
        if 'wait_times' in config:
            self._validate_wait_times(f"{prefix}.wait_times", config['wait_times'])
        
        # Validate selectors
        if 'selectors' in config:
            self._validate_selectors(f"{prefix}.selectors", config['selectors'])
        
        # Validate categories
        if 'categories' in config:
            if not isinstance(config['categories'], dict):
                self.errors.append(f"{prefix} 'categories' must be a dictionary")
            elif len(config['categories']) == 0:
                self.warnings.append(f"{prefix} No categories defined")
            else:
                for cat_key, cat_config in config['categories'].items():
                    self._validate_category(f"{prefix}.{cat_key}", cat_config)
    
    def _validate_category(self, prefix: str, config: Dict):
        """Validate category-level configuration"""
        
        if not isinstance(config, dict):
            self.errors.append(f"{prefix} Category config must be a dictionary")
            return
        
        # Check required fields
        for field in self.REQUIRED_CATEGORY_FIELDS:
            if field not in config:
                self.errors.append(f"{prefix} Missing required field: '{field}'")
        
        # Validate URL
        if 'url' in config:
            if not self._is_valid_url(config['url']):
                self.errors.append(f"{prefix} 'url' must be a valid URL")
        
        # Validate type
        if 'type' in config:
            if config['type'] not in self.VALID_PAGINATION_TYPES:
                self.errors.append(
                    f"{prefix} 'type' must be one of: {', '.join(self.VALID_PAGINATION_TYPES)}"
                )
        
        # Validate enabled flag
        if 'enabled' in config and not isinstance(config['enabled'], bool):
            self.errors.append(f"{prefix} 'enabled' must be boolean (true/false)")
        
        # Validate pagination-specific fields
        pagination_type = config.get('type')
        
        if pagination_type == 'pagination':
            if 'pages' in config:
                if not isinstance(config['pages'], int) or config['pages'] < 1:
                    self.errors.append(f"{prefix} 'pages' must be a positive integer")
        
        elif pagination_type in ['scroll', 'infinite_scroll']:
            if 'scrolls' in config:
                if not isinstance(config['scrolls'], int) or config['scrolls'] < 1:
                    self.errors.append(f"{prefix} 'scrolls' must be a positive integer")
        
        elif pagination_type == 'load_more':
            if 'clicks' in config:
                if not isinstance(config['clicks'], int) or config['clicks'] < 1:
                    self.errors.append(f"{prefix} 'clicks' must be a positive integer")
        
        # Validate wait_times
        if 'wait_times' in config:
            self._validate_wait_times(f"{prefix}.wait_times", config['wait_times'])
        
        # Validate wait_for
        if 'wait_for' in config:
            self._validate_wait_for(f"{prefix}.wait_for", config['wait_for'])
        
        # Validate selectors
        if 'selectors' in config:
            self._validate_selectors(f"{prefix}.selectors", config['selectors'])
    
    def _validate_wait_times(self, prefix: str, config: Dict):
        """Validate wait_times configuration"""
        
        if not isinstance(config, dict):
            self.errors.append(f"{prefix} must be a dictionary")
            return
        
        # Known wait time fields
        wait_fields = ['page_load', 'after_scroll', 'after_click', 'element_timeout', 'between_articles']
        
        for field, value in config.items():
            field_prefix = f"{prefix}.{field}"
            
            # Warn about unknown fields
            if field not in wait_fields:
                self.warnings.append(f"{field_prefix} Unknown wait_time field (typo?)")
            
            # Validate type and range
            if not isinstance(value, (int, float)):
                self.errors.append(f"{field_prefix} must be a number")
            elif value < 0:
                self.errors.append(f"{field_prefix} cannot be negative")
            elif value > 120:
                self.warnings.append(f"{field_prefix} Very long wait time ({value}s) - intentional?")
    
    def _validate_wait_for(self, prefix: str, config):
        """Validate wait_for configuration"""
        
        # Can be single dict or list of dicts
        configs = config if isinstance(config, list) else [config]
        
        for idx, wait_config in enumerate(configs):
            if isinstance(config, list):
                item_prefix = f"{prefix}[{idx}]"
            else:
                item_prefix = prefix
            
            if not isinstance(wait_config, dict):
                self.errors.append(f"{item_prefix} must be a dictionary")
                continue
            
            # Validate element selector
            if 'element' not in wait_config:
                self.errors.append(f"{item_prefix} Missing required field: 'element'")
            else:
                self._validate_selector_config(f"{item_prefix}.element", wait_config['element'])
            
            # Validate condition
            if 'condition' in wait_config:
                condition = wait_config['condition']
                if condition not in self.VALID_WAIT_CONDITIONS:
                    self.errors.append(
                        f"{item_prefix}.condition Invalid: '{condition}'. "
                        f"Must be one of: {', '.join(self.VALID_WAIT_CONDITIONS)}"
                    )
                
                # If condition is 'count', require 'count' field
                if condition == 'count' and 'count' not in wait_config:
                    self.errors.append(f"{item_prefix} condition='count' requires 'count' field")
            
            # Validate count (if present)
            if 'count' in wait_config:
                count = wait_config['count']
                if not isinstance(count, int) or count < 1:
                    self.errors.append(f"{item_prefix}.count must be a positive integer")
            
            # Validate timeout
            if 'timeout' in wait_config:
                timeout = wait_config['timeout']
                if not isinstance(timeout, (int, float)):
                    self.errors.append(f"{item_prefix}.timeout must be a number")
                elif timeout <= 0:
                    self.errors.append(f"{item_prefix}.timeout must be positive")
                elif timeout > 120:
                    self.warnings.append(f"{item_prefix}.timeout Very long ({timeout}s)")
            
            # Validate fallback_wait
            if 'fallback_wait' in wait_config:
                fallback = wait_config['fallback_wait']
                if not isinstance(fallback, (int, float)):
                    self.errors.append(f"{item_prefix}.fallback_wait must be a number")
                elif fallback < 0:
                    self.errors.append(f"{item_prefix}.fallback_wait cannot be negative")
    
    def _validate_selectors(self, prefix: str, config: Dict):
        """Validate selectors configuration"""
        
        if not isinstance(config, dict):
            self.errors.append(f"{prefix} must be a dictionary")
            return
        
        for selector_name, selector_config in config.items():
            self._validate_selector_config(f"{prefix}.{selector_name}", selector_config)
    
    def _validate_selector_config(self, prefix: str, config):
        """Validate individual selector configuration"""
        
        # String shorthand (CSS selector)
        if isinstance(config, str):
            if not config.strip():
                self.errors.append(f"{prefix} Selector string cannot be empty")
            return
        
        # List of selectors (fallback chain)
        if isinstance(config, list):
            if len(config) == 0:
                self.errors.append(f"{prefix} Selector list cannot be empty")
            else:
                for idx, item in enumerate(config):
                    self._validate_selector_config(f"{prefix}[{idx}]", item)
            return
        
        # Dictionary (explicit type + options)
        if isinstance(config, dict):
            # Validate type
            if 'type' in config:
                selector_type = config['type']
                if selector_type not in self.VALID_SELECTOR_TYPES:
                    self.errors.append(
                        f"{prefix}.type Invalid: '{selector_type}'. "
                        f"Must be 'css' or 'xpath'"
                    )
            
            # Validate value
            if 'value' not in config:
                self.errors.append(f"{prefix} Missing required field: 'value'")
            elif not isinstance(config['value'], str):
                self.errors.append(f"{prefix}.value must be a string")
            elif not config['value'].strip():
                self.errors.append(f"{prefix}.value cannot be empty")
            
            # Validate multiple (for XPath multi-node extraction)
            if 'multiple' in config:
                if not isinstance(config['multiple'], bool):
                    self.errors.append(f"{prefix}.multiple must be boolean (true/false)")
            
            # Validate join (for multi-node extraction)
            if 'join' in config:
                if not isinstance(config['join'], str):
                    self.errors.append(f"{prefix}.join must be a string")
                
                # Warn if join used without multiple
                if not config.get('multiple', False):
                    self.warnings.append(
                        f"{prefix}.join specified but 'multiple: true' not set - "
                        "join will have no effect"
                    )
            
            return
        
        # Invalid type
        self.errors.append(f"{prefix} Selector must be string, list, or dictionary")
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        if not isinstance(url, str):
            return False
        url = url.strip()
        return url.startswith('http://') or url.startswith('https://')


def validate_config_file(yaml_path: str, verbose: bool = True) -> bool:
    """
    Validate YAML config file against schema
    
    Args:
        yaml_path: Path to YAML config file
        verbose: Print detailed error messages
    
    Returns:
        True if valid, False otherwise
    """
    yaml_path = Path(yaml_path)
    
    if not yaml_path.exists():
        if verbose:
            print(f"❌ ERROR: File not found: {yaml_path}")
        return False
    
    try:
        # Load YAML (safely)
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        if verbose:
            print(f"❌ YAML Parse Error: {yaml_path}")
            print(f"   {str(e)}")
        return False
    except Exception as e:
        if verbose:
            print(f"❌ Error reading file: {yaml_path}")
            print(f"   {str(e)}")
        return False
    
    # Validate configuration
    validator = ConfigValidator()
    is_valid, errors, warnings = validator.validate_config(config)
    
    if verbose:
        if is_valid:
            print(f"✅ {yaml_path.name} is VALID")
            if warnings:
                print(f"\n⚠️  {len(warnings)} Warning(s):")
                for warning in warnings:
                    print(f"   • {warning}")
        else:
            print(f"❌ {yaml_path.name} is INVALID")
            print(f"\n🚫 {len(errors)} Error(s):")
            for error in errors:
                print(f"   • {error}")
            
            if warnings:
                print(f"\n⚠️  {len(warnings)} Warning(s):")
                for warning in warnings:
                    print(f"   • {warning}")
    
    return is_valid


def validate_directory(config_dir: str, pattern: str = '*.yaml') -> Tuple[int, int]:
    """
    Validate all YAML files in directory
    
    Returns:
        (valid_count, total_count)
    """
    config_dir = Path(config_dir)
    
    if not config_dir.exists():
        print(f"❌ Directory not found: {config_dir}")
        return 0, 0
    
    yaml_files = list(config_dir.glob(pattern))
    
    if not yaml_files:
        print(f"⚠️  No YAML files found in: {config_dir}")
        return 0, 0
    
    print(f"🔍 Validating {len(yaml_files)} file(s) in {config_dir}\n")
    
    valid_count = 0
    for yaml_file in yaml_files:
        if validate_config_file(yaml_file, verbose=True):
            valid_count += 1
        print()  # Blank line between files
    
    print("=" * 60)
    print(f"✅ Valid: {valid_count}/{len(yaml_files)}")
    if valid_count < len(yaml_files):
        print(f"❌ Invalid: {len(yaml_files) - valid_count}/{len(yaml_files)}")
    
    return valid_count, len(yaml_files)


def main():
    """CLI interface for config validation"""
    if len(sys.argv) < 2:
        print("Usage: python config_validator.py <config_file.yaml>")
        print("   or: python config_validator.py <config_dir> --all")
        sys.exit(1)
    
    path = sys.argv[1]
    path_obj = Path(path)
    
    if '--all' in sys.argv or path_obj.is_dir():
        # Validate directory
        valid, total = validate_directory(path)
        sys.exit(0 if valid == total else 1)
    else:
        # Validate single file
        is_valid = validate_config_file(path, verbose=True)
        sys.exit(0 if is_valid else 1)


if __name__ == '__main__':
    main()
