"""
Complete Integration Example

Demonstrates how to use ALL advanced features together:
- Multi-language support
- Article deduplication
- Browser fingerprinting prevention
- CLI tools integration
- Configuration wizard
- Monitoring and logging

This is a production-ready example showing best practices.
"""

import sys
from pathlib import Path
import yaml
import logging
from datetime import datetime
from typing import List, Dict

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from advanced_features import (
    LanguageDetector,
    ArticleDeduplicator,
    StealthBrowser,
    MultiLanguageConfig
)
from config_validator import ConfigValidator
from error_handler import ScraperErrorHandler, ErrorType
from scraper_monitor import ScraperMonitor, ScrapeResult
from performance_utils import ParallelScraper, IncrementalScraper
from security_utils import safe_load_yaml, RateLimiter


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductionScraper:
    """
    Production-ready scraper using all advanced features
    """
    
    def __init__(self, config_path: str):
        """
        Initialize scraper with configuration
        
        Args:
            config_path: Path to YAML configuration file
        """
        logger.info(f"🚀 Initializing Production Scraper")
        
        # 1. Validate configuration
        logger.info("1. Validating configuration...")
        validator = ConfigValidator()
        
        with open(config_path) as f:
            config_text = f.read()
        
        is_valid, errors = validator.validate_config_string(config_text)
        if not is_valid:
            raise ValueError(f"Invalid configuration: {errors}")
        
        logger.info("✅ Configuration validated")
        
        # 2. Load configuration safely
        logger.info("2. Loading configuration...")
        self.config = safe_load_yaml(config_path)
        logger.info(f"✅ Loaded {len(self.config)} websites")
        
        # 3. Initialize components
        logger.info("3. Initializing components...")
        
        self.lang_detector = LanguageDetector()
        self.deduplicator = ArticleDeduplicator('article_dedup.db')
        self.stealth = StealthBrowser()
        self.error_handler = ScraperErrorHandler()
        self.monitor = ScraperMonitor()
        self.rate_limiter = RateLimiter(requests_per_minute=20)
        
        # Incremental scraper (avoid re-scraping)
        self.incremental = IncrementalScraper('article_scraping.db')
        
        logger.info("✅ All components initialized")
    
    def scrape_website(
        self,
        website_name: str,
        category: str = None,
        max_articles: int = None
    ) -> ScrapeResult:
        """
        Scrape a single website with all advanced features
        
        Args:
            website_name: Website identifier
            category: Optional category filter
            max_articles: Maximum articles to scrape
        
        Returns:
            ScrapeResult with metrics
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"📰 Scraping: {website_name}")
        logger.info(f"{'='*70}\n")
        
        if website_name not in self.config:
            raise ValueError(f"Website '{website_name}' not found in config")
        
        website_config = self.config[website_name]
        start_time = datetime.now()
        
        try:
            # 1. Check if already scraped (incremental)
            if self.incremental.was_scraped_recently(website_name, hours=24):
                logger.info("⏭️  Skipping: scraped within last 24 hours")
                return ScrapeResult(
                    website=website_name,
                    success=True,
                    articles_scraped=0,
                    sentences_extracted=0,
                    duration=(datetime.now() - start_time).total_seconds(),
                    error=None
                )
            
            # 2. Rate limiting
            logger.info("⏳ Checking rate limit...")
            self.rate_limiter.wait_if_needed()
            
            # 3. Create stealth browser
            logger.info("🕵️  Creating stealth browser...")
            driver = self._create_stealth_driver()
            
            # 4. Scrape with error handling
            logger.info("🔍 Starting scrape...")
            
            articles = self.error_handler.safe_scrape(
                lambda: self._scrape_articles(driver, website_config, category),
                website_name
            )
            
            driver.quit()
            
            if not articles:
                logger.warning("⚠️  No articles found")
                return self._create_result(website_name, [], start_time)
            
            logger.info(f"📄 Found {len(articles)} articles")
            
            # 5. Language detection and filtering
            logger.info("🌐 Detecting languages...")
            articles = self._filter_by_language(articles, website_config)
            logger.info(f"✅ {len(articles)} articles after language filter")
            
            # 6. Deduplication
            logger.info("🔍 Checking for duplicates...")
            unique_articles = self._deduplicate_articles(articles)
            logger.info(f"✅ {len(unique_articles)} unique articles")
            
            # 7. Extract sentences
            logger.info("📝 Extracting sentences...")
            sentences = self._extract_sentences(unique_articles)
            logger.info(f"✅ Extracted {len(sentences)} sentences")
            
            # 8. Save to corpus
            logger.info("💾 Saving to corpus...")
            self._save_to_corpus(unique_articles, sentences, website_name)
            
            # 9. Update incremental tracker
            for article in unique_articles:
                self.incremental.mark_as_scraped(website_name, article['url'])
            
            # 10. Create result
            result = self._create_result(
                website_name,
                unique_articles,
                start_time,
                sentences_count=len(sentences)
            )
            
            # 11. Log metrics
            self.monitor.log_scrape(result)
            
            logger.info(f"\n✅ Scraping completed successfully!")
            logger.info(f"   Articles: {len(unique_articles)}")
            logger.info(f"   Sentences: {len(sentences)}")
            logger.info(f"   Duration: {result.duration:.2f}s\n")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Scraping failed: {e}", exc_info=True)
            
            result = ScrapeResult(
                website=website_name,
                success=False,
                articles_scraped=0,
                sentences_extracted=0,
                duration=(datetime.now() - start_time).total_seconds(),
                error=str(e)
            )
            
            self.monitor.log_scrape(result)
            
            return result
    
    def scrape_all_websites(
        self,
        parallel: bool = True,
        max_workers: int = 3
    ) -> List[ScrapeResult]:
        """
        Scrape all configured websites
        
        Args:
            parallel: Whether to use parallel scraping
            max_workers: Number of parallel workers
        
        Returns:
            List of scrape results
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"🌐 Scraping ALL Websites")
        logger.info(f"{'='*70}\n")
        
        if parallel:
            # Use parallel scraper
            logger.info(f"⚡ Using parallel scraping ({max_workers} workers)")
            
            parallel_scraper = ParallelScraper(max_workers=max_workers)
            
            # Create tasks
            tasks = [
                (website_name, None)  # (website, category)
                for website_name in self.config.keys()
            ]
            
            results = parallel_scraper.scrape_parallel(
                tasks,
                self.scrape_website
            )
        else:
            # Sequential scraping
            logger.info("🔄 Using sequential scraping")
            
            results = []
            for website_name in self.config.keys():
                result = self.scrape_website(website_name)
                results.append(result)
        
        # Summary
        logger.info(f"\n{'='*70}")
        logger.info(f"📊 Summary")
        logger.info(f"{'='*70}\n")
        
        total_articles = sum(r.articles_scraped for r in results)
        total_sentences = sum(r.sentences_extracted for r in results)
        success_count = sum(1 for r in results if r.success)
        
        logger.info(f"Websites scraped: {len(results)}")
        logger.info(f"Successful: {success_count}")
        logger.info(f"Failed: {len(results) - success_count}")
        logger.info(f"Total articles: {total_articles}")
        logger.info(f"Total sentences: {total_sentences}")
        
        # Deduplication stats
        dedup_stats = self.deduplicator.get_stats()
        logger.info(f"\nDeduplication:")
        logger.info(f"  Unique articles: {dedup_stats['unique_articles']}")
        logger.info(f"  Duplicates: {dedup_stats['duplicates_detected']}")
        logger.info(f"  Rate: {dedup_stats['deduplication_rate']}")
        
        return results
    
    def _create_stealth_driver(self):
        """Create Selenium driver with stealth mode"""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options_config = self.stealth.get_stealth_options()
        
        options = Options()
        options.add_argument(f"user-agent={options_config['user_agent']}")
        
        for arg in options_config['arguments']:
            options.add_argument(arg)
        
        driver = webdriver.Chrome(options=options)
        self.stealth.apply_stealth_mode(driver)
        
        return driver
    
    def _scrape_articles(
        self,
        driver,
        website_config: Dict,
        category: str = None
    ) -> List[Dict]:
        """
        Scrape articles from website
        
        This is a placeholder - implement actual scraping logic
        """
        # TODO: Implement actual scraping using selectors from config
        
        # Simulated articles for demo
        return [
            {
                'url': 'https://example.com/article1',
                'title': 'هەواڵی یەکەم',
                'content': 'ناوەرۆکی هەواڵ...',
                'date': datetime.now().isoformat()
            },
            {
                'url': 'https://example.com/article2',
                'title': 'Breaking News',
                'content': 'Article content...',
                'date': datetime.now().isoformat()
            }
        ]
    
    def _filter_by_language(
        self,
        articles: List[Dict],
        website_config: Dict
    ) -> List[Dict]:
        """Filter articles by language if configured"""
        lang_config = website_config.get('language_detection', {})
        
        if not lang_config.get('enabled'):
            return articles
        
        target_languages = lang_config.get('filter', ['ckb', 'ar'])
        
        return self.lang_detector.filter_by_language(
            articles,
            target_languages
        )
    
    def _deduplicate_articles(
        self,
        articles: List[Dict]
    ) -> List[Dict]:
        """Remove duplicate articles"""
        unique = []
        
        for article in articles:
            is_dup, reason = self.deduplicator.is_duplicate(
                article,
                article['url'],
                article['title'],
                article.get('content', '')
            )
            
            if not is_dup:
                unique.append(article)
            else:
                logger.debug(f"Skipping duplicate: {reason}")
        
        return unique
    
    def _extract_sentences(
        self,
        articles: List[Dict]
    ) -> List[str]:
        """Extract sentences from articles"""
        sentences = []
        
        for article in articles:
            content = article.get('content', '')
            
            # Simple sentence splitting (improve this)
            article_sentences = content.split('.')
            article_sentences = [
                s.strip() for s in article_sentences
                if len(s.strip()) > 20
            ]
            
            sentences.extend(article_sentences)
        
        return sentences
    
    def _save_to_corpus(
        self,
        articles: List[Dict],
        sentences: List[str],
        website_name: str
    ):
        """Save to training corpus"""
        corpus_dir = Path('corpus')
        corpus_dir.mkdir(exist_ok=True)
        
        # Save sentences to file
        corpus_file = corpus_dir / f'{website_name}_corpus.txt'
        
        with open(corpus_file, 'a', encoding='utf-8') as f:
            for sentence in sentences:
                f.write(sentence + '\n')
        
        logger.info(f"💾 Saved to: {corpus_file}")
    
    def _create_result(
        self,
        website_name: str,
        articles: List[Dict],
        start_time: datetime,
        sentences_count: int = 0
    ) -> ScrapeResult:
        """Create ScrapeResult object"""
        return ScrapeResult(
            website=website_name,
            success=True,
            articles_scraped=len(articles),
            sentences_extracted=sentences_count,
            duration=(datetime.now() - start_time).total_seconds(),
            error=None
        )


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Production Scraper with Advanced Features'
    )
    
    parser.add_argument(
        '--config',
        default='websites.yaml',
        help='Configuration file'
    )
    
    parser.add_argument(
        '--website',
        help='Scrape single website'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Scrape all websites'
    )
    
    parser.add_argument(
        '--parallel',
        action='store_true',
        default=True,
        help='Use parallel scraping (default: True)'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=3,
        help='Number of parallel workers (default: 3)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize scraper
        scraper = ProductionScraper(args.config)
        
        if args.all:
            # Scrape all websites
            results = scraper.scrape_all_websites(
                parallel=args.parallel,
                max_workers=args.workers
            )
        elif args.website:
            # Scrape single website
            result = scraper.scrape_website(args.website)
        else:
            parser.print_help()
            return
        
        logger.info("\n✅ Scraping completed!")
        
    except Exception as e:
        logger.error(f"\n❌ Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
