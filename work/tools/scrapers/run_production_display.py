#!/usr/bin/env python3
"""
Production scraper with fixed header, fixed footer, and scrolling logs in the middle
"""

import sys
import os
import logging
import argparse
import signal
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from threading import Lock
import threading
import time

# Import scraper
try:
    from generic_scraper import GenericScraper
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from generic_scraper import GenericScraper


class FixedDisplay:
    """Manages fixed header and footer with scrolling logs in middle"""
    
    def __init__(self, total_websites):
        self.total = total_websites
        self.completed = 0
        self.failed = 0
        self.active_workers = {}
        self.start_time = datetime.now()
        self.lock = Lock()
        
        # Display layout
        self.header_lines = 4
        self.log_header_lines = 2  # Column headers for logs
        self.footer_lines = 4
        self.term_height = self.get_terminal_height()
        
        # Statistics for footer
        self.total_articles = 0
        self.total_sentences = 0
        
        # Auto-refresh footer
        self.running = True
        self.refresh_thread = None
    
    def get_terminal_height(self):
        """Get actual terminal height"""
        try:
            import shutil
            cols, rows = shutil.get_terminal_size()
            # Use actual terminal height, with minimum of 20 lines
            return max(rows, 20)
        except:
            # Fallback if can't detect
            return 40
        
    def clear_screen(self):
        """Clear screen and set up display"""
        # Clear screen
        sys.stdout.write('\033[2J')
        # Hide cursor
        sys.stdout.write('\033[?25l')
        # Move to top
        sys.stdout.write('\033[H')
        sys.stdout.flush()
    
    def draw_header(self):
        """Draw the fixed header at top"""
        with self.lock:
            elapsed = int((datetime.now() - self.start_time).total_seconds())
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours > 0 else f"{minutes:02d}:{seconds:02d}"
            
            # Get terminal width
            try:
                import shutil
                term_width, _ = shutil.get_terminal_size()
            except:
                term_width = 80
            
            sep_line = "=" * (term_width - 1)
            
            # Calculate rates
            rate_websites = (self.completed / elapsed * 60) if elapsed > 0 else 0
            rate_sentences = (self.total_sentences / elapsed * 60) if elapsed > 0 else 0
            
            # Active workers info
            active_count = len(self.active_workers)
            workers_str = ", ".join([f"{k}:{v['website'][:12]}" for k, v in sorted(self.active_workers.items())])
            if not workers_str:
                workers_str = "Idle"
            
            # Line 1: Title with key metrics
            sys.stdout.write('\033[H')  # Move to home
            sys.stdout.write('\033[2K')  # Clear line
            sys.stdout.write(f'\033[1;96m{sep_line}\033[0m\n')
            
            # Line 2: Status and timing
            sys.stdout.write('\033[2K')
            sys.stdout.write(f'\033[1;92m🚀 PRODUCTION SCRAPER\033[0m | '
                           f'\033[96mTime:\033[0m {time_str} | '
                           f'\033[93mWorkers:\033[0m {active_count}/{self.total} | '
                           f'\033[92mRate:\033[0m {rate_sentences:.1f} sent/min\n')
            
            # Line 3: Active workers
            sys.stdout.write('\033[2K')
            max_workers_len = term_width - 12
            sys.stdout.write(f'\033[93m▶ Active:\033[0m {workers_str[:max_workers_len]}\n')
            
            # Line 4: Separator
            sys.stdout.write('\033[2K')
            sys.stdout.write(f'\033[1;96m{sep_line}\033[0m\n')
            
            sys.stdout.flush()
    
    def draw_log_header(self):
        """Draw column headers for the scrolling log section"""
        with self.lock:
            # Get terminal width
            try:
                import shutil
                term_width, _ = shutil.get_terminal_size()
            except:
                term_width = 80
            
            # Position after main header
            log_header_start = self.header_lines + 1
            
            # Line 1: Column headers
            sys.stdout.write(f'\033[{log_header_start};1H')
            sys.stdout.write('\033[2K')
            sys.stdout.write('\033[1;93m')  # Yellow bold
            sys.stdout.write(f"{'TIMESTAMP':<12} {'STATUS':<10} {'WEBSITE':<20} {'CATEGORY':<15} SCRAPE LOGS")
            sys.stdout.write('\033[0m\n')
            
            # Line 2: Separator
            sys.stdout.write('\033[2K')
            sys.stdout.write('\033[90m')  # Gray
            sys.stdout.write('-' * (term_width - 1))
            sys.stdout.write('\033[0m\n')
            
            sys.stdout.flush()
    
    def draw_footer(self):
        """Draw the fixed footer at bottom"""
        with self.lock:
            # Update terminal height dynamically
            self.term_height = self.get_terminal_height()
            
            elapsed = int((datetime.now() - self.start_time).total_seconds())
            progress = self.completed / self.total if self.total > 0 else 0
            percentage = int(progress * 100)
            
            # Get terminal width
            try:
                import shutil
                term_width, _ = shutil.get_terminal_size()
            except:
                term_width = 80
            
            # Calculate progress bar length based on terminal width
            bar_length = min(30, term_width - 50)  # Dynamic but max 30
            filled = int(bar_length * progress)
            bar = "█" * filled + "░" * (bar_length - filled)
            sep_line = "=" * (term_width - 1)
            
            # Calculate rates and averages - LIVE UPDATES
            # For workers in progress, estimate based on active workers
            active_count = len(self.active_workers)
            total_in_progress = self.completed + active_count
            
            # Average time per site (include in-progress time for live estimate)
            avg_time_per_site = elapsed / total_in_progress if total_in_progress > 0 else 0
            
            # Calculate ETA based on remaining sites
            remaining_sites = self.total - self.completed
            eta_seconds = int(remaining_sites * avg_time_per_site) if avg_time_per_site > 0 else 0
            eta_minutes = eta_seconds // 60
            
            # Success rate: completed successfully / total completed (not total sites)
            if self.completed > 0:
                success_rate = ((self.completed - self.failed) / self.completed) * 100
            else:
                success_rate = 100.0  # Before any completions, assume success
            
            # Performance average: current sentences / sites being processed (live estimate)
            if total_in_progress > 0:
                avg_sentences_per_site = self.total_sentences / total_in_progress
            else:
                avg_sentences_per_site = 0
            
            # Format numbers
            articles_str = f"{self.total_articles:,}"
            sentences_str = f"{self.total_sentences:,}"
            
            # Calculate footer position (4 lines from bottom)
            footer_start = self.term_height - self.footer_lines + 1
            
            # Line 1: Separator (no newline at end, we'll manually position each line)
            sys.stdout.write(f'\033[{footer_start};1H')  # Move to footer position
            sys.stdout.write('\033[2K')
            sys.stdout.write(f'\033[1;96m{sep_line}\033[0m')
            
            # Line 2: Progress bar with ETA
            sys.stdout.write(f'\033[{footer_start + 1};1H')  # Explicit positioning
            sys.stdout.write('\033[2K')
            if remaining_sites > 0 and avg_time_per_site > 0:
                eta_str = f"ETA: {eta_minutes}m {eta_seconds % 60}s"
            elif self.completed >= self.total:
                eta_str = "Complete"
            else:
                eta_str = "Calculating..."
            sys.stdout.write(f'\033[93m■\033[0m Progress: [{bar}] {percentage}% | {self.completed}/{self.total} sites | {eta_str}')
            
            # Line 3: Collection stats
            sys.stdout.write(f'\033[{footer_start + 2};1H')  # Explicit positioning
            sys.stdout.write('\033[2K')
            sys.stdout.write(f'\033[93m■\033[0m Collected: '
                           f'\033[92m{articles_str}\033[0m articles, '
                           f'\033[92m{sentences_str}\033[0m sentences | '
                           f'\033[96mSuccess:\033[0m {success_rate:.0f}%')
            
            # Line 4: Performance metrics
            sys.stdout.write(f'\033[{footer_start + 3};1H')  # Explicit positioning
            sys.stdout.write('\033[2K')
            sys.stdout.write(f'\033[93m■\033[0m Performance: '
                           f'\033[96mAvg:\033[0m {avg_sentences_per_site:.0f} sent/site, '
                           f'{avg_time_per_site:.0f}s/site | '
                           f'\033[91mFailed:\033[0m {self.failed}')
            
            sys.stdout.flush()
    
    def update_display(self):
        """Update header, log headers, and footer"""
        self.draw_header()
        self.draw_log_header()
        self.draw_footer()
    
    def _auto_refresh_display(self):
        """Background thread to auto-refresh display every 2 seconds"""
        while self.running:
            time.sleep(2)
            if self.running:
                self.update_display()
    
    def start_auto_refresh(self):
        """Start background thread for auto-refreshing display"""
        self.running = True
        self.refresh_thread = threading.Thread(target=self._auto_refresh_display, daemon=True)
        self.refresh_thread.start()
    
    def stop_auto_refresh(self):
        """Stop background auto-refresh thread"""
        self.running = False
        if self.refresh_thread:
            self.refresh_thread.join(timeout=3)
    
    def worker_start(self, worker_id, website):
        """Register worker start"""
        with self.lock:
            self.active_workers[worker_id] = {
                'website': website,
                'start': datetime.now()
            }
        self.update_display()
    
    def update_live_stats(self, articles=0, sentences=0):
        """Update live statistics during scraping (can be called anytime)"""
        with self.lock:
            self.total_articles = articles
            self.total_sentences = sentences
    
    def worker_complete(self, worker_id, success=True, articles=0, sentences=0):
        """Register worker completion"""
        with self.lock:
            if worker_id in self.active_workers:
                del self.active_workers[worker_id]
            self.completed += 1
            if not success:
                self.failed += 1
            self.total_articles += articles
            self.total_sentences += sentences
        
        # Log completion
        logging.info(f"✅ COMPLETED: Worker {worker_id} | Articles: {articles} | Sentences: {sentences} | Progress: {self.completed}/{self.total}")
        
        # Display update happens automatically via auto-refresh thread
        self.update_display()


