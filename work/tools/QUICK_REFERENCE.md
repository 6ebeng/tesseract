# 🚀 Quick Reference - Modular Corpus Expansion

## 📋 File Structure

```
tools/
├── scrapers/              # Package
│   ├── base_scraper.py   # Base classes
│   ├── config.py         # Settings
│   └── *_scraper.py      # Individual scrapers
├── expand_corpus_modular.py  # Main script
├── test_scrapers.py          # Verification tool
└── MODULAR_ARCHITECTURE.md   # Full docs
```

## ⚡ Quick Commands

### Test Scrapers (2 min)

```bash
wsl -d Ubuntu -- python3 /mnt/c/tesseract/work/tools/test_scrapers.py
```

### Run Collection (140 min)

```bash
wsl -d Ubuntu -- sudo docker start flaresolverr
wsl -d Ubuntu -- python3 /mnt/c/tesseract/work/tools/expand_corpus_modular.py
```

### Validate Syntax

```bash
wsl -d Ubuntu -- bash -lc "cd /mnt/c/tesseract/work/tools && python3 -m py_compile scrapers/*.py *.py"
```

## 🎯 Status

**Framework**: ✅ Complete  
**Scrapers**: 1/8 done (Kurdsat working)  
**Test Tool**: ✅ Working  
**Docs**: ✅ Complete

## 📝 TODO

Migrate 7 scrapers from `expand_corpus_batch3_reliable.py`:

- [ ] Rudaw (lines 115-158)
- [ ] Khak (lines 159-199)
- [ ] NRT (lines 200-291)
- [ ] Awene (lines 292-440)
- [ ] Kurdistan24 (lines 441-692)
- [ ] Xendan (lines 466-692)
- [ ] Sekokurd (lines 693-802)

## 🔧 How to Add Scraper

1. **Create** `scrapers/newsource_scraper.py`
2. **Configure** in `scrapers/config.py`
3. **Register** in `expand_corpus_modular.py`
4. **Test** with `test_scrapers.py`

## 📚 Full Documentation

- **Architecture**: `MODULAR_ARCHITECTURE.md`
- **Summary**: `REFACTORING_SUMMARY.md`
- **This Guide**: `QUICK_REFERENCE.md`

## ✅ Benefits

- ✅ Test in 2 min (was 2 hours)
- ✅ Easy debugging
- ✅ Isolated changes
- ✅ Parallel development
- ✅ Better maintainability
