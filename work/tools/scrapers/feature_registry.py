"""
Centralized Feature Registry

Eliminates repetitive feature detection try/except blocks across codebase.
Provides lazy-loading of optional components.

Usage:
    from feature_registry import FeatureRegistry
    
    # Get feature class (None if not available)
    LanguageDetector = FeatureRegistry.get('language_detector')
    
    # Check availability
    if FeatureRegistry.is_available('stealth'):
        stealth = FeatureRegistry.get('stealth')()
    
    # Get instance directly
    monitor = FeatureRegistry.get_instance('monitor')
"""

from typing import Optional, Any, Dict
import logging

logger = logging.getLogger(__name__)


class FeatureRegistry:
    """
    Lazy-loading registry for optional scraper features
    
    Benefits:
    - Single source of truth for feature detection
    - Lazy imports (only load what's needed)
    - Consistent error handling
    - Easy to add new features
    """
    
    # Cache for loaded feature classes
    _features: Dict[str, Optional[Any]] = {}
    
    # Cache for feature instances
    _instances: Dict[str, Any] = {}
    
    # Feature import mappings
    _FEATURE_MAP = {
        # Advanced features
        'language_detector': ('advanced_features', 'LanguageDetector'),
        'deduplicator': ('advanced_features', 'ArticleDeduplicator'),
        'stealth': ('advanced_features', 'StealthBrowser'),
        
        # Error handling
        'error_handler': ('error_handler', 'ScraperErrorHandler'),
        
        # Monitoring
        'monitor': ('scraper_monitor', 'ScraperMonitor'),
        'scrape_result': ('scraper_monitor', 'ScrapeResult'),
        
        # Security
        'rate_limiter': ('security_utils', 'RateLimiter'),
        'safe_load_yaml': ('security_utils', 'safe_load_yaml'),
        
        # Network features
        'session_manager': ('network_features', 'SessionManager'),
        'response_cache': ('network_features', 'ResponseCache'),
        'retry_handler': ('network_features', 'RetryHandler'),
        'proxy_manager': ('network_features', 'ProxyManager'),
        
        # Base components
        'simple_qc': ('base_scraper', 'SimpleQC'),
        'base_scraper': ('base_scraper', 'BaseScraper'),
    }
    
    @classmethod
    def get(cls, feature_name: str) -> Optional[Any]:
        """
        Get feature class if available, else None
        
        Args:
            feature_name: Feature identifier (e.g., 'language_detector')
        
        Returns:
            Feature class if available, None if not installed
        
        Examples:
            LanguageDetector = FeatureRegistry.get('language_detector')
            if LanguageDetector:
                detector = LanguageDetector()
        """
        # Return cached result if already checked
        if feature_name in cls._features:
            return cls._features[feature_name]
        
        # Check if feature is known
        if feature_name not in cls._FEATURE_MAP:
            logger.warning(f"Unknown feature: {feature_name}")
            cls._features[feature_name] = None
            return None
        
        # Try to import feature
        module_name, class_name = cls._FEATURE_MAP[feature_name]
        
        try:
            # Try relative import first (for scrapers package modules)
            try:
                module = __import__(f'scrapers.{module_name}', fromlist=[class_name])
            except (ImportError, ModuleNotFoundError):
                # Fallback to direct import (for installed packages like langdetect)
                module = __import__(module_name, fromlist=[class_name])
            
            feature_class = getattr(module, class_name)
            cls._features[feature_name] = feature_class
            logger.debug(f"✅ Feature loaded: {feature_name}")
            return feature_class
        except ImportError as e:
            logger.debug(f"⚠️  Feature not available: {feature_name} ({e})")
            cls._features[feature_name] = None
            return None
        except AttributeError as e:
            logger.warning(f"⚠️  Feature import error: {feature_name} ({e})")
            cls._features[feature_name] = None
            return None
    
    @classmethod
    def is_available(cls, feature_name: str) -> bool:
        """
        Check if feature is available
        
        Args:
            feature_name: Feature identifier
        
        Returns:
            True if feature is installed and importable
        
        Examples:
            if FeatureRegistry.is_available('stealth'):
                print("Stealth mode available")
        """
        return cls.get(feature_name) is not None
    
    @classmethod
    def get_instance(cls, feature_name: str, *args, **kwargs) -> Optional[Any]:
        """
        Get singleton instance of feature (creates if needed)
        
        Args:
            feature_name: Feature identifier
            *args, **kwargs: Arguments for feature constructor (first time only)
        
        Returns:
            Feature instance if available, None otherwise
        
        Examples:
            monitor = FeatureRegistry.get_instance('monitor')
            rate_limiter = FeatureRegistry.get_instance('rate_limiter', 
                                                        requests_per_minute=30)
        """
        # Return cached instance if exists
        if feature_name in cls._instances:
            return cls._instances[feature_name]
        
        # Get feature class
        feature_class = cls.get(feature_name)
        if feature_class is None:
            return None
        
        # Create instance
        try:
            instance = feature_class(*args, **kwargs)
            cls._instances[feature_name] = instance
            logger.debug(f"✅ Feature instance created: {feature_name}")
            return instance
        except Exception as e:
            logger.error(f"Failed to create {feature_name} instance: {e}")
            return None
    
    @classmethod
    def clear_cache(cls):
        """Clear cached features and instances (for testing)"""
        cls._features.clear()
        cls._instances.clear()
    
    @classmethod
    def get_available_features(cls) -> Dict[str, bool]:
        """
        Get status of all known features
        
        Returns:
            Dict mapping feature names to availability status
        
        Examples:
            features = FeatureRegistry.get_available_features()
            print(f"Available features: {features}")
        """
        status = {}
        for feature_name in cls._FEATURE_MAP.keys():
            status[feature_name] = cls.is_available(feature_name)
        return status
    
    @classmethod
    def register_feature(cls, feature_name: str, module_name: str, class_name: str):
        """
        Register a new feature dynamically
        
        Args:
            feature_name: Feature identifier
            module_name: Python module containing the feature
            class_name: Class name within the module
        
        Examples:
            FeatureRegistry.register_feature(
                'my_feature',
                'my_module',
                'MyFeatureClass'
            )
        """
        cls._FEATURE_MAP[feature_name] = (module_name, class_name)
        # Clear cache for this feature if it exists
        if feature_name in cls._features:
            del cls._features[feature_name]
        if feature_name in cls._instances:
            del cls._instances[feature_name]


