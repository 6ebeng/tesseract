# Quick Start Guide - Advanced Features

**For users who want to start using the new features immediately**

---

## 1. Rate Limiting (No Installation Needed)

**Prevents websites from blocking you due to high request rates**

### Enable in Your Config

```yaml
# Add to any website config (e.g., rudaw.yaml)
rate_limiting:
  enabled: true
  max_requests_per_minute: 30 # Adjust as needed
```

### How to Use

Just enable it! The scraper will automatically:

- Track request times
- Enforce minimum delays
- Wait when limit is reached

**No code changes needed!**

---

## 2. Redis Caching (Requires Redis)

**Makes re-runs 10-100x faster by caching scraped data**

### Installation

```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo service redis-server start

# macOS
brew install redis
brew services start redis

# Python package
pip install redis
```

### Enable in Your Config

```yaml
caching:
  enabled: true
  redis_host: 'localhost'
  redis_port: 6379
  redis_db: 0
  ttl_hours: 24 # Cache for 24 hours
```

### Test It Works

```bash
# Check Redis is running
redis-cli ping
# Should return: PONG

# Test scraper with cache
python3 generic_scraper.py rudaw --max-articles 5

# Run again - should be MUCH faster!
python3 generic_scraper.py rudaw --max-articles 5
```

### Clear Cache When Needed

```bash
# Clear all cache
redis-cli FLUSHDB

# Or in Python
from advanced_features import RedisCache
cache = RedisCache()
cache.invalidate('*')  # Clear all
```

---

## 3. Retry Logic (No Installation Needed)

**Automatically retries failed requests**

### Enable in Your Config

```yaml
retry:
  enabled: true
  max_attempts: 3 # Total tries (including first)
  delay_seconds: 2.0 # Wait 2 seconds between retries
  retry_on_empty: true # Retry if result is empty
```

### What It Handles

- Network connection errors
- Timeouts
- Empty results (if enabled)

**No code changes needed!**

---

## 4. Proxy Rotation (Requires Proxy List)

**Bypass IP-based blocking by rotating proxies**

### Setup

**1. Get proxies** (see `proxies.txt.example` for sources)

**2. Create `proxies.txt`:**

```text
# One proxy per line
http://proxy1.example.com:8080
http://user:pass@proxy2.example.com:3128
socks5://proxy3.example.com:1080
```

**3. Enable in config:**

```yaml
proxy:
  enabled: true
  proxy_file: 'proxies.txt'
  rotation_strategy: 'round_robin' # or 'random'
```

### Test Your Proxies

```bash
# Test a proxy with curl
curl -x http://proxy:port https://api.ipify.org
# Should return proxy's IP, not yours
```

---

## Complete Example Config

```yaml
# rudaw.yaml with ALL advanced features enabled
name: 'Rudaw News'
base_url: 'https://www.rudaw.net'
enabled: true

# Rate limiting (prevent blocking)
rate_limiting:
  enabled: true
  max_requests_per_minute: 30

# Redis caching (faster re-runs)
caching:
  enabled: true
  redis_host: 'localhost'
  redis_port: 6379
  ttl_hours: 24

# Retry logic (handle errors)
retry:
  enabled: true
  max_attempts: 3
  delay_seconds: 2.0
  retry_on_empty: true

# Proxy rotation (bypass IP blocks)
proxy:
  enabled: false # Enable if you have proxies
  proxy_file: 'proxies.txt'
  rotation_strategy: 'round_robin'
# ... rest of config (selectors, pagination, etc.)
```

---

## Testing the Features

### Test Rate Limiting

```bash
# Run scraper with verbose logging
python3 generic_scraper.py rudaw --verbose

# You'll see logs like:
# ⏱️  Rate limiter initialized: 30 req/min (min delay: 2.00s)
# ⏳ Rate limit reached (30 req/min). Waiting 5.2s...
```

### Test Redis Caching

