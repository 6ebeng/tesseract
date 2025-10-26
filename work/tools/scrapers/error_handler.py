"""
Error Handling Framework for Web Scrapers

Provides comprehensive error handling with:
- Retry logic with exponential backoff
- Graceful degradation for selector failures
- WebDriver crash recovery
- Error logging and classification

Usage:
    from error_handler import ScraperErrorHandler
    
    handler = ScraperErrorHandler(max_retries=3)
    
    # Safe scraping with auto-retry
    result = handler.safe_scrape(scraper.scrape_category, 'politics', pages=5)
    
    # Get error summary
    handler.print_summary()
"""

import time
import logging
from datetime import datetime
from typing import Callable, Any, Dict, List, Optional
from enum import Enum
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
    StaleElementReferenceException,
    ElementNotInteractableException
)


class ErrorType(Enum):
    """Classification of error types"""
    TIMEOUT = "timeout"
    ELEMENT_NOT_FOUND = "element_not_found"
    STALE_ELEMENT = "stale_element"
    DRIVER_CRASH = "driver_crash"
    NETWORK = "network"
    INVALID_CONFIG = "invalid_config"
    UNEXPECTED = "unexpected"


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"           # Recoverable, no impact
    MEDIUM = "medium"     # Partial failure, degraded operation
    HIGH = "high"         # Complete failure, needs attention
    CRITICAL = "critical" # System-wide issue, requires immediate action


class ScraperError:
    """Represents a scraper error with context"""
    
    def __init__(
        self,
        error_type: ErrorType,
        severity: ErrorSeverity,
        message: str,
        context: Dict[str, Any],
        exception: Optional[Exception] = None
    ):
        self.error_type = error_type
        self.severity = severity
        self.message = message
        self.context = context
        self.exception = exception
        self.timestamp = datetime.now()
    
    def __str__(self):
        return (
            f"[{self.timestamp.strftime('%H:%M:%S')}] "
            f"{self.severity.value.upper()}: {self.message}"
        )


