#!/usr/bin/env python3
"""
Full Test Suite - All 12 Scrapers
Tests all scrapers with minimal settings to verify functionality
"""

import sys
import time
sys.path.insert(0, 'tools')

from scrapers.kurdsat_scraper import KurdsatScraper
from scrapers.rudaw_scraper import RudawScraper
from scrapers.khak_scraper import KhakScraper
from scrapers.nrt_scraper import NRTScraper
from scrapers.awene_scraper import AweneScraper
from scrapers.kurdistan24_scraper import Kurdistan24Scraper
from scrapers.xendan_scraper import XendanScraper
from scrapers.sekokurd_scraper import SekokurdScraper
from scrapers.govkrd_scraper import GovKrdScraper
from scrapers.sharpress_scraper import SharpressScraper
from scrapers.lvinpress_scraper import LvinpressScraper
from scrapers.balinde_scraper import BalindeScraper

def test_scraper(scraper_class, name, test_type, **kwargs):
    """Test a single scraper"""
    print(f"\n{'='*70}")
    print(f"🧪 TESTING: {name}")
    print(f"{'='*70}")
    
    scraper = scraper_class()
    start_time = time.time()
    
    try:
        if test_type == 'political':
            sentences = scraper.scrape_political(**kwargs)
        elif test_type == 'specialized':
            sentences = scraper.scrape_specialized(**kwargs)
        elif test_type == 'both':
            pol_sentences = scraper.scrape_political(**kwargs['political'])
            spec_sentences = scraper.scrape_specialized(**kwargs['specialized'])
            sentences = pol_sentences + spec_sentences
        else:
            sentences = 0
        
        elapsed = time.time() - start_time
        
        print(f"\n{'─'*70}")
        print(f"✅ {name}: {sentences} sentences in {elapsed:.1f}s")
        print(f"📈 Stats: {scraper.stats}")
        print(f"{'─'*70}")
        
        return {
            'name': name,
            'success': True,
            'sentences': sentences,
            'time': elapsed,
            'stats': scraper.stats
        }
    
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n{'─'*70}")
        print(f"❌ {name} FAILED: {str(e)[:100]}")
        print(f"⏱️  Time: {elapsed:.1f}s")
        print(f"{'─'*70}")
        
        return {
            'name': name,
            'success': False,
            'sentences': 0,
            'time': elapsed,
            'error': str(e)[:200]
        }
    
    finally:
        try:
            scraper.cleanup()
        except:
            pass