```bash
# First run (no cache)
time python3 generic_scraper.py rudaw --max-articles 10
# Note the time (e.g., 45 seconds)

# Second run (with cache)
time python3 generic_scraper.py rudaw --max-articles 10
# Should be MUCH faster (e.g., 2 seconds)

# Check cache in Redis
redis-cli
> KEYS scraper:*
> GET scraper:html:abc123...
```

### Test Retry Logic

```bash
# Disconnect internet temporarily, run scraper
python3 generic_scraper.py rudaw

# You'll see logs like:
# Attempt 1/3...
# ⚠️  ConnectionError on attempt 1/3: Connection refused
# ⏳ Retrying in 2.0s...
# Attempt 2/3...
```

### Test Proxy Rotation

```bash
# First, verify proxies work
curl -x http://proxy:port https://api.ipify.org

# Run scraper with proxy config
python3 generic_scraper.py rudaw

# Check logs:
# 🔄 Proxy rotator initialized: 3 proxies (round_robin)
# 🔄 Using proxy: proxy1.example.com:8080
# 🔄 Using proxy: proxy2.example.com:3128
```

---

## Recommended Settings

### For Development (Fast Iterations)

```yaml
rate_limiting:
  enabled: false # No delays

caching:
  enabled: true
  ttl_hours: 168 # Cache for 1 week

retry:
  enabled: false # Fail fast

proxy:
  enabled: false
```

**Why:** Fast iterations, use cached data, no waiting.

---

### For Production (Polite & Robust)

```yaml
rate_limiting:
  enabled: true
  max_requests_per_minute: 20 # Conservative

caching:
  enabled: true
  ttl_hours: 24 # Fresh daily

retry:
  enabled: true
  max_attempts: 5 # More attempts
  delay_seconds: 3.0 # Longer delays

proxy:
  enabled: false # Enable if getting blocked
```

**Why:** Respectful to servers, handles errors well.

---

### For Aggressive Scraping (Fast but Risky)

```yaml
rate_limiting:
  enabled: true
  max_requests_per_minute: 60 # High rate

caching:
  enabled: true
  ttl_hours: 1 # Short cache

retry:
  enabled: true
  max_attempts: 3
  delay_seconds: 1.0 # Short delays

proxy:
  enabled: true # Rotate to avoid blocks
  rotation_strategy: 'random'
```

**Why:** Fast scraping, use proxies to mitigate blocking risk.

---

## Troubleshooting

### Redis not found

```
❌ Redis connection failed: Connection refused
```

**Fix:**

```bash
# Check if Redis is running
sudo service redis-server status

# Start Redis
sudo service redis-server start

# Or install
sudo apt-get install redis-server
```

---

### Proxy not working

```
⚠️  High failure rate for proxy proxy1.com:8080 (90.0%)
```

**Fix:**

```bash
# Test proxy manually
curl -x http://proxy1.com:8080 https://google.com

# Remove dead proxies from proxies.txt
# Or get new proxies
```

---

### Rate limiting too slow

```
# Scraping is very slow
```

**Fix:**

```yaml
# Increase rate limit
rate_limiting:
  max_requests_per_minute: 60  # Was 20

# Or disable for testing
rate_limiting:
  enabled: false
```

---

## Getting Help

1. **Read full documentation:** `docs/ADVANCED_FEATURES.md`
2. **Check examples:** `TEMPLATE.yaml`
3. **Test features:** `python3 advanced_features.py` (runs demo)
4. **Check logs:** Add `--verbose` flag

---

## Summary

✅ **All 4 features are production-ready**  
✅ **All are optional - enable as needed**  
✅ **No code changes required - just config**  
✅ **Comprehensive documentation available**

Start with **rate limiting** (easiest, no setup).  
Add **caching** for faster development.  
Enable **retry** for robustness.  
Use **proxies** if getting blocked.

**Happy scraping!** 🚀
