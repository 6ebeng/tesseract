# FlareSolverr Setup Guide for Kurdistan24

## Overview

FlareSolverr is a proxy server that bypasses Cloudflare protection. We'll use it to scrape Kurdistan24, which blocks automated access.

---

## Installation Steps

### Step 1: Run Installation Script

```bash
cd /mnt/c/tesseract/work/tools
chmod +x install_flaresolverr.sh
./install_flaresolverr.sh
```

**What it does:**
- ✅ Installs Docker on WSL Ubuntu
- ✅ Pulls FlareSolverr Docker image
- ✅ Starts FlareSolverr container on port 8191
- ✅ Installs Python dependencies (requests, beautifulsoup4)

**Estimated time:** 5-10 minutes

---

### Step 2: Verify Installation

```bash
# Check Docker is running
sudo service docker status

# Check FlareSolverr container
sudo docker ps | grep flaresolverr

# Test FlareSolverr API
curl -X POST http://localhost:8191/v1 \
    -H "Content-Type: application/json" \
    -d '{"cmd":"sessions.list"}'
```

**Expected output:** Should see `"sessions":[]`

---

### Step 3: Install Python Dependencies

```bash
# Install required packages
pip3 install requests beautifulsoup4
```

---

### Step 4: Test Kurdistan24 Scraping

```bash
cd /mnt/c/tesseract/work
python3 tools/test_k24_flaresolverr.py
```

**What it tests:**
- ✅ FlareSolverr connection
- ✅ Cloudflare bypass
- ✅ Article list extraction
- ✅ Article detail scraping
- ✅ Quality filtering

**Expected:** 5+ quality sentences extracted

---

## Usage

### Start FlareSolverr (if stopped)

```bash
sudo docker start flaresolverr
```

### Stop FlareSolverr

```bash
sudo docker stop flaresolverr
```

### View Logs

```bash
sudo docker logs flaresolverr
```

### Restart FlareSolverr

```bash
sudo docker restart flaresolverr
```

---

## How It Works

1. **Normal scraper → Cloudflare** ❌ Blocked
2. **Scraper → FlareSolverr → Cloudflare** ✅ Bypassed

FlareSolverr:
- Uses real browser (Chromium)
- Solves JavaScript challenges
- Handles CAPTCHAs automatically
- Returns clean HTML to your script

---

## Integration with Batch 3

Once FlareSolverr is working, Kurdistan24 will be added as the 6th source:

1. **Kurdsat**: 1,000 sentences
2. **Rudaw**: 1,000 sentences
3. **Khak TV**: 500 sentences
4. **NRT TV**: 1,000 sentences
5. **Awene**: 700 sentences
6. **Kurdistan24**: 800 sentences

**Total: 5,000+ sentences → 9,700+ combined corpus!**

---

## Troubleshooting

### Docker not starting

```bash
# Restart Docker
sudo service docker restart

# Check status
sudo service docker status
```

### FlareSolverr not responding

```bash
# Restart container
sudo docker restart flaresolverr

# Wait 10 seconds
sleep 10

# Test again
curl http://localhost:8191/
```

### Port 8191 already in use

```bash
# Find what's using the port
sudo lsof -i :8191

# Stop FlareSolverr
sudo docker stop flaresolverr

# Remove container
sudo docker rm flaresolverr

# Restart from scratch
cd /mnt/c/tesseract/work/tools
./install_flaresolverr.sh
```

---

## Performance Notes

- **First request**: Slower (5-10 seconds) - solving Cloudflare
- **Subsequent requests**: Faster (2-3 seconds) - session cached
- **Memory usage**: ~500MB (Docker + Chromium)
- **Auto-restart**: Container restarts on system reboot

---

## Next Steps

After successful test:
1. ✅ FlareSolverr running
2. ✅ Test script passes
3. → Add Kurdistan24 to main scraper
4. → Run full Batch 3 collection
5. → Achieve 80%+ accuracy target!
