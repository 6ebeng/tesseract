"""
Centralized WebDriver Factory

Eliminates driver initialization duplication across:
- generic_scraper.py
- production_scraper.py
- cli_tools.py
- config_wizard.py

Usage:
    from driver_factory import DriverFactory
    
    driver = DriverFactory.create_headless_driver(
        stealth=True,
        enable_performance_logging=True
    )
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from typing import Optional
import shutil
import logging

logger = logging.getLogger(__name__)


class DriverFactory:
    """Factory for creating WebDriver instances with consistent configuration"""
    
    # Default stealth user agent
    DEFAULT_USER_AGENT = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    
    @staticmethod
    def create_headless_driver(
        stealth: bool = True,
        enable_performance_logging: bool = False,
        block_images: bool = True,
        user_agent: Optional[str] = None,
        window_size: str = '1920,1080',
        proxy: Optional[dict] = None
    ) -> webdriver.Chrome:
        """
        Create a headless Chrome driver with optional stealth mode and proxy
        
        Args:
            stealth: Enable stealth mode to avoid bot detection
            enable_performance_logging: Enable for URL tracking/debugging
            block_images: Block images for faster loading (recommended)
            user_agent: Custom user agent string (uses default if None)
            window_size: Browser window size as 'width,height'
            proxy: Proxy configuration dict (from ProxyRotator.get_next_proxy())
        
        Returns:
            Configured Chrome WebDriver instance
        
        Examples:
            # Basic usage
            driver = DriverFactory.create_headless_driver()
            
            # With URL tracking for debugging
            driver = DriverFactory.create_headless_driver(
                enable_performance_logging=True
            )
            
            # With proxy rotation
            proxy = proxy_rotator.get_next_proxy()
            driver = DriverFactory.create_headless_driver(proxy=proxy)
            
            # Without stealth (faster, but easier to detect)
            driver = DriverFactory.create_headless_driver(stealth=False)
        """
        options = webdriver.ChromeOptions()
        
        # Headless mode (new Chrome 109+ syntax)
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument(f'--window-size={window_size}')
        
        # Performance optimizations
        if block_images:
            prefs = {
                "profile.managed_default_content_settings.images": 2,  # Block images
                "profile.default_content_setting_values.notifications": 2,  # Block notifications
            }
            options.add_experimental_option("prefs", prefs)
        
        # Performance logging for URL tracking (debug mode)
        if enable_performance_logging:
            options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        # Stealth mode - appears more like a real browser
        if stealth:
            ua = user_agent or DriverFactory.DEFAULT_USER_AGENT
            options.add_argument(f"user-agent={ua}")
            
            # Additional stealth arguments
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
        
        # Proxy configuration
        if proxy:
            proxy_url = f"{proxy['host']}:{proxy['port']}"
            
            # Configure proxy based on protocol
            if proxy['protocol'] == 'socks5':
                options.add_argument(f'--proxy-server=socks5://{proxy_url}')
            else:
                # HTTP/HTTPS proxy
                options.add_argument(f'--proxy-server={proxy_url}')
            
            # Add proxy authentication if credentials provided
            if proxy.get('username') and proxy.get('password'):
                # Note: Chrome doesn't support proxy auth via command line
                # This would require a Chrome extension or other workaround
                logger.warning("⚠️  Proxy authentication requires Chrome extension (not yet implemented)")
            
            logger.debug(f"🔀 Proxy configured: {proxy['protocol']}://{proxy_url}")
        
        # Create driver with explicit chromedriver path
        driver = DriverFactory._create_driver_with_service(options)
        
        # Apply JavaScript-based stealth if enabled
        if stealth:
            DriverFactory._apply_stealth_js(driver)
        
        logger.debug(f"✅ Driver created (stealth={stealth}, perf_log={enable_performance_logging})")
        return driver
    
    @staticmethod
    def _create_driver_with_service(options: webdriver.ChromeOptions) -> webdriver.Chrome:
        """
        Create driver with explicit chromedriver path to avoid Selenium Manager issues
        
        Falls back to default driver creation if chromedriver not in PATH
        """
        try:
            # Try to find chromedriver in PATH
            chromedriver_path = shutil.which('chromedriver')
            if chromedriver_path:
                service = Service(chromedriver_path)
                return webdriver.Chrome(service=service, options=options)
            else:
                logger.warning("chromedriver not found in PATH, using default")
                return webdriver.Chrome(options=options)
        except Exception as e:
            logger.warning(f"Failed to create driver with service: {e}, trying fallback")
            # Fallback: try without explicit Service
            return webdriver.Chrome(options=options)
    
    @staticmethod
    def _apply_stealth_js(driver: webdriver.Chrome):
        """
        Apply JavaScript-based stealth techniques to hide automation
        
        Techniques:
        - Override navigator.webdriver property
        - Modify navigator.plugins
        - Set realistic navigator.languages
        """
        try:
            # Override navigator.webdriver (most important)
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """
            })
            
            # Override navigator.plugins to look more realistic
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                """
            })
            
            # Set realistic languages
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en', 'ku']
                    });
                """
            })
            
            logger.debug("✅ Stealth JavaScript applied")
        except Exception as e:
            logger.warning(f"Failed to apply stealth JS: {e}")
    
    @staticmethod
    def apply_advanced_stealth(driver: webdriver.Chrome, stealth_browser=None):
        """
        Apply advanced stealth mode using StealthBrowser component
        
        Args:
            driver: WebDriver instance
            stealth_browser: StealthBrowser instance (from advanced_features.py)
        
        Usage:
            from advanced_features import StealthBrowser
            driver = DriverFactory.create_headless_driver()
            stealth = StealthBrowser()
            DriverFactory.apply_advanced_stealth(driver, stealth)
        """
        if stealth_browser:
            try:
                stealth_browser.apply_stealth_mode(driver)
                logger.debug("✅ Advanced stealth mode applied")
            except Exception as e:
                logger.warning(f"Failed to apply advanced stealth: {e}")


# Convenience function for backward compatibility
def create_stealth_driver(
    enable_performance_logging: bool = False,
    block_images: bool = True
) -> webdriver.Chrome:
    """
    Convenience function - creates driver with stealth enabled by default
    
    Usage:
        driver = create_stealth_driver()
    """
    return DriverFactory.create_headless_driver(
        stealth=True,
        enable_performance_logging=enable_performance_logging,
        block_images=block_images
    )
