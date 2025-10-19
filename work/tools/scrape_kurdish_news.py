#!/usr/bin/env python3
import re, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

class QC:
    def __init__(self):
        self.k = set('ئابپīجچحخدرصژزیشصغڔقص٢ڪطګلنوۖضهۙیۊێ')
    def words(self, t): return len(re.findall(r'[\w\u0600-\u06FF]+', t))
    def zwnj(