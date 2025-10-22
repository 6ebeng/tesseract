#!/usr/bin/env python3
"""Quick diagnostic - test each scraper for 30 seconds max"""

import sys
import signal
sys.path.insert(0, '/mnt/c/tesseract/work/tools')

from scrapers import (
    KurdsatScraper, RudawScraper, KhakScraper, NRTScraper,
    AweneScraper, Kurdistan24Scraper, XendanScraper, SekokurdScraper
)

def timeout_handler(signum, frame):
    raise TimeoutError("Scraper timed out")

def test_scraper(name, scraper_class, test_political=True, test_specialized=False):
    """Test a single scraper with timeout"""
    print(f"\n{'='*70}")
    print(f"Testing {name}")
    print('='*70)
    
    scraper = scraper_class()
    results = {'political': 0, 'specialized': 0, 'error': None}
    
    try:
        # Test political (30 sec timeout)
        if test_political and hasattr(scraper, 'scrape_political'):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)
            try:
                scraper.scrape_political(pages=1, clicks=1, scrolls=1)
                results['political'] = len(scraper.sentences)
                print(f"   Political: {results['political']} sentences")
            except TimeoutError:
                print(f"   Political: TIMEOUT (>30s)")
            except NotImplementedError:
                print(f"   Political: Not implemented")
            except Exception as e:
                print(f"   Political: ERROR - {str(e)[:50]}")
            finally:
                signal.alarm(0)
        
        # Test specialized (30 sec timeout)
        if test_specialized:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)
            try:
                scraper.scrape_specialized(articles_per_category=3, clicks=1, pages_per_category=1)
                results['specialized'] = len(scraper.sentences) - results['political']
                print(f"   Specialized: {results['specialized']} sentences")
            except TimeoutError:
                print(f"   Specialized: TIMEOUT (>30s)")
            except Exception as e:
                print(f"   Specialized: ERROR - {str(e)[:50]}")
            finally:
                signal.alarm(0)
        
        # Show samples
        if scraper.sentences:
            print(f"\n   ✅ Total: {len(scraper.sentences)} sentences")
            print(f"   📄 Samples:")
            for i, sent in enumerate(list(scraper.sentences)[:2], 1):
                print(f"      {i}. {sent[:60]}...")
        else:
            print(f"\n   ❌ NO SENTENCES COLLECTED")
            results['error'] = 'No sentences'
        
    except Exception as e:
        results['error'] = str(e)[:100]
        print(f"   ❌ FATAL ERROR: {results['error']}")
    
    finally:
        try:
            scraper.cleanup()
        except:
            pass
    
    return results

# Test all scrapers
print("="*70)
print("QUICK DIAGNOSTIC TEST")
print("Testing each scraper with 30-second timeout")
print("="*70)

results_summary = {}

# 1. Kurdsat
results_summary['Kurdsat'] = test_scraper('Kurdsat', KurdsatScraper, True, True)

# 2. Rudaw
results_summary['Rudaw'] = test_scraper('Rudaw', RudawScraper, True, True)

# 3. Khak
results_summary['Khak'] = test_scraper('Khak', KhakScraper, True, False)

# 4. NRT
results_summary['NRT'] = test_scraper('NRT', NRTScraper, True, False)

# 5. Awene
results_summary['Awene'] = test_scraper('Awene', AweneScraper, True, True)

# 6. Kurdistan24
results_summary['Kurdistan24'] = test_scraper('Kurdistan24', Kurdistan24Scraper, True, True)

# 7. Xendan
results_summary['Xendan'] = test_scraper('Xendan', XendanScraper, True, True)

# 8. Sekokurd
results_summary['Sekokurd'] = test_scraper('Sekokurd', SekokurdScraper, False, True)

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"\n{'Scraper':<15} {'Political':<12} {'Specialized':<12} {'Status'}")
print("-"*70)

for name, res in results_summary.items():
    pol = f"✅ {res['political']}" if res['political'] > 0 else "❌ 0"
    spec = f"✅ {res['specialized']}" if res['specialized'] > 0 else "❌ 0"
    status = "⚠️ " + res['error'][:20] if res['error'] else "✅ OK"
    print(f"{name:<15} {pol:<12} {spec:<12} {status}")

print("\n" + "="*70)
working = sum(1 for r in results_summary.values() if r['political'] > 0 or r['specialized'] > 0)
print(f"Working: {working}/8 scrapers")
print("="*70)
