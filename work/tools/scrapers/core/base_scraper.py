"""
Base Scraper - Core functionality

Contains essential scraping logic without specific concerns like
pagination, extraction, or URL filtering.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseScraper:
    """
    Base scraper with core configuration and lifecycle management
    
    Responsibilities:
    - Configuration loading
    - Driver lifecycle management
    - Website/category configuration merging
    - Monitoring integration
    """
    
    def __init__(self, config_path: str = 'websites.yaml'):
        """
        Initialize base scraper
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.name = "Generic"
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # Runtime state
        self.current_website = None
        self.driver = None
        self.flaresolverr_session = None
        
        # Tracking
        self.scraped_article_links = set()
        self._scraped_articles_loaded = False
    
    def _load_config(self) -> Dict:
        """
        Load configuration from YAML file
        
        Supports both single file and directory structure:
        - websites.yaml (single file with all configs)
        - configs/ or configs/websites/ (one file per website)
        
        Returns:
            Dict mapping website names to configurations
        """
        # Check if config_path itself is a directory
        if self.config_path.is_dir():
            logger.info(f"Loading from directory: {self.config_path}")
            
            # Check for websites subdirectory
            websites_dir = self.config_path / 'websites'
            if websites_dir.exists() and websites_dir.is_dir():
                logger.info(f"  Using websites subdirectory: {websites_dir}")
                return self._load_from_directory(websites_dir)
            else:
                return self._load_from_directory(self.config_path)
        
        # Load single file
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary")
        
        logger.info(f"✅ Loaded {len(config)} websites from {self.config_path}")
        return config
    
    def _load_from_directory(self, directory: Path) -> Dict:
        """
        Load configurations from directory of YAML files
        
        Args:
            directory: Path to directory containing config files
        
        Returns:
            Dict mapping website names to configurations
        """
        config = {}
        yaml_files = list(directory.glob('*.yaml'))
        
        for yaml_file in yaml_files:
            # Skip template and example files
            if any(skip in yaml_file.name.lower() 
                   for skip in ['template', 'example', 'preset']):
                continue
            
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    website_config = yaml.safe_load(f)
                
                if not isinstance(website_config, dict):
                    logger.warning(f"Skipping {yaml_file.name}: not a dict")
                    continue
                
                # Use filename (without .yaml) as website key
                website_name = yaml_file.stem
                config[website_name] = website_config
                
            except Exception as e:
                logger.error(f"Failed to load {yaml_file.name}: {e}")
        
        logger.info(f"✅ Loaded {len(config)} websites from {len(yaml_files)} files")
        return config
    
    def _apply_defaults(self, website_config: Dict, category_config: Dict) -> Dict:
        """
        Apply intelligent defaults with fallback chain (V4.0):
        Category-specific > Website defaults > Hard-coded defaults
        
        V4.0 Structure:
        - Website has pagination{} at top level
        - Categories can override with pagination{}
        - Selectors at website level, categories can override
        
        Returns merged configuration with all defaults applied
        """
        merged = {}
        
        # Get default configurations (V4.0)
        website_pagination = website_config.get('pagination', {})
        website_selectors = website_config.get('selectors', {})
        website_wait = website_config.get('wait', {})
        
        # Get category overrides (V4.0)
        category_pagination = category_config.get('pagination', {})
        category_selectors = category_config.get('selectors', {})
        category_wait = category_config.get('wait', {})
        
        # 1. URL (required, no default)
        merged['url'] = category_config['url']
        
        # 2. Enabled (default: True)
        merged['enabled'] = category_config.get('enabled', True)
        
        # 3. Pagination type (category pagination > website pagination > 'pagination')
        merged['type'] = (
            category_pagination.get('type') or
            website_pagination.get('type', 'pagination')
        )
        
        # 4. Pagination parameters based on type
        if merged['type'] == 'pagination' or merged['type'] == 'url_template':
            merged['pages'] = (
                category_pagination.get('pages') or
                website_pagination.get('pages', 5)
            )
            # For url_template, also get page_param and path
            if merged['type'] == 'url_template':
                merged['page_param'] = (
                    category_pagination.get('page_param') or
                    website_pagination.get('page_param')
                )
                merged['path'] = (
                    category_pagination.get('path') or
                    website_pagination.get('path')
                )
        elif merged['type'] == 'infinite_scroll':
            merged['scrolls'] = (
                category_pagination.get('scrolls') or
                website_pagination.get('scrolls', 20)
            )
        elif merged['type'] == 'click_load_more':
            merged['clicks'] = (
                category_pagination.get('clicks') or
                website_pagination.get('clicks', 10)
            )
            merged['load_more_button'] = (
                category_pagination.get('load_more_button') or
                website_pagination.get('load_more_button', 'button.load-more')
            )
        
        # 5. Wait configuration (category wait > website wait > defaults)
        if category_wait:
            merged['wait'] = category_wait
        elif website_wait:
            merged['wait'] = website_wait
        else:
            # V4.0: Default wait uses selector=null and timeout
            merged['wait'] = {'selector': None, 'timeout': 3}
        
        # 6. Selectors (category selectors > website selectors)
        # V4.0: Use article_body instead of article_content + article_paragraphs
        merged['selectors'] = {}
        selector_keys = ['article_list', 'article_title', 'article_body']
        
        for key in selector_keys:
            merged['selectors'][key] = (
                category_selectors.get(key) or
                website_selectors.get(key)
            )
        
        # 7. Delay time (category pagination > website pagination > 2 seconds)
        merged['delay'] = (
            category_pagination.get('delay') or
            website_pagination.get('delay', 2)
        )
        
        # 8. Click-through navigation flag (category > website > False)
        merged['click_through_navigation'] = (
            category_config.get('click_through_navigation') or
            website_config.get('click_through_navigation', False)
        )
        
        # 9. Collection wait and article wait (for V4.0+)
        if 'collection_wait' in category_config:
            merged['collection_wait'] = category_config['collection_wait']
        elif 'collection_wait' in website_config:
            merged['collection_wait'] = website_config['collection_wait']
        
        if 'article_wait' in category_config:
            merged['article_wait'] = category_config['article_wait']
        elif 'article_wait' in website_config:
            merged['article_wait'] = website_config['article_wait']
        
        # 10. Back delay for click-through (category > website > 0.5)
        merged['back_delay'] = (
            category_config.get('back_delay') or
            website_config.get('back_delay', 0.5)
        )
        
        return merged
    
    def _create_empty_result(self, website_name: str, reason: str):
        """
        Create empty result for failed scrape
        
        Args:
            website_name: Website identifier
            reason: Failure reason
        
        Returns:
            ScrapeResult indicating failure
        """
        # Import here to avoid circular dependency
        try:
            from ..feature_registry import FeatureRegistry
            ScrapeResult = FeatureRegistry.get('scrape_result')
            
            if ScrapeResult:
                return ScrapeResult(
                    website_name=website_name,
                    success=False,
                    articles_scraped=0,
                    sentences_extracted=0,
                    error=reason
                )
        except:
            pass
        
        # Fallback minimal result
        class MinimalResult:
            def __init__(self, website_name, success, error):
                self.website_name = website_name
                self.success = success
                self.error = error
                self.articles_scraped = 0
                self.sentences_extracted = 0
        
        return MinimalResult(website_name, False, reason)
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                logger.debug("Driver cleaned up")
            except:
                pass
            self.driver = None
