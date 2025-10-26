#!/usr/bin/env python3
"""
Batch update all remaining configs to new structure
"""

import yaml
from pathlib import Path

configs_dir = Path('configs')

# Files to update with their mappings
updates = {
    'awene.yaml': {
        'pagination': {'type': 'pagination', 'pages': 5, 'delay': 2},
        'selectors': {
            'article_list': '.newstopsumbtitle a',
            'article_title': ['h1', 'h2', '.title'],
            'article_body': ['.viewdesc p', 'p']
        },
        'wait': {'selector': None, 'timeout': 2}
    },
    'khak.yaml': {
        'pagination': {'type': 'pagination', 'pages': 10, 'delay': 2},
        'selectors': {
            'article_list': 'a[href*="/article/"]',
            'article_title': ['h1', 'h2', '.title'],
            'article_body': ['main', '.html-content p', '.content p', 'p']
        },
        'wait': {'selector': None, 'timeout': 2}
    },
    'xendan.yaml': {
        'pagination': {'type': 'pagination', 'pages': 5, 'delay': 2},
        'selectors': {
            'article_list': '.card-small',
            'article_title': ['.detail-top h1', 'h2', 'h1'],
            'article_body': ['.detail-big-text-p p', 'p']
        },
        'wait': {'selector': None, 'timeout': 2}
    },
    'lvinpress.yaml': {
        'pagination': {'type': 'pagination', 'pages': 5, 'delay': 2},
        'selectors': {
            'article_list': 'article.elementor-post h3.elementor-post__title a',
            'article_title': ['h1.elementor-heading-title', 'h2.elementor-heading-title', 'h1', 'h2'],
            'article_body': ['.entry-content p', 'div.elementor-widget-theme-post-content div.elementor-widget-container', 'p']
        },
        'wait': {'selector': None, 'timeout': 2}
    },
    'balinde.yaml': {
        'pagination': {'type': 'pagination', 'pages': 5, 'delay': 2},
        'selectors': {
            'article_list': 'div.cards a.card',
            'article_title': ['h1', 'h2', '.title'],
            'article_body': ['.entry-content p', 'div.poet-timeline p', 'p']
        },
        'wait': {'selector': None, 'timeout': 2}
    },
    'kurdistan24.yaml': {
        'pagination': {'type': 'pagination', 'pages': 10, 'delay': 2},
        'selectors': {
            'article_list': '.views-row',
            'article_title': ['h1.text-black', 'h1', 'h2'],
            'article_body': ['.content p', 'p']
        },
        'wait': {'selector': None, 'timeout': 2}
    }
}

print("="*80)
print("Config files to update:")
for filename in updates.keys():
    filepath = configs_dir / filename
    exists = "✅" if filepath.exists() else "❌"
    print(f"  {exists} {filename}")

print("\n" + "="*80)
print("NEW STRUCTURE:")
print("="*80)
print("""
# Universal pagination (applies to all categories)
pagination:
  type: 'pagination'
  pages: 5
  delay: 2

selectors:
  article_list: 'a.link'
  article_title: ['h1', 'h2']
  article_body: ['.content p', 'p']  # Merged content+paragraphs

wait:
  selector: null  # or CSS selector
  timeout: 2

categories:
  category_name:
    url: 'https://...'
    # Inherits pagination and selectors
""")

print("\n" + "="*80)
print("Manual update required - edit each file to match new structure")
print("="*80)