class ColumnFormatter(logging.Formatter):
    """Custom formatter that formats logs into columns matching the header"""
    
    def __init__(self, display=None):
        super().__init__()
        # Thread-safe context tracking per thread
        self.thread_context = {}
        self.display = display
    
    def format(self, record):
        # Parse message to extract components
        message = record.getMessage()
        
        # Get thread-specific context
        thread_id = threading.current_thread().ident
        if thread_id not in self.thread_context:
            self.thread_context[thread_id] = {'website': '', 'category': ''}
        
        ctx = self.thread_context[thread_id]
        
        # Extract website, category, and status from message patterns
        website = ctx['website']
        category = ctx['category']
        status = ""
        scrape_log = message.strip()
        
        # Remove newlines and clean up
        scrape_log = scrape_log.replace('\n', ' ').strip()
        
        # Parse website from patterns like "🌐 Scraping Website: name"
        if "Scraping Website:" in message:
            parts = message.split("Scraping Website:", 1)
            if len(parts) > 1:
                website_name = parts[1].strip()
                ctx['website'] = website_name[:18]
                website = ctx['website']
                ctx['category'] = ""  # Reset category for new website
                scrape_log = f"Starting website scrape"
        
        # Parse category from patterns like "📂 Scraping Category: name"
        elif "Scraping Category:" in message:
            parts = message.split("Scraping Category:", 1)
            if len(parts) > 1:
                category_name = parts[1].strip()
                ctx['category'] = category_name[:13]
                category = ctx['category']
                scrape_log = f"Starting category scrape"
        
        # Parse extraction messages like "✅ Extracted N sentences from category"
        elif "Extracted" in message and "sentences from" in message:
            # Extract sentence count and category
            try:
                parts = message.split("from", 1)
                if len(parts) > 1:
                    cat_name = parts[1].strip()
                    ctx['category'] = cat_name[:13]
                    category = ctx['category']
            except:
                pass
        
        # Parse URL messages like "URL: https://..."
        elif "URL:" in message:
            scrape_log = "Loading URL..."
            
        # Parse error messages with category like "Error scraping category 'name'"
        elif "Error scraping category" in message:
            try:
                # Extract category name from quotes
                start = message.find("'")
                end = message.find("'", start + 1)
                if start != -1 and end != -1:
                    cat_name = message[start+1:end]
                    ctx['category'] = cat_name[:13]
                    category = ctx['category']
            except:
                pass
        
        # Keep current context for other messages
        
        # Parse stats from log messages and update display
        if self.display:
            import re
            
            # Extract article counts from messages like "Found 19 new articles"
            if "Found" in message and "articles" in message:
                try:
                    match = re.search(r'Found (\d+) new articles', message)
                    if match:
                        count = int(match.group(1))
                        # Increment the display's article counter
                        with self.display.lock:
                            self.display.total_articles += count
                except:
                    pass
            
            # Extract sentence counts from messages like "Adding X paragraphs as sentences"
            # Actual format from extraction_mixin.py: "Adding 2 paragraphs as sentences"
            if "paragraphs as sentences" in message.lower():
                try:
                    match = re.search(r'Adding\s+(\d+)\s+paragraphs?\s+as\s+sentences?', message, re.IGNORECASE)
                    if match:
                        count = int(match.group(1))
                        with self.display.lock:
                            self.display.total_sentences += count  # Increment
                except:
                    pass
            
            # Also parse summary messages like "✅ Extracted X sentences from category"
            elif "extracted" in message.lower() and "sentences" in message.lower():
                try:
                    match = re.search(r'Extracted\s+(\d+)\s+sentences?', message, re.IGNORECASE)
                    if match:
                        count = int(match.group(1))
                        with self.display.lock:
                            self.display.total_sentences = count  # Set absolute value
                except:
                    pass
            
            # Extract total counts from completion messages like "Sentences: 1234"
            if "Sentences:" in message and "Articles:" not in message:
                try:
                    match = re.search(r'Sentences:\s*(\d+)', message)
                    if match:
                        count = int(match.group(1))
                        # Set the total (not increment)
                        with self.display.lock:
                            self.display.total_sentences = count
                except:
                    pass
            
            # Extract article totals from completion messages like "Articles: 123"
            if "Articles:" in message and "Sentences:" not in message:
                try:
                    match = re.search(r'Articles:\s*(\d+)', message)
                    if match:
                        count = int(match.group(1))
                        # Set the total (not increment)
                        with self.display.lock:
                            self.display.total_articles = count
                except:
                    pass
        
        # Determine status from level and message content with colored text
        if record.levelno >= logging.ERROR or "❌" in message or "Error" in message or "FAILED" in message.upper():
            status = "\033[91mERROR\033[0m"  # Red
        elif "✅" in message or "complete" in message.lower() or "SUCCESS" in message.upper():
            status = "\033[92mDONE\033[0m"  # Green
        elif "⚠️" in message or "WARNING" in message.upper():
            status = "\033[93mWARN\033[0m"  # Yellow
        elif "Scraping" in message or "Starting" in message or "🌐" in message or "📂" in message:
            status = "\033[96mSTART\033[0m"  # Cyan
        elif "Extracted" in message or "Found" in message or "Saved" in message:
            status = "\033[94mDATA\033[0m"  # Blue
        elif "enabled" in message.lower() or "Redis" in message or "URL:" in message:
            status = "\033[95mINFO\033[0m"  # Magenta
        else:
            status = "\033[97mINFO\033[0m"  # White
        
        # Format timestamp
        timestamp = self.formatTime(record, '%H:%M:%S')
        
        # Truncate scrape_log to fit remaining space
        max_log_len = 55
        if len(scrape_log) > max_log_len:
            scrape_log = scrape_log[:max_log_len-3] + "..."
        
        # Build columnar output: TIMESTAMP STATUS WEBSITE CATEGORY SCRAPE_LOGS
        # Note: status contains ANSI codes (11 chars for codes + 4-6 visible chars)
        # We pad to compensate for the color codes
        formatted = f"{timestamp:<12} {status:<20} {website:<20} {category:<15} {scrape_log}"
        
        return formatted


