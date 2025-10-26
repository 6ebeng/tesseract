#!/usr/bin/env python3
"""
Update all YAML configs with proven legacy selectors
"""

import yaml
from pathlib import Path

# Selector mappings from legacy scrapers
LEGACY_SELECTORS = {
    'khak': {
        'article_list': 'a[href*="/article/"]',
        'article_paragraphs': ['main', '.html-content p', '.content p', 'p'],
        'pagination': {
            'type': 'pagination',
            'pages': 10,
            'url_pattern': '?group=5&page={page}'
        }
    },
    'awene': {
        'article_list_title': '.newstopsumbtitle a',
        'article_paragraphs': ['.viewdesc p'],
        'pagination': {
            'type': 'pagination',
            'pages': 10
        }
    },
    'kurdistan24': {
        'note': 'Requires FlareSolverr - Cloudflare protection',
        'article_list': '.views-row',
        'article_title': 'h1.text-black',
        'article_paragraphs': ['.content p']
    },
    'xendan': {
        'article_list': '.card-small',
        'article_title': ['.detail-top h1', 'h2'],
        'article_paragraphs': ['.detail-big-text-p p'],
        'pagination': {
            'type': 'click_next',
            'next_button': 'a.nextbutton'  # Text: 'دواتر'
        }
    },
    'lvinpress': {
        'article_list': 'article.elementor-post h3.elementor-post__title a',
        'article_paragraphs': ['.entry-content p'],
        'url_filter': 'exclude /video/',
        'pagination': {
            'type': 'pagination',
            'pages': 5,
            'url_pattern': '/page/{page_num}'
        }
    },
    'balinde': {
        'article_list': 'div.cards a.card',
        'article_content': 'div.poet-timeline',
        'article_paragraphs': ['.entry-content p'],
        'pagination': {
            'type': 'pagination',
            'pages': 5,
            'url_pattern': '/page/{page_num}/'
        }
    }
}

print("="*80)
print("LEGACY SELECTOR MAPPING")
print("="*80)

for site, selectors in LEGACY_SELECTORS.items():
    print(f"\n{site.upper()}:")
    for key, value in selectors.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}")

print("\n" + "="*80)
print("To apply these changes, manually update the YAML files in configs/")
print("="*80)
