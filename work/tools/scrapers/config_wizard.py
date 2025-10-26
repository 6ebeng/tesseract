"""
Interactive Configuration Wizard for Web Scrapers

Helps users create YAML configurations through interactive prompts:
- Website setup wizard
- Automatic selector detection
- Validation and testing
- Template generation

Usage:
    python config_wizard.py
    python config_wizard.py --website kurdsat
    python config_wizard.py --auto https://example.com
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
import yaml
import json
from datetime import datetime

# Try to import selenium for auto-detection
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not available - auto-detection disabled")


class ConfigWizard:
    """Interactive configuration wizard"""
    
    def __init__(self):
        self.config = {}
        self.driver = None
    
    def run(self):
        """Run the full wizard"""
        print("=" * 70)
        print("🧙 Web Scraper Configuration Wizard")
        print("=" * 70)
        print()
        print("This wizard will help you create a configuration for a new website.")
        print("You can press Ctrl+C at any time to cancel.\n")
        
        try:
            # Step 1: Basic Information
            print("📝 Step 1: Basic Information\n")
            website_id = self._prompt("Website ID (lowercase, no spaces)", "kurdsat")
            name = self._prompt("Website Name", "Kurdsat")
            base_url = self._prompt("Base URL", "https://kurdsat.tv")
            
            self.config[website_id] = {
                'name': name,
                'base_url': base_url,
                'created': datetime.now().isoformat(),
                'selectors': {},
                'categories': {}
            }
            
            # Step 2: Auto-detection or Manual
            print("\n📡 Step 2: Selector Configuration\n")
            
            if SELENIUM_AVAILABLE:
                auto = self._prompt_bool("Attempt automatic selector detection?", True)
                
                if auto:
                    article_url = self._prompt(
                        "Enter a sample article list URL for detection",
                        f"{base_url}/news"
                    )
                    detected = self._auto_detect_selectors(article_url)
                    
                    if detected:
                        self.config[website_id]['selectors'] = detected
                        print("\n✅ Auto-detection completed!")
                    else:
                        print("\n⚠️  Auto-detection failed, falling back to manual entry")
                        self._manual_selectors(website_id)
                else:
                    self._manual_selectors(website_id)
            else:
                self._manual_selectors(website_id)
            
            # Step 3: Categories
            print("\n📂 Step 3: Categories\n")
            self._configure_categories(website_id)
            
            # Step 4: Advanced Options
            print("\n⚙️  Step 4: Advanced Options\n")
            self._configure_advanced(website_id)
            
            # Step 5: Review and Save
            print("\n📋 Step 5: Review Configuration\n")
            self._review_and_save(website_id)
            
            print("\n✅ Configuration wizard completed successfully!")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Wizard cancelled by user")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)
        finally:
            if self.driver:
                self.driver.quit()
    
    def _prompt(self, question: str, default: Optional[str] = None) -> str:
        """Prompt user for input"""
        if default:
            response = input(f"{question} [{default}]: ").strip()
            return response if response else default
        else:
            while True:
                response = input(f"{question}: ").strip()
                if response:
                    return response
                print("⚠️  This field is required")
    
    def _prompt_bool(self, question: str, default: bool = True) -> bool:
        """Prompt for yes/no"""
        default_str = 'Y/n' if default else 'y/N'
        response = input(f"{question} [{default_str}]: ").strip().lower()
        
        if not response:
            return default
        return response in ('y', 'yes', '1', 'true')
    
    def _prompt_list(self, question: str) -> List[str]:
        """Prompt for comma-separated list"""
        response = input(f"{question} (comma-separated): ").strip()
        if not response:
            return []
        return [item.strip() for item in response.split(',')]
    
    def _manual_selectors(self, website_id: str):
        """Manual selector entry"""
        print("Enter CSS selectors for key elements:")
        print("(Press Enter to skip optional selectors)\n")
        
        selectors = {}
        
        # Required selectors
        selectors['article_list'] = self._prompt(
            "Article list container selector",
            "div.post-card"
        )
        
        selectors['article_link'] = self._prompt(
            "Article link selector (within article_list)",
            "a"
        )
        
        selectors['article_title'] = self._prompt(
            "Article title selector",
            "h1.title"
        )
        
        # Optional selectors
        content_sel = self._prompt(
            "Article content selector (optional)",
            "div.content"
        )
        if content_sel:
            selectors['article_content'] = content_sel
        
        date_sel = self._prompt(
            "Article date selector (optional)",
            "time, .date"
        )
        if date_sel:
            selectors['article_date'] = date_sel
        
        self.config[website_id]['selectors'] = selectors
    
    def _auto_detect_selectors(self, url: str) -> Optional[Dict]:
        """
        Attempt to automatically detect selectors
        
        Returns:
            Detected selectors or None if failed
        """
        print(f"\n🔍 Analyzing {url}...")
        
        try:
            # Create driver
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            self.driver = webdriver.Chrome(options=options)
            
            # Load page
            self.driver.get(url)
            print("✅ Page loaded")
            
            # Wait for page to be ready
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            detected = {}
            
            # Try to find article lists
            print("\n🔍 Looking for article list containers...")
            article_containers = [
                ('article', 'article'),
                ('.article', 'div.article'),
                ('.post', 'div.post'),
                ('.news-item', 'div.news-item'),
                ('.post-card', 'div.post-card'),
            ]
            
            for name, selector in article_containers:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if len(elements) > 2:  # At least 3 articles
                    print(f"   ✅ Found {len(elements)} articles with: {selector}")
                    detected['article_list'] = selector
                    break
            
            if not detected.get('article_list'):
                print("   ❌ Could not detect article list")
                return None
            
            # Find links within first article
            print("\n🔍 Looking for article links...")
            first_article = self.driver.find_element(By.CSS_SELECTOR, detected['article_list'])
            links = first_article.find_elements(By.TAG_NAME, 'a')
            
            if links:
                print(f"   ✅ Found links: 'a'")
                detected['article_link'] = 'a'
            
            # Try to find title
            print("\n🔍 Looking for title selectors...")
            title_selectors = ['h1', 'h2', '.title', '.headline', '.post-title']
            
            for selector in title_selectors:
                if self.driver.find_elements(By.CSS_SELECTOR, selector):
                    print(f"   ✅ Found titles: {selector}")
                    detected['article_title'] = selector
                    break
            
            # Try to find content
            print("\n🔍 Looking for content selectors...")
            content_selectors = [
                '.content',
                '.article-content',
                '.post-content',
                'article p',
                '.entry-content'
            ]
            
            for selector in content_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"   ✅ Found content: {selector}")
                    detected['article_content'] = selector
                    break
            
            print("\n📊 Detection Summary:")
            for key, value in detected.items():
                print(f"   • {key}: {value}")
            
            # Ask user to confirm
            print()
            confirm = self._prompt_bool("Use these detected selectors?", True)
            
            if confirm:
                return detected
            else:
                print("Falling back to manual entry...")
                return None
            
        except Exception as e:
            print(f"❌ Auto-detection failed: {e}")
            return None
    
    def _configure_categories(self, website_id: str):
        """Configure categories"""
        add_categories = self._prompt_bool("Add category-specific configurations?", False)
        
        if not add_categories:
            print("Skipping category configuration")
            return
        
        categories = {}
        
        while True:
            cat_name = input("\nCategory name (or Enter to finish): ").strip()
            if not cat_name:
                break
            
            cat_url = self._prompt(f"URL for category '{cat_name}'")
            
            categories[cat_name] = {
                'url': cat_url,
                'enabled': True
            }
            
            # Optional: category-specific selectors
            override = self._prompt_bool(
                f"Override selectors for '{cat_name}'?",
                False
            )
            
            if override:
                print("Enter overridden selectors (press Enter to skip):")
                overrides = {}
                
                for key in ['article_list', 'article_link', 'article_title', 'article_content']:
                    value = input(f"  {key}: ").strip()
                    if value:
                        overrides[key] = value
                
                if overrides:
                    categories[cat_name]['selectors'] = overrides
        
        if categories:
            self.config[website_id]['categories'] = categories
            print(f"\n✅ Added {len(categories)} categories")
    
    def _configure_advanced(self, website_id: str):
        """Configure advanced options"""
        config_advanced = self._prompt_bool("Configure advanced options?", False)
        
        if not config_advanced:
            print("Using default advanced settings")
            return
        
        website = self.config[website_id]
        
        # Pagination
        print("\n📄 Pagination:")
        enable_pagination = self._prompt_bool("Enable pagination?", True)
        
        if enable_pagination:
            website['pagination'] = {
                'type': self._prompt("Pagination type (next_page/infinite_scroll)", "next_page"),
                'max_pages': int(self._prompt("Max pages to scrape", "5"))
            }
            
            if website['pagination']['type'] == 'next_page':
                website['pagination']['next_button'] = self._prompt(
                    "Next button selector",
                    "a.next"
                )
        
        # Wait strategy
        print("\n⏳ Wait Strategy:")
        configure_wait = self._prompt_bool("Configure wait strategy?", False)
        
        if configure_wait:
            website['wait'] = {
                'type': self._prompt("Wait type (selector/manual)", "selector"),
                'selector': self._prompt("Wait selector", "div.content"),
                'timeout': int(self._prompt("Timeout (seconds)", "10"))
            }
        
        # Language detection
        print("\n🌐 Multi-Language:")
        enable_lang = self._prompt_bool("Enable language detection?", False)
        
        if enable_lang:
            website['language_detection'] = {
                'enabled': True,
                'filter': self._prompt_list("Languages to keep (e.g., ckb, ar, en)")
            }
    
    def _review_and_save(self, website_id: str):
        """Review configuration and save"""
        print("=" * 70)
        print("Configuration Preview:")
        print("=" * 70)
        
        # Pretty print configuration
        config_yaml = yaml.dump(
            self.config,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False
        )
        print(config_yaml)
        
        # Confirm save
        save = self._prompt_bool("\nSave this configuration?", True)
        
        if not save:
            print("Configuration not saved")
            return
        
        # Ask for filename
        default_filename = f"{website_id}_config.yaml"
        filename = self._prompt("Output filename", default_filename)
        
        # Save to file
        output_path = Path(filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print(f"\n✅ Configuration saved to: {output_path.absolute()}")
        
        # Validation
        validate = self._prompt_bool("Validate configuration now?", True)
        
        if validate:
            self._validate_config(output_path)
    
    def _validate_config(self, config_path: Path):
        """Validate saved configuration"""
        print("\n🔍 Validating configuration...")
        
        try:
            # Try to import validator
            from config_validator import ConfigValidator
            
            validator = ConfigValidator()
            with open(config_path) as f:
                config = yaml.safe_load(f)
            
            # Basic validation
            errors = []
            for website_name, website_config in config.items():
                required = ['name', 'base_url', 'selectors']
                for field in required:
                    if field not in website_config:
                        errors.append(f"Missing required field: {field}")
            
            if errors:
                print("\n❌ Validation errors:")
                for error in errors:
                    print(f"   • {error}")
            else:
                print("\n✅ Configuration is valid!")
                
        except ImportError:
            print("⚠️  Validator not available, skipping validation")


def quick_start_template():
    """Generate a quick-start template"""
    template = {
        'example_website': {
            'name': 'Example Website',
            'base_url': 'https://example.com',
            'selectors': {
                'article_list': 'div.article',
                'article_link': 'a',
                'article_title': 'h1',
                'article_content': 'div.content',
                'article_date': 'time'
            },
            'categories': {
                'news': {
                    'url': 'https://example.com/news',
                    'enabled': True
                },
                'opinion': {
                    'url': 'https://example.com/opinion',
                    'enabled': True
                }
            },
            'pagination': {
                'type': 'next_page',
                'max_pages': 5,
                'next_button': 'a.next'
            },
            'wait': {
                'type': 'selector',
                'selector': 'div.content',
                'timeout': 10,
                'fallback': {
                    'type': 'manual',
                    'seconds': 3
                }
            }
        }
    }
    
    return yaml.dump(template, default_flow_style=False, allow_unicode=True, sort_keys=False)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Interactive Configuration Wizard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Run full interactive wizard
  python config_wizard.py
  
  # Generate quick-start template
  python config_wizard.py --template > websites_template.yaml
  
  # Auto-detect selectors from URL
  python config_wizard.py --auto https://example.com/news
        '''
    )
    
    parser.add_argument('--website', help='Website ID for quick setup')
    parser.add_argument('--auto', help='Auto-detect selectors from URL')
    parser.add_argument('--template', action='store_true', help='Generate quick-start template')
    
    args = parser.parse_args()
    
    if args.template:
        print(quick_start_template())
        return
    
    wizard = ConfigWizard()
    
    if args.auto:
        # Quick auto-detection mode
        print(f"🔍 Auto-detecting configuration for: {args.auto}\n")
        
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium not available. Please install: pip install selenium")
            sys.exit(1)
        
        detected = wizard._auto_detect_selectors(args.auto)
        
        if detected:
            print("\n✅ Auto-detection successful!")
            print("\nDetected configuration:")
            print(yaml.dump(detected, default_flow_style=False))
        else:
            print("\n❌ Auto-detection failed")
            print("Please run full wizard: python config_wizard.py")
    else:
        # Full interactive wizard
        wizard.run()


if __name__ == '__main__':
    main()
