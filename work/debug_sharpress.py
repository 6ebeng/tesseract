#!/usr/bin/env python3
"""Debug Sharpress categories one by one"""

import sys
sys.path.insert(0, '/mnt/c/tesseract/work/tools')

from scrapers import SharpressScraper
import time

print("=" * 70)
print("🔍 SHARPRESS CATEGORY DEBUG TEST")
print("=" * 70)

categories = [
    ('Political', 'https://www.sharpress.net/all-hawal.aspx?Cor=Herem&Nawnishan=%DA%A9%D9%88%D8%B1%D8%AF%D8%B3%D8%AA%D8%A7%D9%86'),
    ('Economy', 'https://www.sharpress.net/all-hawal.aspx?Cor=abwri&Nawnishan=%D8%A6%D8%A7%D8%A8%D9%88%D8%B1%DB%8C'),
    ('Sport', 'https://www.sharpress.net/all-hawal.aspx?Cor=Werziş&Nawnishan=%D9%88%DB%95%D8%B1%D8%B2%D8%B4'),
    ('Culture', 'https://www.sharpress.net/all-hawal.aspx?Cor=Kültür&Nawnishan=%DA%A9%D9%88%D9%84%D8%AA%D9%88%D9%88%D8%B1'),
    ('Health', 'https://www.sharpress.net/all-hawal.aspx?Cor=tandrwsti&Nawnishan=%D8%AA%DB%95%D9%86%D8%AF%D8%B1%D9%88%D8%B3%D8%AA%DB%8C'),
    ('Opinion', 'https://www.sharpress.net/opinion.aspx?Cor=Birura&Nawnishan=%D8%A8%DB%8C%D8%B1%D9%88%DA%95%D8%A7'),
    ('Research', 'https://www.sharpress.net/all-hawal.aspx?Cor=Dose&Nawnishan=%D8%AA%D9%88%DB%8E%DA%98%DB%8C%D9%86%DB%95%D9%88%DB%95%20%D9%88%20%D8%B4%DB%8C%DA%A9%D8%A7%D8%B1%DB%8C%DB%8C')
]

results = {}

for cat_name, url in categories:
    print(f"\n{'='*70}")
    print(f"Testing: {cat_name}")
    print(f"URL: {url}")
    print(f"{'='*70}")
    
    scraper = SharpressScraper()
    
    try:
        # Initialize fresh browser for each category
        scraper.init_driver()
        print(f"✅ Browser initialized for {cat_name}")
        
        # Test the category with 1 page
        result = scraper._scrape_category(cat_name, url, pages=1)
        
        results[cat_name] = {
            'status': 'SUCCESS',
            'sentences': result,
            'url': url
        }
        
        print(f"✅ {cat_name}: {result} sentences collected")
        
    except Exception as e:
        results[cat_name] = {
            'status': 'FAILED',
            'error': str(e),
            'url': url
        }
        print(f"❌ {cat_name} failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Always close the browser
        try:
            if scraper.driver:
                scraper.driver.quit()
                print(f"🔄 Browser closed for {cat_name}")
        except:
            pass
        
        # Wait a bit between categories
        time.sleep(2)

print("\n" + "=" * 70)
print("📊 FINAL RESULTS")
print("=" * 70)

total_sentences = 0
working = 0
failed = 0

for cat_name, data in results.items():
    status_icon = "✅" if data['status'] == 'SUCCESS' else "❌"
    if data['status'] == 'SUCCESS':
        print(f"{status_icon} {cat_name}: {data['sentences']} sentences")
        total_sentences += data['sentences']
        working += 1
    else:
        print(f"{status_icon} {cat_name}: FAILED - {data.get('error', 'Unknown error')}")
        failed += 1

print("\n" + "=" * 70)
print(f"✅ Working categories: {working}/{len(categories)}")
print(f"❌ Failed categories: {failed}/{len(categories)}")
print(f"📝 Total sentences: {total_sentences}")
print("=" * 70)
