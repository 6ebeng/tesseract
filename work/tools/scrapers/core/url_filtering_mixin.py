"""
URL Filtering Mixin

Handles URL filtering, deduplication, and tracking:
- URL whitelist/blacklist filtering
- Preset and template support
- Article deduplication (SQLite-based)
- URL tracking for debugging

Usage:
    class MyScraper(URLFilteringMixin, BaseScraper):
        pass
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class URLFilteringMixin:
    """
    Mixin providing URL filtering and deduplication functionality.
    
    Manages:
    - URL whitelist/blacklist with preset/template support
    - Article URL deduplication via SQLite database
    - URL tracking for performance debugging
    """
    
    # ========================================================================
    # Article Link Deduplication
    # ========================================================================
    
    def load_scraped_articles(self):
        """Load previously scraped article links from database."""
        try:
            import sqlite3
            if not self.article_link_db_path.exists():
                return
            
            conn = sqlite3.connect(str(self.article_link_db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT url FROM scraped_articles")
            self.scraped_article_links = set(row[0] for row in cursor.fetchall())
            conn.close()
            
            logger.info(f"📚 Loaded {len(self.scraped_article_links)} previously scraped article URLs")
        except Exception as e:
            logger.warning(f"Could not load scraped articles: {e}")
            self.scraped_article_links = set()
    
    def save_scraped_article(self, url: str):
        """Save a scraped article URL to the database."""
        try:
            import sqlite3
            self.scraped_article_links.add(url)
            
            conn = sqlite3.connect(str(self.article_link_db_path))
            cursor = conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scraped_articles (
                    url TEXT PRIMARY KEY,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert the URL
            cursor.execute(
                "INSERT OR IGNORE INTO scraped_articles (url) VALUES (?)",
                (url,)
            )
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.debug(f"Could not save scraped article: {e}")
    
    def clear_scraped_articles(self):
        """Clear the scraped articles database."""
        try:
            if self.article_link_db_path.exists():
                self.article_link_db_path.unlink()
            self.scraped_article_links = set()
            logger.info("🗑️  Cleared scraped articles database")
        except Exception as e:
            logger.warning(f"Could not clear scraped articles: {e}")
    
    def is_article_scraped(self, url: str) -> bool:
        """Check if an article URL has already been scraped."""
        return url in self.scraped_article_links
    
    # ========================================================================
    # URL Tracking & Debugging
    # ========================================================================
    
    def enable_url_debugging(self):
        """Enable URL tracking to see all requests being made."""
        self.url_debug_mode = True
        self.tracked_urls = []
        self._tracked_url_set = set()
        logger.info("🔍 URL debugging enabled - will track all requests")
    
    def disable_url_debugging(self):
        """Disable URL tracking."""
        self.url_debug_mode = False
        logger.info("🔍 URL debugging disabled")
    
    def get_tracked_urls(self) -> List[str]:
        """Get all tracked URLs."""
        return self.tracked_urls
    
    def save_tracked_urls(self, filename: str = 'tracked_urls.txt'):
        """Save tracked URLs to a file for analysis."""
        if not self.tracked_urls:
            logger.warning("No URLs tracked. Enable URL debugging first.")
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Tracked URLs ({len(self.tracked_urls)} total)\n")
            f.write(f"# Tracked on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Group by resource type
            html_urls = []
            script_urls = []
            style_urls = []
            image_urls = []
            other_urls = []
            
            for url in self.tracked_urls:
                if any(ext in url.lower() for ext in ['.js']):
                    script_urls.append(url)
                elif any(ext in url.lower() for ext in ['.css']):
                    style_urls.append(url)
                elif any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']):
                    image_urls.append(url)
                elif any(ext in url.lower() for ext in ['.html', '.htm']) or '?' in url or url.endswith('/'):
                    html_urls.append(url)
                else:
                    other_urls.append(url)
            
            f.write(f"# HTML Pages ({len(html_urls)})\n")
            for url in html_urls:
                f.write(f"{url}\n")
            
            f.write(f"\n# Scripts ({len(script_urls)})\n")
            for url in script_urls:
                f.write(f"{url}\n")
            
            f.write(f"\n# Styles ({len(style_urls)})\n")
            for url in style_urls:
                f.write(f"{url}\n")
            
            f.write(f"\n# Images ({len(image_urls)})\n")
            for url in image_urls:
                f.write(f"{url}\n")
            
            f.write(f"\n# Other ({len(other_urls)})\n")
            for url in other_urls:
                f.write(f"{url}\n")
        
        logger.info(f"✅ Tracked URLs saved to {filename}")
        logger.info(f"   Total: {len(self.tracked_urls)} URLs")
        logger.info(f"   HTML: {len(html_urls)}, Scripts: {len(script_urls)}, Styles: {len(style_urls)}, Images: {len(image_urls)}, Other: {len(other_urls)}")
    
    def analyze_urls(self) -> Dict:
        """Analyze tracked URLs and provide recommendations."""
        if not self.tracked_urls:
            return {"error": "No URLs tracked. Enable URL debugging first."}
        
        analysis = {
            'total_urls': len(self.tracked_urls),
            'unique_domains': len(set(url.split('/')[2] if len(url.split('/')) > 2 else '' for url in self.tracked_urls)),
            'resource_types': {},
            'third_party_urls': [],
            'recommendations': []
        }
        
        # Categorize URLs
        for url in self.tracked_urls:
            if any(ext in url.lower() for ext in self.blocked_resources):
                resource_type = 'blocked_resource'
            elif '.js' in url.lower():
                resource_type = 'javascript'
            elif '.css' in url.lower():
                resource_type = 'stylesheet'
            elif any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                resource_type = 'image'
            else:
                resource_type = 'html/api'
            
            analysis['resource_types'][resource_type] = analysis['resource_types'].get(resource_type, 0) + 1
            
            # Identify third-party URLs
            if any(tracker in url.lower() for tracker in ['google-analytics', 'facebook', 'twitter', 'ads', 'tracking']):
                analysis['third_party_urls'].append(url)
        
        # Generate recommendations
        if analysis['resource_types'].get('blocked_resource', 0) > 0:
            analysis['recommendations'].append(f"Block {analysis['resource_types']['blocked_resource']} unnecessary resources")
        if len(analysis['third_party_urls']) > 0:
            analysis['recommendations'].append(f"Block {len(analysis['third_party_urls'])} third-party tracking URLs")
        if analysis['resource_types'].get('image', 0) > 10:
            analysis['recommendations'].append("Consider disabling image loading (already implemented)")
        
        return analysis
    
    # ========================================================================
    # URL Filtering (Whitelist/Blacklist)
    # ========================================================================
    
    def set_url_whitelist(self, patterns: List[str]):
        """Set URL whitelist patterns (only these URLs will be loaded)."""
        self.url_whitelist = patterns
        logger.info(f"🔒 URL whitelist set: {len(patterns)} patterns")
    
    def add_to_whitelist(self, pattern: str):
        """Add a pattern to the whitelist."""
        if pattern not in self.url_whitelist:
            self.url_whitelist.append(pattern)
            logger.info(f"✅ Added to whitelist: {pattern}")
    
    def _load_url_filtering(self, website_config: Dict):
        """
        Load URL filtering configuration with preset support.
        
        Supports multiple approaches:
        1. Template-based: template: 'rudaw' (uses predefined template)
        2. Preset-based: preset: 'standard' (applies preset patterns)
        3. Manual: Direct whitelist/blacklist arrays in config
        4. Hybrid: Preset + website-specific whitelist/blacklist additions
        
        Processing order:
        - Load preset/template base patterns (if specified)
        - Add website-specific whitelist patterns (merged/extended)
        - Add website-specific blacklist patterns (merged/extended)
        - Add extra_blacklist patterns (always appended)
        """
        url_filtering = website_config.get('url_filtering', {})
        if not url_filtering:
            self.blocked_resources = list(self._default_blocked_resources)
            return

        # Reset filters to defaults before applying overrides
        self.blocked_resources = list(self._default_blocked_resources)
        self.url_whitelist = []

        if url_filtering.get('disabled'):
            self.blocked_resources = []
            logger.info("📭 URL filtering disabled for this website")
            return
        
        # Try to load presets file
        presets_file = self.config_path / 'url_filtering_presets.yaml' if self.config_path.is_dir() else None
        presets = {}
        resource_types = {}
        templates = {}
        
        if presets_file and presets_file.exists():
            try:
                with open(presets_file, 'r', encoding='utf-8') as f:
                    presets_data = yaml.safe_load(f) or {}
                    presets = presets_data.get('presets', {})
                    resource_types = presets_data.get('resource_types', {})
                    templates = presets_data.get('templates', {})
                logger.debug(f"📦 Loaded {len(presets)} presets from url_filtering_presets.yaml")
            except Exception as e:
                logger.warning(f"Could not load URL filtering presets: {e}")
        
        # Step 1: Process template (if specified)
        template_whitelist = []
        template_blacklist = []
        
        if url_filtering.get('template'):
            template_name = url_filtering['template']
            if template_name in templates:
                template = templates[template_name]
                logger.info(f"📋 Using URL filtering template: {template_name}")
                
                # Collect template patterns (don't apply yet)
                template_whitelist = template.get('whitelist', [])
                template_blacklist = template.get('blacklist', [])
                
                # Apply template preset to blocked_resources
                if template.get('preset') and template['preset'] in presets:
                    self._apply_preset(presets[template['preset']], resource_types)
            else:
                logger.warning(f"Template '{template_name}' not found in presets file")
        
        # Step 2: Process preset (if specified and no template)
        elif url_filtering.get('preset'):
            preset_name = url_filtering['preset']
            if preset_name in presets:
                preset = presets[preset_name]
                logger.info(f"📦 Using URL filtering preset: {preset_name} - {preset.get('description', '')}")
                self._apply_preset(preset, resource_types)
            else:
                logger.warning(f"Preset '{preset_name}' not found in presets file")
        
        # Step 3: Merge website-specific whitelist with template/preset whitelist
        final_whitelist = []
        
        # Add template whitelist patterns first
        if template_whitelist:
            final_whitelist.extend(template_whitelist)
            logger.info(f"  ✅ Template whitelist: {len(template_whitelist)} patterns")
        
        # Add website-specific whitelist patterns (merged or standalone)
        website_whitelist = url_filtering.get('whitelist', [])
        if website_whitelist:
            # Merge with template patterns (avoid duplicates)
            for pattern in website_whitelist:
                if pattern not in final_whitelist:
                    final_whitelist.append(pattern)
            logger.info(f"  ✅ Website whitelist: {len(website_whitelist)} patterns")
        
        # Apply final merged whitelist
        if final_whitelist:
            self.set_url_whitelist(final_whitelist)
            logger.info(f"📋 Total whitelist patterns: {len(final_whitelist)}")
        
        # Step 4: Add website-specific blacklist patterns
        website_blacklist = url_filtering.get('blacklist', [])
        if template_blacklist:
            self.blocked_resources.extend(template_blacklist)
            logger.info(f"  🚫 Template blacklist: {len(template_blacklist)} patterns")
        
        if website_blacklist:
            self.blocked_resources.extend(website_blacklist)
            logger.info(f"  🚫 Website blacklist: {len(website_blacklist)} patterns")
        
        # Extra blacklist (for preset + custom additions)
        if url_filtering.get('extra_blacklist'):
            self.blocked_resources.extend(url_filtering['extra_blacklist'])
            logger.info(f"🚫 Added {len(url_filtering['extra_blacklist'])} extra blacklist patterns")
    
    def _apply_preset(self, preset: Dict, resource_types: Dict):
        """Apply a URL filtering preset."""
        # Check if preset uses whitelist-only mode
        if preset.get('mode') == 'whitelist_only':
            logger.info("  ⚠️  Whitelist-only mode - must specify whitelist patterns in config")
            return
        
        # Apply blacklist types from preset
        blacklist_types = preset.get('blacklist_types', [])
        for type_name in blacklist_types:
            if type_name in resource_types:
                patterns = resource_types[type_name]
                self.blocked_resources.extend(patterns)
                logger.info(f"  🚫 Blocking {type_name}: {len(patterns)} patterns")
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics including URL tracking."""
        stats = self.stats.copy()
        stats['tracked_urls_count'] = len(self.tracked_urls)
        stats['url_debug_mode'] = self.url_debug_mode
        stats['whitelist_patterns'] = len(self.url_whitelist)
        return stats
