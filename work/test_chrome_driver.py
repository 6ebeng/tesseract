#!/usr/bin/env python3
"""Test Chrome driver availability"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')

# Specify chromedriver path explicitly
service = Service('/usr/bin/chromedriver')

try:
    driver = webdriver.Chrome(service=service, options=opts)
    print("✓ Chrome driver initialized successfully")
    driver.get('https://www.google.com')
    print(f"✓ Loaded page: {driver.title}")
    driver.quit()
    print("✓ Test passed")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
