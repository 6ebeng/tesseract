"""
Integration Example: Using All Production Features Together

This example shows how to integrate all the production-ready components:
- Configuration validation
- Error handling with retry
- Monitoring and metrics
- Performance optimization
- Security best practices

Run this to see a complete, production-ready scraping workflow.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config_validator import validate_config_file
from error_handler import ScraperErrorHandler
from scraper_monitor import ScraperMonitor, ScrapeResult
from performance_utils import ParallelScraper, IncrementalScraper, ScraperCache
from security_utils import safe_load_yaml, RateLimiter


def main():
    """Complete production-ready scraping workflow"""
    
    print("=" * 70)
    print("🚀 PRODUCTION-READY SCRAPER INTEGRATION EXAMPLE")
    print("=" * 70)
    print()
    
    # ==================== STEP 1: VALIDATE CONFIGURATION ====================
    print("📋 Step 1: Validating Configuration...")
    print("-" * 70)
    
    config_path = "config/websites.yaml"
    
    # Validate config file
    if not validate_config_file(config_path, verbose=True):
        print("\n❌ Configuration validation failed!")
        print("   Fix errors before proceeding.")
        return 1
    
    print("\n✅ Configuration is valid!\n")
    
    # ==================== STEP 2: LOAD CONFIGURATION SAFELY ====================
    print("🔒 Step 2: Loading Configuration Securely...")
    print("-" * 70)
    
    try:
        # ALWAYS use safe_load_yaml (not yaml.load)
        config = safe_load_yaml(config_path)
        print(f"✅ Safely loaded config: {len(config)} websites configured")
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return 1
    
    print()
    
    # ==================== STEP 3: INITIALIZE COMPONENTS ====================
    print("⚙️  Step 3: Initializing Production Components...")
    print("-" * 70)
    
    # Error handler with auto-retry
    error_handler = ScraperErrorHandler(
        max_retries=3,
        base_retry_delay=5.0
    )
    print("✅ Error handler initialized (max_retries=3)")
    
    # Monitoring and metrics
    monitor = ScraperMonitor(
        log_dir='logs',
        alert_thresholds={
            'failure_rate': 0.2,
            'min_sentences': 10,
            'max_duration': 300
        }
    )
    print("✅ Monitoring initialized (logs/)")
    
    # Rate limiter for politeness
    rate_limiter = RateLimiter(
        requests_per_minute=20,
        burst_limit=5
    )
    print("✅ Rate limiter initialized (20 req/min)")
    
    # Incremental scraper to avoid re-scraping
    incremental = IncrementalScraper('scraper_state.db')
    print("✅ Incremental scraper initialized")
    
    # Cache for performance
    cache = ScraperCache(max_size=1000, ttl_seconds=3600)
    print("✅ Cache initialized (max_size=1000)")
    
    # Parallel scraper for concurrent execution
    parallel = ParallelScraper(max_workers=3)
    print("✅ Parallel scraper initialized (3 workers)")
    
    print()
    
    # ==================== STEP 4: SIMULATE SCRAPING ====================
    print("🌐 Step 4: Simulating Scraping Operations...")
    print("-" * 70)
    
    # Simulate scraping multiple websites
    test_results = [
        {
            'website': 'kurdsat',
            'category': 'politics',
            'success': True,
            'articles': 15,
            'sentences': 450,
            'duration': 45.2
        },
        {
            'website': 'rudaw',
            'category': 'economy',
            'success': True,
            'articles': 20,
            'sentences': 680,
            'duration': 52.1
        },
        {
            'website': 'nrt',
            'category': 'politics',
            'success': False,
            'articles': 0,
            'sentences': 0,
            'duration': 10.5,
            'error': 'Timeout waiting for element'
        },
        {
            'website': 'khak',
            'category': 'technology',
            'success': True,
            'articles': 8,
            'sentences': 250,
            'duration': 30.8
        },
    ]
    
    for result_data in test_results:
        # Apply rate limiting
        rate_limiter.wait_if_needed()
        
        # Create result object
        result = ScrapeResult(
            website=result_data['website'],
            category=result_data['category'],
            success=result_data['success'],
            article_count=result_data['articles'],
            sentence_count=result_data['sentences'],
            duration_seconds=result_data['duration'],
            error=result_data.get('error')
        )
        
        # Record in monitoring system
        monitor.record_scrape_result(
            result_data['website'],
            result_data['category'],
            result
        )
        
        # Display result
        if result.success:
            print(f"✅ {result.website}.{result.category}: "
                  f"{result.sentence_count} sentences in {result.duration_seconds:.1f}s")
        else:
            print(f"❌ {result.website}.{result.category}: {result.error}")
    
    print()
    
    # ==================== STEP 5: REVIEW MONITORING DATA ====================
    print("📊 Step 5: Performance Report")
    print("-" * 70)
    
    # Generate and display report
    monitor.print_summary()
    
    # Export metrics
    metrics_file = 'logs/metrics_example.json'
    monitor.export_metrics(metrics_file)
    print(f"\n💾 Metrics exported to: {metrics_file}")
    
    print()
    
    # ==================== STEP 6: ERROR SUMMARY ====================
    print("⚠️  Step 6: Error Analysis")
    print("-" * 70)
    
    error_handler.print_summary()
    
    print()
    
    # ==================== STEP 7: PERFORMANCE STATS ====================
    print("⚡ Step 7: Performance Statistics")
    print("-" * 70)
    
    # Incremental scraper stats
    incremental_stats = incremental.get_stats()
    print(f"Incremental Scraper:")
    print(f"  • Tracked articles: {incremental_stats['total_articles']:,}")
    
    # Cache stats
    cache_stats = cache.get_stats()
    print(f"\nCache:")
    print(f"  • Entries: {cache_stats['total_entries']}")
    print(f"  • Utilization: {cache_stats['utilization']}")
    
    # Rate limiter stats
    rate_stats = rate_limiter.get_stats()
    print(f"\nRate Limiter:")
    print(f"  • Requests last minute: {rate_stats['requests_last_minute']}")
    print(f"  • Utilization: {rate_stats['utilization']}")
    
    print()
    
    # ==================== COMPLETION ====================
    print("=" * 70)
    print("✅ INTEGRATION EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print("Next Steps:")
    print("  1. Review logs in logs/scraper.log")
    print("  2. Check metrics in logs/metrics_example.json")
    print("  3. Integrate with your actual scraper code")
    print("  4. Deploy monitoring to production")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
