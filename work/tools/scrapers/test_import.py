#!/usr/bin/env python3
"""Test generic_scraper imports"""
import sys

try:
    import generic_scraper
    print("✅ generic_scraper imports successfully")
    sys.exit(0)
except Exception as e:
    print(f"❌ Error importing generic_scraper: {e}")
    sys.exit(1)
