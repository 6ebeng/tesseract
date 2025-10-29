#!/usr/bin/env python3
"""
Analyze tracked URLs to suggest whitelist patterns for optimization
"""
import re
from pathlib import Path
from collections import Counter
from urllib.parse import urlparse

def analyze_tracked_urls(file_path):
    """Analyze tracked URLs and suggest whitelist patterns"""
    with open(file_path, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    # Parse domains and paths
    domains = []
    paths = []
    extensions = []
    
    for url in urls:
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path
        
        domains.append(domain)
        paths.append(path)
        
        # Extract file extensions
        if '.' in path.split('/')[-1]:
            ext = path.split('.')[-1].split('?')[0].lower()
            if len(ext) <= 5:  # Valid extensions
                extensions.append(ext)
    
    # Count frequencies
    domain_counts = Counter(domains)
    ext_counts = Counter(extensions)
    
    # Identify common path patterns
    path_patterns = []
    for path in paths:
        # Extract path segments
        segments = [s for s in path.split('/') if s]
        if segments:
            path_patterns.append('/' + segments[0] + '/')
    
    pattern_counts = Counter(path_patterns)
    
    return {
        'total_urls': len(urls),
        'domains': domain_counts,
        'extensions': ext_counts,
        'path_patterns': pattern_counts
    }

# Get all tracked URL files
tracked_dir = Path('tracked_urls')
files = sorted(tracked_dir.glob('tracked_urls_*.txt'))

print('🔍 Analyzing tracked URLs for optimization...\n')

results = {}
for file in files:
    website_name = file.stem.replace('tracked_urls_', '').split('_')[0]
    
    if website_name not in results:
        results[website_name] = {
            'files': [],
            'total_urls': 0,
            'domains': Counter(),
            'extensions': Counter(),
            'path_patterns': Counter()
        }
    
    analysis = analyze_tracked_urls(file)
    results[website_name]['files'].append(file.name)
    results[website_name]['total_urls'] += analysis['total_urls']
    results[website_name]['domains'].update(analysis['domains'])
    results[website_name]['extensions'].update(analysis['extensions'])
    results[website_name]['path_patterns'].update(analysis['path_patterns'])

# Print summary and suggestions
for website, data in sorted(results.items()):
    print(f'\n{"="*70}')
    print(f'📊 {website.upper()}')
    print(f'{"="*70}')
    print(f'Total URLs tracked: {data["total_urls"]}')
    print(f'Files analyzed: {len(data["files"])}')
    
    # Top domains
    print(f'\n🌐 Top domains:')
    for domain, count in data['domains'].most_common(5):
        pct = (count / data['total_urls']) * 100
        print(f'  • {domain}: {count} ({pct:.1f}%)')
    
    # Top file types
    if data['extensions']:
        print(f'\n📁 Top file types:')
        for ext, count in data['extensions'].most_common(10):
            print(f'  • .{ext}: {count}')
    
    # Top path patterns
    if data['path_patterns']:
        print(f'\n📂 Top path patterns:')
        for pattern, count in data['path_patterns'].most_common(10):
            print(f'  • {pattern}: {count}')
    
    # Generate suggestions
    print(f'\n💡 Suggested whitelist patterns:')
    
    # Content URLs
    content_urls = []
    for pattern, count in data['path_patterns'].most_common(5):
        if count >= 2:
            content_urls.append(pattern + '*')
    
    if content_urls:
        print(f'  Content:')
        for pattern in content_urls[:5]:
            print(f'    - \'{pattern}\'')
    
    # Static resources
    static_exts = {'js', 'css', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'woff', 'woff2', 'ttf', 'ico', 'webp'}
    needed_static = [ext for ext, count in data['extensions'].items() if ext in static_exts and count >= 3]
    
    if needed_static:
        print(f'  Static resources:')
        for ext in sorted(needed_static)[:10]:
            print(f'    - \'*.{ext}\'')

print(f'\n{"="*70}')
print('✅ Analysis complete!')
