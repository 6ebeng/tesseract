#!/usr/bin/env python3
"""
Compare URL tracking before and after whitelist optimization
"""
from pathlib import Path
from collections import Counter
from urllib.parse import urlparse

def analyze_urls(file_path):
    """Analyze URLs in tracked file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    domains = Counter()
    blocked_patterns = {
        'analytics': 0,
        'tracking': 0,
        'ads': 0,
        'social': 0,
        'fonts': 0,
        'content': 0
    }
    
    for url in urls:
        parsed = urlparse(url)
        domain = parsed.netloc
        domains[domain] += 1
        
        # Categorize
        if any(x in domain for x in ['analytics', 'googletagmanager', 'doubleclick', 'stats.g']):
            blocked_patterns['analytics'] += 1
        elif any(x in domain for x in ['facebook', 'twitter', 'addtoany', 'social']):
            blocked_patterns['social'] += 1
        elif any(x in domain for x in ['googleadservices', 'adservice', 'doubleclick.net']):
            blocked_patterns['ads'] += 1
        elif 'fonts' in domain or 'fonts' in url:
            blocked_patterns['fonts'] += 1
        elif any(x in domain for x in ['cloudflareinsights', 'rum', 'beacon']):
            blocked_patterns['tracking'] += 1
        else:
            blocked_patterns['content'] += 1
    
    return {
        'total': len(urls),
        'domains': domains,
        'categories': blocked_patterns
    }

# Analyze tracked URLs
tracked_file = Path('tracked_urls/tracked_urls_nrt_news.txt')

if tracked_file.exists():
    print('📊 URL Tracking Analysis (NRT News)\n')
    print('='*70)
    
    analysis = analyze_urls(tracked_file)
    
    print(f'\n📈 Total URLs Tracked: {analysis["total"]}')
    
    print(f'\n📂 URL Categories:')
    for category, count in sorted(analysis['categories'].items(), key=lambda x: x[1], reverse=True):
        pct = (count / analysis['total']) * 100
        print(f'  • {category.capitalize()}: {count} ({pct:.1f}%)')
    
    print(f'\n🌐 Top Domains:')
    for domain, count in analysis['domains'].most_common(10):
        pct = (count / analysis['total']) * 100
        print(f'  • {domain}: {count} ({pct:.1f}%)')
    
    # Calculate waste
    wasted = sum([
        analysis['categories']['analytics'],
        analysis['categories']['tracking'],
        analysis['categories']['ads'],
        analysis['categories']['social']
    ])
    waste_pct = (wasted / analysis['total']) * 100
    
    print(f'\n⚠️  Potentially Unnecessary Requests: {wasted} ({waste_pct:.1f}%)')
    print(f'   These could be blocked with better whitelist patterns')
    
    print(f'\n✅ Content Requests: {analysis["categories"]["content"]} ({(analysis["categories"]["content"]/analysis["total"])*100:.1f}%)')
    print(f'   These are essential for scraping')
    
    print('\n' + '='*70)
    print('\n💡 Recommendation:')
    print('   The current whitelist allows too many tracking/analytics URLs.')
    print('   This is because wildcards like "*.js" match ALL JavaScript,')
    print('   including analytics scripts.')
    print('')
    print('   Better approach:')
    print('   - Use domain-specific patterns: "*.nrttv.com/*"')
    print('   - Block analytics explicitly in blacklist')
    print('   - Keep whitelist for essential resources only')

else:
    print(f'❌ File not found: {tracked_file}')
