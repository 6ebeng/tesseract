#!/usr/bin/env python3
"""
Scraper Test & Verification Tool
Tests all Kurdish news scrapers to identify which ones are working properly
"""

import sys
import time
from pathlib import Path

# Add scrapers directory to path
sys.path.insert(0, str(Path(__file__).parent))

from scrapers.base_scraper import BaseScraper
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


class ScraperTester:
    """Test framework for Kurdish scrapers"""
    
    def __init__(self):
        self.results = {}
    
    def test_scraper(self, scraper_class, test_political=True, test_specialized=False):
        """Test a scraper class"""
        scraper_name = scraper_class.__name__.replace('Scraper', '')
        print(f"\n{'='*70}")
        print(f"Testing {scraper_name}")
        print(f"{'='*70}")
        
        scraper = None
        result = {
            'name': scraper_name,
            'political': {'success': False, 'sentences': 0, 'error': None},
            'specialized': {'success': False, 'sentences': 0, 'error': None}
        }
        
        try:
            scraper = scraper_class()
            
            # Test political scraping
            if test_political:
                print(f"\n🧪 Testing Political Scraping...")
                try:
                    start_time = time.time()
                    # Use minimal parameters for quick testing
                    if hasattr(scraper, 'scrape_political'):
                        count = scraper.scrape_political(clicks=3) if 'clicks' in str(scraper.scrape_political.__code__.co_varnames) else \
                                scraper.scrape_political(scrolls=3) if 'scrolls' in str(scraper.scrape_political.__code__.co_varnames) else \
                                scraper.scrape_political(pages=2)
                        
                        elapsed = time.time() - start_time
                        result['political']['success'] = count > 0
                        result['political']['sentences'] = count
                        result['political']['time'] = elapsed
                        
                        if count > 0:
                            print(f"   ✅ SUCCESS: {count} sentences in {elapsed:.1f}s")
                            # Show sample sentences
                            samples = list(scraper.sentences)[:3]
                            print(f"   📄 Sample sentences:")
                            for i, sent in enumerate(samples, 1):
                                print(f"      {i}. {sent[:80]}...")
                        else:
                            print(f"   ⚠️  WARNING: No sentences collected")
                            result['political']['error'] = "No sentences found"
                    
                except NotImplementedError:
                    result['political']['error'] = "Not implemented"
                    print(f"   ℹ️  Political scraping not implemented")
                except Exception as e:
                    result['political']['error'] = str(e)
                    print(f"   ❌ FAILED: {e}")
            else:
                result['political']['error'] = "Not implemented"
            
            # Test specialized scraping
            if test_specialized and hasattr(scraper, 'scrape_specialized'):
                print(f"\n🧪 Testing Specialized Scraping...")
                try:
                    start_time = time.time()
                    # Clear previous sentences to isolate specialized results
                    scraper.sentences.clear()
                    
                    count = scraper.scrape_specialized(articles_per_category=5)
                    elapsed = time.time() - start_time
                    
                    result['specialized']['success'] = count > 0
                    result['specialized']['sentences'] = count
                    result['specialized']['time'] = elapsed
                    
                    if count > 0:
                        print(f"   ✅ SUCCESS: {count} sentences in {elapsed:.1f}s")
                    else:
                        print(f"   ⚠️  WARNING: No sentences collected")
                        result['specialized']['error'] = "No sentences found"
                
                except NotImplementedError:
                    result['specialized']['error'] = "Not implemented"
                    print(f"   ℹ️  Specialized scraping not implemented")
                except Exception as e:
                    result['specialized']['error'] = str(e)
                    print(f"   ❌ FAILED: {e}")
        
        except Exception as e:
            result['political']['error'] = str(e)
            print(f"❌ CRITICAL ERROR: {e}")
        
        finally:
            if scraper:
                scraper.cleanup()
        
        self.results[scraper_name] = result
        return result
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*70}")
        print("TEST SUMMARY")
        print(f"{'='*70}\n")
        
        print(f"{'Scraper':<20} {'Political':<15} {'Specialized':<15} {'Status'}")
        print(f"{'-'*70}")
        
        for name, result in self.results.items():
            pol_status = "✅" if result['political']['success'] else \
                        "➖" if result['political']['error'] == "Not implemented" else "❌"
            spec_status = "✅" if result['specialized']['success'] else \
                         "➖" if result['specialized']['error'] == "Not implemented" else "❌"
            
            pol_count = result['political']['sentences']
            spec_count = result['specialized']['sentences']
            
            # Scraper is working if either political OR specialized is successful
            overall_status = "✅ WORKING" if (result['political']['success'] or result['specialized']['success']) else "❌ BROKEN"
            
            print(f"{name:<20} {pol_status} {pol_count:<12} {spec_status} {spec_count:<12} {overall_status}")
        
        # Overall stats
        total_tested = len(self.results)
        working = sum(1 for r in self.results.values() if (r['political']['success'] or r['specialized']['success']))
        
        print(f"\n{'='*70}")
        print(f"Overall: {working}/{total_tested} scrapers working ({working/total_tested*100:.0f}%)")
        print(f"{'='*70}\n")
        
        # Failed scrapers details
        failed = [name for name, r in self.results.items() if not (r['political']['success'] or r['specialized']['success'])]
        if failed:
            print("⚠️  FAILED SCRAPERS:")
            for name in failed:
                error = self.results[name]['political']['error']
                print(f"   ❌ {name}: {error}")
            print()


def main():
    """Run scraper tests"""
    print("="*70)
    print("KURDISH NEWS SCRAPER VERIFICATION TOOL")
    print("Testing all scrapers with minimal parameters")
    print("="*70)
    
    tester = ScraperTester()
    
    # List of scrapers to test
    scrapers_to_test = [
        (KurdsatScraper, True, True),  # (Class, test_political, test_specialized)
        (RudawScraper, True, True),
        (KhakScraper, True, False),     # No specialized
        (NRTScraper, True, True),       # 5 specialized categories
        (AweneScraper, True, True),
        (Kurdistan24Scraper, True, True),  # Requires FlareSolverr
        (XendanScraper, True, True),
        (SekokurdScraper, False, True), # No political
        (GovKrdScraper, True, False),   # Government news only
        (SharpressScraper, True, True), # 5 specialized categories
    ]
    
    for scraper_class, test_pol, test_spec in scrapers_to_test:
        tester.test_scraper(scraper_class, test_pol, test_spec)
        time.sleep(2)  # Brief pause between tests
    
    # Print summary
    tester.print_summary()
    
    # Exit code: success if at least one mode (political or specialized) works for all scrapers
    working_count = sum(1 for r in tester.results.values() if (r['political']['success'] or r['specialized']['success']))
    sys.exit(0 if working_count == len(tester.results) else 1)


if __name__ == '__main__':
    main()