# Convenience functions for common features

def get_language_detector():
    """Get LanguageDetector instance (None if not available)"""
    return FeatureRegistry.get_instance('language_detector')


def get_deduplicator(db_path: str = 'article_dedup.db'):
    """Get ArticleDeduplicator instance (None if not available)"""
    return FeatureRegistry.get_instance('deduplicator', db_path)


def get_stealth_browser():
    """Get StealthBrowser instance (None if not available)"""
    return FeatureRegistry.get_instance('stealth')


def get_error_handler(max_retries: int = 3):
    """Get ScraperErrorHandler instance (None if not available)"""
    return FeatureRegistry.get_instance('error_handler', max_retries=max_retries)


def get_monitor(log_dir: str = 'logs'):
    """Get ScraperMonitor instance (None if not available)"""
    return FeatureRegistry.get_instance('monitor', log_dir=log_dir)


def get_rate_limiter(requests_per_minute: int = 30):
    """Get RateLimiter instance (None if not available)"""
    return FeatureRegistry.get_instance('rate_limiter', 
                                       requests_per_minute=requests_per_minute)


# Check if core features are available at module load
HAS_ADVANCED = (
    FeatureRegistry.is_available('language_detector') and
    FeatureRegistry.is_available('deduplicator') and
    FeatureRegistry.is_available('stealth')
)

HAS_MONITORING = FeatureRegistry.is_available('monitor')
HAS_ERROR_HANDLER = FeatureRegistry.is_available('error_handler')
HAS_SECURITY = FeatureRegistry.is_available('rate_limiter')
HAS_NETWORK = FeatureRegistry.is_available('session_manager')
