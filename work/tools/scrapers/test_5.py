#!/usr/bin/env python3
from generic_scraper import GenericScraper

s = GenericScraper('websites.yaml')
sentences = s.scrape_category('kurdsat', 'news', max_articles=5)

print(f'\n✅ Extracted {len(sentences)} sentences from 5 articles')
print('\nFirst 5 sentences:')
for i, sent in enumerate(sentences[:5]):
    print(f'{i+1}. {sent[:120]}...')
