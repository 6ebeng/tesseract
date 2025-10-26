"""
Admin Dashboard for Web Scraper Framework

Real-time monitoring dashboard with:
- Live scraper status
- Historical metrics and charts
- Error logs and debugging
- Website health monitoring

Usage:
    python app.py
    
Then open: http://localhost:5000
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
import sys
from collections import defaultdict

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from performance_utils import IncrementalScraper
    from scraper_monitor import ScraperMonitor, ScrapeResult
    from advanced_features import ArticleDeduplicator
except ImportError:
    print("⚠️  Warning: Could not import framework components")


app = Flask(__name__)
CORS(app)

# Configuration
DB_PATH = Path('../article_scraping.db')
DEDUP_DB_PATH = Path('../article_dedup.db')
LOGS_PATH = Path('../logs')


class DashboardDataProvider:
    """Provide data for dashboard"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.dedup_db_path = DEDUP_DB_PATH
    
    def get_overview_stats(self) -> Dict:
        """Get overview statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total articles
            cursor.execute('SELECT COUNT(*) FROM scraped_articles')
            total_articles = cursor.fetchone()[0]
            
            # Articles today
            today = datetime.now().date().isoformat()
            cursor.execute(
                'SELECT COUNT(*) FROM scraped_articles WHERE DATE(scraped_at) = ?',
                (today,)
            )
            articles_today = cursor.fetchone()[0]
            
            # Total sentences (estimated)
            total_sentences = total_articles * 15  # Rough estimate
            
            # Active websites
            cursor.execute('SELECT COUNT(DISTINCT website) FROM scraped_articles')
            active_websites = cursor.fetchone()[0]
            
            conn.close()
            
            # Deduplication stats
            dedup_stats = self._get_dedup_stats()
            
            return {
                'total_articles': total_articles,
                'articles_today': articles_today,
                'total_sentences': total_sentences,
                'active_websites': active_websites,
                'deduplication_rate': dedup_stats.get('deduplication_rate', '0%'),
                'duplicates_detected': dedup_stats.get('duplicates_detected', 0)
            }
        except Exception as e:
            print(f"Error getting overview stats: {e}")
            return {
                'total_articles': 0,
                'articles_today': 0,
                'total_sentences': 0,
                'active_websites': 0,
                'deduplication_rate': '0%',
                'duplicates_detected': 0
            }
    
    def get_website_status(self) -> List[Dict]:
        """Get per-website status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get last scrape time and article count per website
            cursor.execute('''
                SELECT 
                    website,
                    MAX(scraped_at) as last_scrape,
                    COUNT(*) as total_articles,
                    COUNT(CASE WHEN DATE(scraped_at) = DATE('now') THEN 1 END) as today_articles
                FROM scraped_articles
                GROUP BY website
                ORDER BY last_scrape DESC
            ''')
            
            results = []
            for row in cursor.fetchall():
                website, last_scrape, total, today = row
                
                # Calculate status
                if last_scrape:
                    last_scrape_dt = datetime.fromisoformat(last_scrape)
                    hours_ago = (datetime.now() - last_scrape_dt).total_seconds() / 3600
                    
                    if hours_ago < 2:
                        status = 'active'
                        status_color = 'success'
                    elif hours_ago < 24:
                        status = 'idle'
                        status_color = 'warning'
                    else:
                        status = 'stale'
                        status_color = 'danger'
                else:
                    status = 'unknown'
                    status_color = 'secondary'
                    hours_ago = 0
                
                results.append({
                    'website': website,
                    'status': status,
                    'status_color': status_color,
                    'last_scrape': last_scrape,
                    'hours_ago': round(hours_ago, 1),
                    'total_articles': total,
                    'today_articles': today
                })
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"Error getting website status: {e}")
            return []
    
    def get_recent_activity(self, limit: int = 50) -> List[Dict]:
        """Get recent scraping activity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    website,
                    url,
                    title,
                    scraped_at
                FROM scraped_articles
                ORDER BY scraped_at DESC
                LIMIT ?
            ''', (limit,))
            
            results = []
            for row in cursor.fetchall():
                website, url, title, scraped_at = row
                results.append({
                    'website': website,
                    'url': url,
                    'title': title[:100] if title else 'No title',
                    'scraped_at': scraped_at,
                    'time_ago': self._time_ago(scraped_at)
                })
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"Error getting recent activity: {e}")
            return []
    
    def get_metrics_history(self, days: int = 7) -> Dict:
        """Get metrics history for charts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get daily article counts
            cursor.execute('''
                SELECT 
                    DATE(scraped_at) as date,
                    COUNT(*) as count
                FROM scraped_articles
                WHERE scraped_at >= DATE('now', '-' || ? || ' days')
                GROUP BY DATE(scraped_at)
                ORDER BY date
            ''', (days,))
            
            daily_data = []
            labels = []
            for row in cursor.fetchall():
                date, count = row
                labels.append(date)
                daily_data.append(count)
            
            # Get articles by website
            cursor.execute('''
                SELECT 
                    website,
                    COUNT(*) as count
                FROM scraped_articles
                WHERE scraped_at >= DATE('now', '-' || ? || ' days')
                GROUP BY website
                ORDER BY count DESC
                LIMIT 10
            ''', (days,))
            
            website_data = []
            website_labels = []
            for row in cursor.fetchall():
                website, count = row
                website_labels.append(website)
                website_data.append(count)
            
            conn.close()
            
            return {
                'daily': {
                    'labels': labels,
                    'data': daily_data
                },
                'by_website': {
                    'labels': website_labels,
                    'data': website_data
                }
            }
            
        except Exception as e:
            print(f"Error getting metrics history: {e}")
            return {
                'daily': {'labels': [], 'data': []},
                'by_website': {'labels': [], 'data': []}
            }
    
    def get_error_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent error logs"""
        try:
            # Try to read from JSON log file
            log_file = LOGS_PATH / 'scraper.json.log'
            
            if not log_file.exists():
                return []
            
            errors = []
            with open(log_file, 'r') as f:
                for line in f.readlines()[-limit:]:
                    try:
                        log_entry = json.loads(line)
                        if log_entry.get('level') in ('ERROR', 'WARNING'):
                            errors.append({
                                'timestamp': log_entry.get('timestamp'),
                                'level': log_entry.get('level'),
                                'message': log_entry.get('message'),
                                'website': log_entry.get('website', 'unknown')
                            })
                    except json.JSONDecodeError:
                        continue
            
            return list(reversed(errors))  # Most recent first
            
        except Exception as e:
            print(f"Error getting error logs: {e}")
            return []
    
    def _get_dedup_stats(self) -> Dict:
        """Get deduplication statistics"""
        try:
            if not self.dedup_db_path.exists():
                return {}
            
            dedup = ArticleDeduplicator(str(self.dedup_db_path))
            return dedup.get_stats()
        except Exception as e:
            print(f"Error getting dedup stats: {e}")
            return {}
    
    def _time_ago(self, timestamp_str: str) -> str:
        """Convert timestamp to human-readable time ago"""
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            delta = datetime.now() - timestamp
            
            if delta.days > 0:
                return f"{delta.days}d ago"
            elif delta.seconds >= 3600:
                hours = delta.seconds // 3600
                return f"{hours}h ago"
            elif delta.seconds >= 60:
                minutes = delta.seconds // 60
                return f"{minutes}m ago"
            else:
                return "just now"
        except:
            return "unknown"


# Initialize data provider
data_provider = DashboardDataProvider()


# Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/overview')
def api_overview():
    """API: Overview statistics"""
    stats = data_provider.get_overview_stats()
    return jsonify(stats)


@app.route('/api/websites')
def api_websites():
    """API: Website status"""
    websites = data_provider.get_website_status()
    return jsonify(websites)


@app.route('/api/activity')
def api_activity():
    """API: Recent activity"""
    limit = request.args.get('limit', 50, type=int)
    activity = data_provider.get_recent_activity(limit)
    return jsonify(activity)


@app.route('/api/metrics')
def api_metrics():
    """API: Metrics history"""
    days = request.args.get('days', 7, type=int)
    metrics = data_provider.get_metrics_history(days)
    return jsonify(metrics)


@app.route('/api/errors')
def api_errors():
    """API: Error logs"""
    limit = request.args.get('limit', 100, type=int)
    errors = data_provider.get_error_logs(limit)
    return jsonify(errors)


@app.route('/api/health')
def api_health():
    """API: Health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


if __name__ == '__main__':
    print("=" * 70)
    print("🚀 Starting Admin Dashboard")
    print("=" * 70)
    print()
    print(f"Dashboard URL: http://localhost:5000")
    print(f"Database: {DB_PATH}")
    print()
    print("Press Ctrl+C to stop")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