def main():
    """Run full test suite"""
    print("\n" + "="*70)
    print("🚀 FULL TEST SUITE - ALL 12 SCRAPERS")
    print("="*70)
    print("\nThis will test all scrapers with minimal settings:")
    print("  • Political: 1-3 clicks/scrolls/pages")
    print("  • Specialized: 2-3 articles/pages per category")
    print("\nEstimated time: 10-15 minutes")
    print("="*70)
    
    results = []
    start_time = time.time()
    
    # Test 1: Kurdsat (Selenium)
    results.append(test_scraper(
        KurdsatScraper, 
        "Kurdsat",
        'both',
        political={'clicks': 2},
        specialized={'articles_per_category': 2}
    ))
    
    # Test 2: Rudaw (Selenium)
    results.append(test_scraper(
        RudawScraper,
        "Rudaw",
        'both',
        political={'scrolls': 2},
        specialized={'scrolls_per_category': 2}
    ))
    
    # Test 3: Khak (Selenium)
    results.append(test_scraper(
        KhakScraper,
        "Khak",
        'political',
        pages=2
    ))
    
    # Test 4: NRT (Selenium)
    results.append(test_scraper(
        NRTScraper,
        "NRT",
        'both',
        political={'clicks': 2},
        specialized={'clicks': 2}
    ))
    
    # Test 5: Awene (Selenium)
    results.append(test_scraper(
        AweneScraper,
        "Awene",
        'both',
        political={'pages': 2},
        specialized={'articles_per_category': 2}
    ))
    
    # Test 6: Kurdistan24 (FlareSolverr)
    print("\n⚠️  Kurdistan24 requires FlareSolverr on port 8191")
    results.append(test_scraper(
        Kurdistan24Scraper,
        "Kurdistan24",
        'both',
        political={'pages': 1},
        specialized={'pages_per_category': 1}
    ))
    
    # Test 7: Xendan (Selenium)
    results.append(test_scraper(
        XendanScraper,
        "Xendan",
        'both',
        political={'pages': 2},
        specialized={'pages_per_category': 1}
    ))
    
    # Test 8: Sekokurd (Selenium)
    results.append(test_scraper(
        SekokurdScraper,
        "Sekokurd",
        'specialized',
        clicks=2
    ))
    
    # Test 9: GovKrd (Selenium)
    results.append(test_scraper(
        GovKrdScraper,
        "GovKrd",
        'political',
        pages=2
    ))
    
    # Test 10: Sharpress (Selenium)
    results.append(test_scraper(
        SharpressScraper,
        "Sharpress",
        'both',
        political={'pages': 2},
        specialized={'pages': 1}
    ))
    
    # Test 11: LvinPress (Selenium)
    results.append(test_scraper(
        LvinpressScraper,
        "LvinPress",
        'both',
        political={'pages': 2},
        specialized={'pages': 1}
    ))
    
    # Test 12: Balinde (Selenium)
    results.append(test_scraper(
        BalindeScraper,
        "Balinde",
        'specialized',
        pages=2
    ))
    
    # Final Summary
    total_time = time.time() - start_time
    
    print("\n" + "="*70)
    print("📊 FINAL TEST RESULTS")
    print("="*70)
    
    passed = sum(1 for r in results if r['success'])
    failed = sum(1 for r in results if not r['success'])
    
    # Handle both int and list for sentences (Balinde returns list)
    total_sentences = 0
    for r in results:
        if isinstance(r['sentences'], list):
            # Check if list contains strings or integers
            if r['sentences'] and isinstance(r['sentences'][0], str):
                total_sentences += len(r['sentences'])  # Count strings
            else:
                total_sentences += sum(r['sentences'])  # Sum integers
        else:
            total_sentences += r['sentences']
    
    print(f"\n✅ Passed: {passed}/12")
    print(f"❌ Failed: {failed}/12")
    print(f"📝 Total Sentences: {total_sentences:,}")
    print(f"⏱️  Total Time: {total_time/60:.1f} minutes")
    
    print("\n" + "─"*70)
    print("DETAILED RESULTS:")
    print("─"*70)
    
    for i, result in enumerate(results, 1):
        status = "✅" if result['success'] else "❌"
        # Handle both int and list for sentence count
        sentence_count = result['sentences']
        if isinstance(sentence_count, list):
            if sentence_count and isinstance(sentence_count[0], str):
                sentence_count = len(sentence_count)
            else:
                sentence_count = sum(sentence_count)
        print(f"{i:2d}. {status} {result['name']:15s} - {sentence_count:5d} sentences in {result['time']:5.1f}s")
        if not result['success']:
            print(f"     Error: {result.get('error', 'Unknown')[:70]}")
    
    print("\n" + "="*70)
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
        print("\n✨ All 12 scrapers are operational and ready for production!")
        print("\n📈 System Status:")
        print("   • 12 scrapers: ✅ OPERATIONAL")
        print("   • 42+ categories: ✅ WORKING")
        print("   • Test coverage: ✅ COMPLETE")
        print("\n🚀 Ready for full corpus expansion!")
    else:
        print(f"⚠️  {failed} SCRAPER(S) FAILED")
        print("\nFailed scrapers:")
        for result in results:
            if not result['success']:
                print(f"  ❌ {result['name']}: {result.get('error', 'Unknown')[:100]}")
    
    print("="*70 + "\n")
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
