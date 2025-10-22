#!/usr/bin/env python3
"""
Kurdish Corpus Expansion - Main Orchestrator
Modular, maintainable corpus expansion with proper testing
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add scrapers directory to path
sys.path.insert(0, str(Path(__file__).parent))

from scrapers.config import SCRAPER_CONFIGS, OUTPUT_FILE
from scrapers.kurdsat_scraper import KurdsatScraper
from scrapers.rudaw_scraper import RudawScraper
from scrapers.khak_scraper import KhakScraper
from scrapers.nrt_scraper import NRTScraper
from scrapers.awene_scraper import AweneScraper
from scrapers.kurdistan24_scraper import Kurdistan24Scraper
from scrapers.xendan_scraper import XendanScraper
from scrapers.sekokurd_scraper import SekokurdScraper


class CorpusExpansionOrchestrator:
    """Main orchestrator for corpus expansion"""
    
    def __init__(self):
        self.scrapers = []
        self.all_sentences = set()
        self.stats = {}
        self.start_time = None
    
    def register_scraper(self, scraper_class, config_key):
        """Register a scraper with its configuration"""
        config = SCRAPER_CONFIGS.get(config_key)
        if not config or not config.get('enabled', True):
            print(f"⏭️  Skipping {config_key} (disabled)")
            return
        
        self.scrapers.append({
            'class': scraper_class,
            'config_key': config_key,
            'config': config
        })
    
    def run_scraper(self, scraper_info):
        """Run a single scraper"""
        config_key = scraper_info['config_key']
        config = scraper_info['config']
        scraper_class = scraper_info['class']
        
        print(f"\n{'='*70}")
        print(f"SCRAPER: {config_key.upper()}")
        print(f"{'='*70}")
        
        scraper = None
        scraper_stats = {
            'political': 0,
            'specialized': 0,
            'total': 0,
            'time': 0,
            'errors': []
        }
        
        try:
            scraper = scraper_class()
            start_time = time.time()
            
            # Run political scraping
            if config.get('political'):
                try:
                    print(f"\n📰 Running Political Scraping...")
                    count = scraper.scrape_political(**config['political'])
                    scraper_stats['political'] = count
                    print(f"   ✅ Collected {count} sentences")
                except Exception as e:
                    error = f"Political scraping failed: {e}"
                    scraper_stats['errors'].append(error)
                    print(f"   ❌ {error}")
            
            # Run specialized scraping
            if config.get('specialized'):
                try:
                    print(f"\n📚 Running Specialized Scraping...")
                    count = scraper.scrape_specialized(**config['specialized'])
                    scraper_stats['specialized'] = count
                    print(f"   ✅ Collected {count} sentences")
                except NotImplementedError:
                    print(f"   ℹ️  Specialized scraping not implemented")
                except Exception as e:
                    error = f"Specialized scraping failed: {e}"
                    scraper_stats['errors'].append(error)
                    print(f"   ❌ {error}")
            
            # Collect sentences
            self.all_sentences.update(scraper.sentences)
            
            elapsed = time.time() - start_time
            scraper_stats['time'] = elapsed
            scraper_stats['total'] = len(scraper.sentences)
            
            print(f"\n✅ {config_key.upper()}: {scraper_stats['total']} unique sentences in {elapsed:.1f}s")
        
        except Exception as e:
            error = f"Critical error: {e}"
            scraper_stats['errors'].append(error)
            print(f"\n❌ {config_key.upper()} FAILED: {e}")
        
        finally:
            if scraper:
                scraper.cleanup()
        
        self.stats[config_key] = scraper_stats
        return scraper_stats
    
    def run_all(self):
        """Run all registered scrapers"""
        print("="*70)
        print("KURDISH CORPUS EXPANSION - BATCH 3 (MODULAR)")
        print(f"Registered scrapers: {len(self.scrapers)}")
        print("="*70)
        
        self.start_time = datetime.now()
        
        for scraper_info in self.scrapers:
            self.run_scraper(scraper_info)
            time.sleep(2)  # Brief pause between scrapers
        
        self.print_summary()
        self.save_corpus()
    
    def print_summary(self):
        """Print collection summary"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        print(f"\n{'='*70}")
        print("COLLECTION SUMMARY")
        print(f"{'='*70}\n")
        
        print(f"{'Scraper':<15} {'Political':<12} {'Specialized':<12} {'Total':<10} {'Time(s)':<10} {'Status'}")
        print(f"{'-'*70}")
        
        total_political = 0
        total_specialized = 0
        total_time = 0
        
        for name, stats in self.stats.items():
            pol = stats['political']
            spec = stats['specialized']
            tot = stats['total']
            t = stats['time']
            errors = len(stats['errors'])
            
            status = "✅" if tot > 0 else "❌"
            if errors > 0:
                status = "⚠️"
            
            print(f"{name:<15} {pol:<12} {spec:<12} {tot:<10} {t:<10.1f} {status}")
            
            total_political += pol
            total_specialized += spec
            total_time += t
        
        print(f"{'-'*70}")
        print(f"{'TOTAL':<15} {total_political:<12} {total_specialized:<12} {len(self.all_sentences):<10} {total_time:<10.1f}")
        
        print(f"\n{'='*70}")
        print(f"✅ TOTAL UNIQUE SENTENCES: {len(self.all_sentences)}")
        print(f"⏱️  TOTAL TIME: {elapsed/60:.1f} minutes")
        print(f"{'='*70}\n")
        
        # Report errors
        errors = [(name, stats['errors']) for name, stats in self.stats.items() if stats['errors']]
        if errors:
            print("⚠️  ERRORS ENCOUNTERED:")
            for name, error_list in errors:
                for error in error_list:
                    print(f"   {name}: {error}")
            print()
    
    def save_corpus(self):
        """Save collected corpus to file"""
        if not self.all_sentences:
            print("❌ No sentences to save!")
            return
        
        sorted_sentences = sorted(self.all_sentences)
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("# Kurdish Expanded Corpus - Batch 3 (Modular)\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total unique sentences: {len(sorted_sentences)}\n")
            f.write("#\n")
            f.write("# Source Statistics:\n")
            
            for name, stats in self.stats.items():
                f.write(f"#   {name}: Political={stats['political']}, Specialized={stats['specialized']}, Total={stats['total']}\n")
            
            f.write("#\n")
            
            for sent in sorted_sentences:
                f.write(sent + '\n')
        
        print(f"✅ Saved {len(sorted_sentences)} sentences to {OUTPUT_FILE}")


def main():
    """Main entry point"""
    orchestrator = CorpusExpansionOrchestrator()
    
    # Register all scrapers
    orchestrator.register_scraper(KurdsatScraper, 'kurdsat')
    orchestrator.register_scraper(RudawScraper, 'rudaw')
    orchestrator.register_scraper(KhakScraper, 'khak')
    orchestrator.register_scraper(NRTScraper, 'nrt')
    orchestrator.register_scraper(AweneScraper, 'awene')
    orchestrator.register_scraper(Kurdistan24Scraper, 'kurdistan24')
    orchestrator.register_scraper(XendanScraper, 'xendan')
    orchestrator.register_scraper(SekokurdScraper, 'sekokurd')
    
    # Run collection
    orchestrator.run_all()


if __name__ == '__main__':
    main()
