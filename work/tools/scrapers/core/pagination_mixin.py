"""
Pagination Mixin

Handles all pagination strategies:
- URL template (page numbers in URL)
- Infinite scroll (scroll to load more)
- Click load more (button clicking)
- Traditional next-button navigation

Usage:
    class MyStraper(PaginationMixin, BaseScraper):
        pass
"""

import time
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class PaginationMixin:
    """
    Mixin providing pagination functionality for web scrapers.
    
    Supports multiple pagination strategies:
    - pagination/url_template: Page numbers in URL
    - infinite_scroll: Scroll down to load content
    - click_load_more: Click button to load more
    
    Requires driver and helper methods from other mixins.
    """
    
    def _scrape_pagination(
        self,
        website_config: Dict,
        category_config: Dict
    ) -> List[str]:
        """
        Scrape articles from paginated list.
        
        Supports two modes:
        1. URL template: Build URLs with page numbers
        2. Next button: Click next button to navigate
        
        Args:
            website_config: Website configuration
            category_config: Category configuration (with defaults applied)
        
        Returns:
            List of article URLs
        """
        article_links = []
        max_pages = category_config.get('pages', 5)
        base_url = category_config.get('url', '')
        pagination_type = category_config.get('type', 'pagination')
        page_param = category_config.get('page_param')  # e.g., 'page', 'p'
        path_template = category_config.get('path')  # e.g., '/page/{page}'
        
        # Clean base URL: remove existing page parameters if page_param is specified
        if page_param and page_param in base_url:
            import re
            base_url = re.sub(rf'[?&]{page_param}=\d+', '', base_url)
            base_url = base_url.rstrip('?&')
            logger.info(f"   Cleaned URL: {base_url}")
        
        # Check if using URL template pagination
        is_url_template = (
            pagination_type == 'url_template' or 
            '{page}' in base_url or 
            page_param or 
            path_template
        )
        
        for page in range(max_pages):
            logger.info(f"   Page {page + 1}/{max_pages}...")
            
            # Navigate to page if using URL template
            if is_url_template:
                page_url = self._build_page_url(
                    base_url, page, page_param, path_template
                )
                
                if not page_url:
                    logger.error("Failed to build page URL")
                    break
                
                # Use FlareSolverr or Selenium
                if self.flaresolverr_session:
                    if not self._scrape_page_flaresolverr(
                        page_url, category_config, article_links, page
                    ):
                        break
                    continue
                else:
                    if not self._safe_get(page_url):
                        logger.info(f"   Failed to load page {page + 1}")
                        break
                    self._wait_for_page(website_config, category_config, page_type='collection')
                    time.sleep(category_config.get('delay', 2))
            
            # Extract article links from current page (Selenium mode)
            links = self._extract_article_links(category_config)
            new_links = [l for l in links if l not in article_links]
            article_links.extend(new_links)
            
            logger.info(f"   Found {len(new_links)} new articles on page {page + 1}")
            
            # Early exit: if no new articles found, skip remaining pages
            if not new_links and page > 0:
                logger.info(f"   No new articles found - skipping remaining pages")
                break
            
            # Navigate to next page (if not using URL template)
            if not is_url_template and page < max_pages - 1:
                if not self._go_to_next_page(category_config):
                    logger.info(f"   No more pages available")
                    break
                
                self._wait_for_page(website_config, category_config, page_type='collection')
                time.sleep(2)
        
        return article_links
    
    def _scrape_infinite_scroll(
        self,
        website_config: Dict,
        category_config: Dict
    ) -> List[str]:
        """
        Scrape articles from infinite scroll page.
        
        Scrolls down repeatedly and extracts newly loaded content.
        
        Args:
            website_config: Website configuration
            category_config: Category configuration (with defaults applied)
        
        Returns:
            List of article URLs
        """
        article_links = []
        max_scrolls = category_config.get('scrolls', 10)
        
        for scroll in range(max_scrolls):
            self._capture_network_logs()
            
            # Extract current articles
            links = self._extract_article_links(website_config)
            new_links = [l for l in links if l not in article_links]
            
            if not new_links and scroll > 0:
                logger.info(f"   No new articles found after scroll {scroll}")
                break
            
            article_links.extend(new_links)
            logger.info(f"   Scroll {scroll + 1}/{max_scrolls}: {len(new_links)} new articles")
            
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            self._capture_network_logs()
        
        return article_links
    
    def _scrape_click_load_more(
        self,
        website_config: Dict,
        category_config: Dict
    ) -> List[str]:
        """
        Scrape articles by clicking 'Load More' button.
        
        Clicks button repeatedly and extracts newly loaded content.
        
        Args:
            website_config: Website configuration
            category_config: Category configuration (with defaults applied)
        
        Returns:
            List of article URLs
        """
        article_links = []
        max_clicks = category_config.get('clicks', 10)
        load_more_selector = category_config.get('load_more_button', 'button.load-more')
        
        for click in range(max_clicks):
            self._capture_network_logs()
            
            # Extract current articles
            links = self._extract_article_links(category_config)
            new_links = [l for l in links if l not in article_links]
            article_links.extend(new_links)
            
            logger.info(f"   Click {click + 1}/{max_clicks}: {len(new_links)} new articles")
            
            # Click load more button
            try:
                button = self._find_element(load_more_selector, category_config)
                
                if not button:
                    logger.info(f"   Load more button not found")
                    break
                
                # Scroll to button and click
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                time.sleep(1)
                self.driver.execute_script("arguments[0].click();", button)
                time.sleep(2)
                self._capture_network_logs()
                
            except Exception as e:
                logger.debug(f"   Could not click load more: {e}")
                break
        
        return article_links
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _build_page_url(
        self,
        base_url: str,
        page: int,
        page_param: str = None,
        path_template: str = None
    ) -> str:
        """
        Build page URL based on configuration.
        
        Supports three formats:
        1. Template substitution: url with {page} placeholder
        2. Path template: append path pattern to base URL
        3. Parameter appending: ?param=N or &param=N
        
        Args:
            base_url: Base URL
            page: Page number (0-indexed)
            page_param: URL parameter name (e.g., 'page')
            path_template: Path template (e.g., '/page/{page}')
        
        Returns:
            Complete page URL or None if configuration invalid
        """
        if '{page}' in base_url:
            # Template substitution
            return base_url.format(page=page + 1)
        
        elif path_template:
            # Path template: page 1 usually doesn't need the path suffix
            if page == 0:
                return base_url
            else:
                path = path_template.format(page=page + 1)
                return base_url.rstrip('/') + path
        
        elif page_param:
            # Parameter appending
            separator = '&' if '?' in base_url else '?'
            return f"{base_url}{separator}{page_param}={page + 1}"
        
        else:
            logger.error("url_template type requires either {page} in URL, page_param, or path")
            return None
    
    def _scrape_page_flaresolverr(
        self,
        page_url: str,
        category_config: Dict,
        article_links: List[str],
        page: int
    ) -> bool:
        """
        Scrape a single page using FlareSolverr.
        
        Args:
            page_url: URL to scrape
            category_config: Category configuration
            article_links: List to append new links to (modified in place)
            page: Page number (0-indexed)
        
        Returns:
            True if successful, False otherwise
        """
        html = self._flaresolverr_get(page_url)
        if not html:
            logger.info(f"   Failed to load page {page + 1} via FlareSolverr")
            return False
        
        # Parse HTML and extract links using BeautifulSoup
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        links = self._extract_article_links_from_soup(soup, category_config)
        new_links = [l for l in links if l not in article_links]
        article_links.extend(new_links)
        
        logger.info(f"   Found {len(new_links)} new articles on page {page + 1}")
        
        # Early exit: if no new articles found, skip remaining pages
        if not new_links and page > 0:
            logger.info(f"   No new articles found - skipping remaining pages")
            return False
        
        time.sleep(category_config.get('delay', 2))
        return True
    
    def _go_to_next_page(self, category_config: Dict) -> bool:
        """
        Navigate to next page using next button.
        
        Args:
            category_config: Category configuration
        
        Returns:
            True if navigation successful, False otherwise
        """
        next_button_selector = category_config.get('next_button', 'a.next')
        
        try:
            button = self._find_element(next_button_selector, {})
            if button:
                button.click()
                return True
        except:
            pass
        
        return False
    
    def _extract_article_links_from_soup(self, soup, config: Dict) -> List[str]:
        """
        Extract article links from BeautifulSoup object.
        
        Used for FlareSolverr mode where we get HTML instead of using Selenium.
        
        Args:
            soup: BeautifulSoup parsed HTML
            config: Category configuration
        
        Returns:
            List of article URLs
        """
        selectors = config.get('selectors', {})
        article_list_selector = selectors.get('article_list')
        
        links = []
        
        try:
            # Handle multiple selector formats
            if isinstance(article_list_selector, str):
                selectors_to_try = [article_list_selector]
            elif isinstance(article_list_selector, list):
                selectors_to_try = article_list_selector
            else:
                selectors_to_try = []
            
            # Try each selector
            for selector in selectors_to_try:
                articles = soup.select(selector)
                
                for article in articles:
                    try:
                        # Get href from element or find 'a' tag inside
                        href = article.get('href')
                        if not href:
                            # Find <a> tags with specific paths
                            a_tag = article.find('a', href=lambda x: x and (
                                '/story/' in x or '/opinion/' in x
                            ))
                            if not a_tag:
                                # Fallback: find any <a> tag
                                a_tag = article.find('a')
                            if a_tag:
                                href = a_tag.get('href')
                        
                        if href:
                            # Make absolute URL if needed
                            if href.startswith('/'):
                                base_url = config.get('url', '')
                                if '://' in base_url:
                                    from urllib.parse import urlparse
                                    parsed = urlparse(base_url)
                                    href = f"{parsed.scheme}://{parsed.netloc}{href}"
                            
                            if href and href not in links and href.startswith('http'):
                                links.append(href)
                    except Exception:
                        continue
                
                if links:
                    break  # Found links with this selector
        
        except Exception as e:
            logger.warning(f"Error extracting article links from soup: {e}")
        
        return links
