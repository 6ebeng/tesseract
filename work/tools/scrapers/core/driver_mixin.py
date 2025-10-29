"""
Driver Mixin

Handles browser driver and page interaction:
- WebDriver management (uses DriverFactory)
- FlareSolverr integration for Cloudflare bypass
- Element finding with fallback support
- Page wait logic
- Network log capture

Usage:
    class MyScraper(DriverMixin, BaseScraper):
        pass
"""

import time
import json
import logging
import requests
from typing import Dict, List, Optional, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Import centralized utilities
try:
    from ..driver_factory import DriverFactory
except ImportError:
    try:
        from .driver_factory import DriverFactory
    except ImportError:
        from driver_factory import DriverFactory

logger = logging.getLogger(__name__)


class DriverMixin:
    """
    Mixin providing browser driver and page interaction functionality.
    
    Manages:
    - WebDriver initialization via DriverFactory
    - FlareSolverr session for Cloudflare bypass
    - Element finding with CSS/XPath support
    - Smart page wait logic
    - Network activity logging
    """
    
    # ========================================================================
    # Driver Initialization
    # ========================================================================
    
    def _init_stealth_driver(self):
        """Initialize Selenium WebDriver with stealth mode."""
        if self.driver:
            return
        
        logger.info("🚀 Initializing headless Chrome driver...")
        
        # Use DriverFactory for centralized driver creation
        self.driver = DriverFactory.create_headless_driver(
            stealth=True,
            enable_performance_logging=self.url_debug_mode,
            block_images=True
        )
        
        logger.info("✅ Driver initialized successfully")
    
    # ========================================================================
    # FlareSolverr Integration
    # ========================================================================
    
    def _init_flaresolverr(self, website_config: Dict) -> bool:
        """
        Initialize FlareSolverr session for Cloudflare bypass.
        
        Returns True if session created successfully, False otherwise.
        """
        flaresolverr_config = website_config.get('flaresolverr', {})
        
        if not flaresolverr_config.get('enabled', False):
            return False
        
        flaresolverr_url = flaresolverr_config.get('url', 'http://localhost:8191')
        max_timeout = flaresolverr_config.get('max_timeout', 60000)
        
        # Retry logic for FlareSolverr startup
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Check if FlareSolverr is running
                if attempt == 0:
                    logger.info(f"🔍 Checking FlareSolverr at {flaresolverr_url}")
                else:
                    logger.info(f"🔍 Retry {attempt + 1}/{max_retries}...")
                
                response = requests.get(flaresolverr_url, timeout=5)
                
                if response.status_code != 200:
                    logger.error(f"❌ FlareSolverr not responding (status {response.status_code})")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return False
                
                data = response.json()
                logger.info(f"✅ FlareSolverr v{data.get('version', 'unknown')} is running")
                
                # Create session
                session_id = f"session_{int(time.time())}"
                logger.info(f"🔧 Creating FlareSolverr session: {session_id}")
                
                response = requests.post(
                    f'{flaresolverr_url}/v1',
                    json={
                        "cmd": "sessions.create",
                        "session": session_id,
                        "maxTimeout": max_timeout
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('status') == 'ok':
                        self.flaresolverr_session = {
                            'id': session_id,
                            'url': flaresolverr_url,
                            'max_timeout': max_timeout
                        }
                        logger.info(f"✅ FlareSolverr session created: {session_id}")
                        return True
                    else:
                        logger.error(f"❌ FlareSolverr session creation failed: {result.get('message')}")
                        return False
                else:
                    logger.error(f"❌ FlareSolverr API error (status {response.status_code})")
                    return False
                    
            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries - 1:
                    logger.warning(f"⏳ Connection error, waiting {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"❌ Cannot connect to FlareSolverr at {flaresolverr_url} after {max_retries} attempts")
                    logger.error(f"   Make sure FlareSolverr is running: docker start flaresolverr")
                    logger.error(f"   Error: {e}")
                    return False
            except Exception as e:
                logger.error(f"❌ FlareSolverr initialization error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    return False
        
        return False
    
    def _destroy_flaresolverr_session(self):
        """Clean up FlareSolverr session."""
        if not self.flaresolverr_session:
            return
        
        try:
            session_id = self.flaresolverr_session['id']
            flaresolverr_url = self.flaresolverr_session['url']
            
            logger.info(f"🧹 Destroying FlareSolverr session: {session_id}")
            
            response = requests.post(
                f'{flaresolverr_url}/v1',
                json={
                    "cmd": "sessions.destroy",
                    "session": session_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ FlareSolverr session destroyed")
            else:
                logger.warning(f"⚠️ Failed to destroy FlareSolverr session (status {response.status_code})")
                
        except Exception as e:
            logger.warning(f"⚠️ Error destroying FlareSolverr session: {e}")
        finally:
            self.flaresolverr_session = None
    
    def _flaresolverr_get(self, url: str) -> Optional[str]:
        """
        Fetch URL using FlareSolverr to bypass Cloudflare.
        
        Returns HTML content or None if failed.
        """
        if not self.flaresolverr_session:
            logger.error("❌ FlareSolverr session not initialized")
            return None
        
        try:
            session_id = self.flaresolverr_session['id']
            flaresolverr_url = self.flaresolverr_session['url']
            max_timeout = self.flaresolverr_session['max_timeout']
            
            logger.info(f"🌐 Fetching via FlareSolverr: {url}")
            
            response = requests.post(
                f'{flaresolverr_url}/v1',
                json={
                    "cmd": "request.get",
                    "url": url,
                    "session": session_id,
                    "maxTimeout": max_timeout
                },
                timeout=max_timeout / 1000 + 10  # Add 10s buffer to timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('status') == 'ok':
                    solution = result.get('solution', {})
                    html = solution.get('response')
                    
                    if html:
                        session_id = self.flaresolverr_session.get('id') if self.flaresolverr_session else 'unknown'
                        logger.info(f"✅ FlareSolverr (session={session_id}) fetched {len(html)} bytes")
                        return html
                    else:
                        logger.error(f"❌ FlareSolverr returned empty response")
                        return None
                else:
                    error_msg = result.get('message', 'Unknown error')
                    logger.error(f"❌ FlareSolverr request failed: {error_msg}")
                    return None
            else:
                logger.error(f"❌ FlareSolverr API error (status {response.status_code})")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ FlareSolverr request timeout for {url}")
            return None
        except Exception as e:
            logger.error(f"❌ FlareSolverr request error: {e}")
            return None
    
    # ========================================================================
    # Page Navigation & Waiting
    # ========================================================================
    
    def _safe_get(self, url: str, delay: int = 2) -> bool:
        """Safely navigate to URL with error handling."""
        try:
            if not self.driver:
                self._init_stealth_driver()
            
            # Track URL if debugging is enabled
            if self.url_debug_mode and url not in self._tracked_url_set:
                self.tracked_urls.append(url)
                self._tracked_url_set.add(url)
                logger.debug(f"📍 Tracked: {url}")
            
            self.driver.get(url)
            time.sleep(delay)
            self._capture_network_logs()
            return True
        except Exception as e:
            logger.error(f"Failed to load {url}: {e}")
            return False
    
    def _wait_for_page(
        self,
        website_config: Dict,
        category_config: Dict = None,
        page_type: str = 'collection'
    ):
        """
        Wait for page to load based on configuration (V4.0+).
        
        Args:
            website_config: Website configuration
            category_config: Category configuration (optional)
            page_type: Type of page - 'collection' for list pages, 'article' for article pages
        
        Supports:
            - collection_wait: Wait config for collection/list pages
            - article_wait: Wait config for article pages (can be int seconds or dict)
            - wait: Default wait config for both types (fallback)
        """
        # Determine which wait config to use based on page type
        wait_config = None
        
        if page_type == 'collection':
            # Try collection_wait first, then fall back to wait
            if category_config:
                wait_config = category_config.get('collection_wait')
            if not wait_config and website_config:
                wait_config = website_config.get('collection_wait')
            if not wait_config:
                # Fall back to generic 'wait'
                wait_config = category_config.get('wait') if category_config else None
                if not wait_config:
                    wait_config = website_config.get('wait', {})
        
        elif page_type == 'article':
            # Try article_wait first, then fall back to wait
            if category_config:
                article_wait = category_config.get('article_wait')
                if article_wait is not None:
                    # article_wait can be int (seconds) or dict
                    if isinstance(article_wait, int):
                        wait_config = {'selector': None, 'timeout': article_wait}
                    else:
                        wait_config = article_wait
            
            if not wait_config and website_config:
                article_wait = website_config.get('article_wait')
                if article_wait is not None:
                    if isinstance(article_wait, int):
                        wait_config = {'selector': None, 'timeout': article_wait}
                    else:
                        wait_config = article_wait
            
            if not wait_config:
                # Fall back to generic 'wait'
                wait_config = category_config.get('wait') if category_config else None
                if not wait_config:
                    wait_config = website_config.get('wait', {})
        
        # Default wait config if nothing specified
        if not wait_config:
            wait_config = {}
        
        # V4.0: Use selector + timeout (null selector = manual delay)
        selector = wait_config.get('selector')  # Can be null/None or CSS selector
        timeout = wait_config.get('timeout', 3)  # Default 3 seconds
        
        if selector:
            # Wait for specific selector (V4.0: selector is not null)
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
            except TimeoutException:
                logger.warning(f"Timeout waiting for selector: {selector}")
                # Fallback to manual delay
                time.sleep(timeout)
        else:
            # Manual delay (V4.0: selector is null)
            time.sleep(timeout)

        self._capture_network_logs()
    
    def _capture_network_logs(self):
        """Capture network activity from Chrome performance logs when debugging."""
        if not self.url_debug_mode or not self.driver:
            return

        try:
            performance_logs = self.driver.get_log('performance')
        except Exception as exc:
            logger.debug(f"   Unable to fetch performance logs: {exc}")
            return

        for entry in performance_logs:
            try:
                message = json.loads(entry.get('message', '{}'))
                message_data = message.get('message', {})
                method = message_data.get('method')

                if method not in ('Network.requestWillBeSent', 'Network.responseReceived'):
                    continue

                params = message_data.get('params', {})
                url = None

                if method == 'Network.requestWillBeSent':
                    request = params.get('request', {})
                    url = request.get('url')
                elif method == 'Network.responseReceived':
                    response = params.get('response', {})
                    url = response.get('url')

                if not url or not url.startswith(('http://', 'https://')):
                    continue

                if url not in self._tracked_url_set:
                    self.tracked_urls.append(url)
                    self._tracked_url_set.add(url)
            except (json.JSONDecodeError, TypeError):
                continue
            except Exception as exc:
                logger.debug(f"   Failed to parse performance log entry: {exc}")
    
    # ========================================================================
    # Element Finding
    # ========================================================================
    
    def _find_element(
        self,
        selector: Any,
        website_config: Dict
    ):
        """
        Find element with fallback support.
        
        Supports:
        - String: CSS or XPath (auto-detected if starts with //)
        - List: Array of CSS/XPath strings (tries each until one works)
        - Dict with 'selector' key: {'selector': '//...', 'multiple': true, 'delimiter': '\\n'}
        - Dict with 'type' key: {'type': 'xpath', 'value': '//...'} (legacy)
        """
        if not selector:
            return None
        
        # Normalize to list of selectors
        if isinstance(selector, str):
            selectors = [selector]
        elif isinstance(selector, list):
            selectors = selector
        elif isinstance(selector, dict):
            # Handle dict formats - extract the actual selector
            if 'selector' in selector:
                # New format: {'selector': '//... or CSS or [...array]', 'multiple': true, 'delimiter': '\n'}
                extracted = selector.get('selector')
                # The selector value itself can be a string or array
                if isinstance(extracted, list):
                    selectors = extracted
                else:
                    selectors = [extracted]
            elif 'type' in selector and 'value' in selector:
                # Old format: {'type': 'xpath', 'value': '//...'}
                selectors = [selector.get('value')]
            else:
                return None
        else:
            return None
        
        # Try each selector until one returns an element
        for sel in selectors:
            if not sel or not isinstance(sel, str):
                continue
                
            try:
                # Auto-detect XPath (starts with // or /)
                if sel.startswith('//') or sel.startswith('/'):
                    return self.driver.find_element(By.XPATH, sel)
                else:
                    return self.driver.find_element(By.CSS_SELECTOR, sel)
            except:
                continue
        
        return None
    
    def _find_elements(
        self,
        selector: Any,
        website_config: Dict
    ) -> List:
        """
        Find elements with fallback support.
        
        Supports:
        - String: CSS or XPath (auto-detected if starts with //)
        - List: Array of CSS/XPath strings (tries each until one works)
        - Dict with 'selector' key: {'selector': '//...', 'multiple': true, 'delimiter': '\\n'}
        - Dict with 'type' key: {'type': 'xpath', 'value': '//...'} (legacy)
        """
        if not selector:
            return []
        
        # Normalize to list of selectors
        if isinstance(selector, str):
            selectors = [selector]
        elif isinstance(selector, list):
            selectors = selector
        elif isinstance(selector, dict):
            # Handle dict formats - extract the actual selector
            if 'selector' in selector:
                # New format: {'selector': '//... or CSS or [...array]', 'multiple': true, 'delimiter': '\n'}
                extracted = selector.get('selector')
                # The selector value itself can be a string or array
                if isinstance(extracted, list):
                    selectors = extracted
                else:
                    selectors = [extracted]
            elif 'type' in selector and 'value' in selector:
                # Old format: {'type': 'xpath', 'value': '//...'}
                selectors = [selector.get('value')]
            else:
                return []
        else:
            return []
        
        # Try each selector until one returns elements
        for sel in selectors:
            if not sel or not isinstance(sel, str):
                continue
                
            try:
                # Auto-detect XPath (starts with // or /)
                if sel.startswith('//') or sel.startswith('/'):
                    elements = self.driver.find_elements(By.XPATH, sel)
                else:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, sel)
                
                if elements:
                    return elements
            except:
                continue
        
        return []
    
    def _extract_text(self, selector: Any) -> str:
        """Extract text from element."""
        elem = self._find_element(selector, {})
        if elem:
            return elem.text.strip()
        return ''
