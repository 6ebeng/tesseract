"""
Monitoring and Observability System for Web Scrapers

Features:
- Structured logging (JSON format)
- Metrics tracking (success rate, performance, articles)
- Alerting on thresholds
- Performance analytics
- Error tracking

Usage:
    from scraper_monitor import ScraperMonitor
    
    monitor = ScraperMonitor()
    
    # Record scrape result
    monitor.record_scrape_result('kurdsat', 'politics', result)
    
    # Generate report
    report = monitor.generate_report()
    print(report)
    
    # Export metrics
    monitor.export_metrics('metrics.json')
"""

import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class ScrapeResult:
    """Result of a scrape operation"""
    website: str
    category: str
    success: bool
    article_count: int
    sentence_count: int
    duration_seconds: float
    error: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ScraperMonitor:
    """
    Comprehensive monitoring system for scraper health and performance
    
    Tracks:
    - Success/failure rates
    - Article and sentence counts
    - Performance metrics
    - Error patterns
    - Alerts on thresholds
    """
    
    def __init__(
        self,
        log_dir: str = 'logs',
        alert_thresholds: Optional[Dict] = None
    ):
        """
        Args:
            log_dir: Directory for log files
            alert_thresholds: Custom alert thresholds
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Metrics storage
        self.metrics = {
            'total_runs': 0,
            'successful_runs': 0,
            'failed_runs': 0,
            'total_articles': 0,
            'total_sentences': 0,
            'total_duration': 0.0,
            'by_website': defaultdict(lambda: {
                'runs': 0,
                'successes': 0,
                'failures': 0,
                'articles': 0,
                'sentences': 0,
                'duration': 0.0
            }),
            'by_category': defaultdict(lambda: {
                'runs': 0,
                'successes': 0,
                'failures': 0,
                'articles': 0,
                'sentences': 0
            })
        }
        
        # Recent results (last 100)
        self.recent_results: List[ScrapeResult] = []
        self.max_recent_results = 100
        
        # Error tracking
        self.errors: List[Dict] = []
        self.max_errors = 100
        
        # Alert thresholds
        self.alert_thresholds = alert_thresholds or {
            'failure_rate': 0.2,       # Alert if >20% fail
            'min_sentences': 10,       # Alert if <10 sentences
            'max_duration': 300,       # Alert if >5 minutes
            'min_success_rate': 0.8    # Alert if success <80%
        }
        
        # Setup logging
        self.setup_logging()
    
    def setup_logging(self):
        """Configure structured logging"""
        # Create formatters
        json_formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": "%(message)s"}'
        )
        
        text_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
        )
        
        # File handler (JSON format)
        json_handler = logging.FileHandler(
            self.log_dir / 'scraper.json.log'
        )
        json_handler.setFormatter(json_formatter)
        json_handler.setLevel(logging.INFO)
        
        # File handler (text format)
        text_handler = logging.FileHandler(
            self.log_dir / 'scraper.log'
        )
        text_handler.setFormatter(text_formatter)
        text_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(text_formatter)
        console_handler.setLevel(logging.INFO)
        
        # Configure logger
        logger = logging.getLogger('scraper')
        logger.setLevel(logging.INFO)
        logger.addHandler(json_handler)
        logger.addHandler(text_handler)
        logger.addHandler(console_handler)
        
        self.logger = logger
    
    def record_scrape_result(self, website: str, category: str, result: ScrapeResult):
        """
        Record the result of a scrape operation
        
        Args:
            website: Website name
            category: Category name
            result: ScrapeResult object
        """
        # Update global metrics
        self.metrics['total_runs'] += 1
        
        if result.success:
            self.metrics['successful_runs'] += 1
            self.metrics['total_articles'] += result.article_count
            self.metrics['total_sentences'] += result.sentence_count
            self.metrics['total_duration'] += result.duration_seconds
            
            # Log success
            self.logger.info(
                f"✅ {website}.{category} | "
                f"Articles: {result.article_count} | "
                f"Sentences: {result.sentence_count} | "
                f"Duration: {result.duration_seconds:.1f}s"
            )
        else:
            self.metrics['failed_runs'] += 1
            
            # Log failure
            self.logger.error(
                f"❌ {website}.{category} | "
                f"Error: {result.error}"
            )
            
            # Track error
            self.errors.append({
                'timestamp': result.timestamp.isoformat(),
                'website': website,
                'category': category,
                'error': result.error
            })
            
            # Trim error list
            if len(self.errors) > self.max_errors:
                self.errors = self.errors[-self.max_errors:]
        
        # Update per-website metrics
        website_metrics = self.metrics['by_website'][website]
        website_metrics['runs'] += 1
        if result.success:
            website_metrics['successes'] += 1
            website_metrics['articles'] += result.article_count
            website_metrics['sentences'] += result.sentence_count
            website_metrics['duration'] += result.duration_seconds
        else:
            website_metrics['failures'] += 1
        
        # Update per-category metrics
        category_metrics = self.metrics['by_category'][category]
        category_metrics['runs'] += 1
        if result.success:
            category_metrics['successes'] += 1
            category_metrics['articles'] += result.article_count
            category_metrics['sentences'] += result.sentence_count
        else:
            category_metrics['failures'] += 1
        
        # Store recent result
        self.recent_results.append(result)
        if len(self.recent_results) > self.max_recent_results:
            self.recent_results = self.recent_results[-self.max_recent_results:]
        
        # Check alert thresholds
        self.check_alerts(result)
    
    def check_alerts(self, result: ScrapeResult):
        """Check if any alert thresholds are exceeded"""
        alerts = []
        
        # Check overall failure rate
        if self.metrics['total_runs'] >= 10:
            failure_rate = self.metrics['failed_runs'] / self.metrics['total_runs']
            if failure_rate > self.alert_thresholds['failure_rate']:
                alerts.append(
                    f"⚠️  HIGH FAILURE RATE: {failure_rate:.1%} "
                    f"({self.metrics['failed_runs']}/{self.metrics['total_runs']})"
                )
        
        # Check if this scrape was successful but got too few sentences
        if result.success and result.sentence_count < self.alert_thresholds['min_sentences']:
            alerts.append(
                f"⚠️  LOW SENTENCE COUNT: {result.website}.{result.category} "
                f"got only {result.sentence_count} sentences"
            )
        
        # Check if scrape took too long
        if result.duration_seconds > self.alert_thresholds['max_duration']:
            alerts.append(
                f"⚠️  SLOW SCRAPE: {result.website}.{result.category} "
                f"took {result.duration_seconds:.1f}s"
            )
        
        # Send alerts
        for alert_msg in alerts:
            self.send_alert(alert_msg)
    
    def send_alert(self, message: str):
        """
        Send alert notification
        
        In production, this would send email/Slack/etc.
        For now, just logs as warning.
        """
        self.logger.warning(f"🚨 ALERT: {message}")
        print(f"\n🚨 ALERT: {message}\n")
    
    def get_success_rate(self) -> float:
        """Calculate overall success rate"""
        if self.metrics['total_runs'] == 0:
            return 0.0
        return self.metrics['successful_runs'] / self.metrics['total_runs']
    
    def get_avg_duration(self) -> float:
        """Calculate average scrape duration"""
        if self.metrics['successful_runs'] == 0:
            return 0.0
        return self.metrics['total_duration'] / self.metrics['successful_runs']
    
    def get_avg_sentences_per_article(self) -> float:
        """Calculate average sentences per article"""
        if self.metrics['total_articles'] == 0:
            return 0.0
        return self.metrics['total_sentences'] / self.metrics['total_articles']
    
    def get_website_stats(self, website: str) -> Dict[str, Any]:
        """Get statistics for a specific website"""
        stats = self.metrics['by_website'][website]
        
        if stats['runs'] == 0:
            return {'error': 'No data for this website'}
        
        success_rate = stats['successes'] / stats['runs']
        avg_duration = stats['duration'] / stats['successes'] if stats['successes'] > 0 else 0
        avg_articles = stats['articles'] / stats['successes'] if stats['successes'] > 0 else 0
        avg_sentences = stats['sentences'] / stats['successes'] if stats['successes'] > 0 else 0
        
        return {
            'website': website,
            'total_runs': stats['runs'],
            'success_rate': f"{success_rate:.1%}",
            'total_articles': stats['articles'],
            'total_sentences': stats['sentences'],
            'avg_duration': f"{avg_duration:.1f}s",
            'avg_articles_per_run': f"{avg_articles:.1f}",
            'avg_sentences_per_run': f"{avg_sentences:.1f}"
        }
    
    def get_category_stats(self, category: str) -> Dict[str, Any]:
        """Get statistics for a specific category"""
        stats = self.metrics['by_category'][category]
        
        if stats['runs'] == 0:
            return {'error': 'No data for this category'}
        
        success_rate = stats['successes'] / stats['runs']
        avg_articles = stats['articles'] / stats['successes'] if stats['successes'] > 0 else 0
        avg_sentences = stats['sentences'] / stats['successes'] if stats['successes'] > 0 else 0
        
        return {
            'category': category,
            'total_runs': stats['runs'],
            'success_rate': f"{success_rate:.1%}",
            'total_articles': stats['articles'],
            'total_sentences': stats['sentences'],
            'avg_articles_per_run': f"{avg_articles:.1f}",
            'avg_sentences_per_run': f"{avg_sentences:.1f}"
        }
    
    def generate_report(self) -> str:
        """Generate comprehensive performance report"""
        lines = [
            "",
            "=" * 70,
            "📊 SCRAPER PERFORMANCE REPORT",
            "=" * 70,
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "OVERALL STATISTICS",
            "-" * 70,
            f"Total Runs:           {self.metrics['total_runs']}",
            f"Successful:           {self.metrics['successful_runs']} "
            f"({self.get_success_rate():.1%})",
            f"Failed:               {self.metrics['failed_runs']} "
            f"({(1 - self.get_success_rate()):.1%})",
            "",
            f"Total Articles:       {self.metrics['total_articles']:,}",
            f"Total Sentences:      {self.metrics['total_sentences']:,}",
            f"Avg Sentences/Article: {self.get_avg_sentences_per_article():.1f}",
            "",
            f"Avg Duration:         {self.get_avg_duration():.1f}s",
            ""
        ]
        
        # Per-website stats
        if self.metrics['by_website']:
            lines.extend([
                "BY WEBSITE",
                "-" * 70
            ])
            
            for website in sorted(self.metrics['by_website'].keys()):
                stats = self.get_website_stats(website)
                if 'error' not in stats:
                    lines.append(
                        f"{website:15} | Runs: {stats['total_runs']:3} | "
                        f"Success: {stats['success_rate']:6} | "
                        f"Sentences: {stats['total_sentences']:5}"
                    )
            lines.append("")
        
        # Per-category stats
        if self.metrics['by_category']:
            lines.extend([
                "BY CATEGORY",
                "-" * 70
            ])
            
            for category in sorted(self.metrics['by_category'].keys()):
                stats = self.get_category_stats(category)
                if 'error' not in stats:
                    lines.append(
                        f"{category:15} | Runs: {stats['total_runs']:3} | "
                        f"Success: {stats['success_rate']:6} | "
                        f"Sentences: {stats['total_sentences']:5}"
                    )
            lines.append("")
        
        # Recent errors
        if self.errors:
            lines.extend([
                "RECENT ERRORS",
                "-" * 70
            ])
            
            for error in self.errors[-10:]:
                timestamp = datetime.fromisoformat(error['timestamp'])
                lines.append(
                    f"[{timestamp.strftime('%H:%M:%S')}] "
                    f"{error['website']}.{error['category']}: {error['error']}"
                )
            lines.append("")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def export_metrics(self, filepath: str):
        """Export metrics to JSON file"""
        # Convert defaultdict to regular dict for JSON serialization
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'total_runs': self.metrics['total_runs'],
                'successful_runs': self.metrics['successful_runs'],
                'failed_runs': self.metrics['failed_runs'],
                'total_articles': self.metrics['total_articles'],
                'total_sentences': self.metrics['total_sentences'],
                'total_duration': self.metrics['total_duration'],
                'success_rate': self.get_success_rate(),
                'avg_duration': self.get_avg_duration(),
                'avg_sentences_per_article': self.get_avg_sentences_per_article(),
                'by_website': dict(self.metrics['by_website']),
                'by_category': dict(self.metrics['by_category'])
            },
            'recent_errors': self.errors[-20:]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Metrics exported to: {filepath}")
    
    def print_summary(self):
        """Print summary to console"""
        print(self.generate_report())


# Example usage
if __name__ == '__main__':
    # Create monitor
    monitor = ScraperMonitor()
    
    # Simulate some scrape results
    results = [
        ScrapeResult('kurdsat', 'politics', True, 15, 450, 45.2),
        ScrapeResult('rudaw', 'economy', True, 20, 680, 52.1),
        ScrapeResult('nrt', 'politics', False, 0, 0, 10.5, error='Timeout'),
        ScrapeResult('khak', 'technology', True, 8, 250, 30.8),
    ]
    
    for result in results:
        monitor.record_scrape_result(result.website, result.category, result)
    
    # Generate report
    monitor.print_summary()
    
    # Export metrics
    monitor.export_metrics('metrics_example.json')
