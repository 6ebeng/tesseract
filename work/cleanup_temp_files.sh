#!/bin/bash
# Cleanup unnecessary temporary and legacy files

echo "=========================================="
echo "🧹 CLEANING UP UNNECESSARY FILES"
echo "=========================================="

cd /mnt/c/tesseract/work

# Count files before cleanup
echo ""
echo "📊 Files before cleanup:"
find . -maxdepth 1 -type f | wc -l

echo ""
echo "🗑️  Removing temporary test scripts..."

# Remove debug/test scripts
rm -f debug_lvinpress_article.py
rm -f debug_rudaw_sentences.py
rm -f debug_sharpress.py
rm -f debug_splitting_strategies.py
rm -f debug_video_article.py
rm -f demo_clean_errors.py
rm -f test_clean_errors.py
rm -f test_clean_output.py
rm -f test_fixer.py
rm -f test_lvinpress_quick.py
rm -f test_opinion.py
rm -f test_pag2.py
rm -f test_pagination.py
rm -f test_pagination_direct.py
rm -f test_rudaw_interview.py
rm -f test_rudaw_specialized.py
rm -f test_sharpress.py
rm -f test_sharpress_quick.py
rm -f test_video_extraction.py
rm -f verify_opinion_pagination.py
rm -f verify_pagination.py
rm -f test_balinde.py
rm -f check_video_content.py

# Remove legacy check scripts
rm -f check_ocr_zwnj.py
rm -f check_source_zwnj.py
rm -f check_unicode_cat.py
rm -f check_zwnj.py

# Remove temporary output files
rm -f scrape_log.txt
rm -f sharpress_live.log
rm -f sharpress_output.txt
rm -f sharpress_test_output.txt
rm -f zwnj_line.txt
rm -f mgk_phase4.txt
rm -f mgk_phase4_processed.txt
rm -f mgk_phase4_v2.txt
rm -f mgk_phase4_v3.txt

# Remove legacy documentation (keeping only essential docs)
rm -f ACCURACY_IMPROVEMENT_PLAN.md
rm -f AWENE_SPECIALIZED_ADDED.md
rm -f ECONOMY_ADDED.md
rm -f ECONOMY_VERIFIED.md
rm -f FLARESOLVERR_SETUP.md
rm -f INTEGRATION_FINAL.md
rm -f SEKOKURD_ADDED.md
rm -f READY_TO_EXECUTE.md
rm -f QUICK_REFERENCE.md
rm -f CLEAN_ERROR_MESSAGES.md

# Remove Python cache directories
rm -rf __pycache__

echo "✅ Removed temporary test scripts"
echo "✅ Removed legacy check scripts"
echo "✅ Removed temporary output files"
echo "✅ Removed legacy documentation"
echo "✅ Removed Python cache"

# Clean up tools directory
echo ""
echo "🗑️  Cleaning tools directory..."
cd tools

# Remove legacy scraper scripts
rm -f scrape_kurdish_news.py
rm -f scrape_rudaw_live.py
rm -f run_scraper.py
rm -f test_sharpress.py

# Remove legacy corpus expansion scripts
rm -f expand_corpus_batch3.py
rm -f expand_corpus_batch3_reliable.py

# Remove Python cache
rm -rf __pycache__

echo "✅ Cleaned tools directory"

cd ..

# Count files after cleanup
echo ""
echo "📊 Files after cleanup:"
find . -maxdepth 1 -type f | wc -l

echo ""
echo "=========================================="
echo "✅ CLEANUP COMPLETE"
echo "=========================================="
echo ""
echo "Kept essential files:"
echo "  ✅ Main scripts (execute_ckb_training.sh, generate_ckb_training_data.sh)"
echo "  ✅ Core tools (verify_ckb_traineddata.py, kurdish_character_fixer.py)"
echo "  ✅ README.md and Makefile"
echo "  ✅ Active corpus and training files"
echo "  ✅ Modular scraper system (tools/scrapers/)"
echo ""
echo "Removed:"
echo "  🗑️  Temporary test scripts (30+ files)"
echo "  🗑️  Legacy documentation (10+ files)"
echo "  🗑️  Debug scripts and outputs"
echo "  🗑️  Python cache directories"
echo ""
