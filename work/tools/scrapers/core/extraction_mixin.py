"""
Extraction Mixin

Handles content extraction from web pages:
- Extract article links from list pages
- Extract article content (title + body)
- Support for click-through navigation
- Language detection and filtering
- Deduplication

Usage:
    class MyScraper(ExtractionMixin, PaginationMixin, BaseScraper):
        pass
"""

import re
import time
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ExtractionMixin:
    """
    Mixin providing content extraction functionality.
    
    Extracts article links and content from web pages using configured selectors.
    Supports both Selenium and FlareSolverr modes.
    """
    
    def _extract_article_links(self, config: Dict) -> List[str]:
        """
        Extract article links from current page.
        
        Args:
            config: Configuration with merged selectors
        
        Returns:
            List of article URLs
        """
        selectors = config.get('selectors', {})
        article_list_selector = selectors.get('article_list')
        
        links = []
        
        try:
            # Find all article elements
            articles = self._find_elements(article_list_selector, config)
            
            for article in articles:
                try:
                    # Check if the element itself is a link
                    href = article.get_attribute('href')
                    if href and href not in links:
                        links.append(href)
                except Exception:
                    continue
        
        except Exception as e:
            logger.warning(f"Error extracting article links: {e}")
        
        return links
    
    def _extract_article_elements(self, config: Dict) -> List:
        """
        Extract article elements (not URLs) for click-through navigation.
        
        Used when click_through_navigation is enabled.
        Returns list of WebElements that can be clicked.
        
        Args:
            config: Configuration with selectors
        
        Returns:
            List of WebElements
        """
        selectors = config.get('selectors', {})
        article_list_selector = selectors.get('article_list')
        
        elements = []
        
        try:
            elements = self._find_elements(article_list_selector, config)
        except Exception as e:
            logger.warning(f"Error extracting article elements: {e}")
        
        return elements
    
    def _extract_from_articles(
        self,
        article_links: List[str],
        website_config: Dict,
        category_config: Dict
    ) -> List[str]:
        """
        Extract sentences from article pages.
        
        Navigates to each article URL and extracts content using selectors.
        Supports both Selenium and FlareSolverr modes.
        
        Args:
            article_links: List of article URLs to visit
            website_config: Website configuration
            category_config: Category configuration with merged selectors
        
        Returns:
            List of extracted sentences
        """
        sentences = []
        selectors = category_config.get('selectors', website_config.get('selectors', {}))
        
        for i, link in enumerate(article_links):
            try:
                # Skip if article already scraped
                if self.is_article_scraped(link):
                    logger.debug(f"   ⏭️  Skipping already scraped article: {link}")
                    continue
                
                # Extract using FlareSolverr or Selenium
                if self.flaresolverr_session:
                    article_text = self._extract_article_flaresolverr(
                        link, selectors
                    )
                else:
                    article_text = self._extract_article_selenium(
                        link, website_config, category_config, selectors
                    )
                
                # Process extracted text
                if article_text:
                    full_text = ' '.join(article_text)
                    
                    # Language detection and filtering
                    if not self._check_language(full_text, website_config):
                        continue
                    
                    # Deduplication check
                    if self.deduplicator:
                        is_dup, reason = self.deduplicator.is_duplicate(
                            {},
                            link,
                            article_text[0] if article_text else '',  # title
                            full_text
                        )
                        if is_dup:
                            logger.info(f"   ⚠️  Skipping duplicate: {reason}")
                            self.stats['duplicates_skipped'] += 1
                            continue
                    
                    # Get delimiter from selector config
                    body_selector = selectors.get('article_body', 'p')
                    delimiter = self._get_delimiter(body_selector)
                    
                    # Add sentences
                    logger.info(f"   ➕ Adding sentences (delimiter={delimiter})...")
                    if delimiter:
                        # Join all paragraphs and split by delimiter
                        combined_text = delimiter.join(article_text)
                        split_sentences = [
                            s.strip() for s in combined_text.split(delimiter) 
                            if s.strip() and len(s.strip()) > 20
                        ]
                        logger.info(f"      Split into {len(split_sentences)} sentences")
                        sentences.extend(split_sentences)
                    else:
                        # Use paragraphs as-is
                        logger.info(f"      Adding {len(article_text)} paragraphs as sentences")
                        sentences.extend(article_text)
                    
                    self.stats['articles_processed'] += 1
                    
                    # Mark article as scraped
                    self.save_scraped_article(link)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"   Processed {i + 1}/{len(article_links)} articles...")
                
            except Exception as e:
                logger.debug(f"   Error processing article {link}: {e}")
                continue
        
        self.stats['sentences_extracted'] += len(sentences)
        return sentences
    
    def _extract_from_articles_click_through(
        self,
        website_config: Dict,
        category_config: Dict,
        max_articles: Optional[int] = None
    ) -> List[str]:
        """
        Extract sentences using click-through navigation.
        
        Clicks article elements from list page instead of navigating to URLs.
        Uses browser back button for efficient navigation.
        
        Args:
            website_config: Website configuration
            category_config: Category configuration with merged selectors
            max_articles: Maximum articles to process
        
        Returns:
            List of extracted sentences
        """
        sentences = []
        selectors = category_config.get('selectors', website_config.get('selectors', {}))
        
        # Get timing configuration
        article_wait = category_config.get('article_wait', website_config.get('article_wait', 2))
        back_delay = category_config.get('back_delay', 0.5)  # Fast back navigation
        
        # Track the list page URL as backup
        list_page_url = self.driver.current_url
        
        logger.info(f"   🖱️  Click-through mode: Using browser back button for fast navigation")
        
        # Extract article list ONCE at the beginning (optimization)
        article_list_selector = selectors.get('article_list')
        initial_elements = self._extract_article_elements(category_config)
        
        if not initial_elements:
            logger.warning("   No article elements found for click-through navigation")
            return []
        
        # Determine how many articles to process
        total_articles = len(initial_elements)
        articles_to_process = min(total_articles, max_articles) if max_articles else total_articles
        
        logger.info(f"   Found {total_articles} articles, will process {articles_to_process}")
        
        # Process each article by index
        for article_index in range(articles_to_process):
            try:
                # Re-select current article element (after back button, elements become stale)
                current_elements = self._find_elements(article_list_selector, category_config)
                
                if article_index >= len(current_elements):
                    logger.warning(f"   Article {article_index + 1} no longer available, stopping")
                    break
                
                element = current_elements[article_index]
                
                # Get article URL for logging
                try:
                    article_url = element.get_attribute('href')
                except:
                    article_url = "unknown"
                
                # Skip if already scraped
                if article_url != "unknown" and self.is_article_scraped(article_url):
                    logger.debug(f"   ⏭️  Skipping already scraped article: {article_url}")
                    continue
                
                # Click the article element
                if not self._click_element(element, article_index + 1):
                    continue
                
                # Wait for article page to load
                time.sleep(article_wait)
                
                # Extract content
                article_text = self._extract_article_content_selenium(
                    selectors, website_config
                )
                
                # Process extracted text
                if article_text:
                    full_text = ' '.join(article_text)
                    
                    # Language detection
                    if not self._check_language(full_text, website_config):
                        self.driver.back()
                        time.sleep(back_delay)
                        continue
                    
                    # Deduplication
                    if self.deduplicator:
                        is_dup, reason = self.deduplicator.is_duplicate(
                            {},
                            article_url,
                            article_text[0] if article_text else '',
                            full_text
                        )
                        if is_dup:
                            logger.debug(f"   Skipping duplicate: {reason}")
                            self.stats['duplicates_skipped'] += 1
                            self.driver.back()
                            time.sleep(back_delay)
                            continue
                    
                    # Get delimiter
                    body_selector = selectors.get('article_body', 'p')
                    delimiter = self._get_delimiter(body_selector)
                    
                    # Add sentences
                    if delimiter:
                        combined_text = delimiter.join(article_text)
                        split_sentences = [
                            s.strip() for s in combined_text.split(delimiter) 
                            if s.strip() and len(s.strip()) > 20
                        ]
                        sentences.extend(split_sentences)
                    else:
                        sentences.extend(article_text)
                    
                    self.stats['articles_processed'] += 1
                    
                    # Mark article as scraped
                    if article_url != "unknown":
                        self.save_scraped_article(article_url)
                
                # Navigate back to list page using browser back button
                self.driver.back()
                time.sleep(back_delay)
                
                if (article_index + 1) % 5 == 0:
                    logger.info(f"   Processed {article_index + 1}/{articles_to_process} articles...")
                
            except Exception as e:
                logger.warning(f"   Error processing article {article_index + 1}: {e}")
                # Try to get back to list page
                try:
                    self.driver.back()
                    time.sleep(back_delay)
                except:
                    # If back fails, navigate to list page URL (last resort)
                    try:
                        logger.debug("   Back button failed, reloading list page...")
                        self.driver.get(list_page_url)
                        time.sleep(2)
                    except:
                        logger.error("   Could not return to list page, aborting")
                        break
                continue
        
        self.stats['sentences_extracted'] += len(sentences)
        return sentences
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _extract_article_flaresolverr(
        self,
        link: str,
        selectors: Dict
    ) -> List[str]:
        """
        Extract article content using FlareSolverr.
        
        Args:
            link: Article URL
            selectors: Selector configuration
        
        Returns:
            List of text paragraphs (including title)
        """
        html = self._flaresolverr_get(link)
        if not html:
            return []
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Attempt to load lxml for XPath support
        lxml_doc = None
        try:
            import lxml.html as lh
            lxml_doc = lh.fromstring(html)
        except Exception:
            pass
        
        # Helper: extract text from lxml or BeautifulSoup node
        def _node_text(node):
            try:
                return node.text_content().strip()  # lxml
            except Exception:
                try:
                    return node.get_text(strip=True)  # BeautifulSoup
                except Exception:
                    return ''
        
        article_text = []
        
        # Extract title
        title = self._extract_title_from_html(soup, lxml_doc, selectors, _node_text)
        if title and len(title.strip()) > 20:
            article_text.append(title.strip())
        
        # Extract body content
        body_text = self._extract_body_from_html(soup, lxml_doc, selectors, _node_text)
        article_text.extend(body_text)
        
        return article_text
    
    def _extract_article_selenium(
        self,
        link: str,
        website_config: Dict,
        category_config: Dict,
        selectors: Dict
    ) -> List[str]:
        """
        Extract article content using Selenium.
        
        Args:
            link: Article URL
            website_config: Website configuration
            category_config: Category configuration
            selectors: Selector configuration
        
        Returns:
            List of text paragraphs (including title)
        """
        if not self._safe_get(link):
            return []
        
        # Wait for article page content
        self._wait_for_page(website_config, category_config, page_type='article')
        
        return self._extract_article_content_selenium(selectors, website_config)
    
    def _extract_article_content_selenium(
        self,
        selectors: Dict,
        website_config: Dict
    ) -> List[str]:
        """
        Extract article content from current Selenium page.
        
        Args:
            selectors: Selector configuration
            website_config: Website configuration
        
        Returns:
            List of text paragraphs (including title)
        """
        article_text = []
        
        # Extract title
        title = self._extract_text(selectors.get('article_title'))
        if title and len(title.strip()) > 20:
            article_text.append(title.strip())
        
        # Extract content using article_body
        body_selector = selectors.get('article_body', 'p')
        paragraphs = self._find_elements(body_selector, website_config)
        
        # Extract text from paragraphs
        for p in paragraphs:
            try:
                text = p.text.strip()
                # Clean HTML tags that might be in the text
                text = re.sub(r'<[^>]+>', '', text)
                if len(text) > 20:
                    article_text.append(text)
            except:
                continue
        
        # Log extraction results
        logger.info(f"   📝 Found title + {len(paragraphs)} paragraph elements, {len(article_text)} total with >20 chars")
        if article_text:
            logger.info(f"      First: {article_text[0][:80]}...")
        
        return article_text
    
    def _extract_title_from_html(
        self,
        soup,
        lxml_doc,
        selectors: Dict,
        node_text_func
    ) -> str:
        """
        Extract title from HTML using BeautifulSoup and/or lxml.
        
        Args:
            soup: BeautifulSoup parsed HTML
            lxml_doc: lxml parsed HTML (or None)
            selectors: Selector configuration
            node_text_func: Function to extract text from node
        
        Returns:
            Extracted title or empty string
        """
        title = None
        title_selector = selectors.get('article_title')
        
        if not title_selector:
            return ''
        
        # Normalize to list
        t_selectors = title_selector if isinstance(title_selector, list) else [title_selector]
        
        for sel in t_selectors:
            if not sel:
                continue
            
            # XPath selector - use lxml if available
            if (isinstance(sel, str) and (sel.startswith('//') or sel.startswith('/'))) and lxml_doc is not None:
                try:
                    res = lxml_doc.xpath(sel)
                    if res:
                        title = node_text_func(res[0])
                        break
                except Exception:
                    pass
            else:
                try:
                    elem = soup.select_one(sel)
                    if elem:
                        title = elem.get_text(strip=True)
                        break
                except Exception:
                    continue
        
        return title or ''
    
    def _extract_body_from_html(
        self,
        soup,
        lxml_doc,
        selectors: Dict,
        node_text_func
    ) -> List[str]:
        """
        Extract body content from HTML using BeautifulSoup and/or lxml.
        
        Args:
            soup: BeautifulSoup parsed HTML
            lxml_doc: lxml parsed HTML (or None)
            selectors: Selector configuration
            node_text_func: Function to extract text from node
        
        Returns:
            List of text paragraphs
        """
        body_selector = selectors.get('article_body', 'p')
        paragraphs = []
        
        # Handle dict format: {selector: '...', multiple: true, delimiter: '\n'}
        actual_selector = body_selector
        if isinstance(body_selector, dict):
            actual_selector = body_selector.get('selector', 'p')
        
        # Normalize selectors list
        sel_list = actual_selector if isinstance(actual_selector, list) else [actual_selector]
        
        # Try selectors in order
        for sel in sel_list:
            if not sel:
                continue
            
            # XPath
            if isinstance(sel, str) and (sel.startswith('//') or sel.startswith('/')):
                if lxml_doc is None:
                    continue
                try:
                    nodes = lxml_doc.xpath(sel)
                    if nodes:
                        paragraphs = nodes
                        break
                except Exception:
                    continue
            else:
                try:
                    bs_nodes = soup.select(sel)
                    if bs_nodes:
                        paragraphs = bs_nodes
                        break
                except Exception:
                    continue
        
        # Extract text from paragraphs
        body_text = []
        for p in paragraphs:
            text = node_text_func(p)
            if len(text) > 20:
                body_text.append(text)
        
        return body_text
    
    def _get_delimiter(self, body_selector) -> str:
        """
        Extract delimiter from selector configuration.
        
        Args:
            body_selector: Body selector (can be string, list, or dict)
        
        Returns:
            Delimiter string or None
        """
        delimiter = None
        if isinstance(body_selector, dict) and 'delimiter' in body_selector:
            delimiter = body_selector.get('delimiter', '\\n')
            if delimiter == '\\n':
                delimiter = '\n'
        return delimiter
    
    def _batch_language_check(self, texts: List[str], website_config: Dict) -> bool:
        """
        Perform batch language detection for efficiency.
        
        Samples first 5-10 sentences to determine overall language.
        This is 90%+ faster than individual detection for homogeneous content.
        Falls back to individual detection if batch check is inconclusive.
        
        Args:
            texts: List of text strings to check
            website_config: Website configuration
        
        Returns:
            True if content passes language filter
        """
        if not self.lang_detector or not texts:
            return True
        
        # Get language filter
        lang_filter = website_config.get('language_detection', {}).get('filter', [])
        if not lang_filter:
            return True  # No filter, accept all
        
        # Sample first few texts for batch detection
        sample_size = min(10, len(texts))
        sample_texts = texts[:sample_size]
        combined = ' '.join(sample_texts)
        
        try:
            detected_lang = self.lang_detector.detect(combined)
            logger.info(f"   🌍 Batch detected language: {detected_lang}")
            
            if detected_lang in lang_filter:
                return True  # Batch check passed
            else:
                logger.info(f"   ⚠️  Batch language check failed ({detected_lang} not in {lang_filter})")
                return False
        except Exception as e:
            logger.debug(f"   Batch language detection failed: {e}, falling back to individual checks")
            # Fall back to individual detection
            return self._check_language(' '.join(texts), website_config)
    
    def _check_language(self, text: str, website_config: Dict) -> bool:
        """
        Check if text language matches filter.
        
        Args:
            text: Text to check
            website_config: Website configuration
        
        Returns:
            True if language matches filter or no filter configured
        """
        if not self.lang_detector:
            return True
        
        lang = self.lang_detector.detect(text)
        logger.info(f"   🌍 Detected language: {lang}")
        
        # Filter by language if configured
        lang_filter = website_config.get('language_detection', {}).get('filter', [])
        if lang_filter:
            logger.info(f"   📋 Language filter: {lang_filter}")
            if lang not in lang_filter:
                logger.info(f"   ⚠️  Skipping article (language '{lang}' not in filter {lang_filter})")
                return False
        
        return True
    
    def _click_element(self, element, index: int) -> bool:
        """
        Click an element with fallback to JavaScript click.
        
        Args:
            element: WebElement to click
            index: Element index for logging
        
        Returns:
            True if click successful, False otherwise
        """
        try:
            element.click()
            return True
        except Exception as click_error:
            logger.debug(f"   Direct click failed, trying JavaScript click: {click_error}")
            try:
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except Exception as js_error:
                logger.warning(f"   Could not click article {index}: {js_error}")
                return False
