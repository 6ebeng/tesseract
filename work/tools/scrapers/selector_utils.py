"""
Selector Utilities

Common selector operations used across scraper, validator, and tools.
Eliminates ~50 lines of duplication.

Usage:
    from selector_utils import SelectorUtils
    
    # Normalize any selector format to standard dict
    normalized = SelectorUtils.normalize_selector('div.article')
    # Returns: {'type': 'css', 'value': 'div.article'}
    
    # Check if selector is XPath
    is_xpath = SelectorUtils.is_xpath('//div[@class="article"]')
    # Returns: True
    
    # Extract selector value from any format
    value = SelectorUtils.extract_value({'selector': 'div.article'})
    # Returns: 'div.article'
"""

from typing import Any, Dict, List, Union, Optional
import logging

logger = logging.getLogger(__name__)


class SelectorUtils:
    """Utilities for working with CSS and XPath selectors"""
    
    @staticmethod
    def normalize_selector(selector: Any) -> Union[Dict, List[Dict]]:
        """
        Normalize selector to standard format
        
        Handles all selector formats:
        - String: 'div.article' → {'type': 'css', 'value': 'div.article'}
        - Dict with 'selector': {'selector': '...', 'multiple': true} → extract
        - Dict with 'value': {'type': 'xpath', 'value': '//...'} → keep
        - List: [...] → normalize each item (fallback chain)
        
        Args:
            selector: Selector in any supported format
        
        Returns:
            Normalized selector dict or list of dicts
        
        Examples:
            # String shorthand
            SelectorUtils.normalize_selector('div.article')
            # → {'type': 'css', 'value': 'div.article'}
            
            # New format with multiple
            SelectorUtils.normalize_selector({
                'selector': 'div.content p',
                'multiple': True,
                'delimiter': '\\n'
            })
            # → {'type': 'css', 'value': 'div.content p', 'multiple': True, ...}
            
            # Fallback chain
            SelectorUtils.normalize_selector(['h1.title', 'h1', 'h2'])
            # → [{'type': 'css', 'value': 'h1.title'}, ...]
        """
        if isinstance(selector, str):
            # Simple string - detect type by syntax
            selector_type = 'xpath' if SelectorUtils.is_xpath(selector) else 'css'
            return {'type': selector_type, 'value': selector}
        
        elif isinstance(selector, dict):
            # Dict format - handle both old and new formats
            if 'selector' in selector:
                # New format: {'selector': '...', 'multiple': true, 'delimiter': '\n'}
                actual_selector = selector['selector']
                
                # Recursively normalize the actual selector
                if isinstance(actual_selector, str):
                    selector_type = 'xpath' if SelectorUtils.is_xpath(actual_selector) else 'css'
                    result = {'type': selector_type, 'value': actual_selector}
                elif isinstance(actual_selector, list):
                    # Selector is a fallback chain
                    result = {'type': 'fallback', 'value': actual_selector}
                elif isinstance(actual_selector, dict):
                    # Nested dict
                    result = SelectorUtils.normalize_selector(actual_selector)
                else:
                    raise ValueError(f"Invalid selector format: {selector}")
                
                # Preserve additional options
                for key in ['multiple', 'delimiter', 'join']:
                    if key in selector:
                        result[key] = selector[key]
                
                return result
            
            elif 'value' in selector:
                # Old format: {'type': 'xpath', 'value': '//...'}
                return {
                    'type': selector.get('type', 'css'),
                    'value': selector['value'],
                    'multiple': selector.get('multiple', False),
                    'join': selector.get('join', '\n')
                }
            
            else:
                raise ValueError(f"Selector dict missing 'selector' or 'value': {selector}")
        
        elif isinstance(selector, list):
            # List of selectors - normalize each one (fallback chain)
            return [SelectorUtils.normalize_selector(s) for s in selector]
        
        elif selector is None:
            # None is valid (means no selector)
            return None
        
        else:
            raise ValueError(f"Invalid selector type: {type(selector)}")
    
    @staticmethod
    def is_xpath(selector_value: str) -> bool:
        """
        Check if selector string is XPath syntax
        
        Args:
            selector_value: Selector string
        
        Returns:
            True if XPath, False if CSS
        
        Examples:
            SelectorUtils.is_xpath('//div[@class="article"]')  # True
            SelectorUtils.is_xpath('/html/body/div')  # True
            SelectorUtils.is_xpath('div.article')  # False
        """
        if not isinstance(selector_value, str):
            return False
        return selector_value.startswith('//') or selector_value.startswith('/')
    
    @staticmethod
    def extract_value(selector: Any) -> Optional[str]:
        """
        Extract the actual selector value from any format
        
        Args:
            selector: Selector in any format
        
        Returns:
            Selector value string, or None
        
        Examples:
            SelectorUtils.extract_value('div.article')
            # → 'div.article'
            
            SelectorUtils.extract_value({'selector': 'div.article'})
            # → 'div.article'
            
            SelectorUtils.extract_value({'type': 'xpath', 'value': '//div'})
            # → '//div'
        """
        if isinstance(selector, str):
            return selector
        elif isinstance(selector, dict):
            if 'selector' in selector:
                actual = selector['selector']
                if isinstance(actual, str):
                    return actual
                elif isinstance(actual, list) and len(actual) > 0:
                    # Return first item in fallback chain
                    return SelectorUtils.extract_value(actual[0])
                else:
                    return SelectorUtils.extract_value(actual)
            elif 'value' in selector:
                return selector['value']
        elif isinstance(selector, list) and len(selector) > 0:
            # Return first item in list
            return SelectorUtils.extract_value(selector[0])
        
        return None
    
    @staticmethod
    def is_fallback_chain(selector: Any) -> bool:
        """
        Check if selector is a fallback chain (list of selectors)
        
        Args:
            selector: Selector in any format
        
        Returns:
            True if selector is a fallback chain
        
        Examples:
            SelectorUtils.is_fallback_chain(['h1.title', 'h1', 'h2'])
            # → True
            
            SelectorUtils.is_fallback_chain('div.article')
            # → False
        """
        return isinstance(selector, list)
    
    @staticmethod
    def get_selector_type(selector: Any) -> str:
        """
        Get selector type: 'css', 'xpath', or 'fallback'
        
        Args:
            selector: Selector in any format
        
        Returns:
            Selector type string
        
        Examples:
            SelectorUtils.get_selector_type('div.article')  # 'css'
            SelectorUtils.get_selector_type('//div')  # 'xpath'
            SelectorUtils.get_selector_type(['h1', 'h2'])  # 'fallback'
        """
        if isinstance(selector, list):
            return 'fallback'
        elif isinstance(selector, str):
            return 'xpath' if SelectorUtils.is_xpath(selector) else 'css'
        elif isinstance(selector, dict):
            if 'type' in selector:
                return selector['type']
            elif 'selector' in selector:
                return SelectorUtils.get_selector_type(selector['selector'])
            elif 'value' in selector:
                return 'xpath' if SelectorUtils.is_xpath(selector['value']) else 'css'
        
        return 'unknown'
    
    @staticmethod
    def has_multiple_option(selector: Any) -> bool:
        """
        Check if selector has 'multiple' option enabled
        
        Args:
            selector: Selector in any format
        
        Returns:
            True if multiple option is enabled
        
        Examples:
            SelectorUtils.has_multiple_option({
                'selector': 'div.content p',
                'multiple': True
            })
            # → True
        """
        if isinstance(selector, dict):
            return selector.get('multiple', False)
        return False
    
    @staticmethod
    def get_delimiter(selector: Any) -> str:
        """
        Get delimiter/join string for multiple results
        
        Args:
            selector: Selector in any format
        
        Returns:
            Delimiter string (default: '\\n')
        
        Examples:
            SelectorUtils.get_delimiter({
                'selector': 'div.content p',
                'multiple': True,
                'delimiter': '\\n\\n'
            })
            # → '\\n\\n'
        """
        if isinstance(selector, dict):
            # Check both 'delimiter' and 'join' (new and old formats)
            delimiter = selector.get('delimiter') or selector.get('join', '\n')
            # Handle escaped newlines
            if delimiter == '\\n':
                delimiter = '\n'
            return delimiter
        return '\n'
    
    @staticmethod
    def to_config_format(selector_type: str, selector_value: str, 
                        multiple: bool = False, delimiter: str = '\n') -> Dict:
        """
        Convert selector components to config dict format
        
        Args:
            selector_type: 'css' or 'xpath'
            selector_value: Selector string
            multiple: Extract multiple elements
            delimiter: Join delimiter for multiple elements
        
        Returns:
            Selector dict in config format
        
        Examples:
            SelectorUtils.to_config_format('xpath', '//div//p', 
                                          multiple=True, delimiter='\\n')
            # → {'type': 'xpath', 'value': '//div//p', 'multiple': True, 'join': '\\n'}
        """
        result = {
            'type': selector_type,
            'value': selector_value
        }
        
        if multiple:
            result['multiple'] = True
            result['join'] = delimiter
        
        return result


# Convenience functions

def normalize(selector: Any) -> Union[Dict, List[Dict]]:
    """Shorthand for SelectorUtils.normalize_selector()"""
    return SelectorUtils.normalize_selector(selector)


def is_xpath(selector: str) -> bool:
    """Shorthand for SelectorUtils.is_xpath()"""
    return SelectorUtils.is_xpath(selector)


def extract_value(selector: Any) -> Optional[str]:
    """Shorthand for SelectorUtils.extract_value()"""
    return SelectorUtils.extract_value(selector)