class ScrollingLogHandler(logging.Handler):
    """Log handler that writes in the scrolling middle section"""
    
    def __init__(self, display):
        super().__init__()
        self.display = display
        # Calculate available lines for logs (terminal height - header - log_header - footer)
        self.max_log_lines = display.term_height - display.header_lines - display.log_header_lines - display.footer_lines
        self.log_start = display.header_lines + display.log_header_lines + 1
        self.log_end = display.term_height - display.footer_lines
        # Keep a buffer of log lines
        self.log_buffer = []
        
    def emit(self, record):
        try:
            msg = self.format(record)
            
            # Get terminal width and limit message length dynamically
            try:
                import shutil
                term_width, _ = shutil.get_terminal_size()
                max_msg_length = term_width - 5
            except:
                max_msg_length = 75
            
            if len(msg) > max_msg_length:
                msg = msg[:max_msg_length - 3] + "..."
            
            # Add to buffer
            self.log_buffer.append(msg)
            
            # Keep only the last N lines that fit in the display
            if len(self.log_buffer) > self.max_log_lines:
                self.log_buffer = self.log_buffer[-self.max_log_lines:]
            
            # Refresh display (header and footer) FIRST
            self.display.update_display()
            
            # Then redraw all visible logs
            for i, log_msg in enumerate(self.log_buffer):
                line_num = self.log_start + i
                sys.stdout.write(f'\033[{line_num};1H')
                sys.stdout.write('\033[2K')  # Clear line
                sys.stdout.write(log_msg)
            
            # Clear any remaining lines if buffer is smaller than max
            for i in range(len(self.log_buffer), self.max_log_lines):
                line_num = self.log_start + i
                sys.stdout.write(f'\033[{line_num};1H')
                sys.stdout.write('\033[2K')
            
            sys.stdout.flush()
        except Exception:
            self.handleError(record)