class ScraperErrorHandler:
    """
    Centralized error handling for web scrapers
    
    Features:
    - Automatic retry with exponential backoff
    - Error classification and tracking
    - WebDriver crash recovery
    - Detailed error logging
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_retry_delay: float = 5.0,
        driver_reinit_callback: Optional[Callable] = None
    ):
        """
        Args:
            max_retries: Maximum retry attempts for transient errors
            base_retry_delay: Base delay between retries (seconds)
            driver_reinit_callback: Function to reinitialize WebDriver after crash
        """
        self.max_retries = max_retries
        self.base_retry_delay = base_retry_delay
        self.driver_reinit_callback = driver_reinit_callback
        
        # Error tracking
        self.errors: List[ScraperError] = []
        self.retry_counts: Dict[str, int] = {}
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def safe_scrape(
        self,
        scrape_func: Callable,
        *args,
        context: Optional[Dict] = None,
        **kwargs
    ) -> Optional[Any]:
        """
        Execute scraping function with automatic retry and error handling
        
        Args:
            scrape_func: Function to execute
            *args: Positional arguments for function
            context: Additional context for error logging
            **kwargs: Keyword arguments for function
        
        Returns:
            Function result or None if all retries failed
        """
        func_name = scrape_func.__name__
        context = context or {}
        context['function'] = func_name
        
        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.info(f"Executing {func_name} (attempt {attempt}/{self.max_retries})")
                result = scrape_func(*args, **kwargs)
                
                # Success - reset retry counter
                if func_name in self.retry_counts:
                    del self.retry_counts[func_name]
                
                return result
                
            except TimeoutException as e:
                error = self._handle_timeout_exception(e, attempt, context)
                if attempt < self.max_retries:
                    self._wait_before_retry(attempt)
                else:
                    self.errors.append(error)
                    return None
            
            except NoSuchElementException as e:
                error = self._handle_element_not_found(e, attempt, context)
                if attempt < self.max_retries:
                    self._wait_before_retry(attempt)
                else:
                    self.errors.append(error)
                    return None
            
            except StaleElementReferenceException as e:
                error = self._handle_stale_element(e, attempt, context)
                if attempt < self.max_retries:
                    self._wait_before_retry(attempt)
                else:
                    self.errors.append(error)
                    return None
            
            except WebDriverException as e:
                if self._is_driver_crash(e):
                    error = self._handle_driver_crash(e, attempt, context)
                    if attempt < self.max_retries:
                        self._wait_before_retry(attempt)
                    else:
                        self.errors.append(error)
                        return None
                else:
                    # Other WebDriver errors
                    error = self._handle_webdriver_exception(e, attempt, context)
                    if attempt < self.max_retries:
                        self._wait_before_retry(attempt)
                    else:
                        self.errors.append(error)
                        return None
            
            except Exception as e:
                error = self._handle_unexpected_exception(e, attempt, context)
                self.errors.append(error)
                # Don't retry unexpected errors
                return None
        
        return None
    
    def _handle_timeout_exception(
        self,
        exception: TimeoutException,
        attempt: int,
        context: Dict
    ) -> ScraperError:
        """Handle timeout exceptions"""
        message = f"Timeout waiting for element (attempt {attempt}/{self.max_retries})"
        
        self.logger.warning(f"{message}: {str(exception)}")
        
        return ScraperError(
            error_type=ErrorType.TIMEOUT,
            severity=ErrorSeverity.MEDIUM if attempt < self.max_retries else ErrorSeverity.HIGH,
            message=message,
            context=context,
            exception=exception
        )
    
    def _handle_element_not_found(
        self,
        exception: NoSuchElementException,
        attempt: int,
        context: Dict
    ) -> ScraperError:
        """Handle element not found exceptions"""
        message = f"Element not found (attempt {attempt}/{self.max_retries})"
        
        self.logger.warning(f"{message}: {str(exception)}")
        
        return ScraperError(
            error_type=ErrorType.ELEMENT_NOT_FOUND,
            severity=ErrorSeverity.MEDIUM,
            message=message,
            context=context,
            exception=exception
        )
    
    def _handle_stale_element(
        self,
        exception: StaleElementReferenceException,
        attempt: int,
        context: Dict
    ) -> ScraperError:
        """Handle stale element exceptions"""
        message = f"Stale element reference (attempt {attempt}/{self.max_retries})"
        
        self.logger.warning(f"{message}: {str(exception)}")
        
        return ScraperError(
            error_type=ErrorType.STALE_ELEMENT,
            severity=ErrorSeverity.LOW,  # Usually recoverable with retry
            message=message,
            context=context,
            exception=exception
        )
    
    def _handle_driver_crash(
        self,
        exception: WebDriverException,
        attempt: int,
        context: Dict
    ) -> ScraperError:
        """Handle WebDriver crash"""
        message = f"WebDriver crashed (attempt {attempt}/{self.max_retries})"
        
        self.logger.error(f"{message}: {str(exception)}")
        
        # Try to reinitialize driver
        if self.driver_reinit_callback:
            try:
                self.logger.info("Attempting to reinitialize WebDriver...")
                self.driver_reinit_callback()
                self.logger.info("WebDriver reinitialized successfully")
            except Exception as reinit_error:
                self.logger.error(f"Failed to reinitialize driver: {reinit_error}")
        
        return ScraperError(
            error_type=ErrorType.DRIVER_CRASH,
            severity=ErrorSeverity.HIGH,
            message=message,
            context=context,
            exception=exception
        )
    
    def _handle_webdriver_exception(
        self,
        exception: WebDriverException,
        attempt: int,
        context: Dict
    ) -> ScraperError:
        """Handle general WebDriver exceptions"""
        message = f"WebDriver error (attempt {attempt}/{self.max_retries})"
        
        self.logger.warning(f"{message}: {str(exception)}")
        
        return ScraperError(
            error_type=ErrorType.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            message=message,
            context=context,
            exception=exception
        )
    
    def _handle_unexpected_exception(
        self,
        exception: Exception,
        attempt: int,
        context: Dict
    ) -> ScraperError:
        """Handle unexpected exceptions"""
        message = f"Unexpected error: {type(exception).__name__}"
        
        self.logger.error(f"{message}: {str(exception)}", exc_info=True)
        
        return ScraperError(
            error_type=ErrorType.UNEXPECTED,
            severity=ErrorSeverity.CRITICAL,
            message=message,
            context=context,
            exception=exception
        )
    
    def _is_driver_crash(self, exception: WebDriverException) -> bool:
        """Check if WebDriver exception indicates a crash"""
        error_msg = str(exception).lower()
        crash_indicators = [
            'chrome crashed',
            'chrome not reachable',
            'session deleted',
            'invalid session',
            'browser closed'
        ]
        return any(indicator in error_msg for indicator in crash_indicators)
    
    def _wait_before_retry(self, attempt: int):
        """Wait before retry with exponential backoff"""
        wait_time = self.base_retry_delay * (2 ** (attempt - 1))
        self.logger.info(f"Waiting {wait_time:.1f}s before retry...")
        time.sleep(wait_time)
    
    def handle_selector_failure(
        self,
        selector_chain: List[str],
        element_name: str,
        context: Dict
    ) -> None:
        """
        Handle when all selectors in fallback chain fail
        
        This is called when all attempts to find an element have failed.
        """
        message = f"All selectors failed for '{element_name}'"
        
        self.logger.warning(message)
        self.logger.debug(f"Tried selectors: {selector_chain}")
        
        error = ScraperError(
            error_type=ErrorType.ELEMENT_NOT_FOUND,
            severity=ErrorSeverity.MEDIUM,
            message=message,
            context={**context, 'selectors': selector_chain, 'element': element_name},
            exception=None
        )
        
        self.errors.append(error)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of all errors"""
        if not self.errors:
            return {'total': 0, 'by_type': {}, 'by_severity': {}}
        
        by_type = {}
        by_severity = {}
        
        for error in self.errors:
            # Count by type
            error_type_str = error.error_type.value
            by_type[error_type_str] = by_type.get(error_type_str, 0) + 1
            
            # Count by severity
            severity_str = error.severity.value
            by_severity[severity_str] = by_severity.get(severity_str, 0) + 1
        
        return {
            'total': len(self.errors),
            'by_type': by_type,
            'by_severity': by_severity
        }
    
    def print_summary(self):
        """Print error summary to console"""
        summary = self.get_error_summary()
        
        if summary['total'] == 0:
            print("✅ No errors encountered")
            return
        
        print(f"\n⚠️  Error Summary: {summary['total']} error(s)")
        print("=" * 60)
        
        print("\nBy Type:")
        for error_type, count in summary['by_type'].items():
            print(f"  • {error_type}: {count}")
        
        print("\nBy Severity:")
        for severity, count in summary['by_severity'].items():
            emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴', 'critical': '💀'}
            print(f"  {emoji.get(severity, '•')} {severity}: {count}")
        
        # Show critical errors
        critical_errors = [e for e in self.errors if e.severity == ErrorSeverity.CRITICAL]
        if critical_errors:
            print("\n💀 CRITICAL ERRORS:")
            for error in critical_errors[:5]:  # Show first 5
                print(f"  • {error.message}")
                if error.context.get('function'):
                    print(f"    Function: {error.context['function']}")
    
    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[ScraperError]:
        """Get all errors of a specific severity"""
        return [e for e in self.errors if e.severity == severity]
    
    def get_errors_by_type(self, error_type: ErrorType) -> List[ScraperError]:
        """Get all errors of a specific type"""
        return [e for e in self.errors if e.error_type == error_type]
    
    def has_critical_errors(self) -> bool:
        """Check if any critical errors occurred"""
        return any(e.severity == ErrorSeverity.CRITICAL for e in self.errors)
    
    def clear_errors(self):
        """Clear error history"""
        self.errors.clear()
        self.retry_counts.clear()