def scrape_website_wrapper(website_name, worker_id, display, config_path):
    """Wrapper function to scrape a single website with status updates"""
    result = None
    success = False
    articles = 0
    sentences = 0
    
    try:
        # Register start
        display.worker_start(worker_id, website_name)
        
        # Create independent scraper instance
        scraper = GenericScraper(config_path)
        
        # Scrape
        result = scraper.scrape_website(website_name)
        
        # Extract result data with proper error handling
        if result:
            # Try multiple attribute names for compatibility
            success = getattr(result, 'success', True)
            articles = getattr(result, 'articles_scraped', getattr(result, 'article_count', 0))
            sentences = getattr(result, 'sentences_extracted', getattr(result, 'sentence_count', 0))
        
    except Exception as e:
        logging.error(f"❌ [{worker_id}] {website_name:15s} | EXCEPTION: {str(e)[:50]}")
        success = False
    
    finally:
        # ALWAYS call worker_complete, even if there was an error
        display.worker_complete(
            worker_id, 
            success=success,
            articles=articles,
            sentences=sentences
        )
    
    return result


def main():
    parser = argparse.ArgumentParser(description='Production Scraper with Fixed Header/Footer')
    parser.add_argument('--config', required=True, help='Path to website configs')
    parser.add_argument('--all', action='store_true', help='Scrape all enabled websites')
    parser.add_argument('--parallel', action='store_true', help='Enable parallel scraping')
    parser.add_argument('--workers', type=int, default=3, help='Number of parallel workers')
    parser.add_argument('--websites', nargs='+', help='Specific websites to scrape')
    parser.add_argument('--fresh', action='store_true', help='Clear deduplication database before scraping')
    
    args = parser.parse_args()
    
    # Clear deduplication database if --fresh flag is used
    if args.fresh:
        dedup_db = Path(__file__).parent / 'article_dedup.db'
        if dedup_db.exists():
            dedup_db.unlink()
            print(f"✅ Cleared deduplication database: {dedup_db}")
        else:
            print("ℹ️  No deduplication database found (fresh start)")
    
    # Flag to track if we're shutting down
    shutdown_flag = threading.Event()
    
    def signal_handler(signum, frame):
        """Handle Ctrl+C gracefully"""
        if not shutdown_flag.is_set():
            shutdown_flag.set()
            sys.stdout.write('\n\n⚠️  Interrupt received - stopping workers...\n')
            sys.stdout.flush()
            raise KeyboardInterrupt
    
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Initialize scraper to get website list
        scraper = GenericScraper(args.config)
        
        if args.all:
            websites = [name for name, cfg in scraper.config.items() if cfg.get('enabled', True)]
        elif args.websites:
            websites = args.websites
        else:
            print("Error: Specify --all or --websites")
            return 1
        
        # Create display
        display = FixedDisplay(len(websites))
        display.clear_screen()
        display.update_display()
        
        # Start auto-refresh to update footer every 2 seconds
        display.start_auto_refresh()
        
        # Setup logging to write in middle section
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Add scrolling log handler
        handler = ScrollingLogHandler(display)
        formatter = ColumnFormatter(display)  # Pass display to extract stats from logs
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
        
        # Log start
        logging.info(f"Starting scraper with {len(websites)} websites")
        
        if args.parallel:
            # Parallel scraping with proper worker management
            executor = ThreadPoolExecutor(max_workers=args.workers)
            futures = []
            
            try:
                # Submit all websites to the executor
                for i, website in enumerate(websites):
                    # Assign worker IDs dynamically based on order
                    worker_id = f"W{i}"
                    future = executor.submit(scrape_website_wrapper, website, worker_id, display, args.config)
                    futures.append((future, website))
                
                # Wait for all futures to complete (allows parallel execution)
                for future, website in futures:
                    try:
                        result = future.result()  # This will wait for the specific future
                        logging.info(f"✅ {website} completed successfully")
                    except Exception as e:
                        logging.error(f"❌ {website} failed: {e}")
                
                # Wait for executor to finish all tasks properly
                executor.shutdown(wait=True)
                
            except KeyboardInterrupt:
                logging.warning("⚠️  Interrupt received - stopping all workers...")
                # Cancel all pending futures
                for future, _ in futures:
                    future.cancel()
                # Shutdown executor immediately
                executor.shutdown(wait=False, cancel_futures=True)
                raise
        else:
            # Sequential scraping
            for i, website in enumerate(websites):
                scrape_website_wrapper(website, f"W0", display, args.config)
        
        # Final log
        logging.info("✅ All scraping complete!")
        time.sleep(2)  # Show final status
        
    finally:
        # Stop auto-refresh
        display.stop_auto_refresh()
        
        # Show cursor and clean up
        sys.stdout.write('\033[?25h')  # Show cursor
        sys.stdout.write(f'\033[{display.term_height + 1};1H')  # Move below footer
        sys.stdout.write('\n')
        sys.stdout.flush()
    
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        # Clean up display
        sys.stdout.write('\033[?25h')  # Show cursor
        sys.stdout.write('\033[r')     # Reset scroll region
        sys.stdout.write('\n\n⚠️  Interrupted by user - stopped all workers\n')
        sys.stdout.flush()
        # Force exit immediately
        os._exit(1)
