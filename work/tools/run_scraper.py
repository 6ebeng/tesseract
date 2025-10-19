#!/usr/bin/env python3
"""Kurdish News Scraper with Selenium - properly handles Kurdsat button and Rudaw scrolling"""
import re, time, sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

class QC:
    def __init__(self):
        self.k = set('ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنوۆهەیێءأؤإآةى')
    def words(self, t): return len(re.findall(r'[\w\u0600-\u06FF]+', t))
    def zwnj(self, t): return (t.count('\u200c')/len(t)*100) if t else 0.0
    def purity(self, t):
        if not t: return 0.0
        k = sum(1 for c in t if c in self.k or '\u0600'<=c<='\u06FF')
        l = sum(1 for c in t if c.isalpha() or '\u0600'<=c<='\u06FF')
        return (k/l*100) if l>0 else 0.0
    def ok(self, s):
        s = s.strip()
        if not s or len(s)<30: return False
        w = self.words(s)
        if w<10 or w>25: return False
        if self.purity(s)<70: return False
        lat = sum(1 for c in s if 'a'<=c.lower()<='z')
        if lat/len(s)>0.15: return False
        if sum(1 for c in s if c.isupper())>len(s)*0.5: return False
        if sum(1 for c in s if c.isdigit())>len(s)*0.2: return False
        return 'http' not in s and 'www.' not in s

class Scraper:
    def __init__(self):
        self.qc, self.sents = QC(), set()
        self.st = {'k':{'a':0,'s':0},'r':{'a':0,'s':0}}
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument('--disable-gpu')
        opts.add_argument('--window-size=1920,1080')
        self.d = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=opts)
    
    def close(self): self.d.quit()
    
    def extr(self, t):
        return [s.strip() for s in re.split(r'[.!?؟]\s+', t) if self.qc.ok(s.strip())]
    
    def kart(self, u):
        try:
            self.d.get(u); time.sleep(2)
            so = BeautifulSoup(self.d.page_source, 'html.parser')
            ar = so.select_one('.article-body')
            if not ar: return []
            res = []
            for p in ar.find_all('p'):
                t = ' '.join(p.get_text(separator=' ', strip=True).split())
                if len(t)>50: res.extend(self.extr(t))
            return res
        except: return []
    
    def rart(self, u):
        try:
            self.d.get(u); time.sleep(2)
            so = BeautifulSoup(self.d.page_source, 'html.parser')
            ar = so.select_one('.bodyContentMainParent') or so.select_one('.article-body')
            if not ar:
                dv = so.find_all('div', class_='selectionShareable')
                if dv:
                    res = []
                    for d in dv:
                        t = ' '.join(d.get_text(separator=' ', strip=True).split())
                        if len(t)>50: res.extend(self.extr(t))
                    return res
                return []
            res = []
            for p in ar.find_all(['p','div']):
                t = ' '.join(p.get_text(separator=' ', strip=True).split())
                if len(t)>50: res.extend(self.extr(t))
            return res
        except: return []
    
    def findk(self):
        li = set()
        print('🔍 Loading Kurdsat news page...')
        self.d.get('https://kurdsat.tv/ckb/news'); time.sleep(3)
        
        # Click "زیاتر ببینە" button 15 times to load more articles
        for i in range(15):
            so = BeautifulSoup(self.d.page_source, 'html.parser')
            for a in so.find_all('a', href=True):
                h = a['href']
                if 'kurdsatnews.com' in h and '/news/' in h:
                    u = h if h.startswith('http') else 'https://kurdsat.tv'+h
                    if u.rstrip('/').split('/')[-1].isdigit(): li.add(u)
            try:
                # Use the exact button structure you provided
                btn = self.d.find_element(By.XPATH, "//button[contains(text(),'زیاتر ببینە')]")
                btn.click(); time.sleep(2)
                print(f'  Clicked See More {i+1}/15: {len(li)} articles found')
            except Exception as e:
                print(f'  No more See More button (clicked {i} times)')
                break
        return list(li)
    
    def findr(self):
        li = set()
        print('🔍 Loading Rudaw news page (scrolling)...')
        self.d.get('https://www.rudaw.net/sorani/news'); time.sleep(3)
        
        # Scroll down 10 times to load more articles
        last = self.d.execute_script('return document.body.scrollHeight')
        for i in range(10):
            # Scroll to bottom
            self.d.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(2)
            
            # Get new height
            new = self.d.execute_script('return document.body.scrollHeight')
            
            # Extract links
            so = BeautifulSoup(self.d.page_source, 'html.parser')
            for a in so.find_all('a', href=True):
                h = a['href']
                if 'rudaw.net/sorani/' in h:
                    u = h if h.startswith('http') else 'https://www.rudaw.net'+h
                    if u.rstrip('/').split('/')[-1].isdigit(): li.add(u)
            
            print(f'  Scroll {i+1}/10: {len(li)} articles found')
            
            # Stop if no new content loaded
            if new == last: break
            last = new
        
        return list(li)[:100]  # Limit to 100
    
    def scrapek(self):
        print(f"\n{'='*70}\n📰 Scraping Kurdsat News\n{'='*70}\n")
        lk = self.findk()
        print(f'\n✓ Found {len(lk)} Kurdsat articles\n')
        
        for i, u in enumerate(lk[:300], 1):
            if len(self.sents) >= 1500:
                print(f'\n🎯 Reached target of 1500 sentences!')
                break
            
            print(f'📄 [{i}/{min(len(lk),300)}] {u[:65]}...', end=' ')
            ss = self.kart(u)
            if ss:
                new = [x for x in ss if x not in self.sents]
                self.sents.update(new)
                self.st['k']['s'] += len(new)
                self.st['k']['a'] += 1
                print(f'✅ {len(new)} (Total: {len(self.sents)})')
            else:
                print('⚠️')
            
            time.sleep(1)
    
    def scraper(self):
        if len(self.sents) >= 1500:
            print('\n✅ Already have 1500 sentences, skipping Rudaw')
            return
        
        print(f"\n{'='*70}\n📰 Scraping Rudaw News\n{'='*70}\n")
        lr = self.findr()
        print(f'\n✓ Found {len(lr)} Rudaw articles\n')
        
        for i, u in enumerate(lr[:200], 1):
            if len(self.sents) >= 1500:
                print(f'\n🎯 Reached target of 1500 sentences!')
                break
            
            print(f'📄 [{i}/{min(len(lr),200)}] {u[:65]}...', end=' ')
            ss = self.rart(u)
            if ss:
                new = [x for x in ss if x not in self.sents]
                self.sents.update(new)
                self.st['r']['s'] += len(new)
                self.st['r']['a'] += 1
                print(f'✅ {len(new)} (Total: {len(self.sents)})')
            else:
                print('⚠️')
            
            time.sleep(1)
    
    def save(self):
        ss = sorted(self.sents)
        with open('/mnt/c/tesseract/work/corpus/kurdish_news_batch2.txt', 'w', encoding='utf-8') as f:
            f.write(f'# Kurdish News Batch 2 (Selenium)\n')
            f.write(f'# Total: {len(ss)} sentences\n')
            f.write(f'# Kurdsat: {self.st["k"]["s"]} from {self.st["k"]["a"]} articles\n')
            f.write(f'# Rudaw: {self.st["r"]["s"]} from {self.st["r"]["a"]} articles\n')
            f.write(f'# Quality: 10-25 words, 0-100% ZWNJ, >70% Kurdish purity\n')
            f.write(f'#\n\n')
            for s in ss: f.write(s + '\n')
        print(f'\n💾 Saved {len(ss)} sentences to corpus/kurdish_news_batch2.txt')
    
    def stats(self):
        print(f"\n{'='*70}\n📊 COLLECTION STATISTICS\n{'='*70}")
        print(f"Kurdsat: {self.st['k']['s']} sentences from {self.st['k']['a']} articles")
        print(f"Rudaw: {self.st['r']['s']} sentences from {self.st['r']['a']} articles")
        pct = len(self.sents)/15*100 if len(self.sents) < 1500 else 100.0
        print(f"Total: {len(self.sents)} unique sentences / 1500 target ({pct:.1f}%)")
        
        if self.sents:
            w = sum(self.qc.words(s) for s in self.sents)
            z = sum(self.qc.zwnj(s) for s in self.sents)
            print(f'Avg words: {w/len(self.sents):.1f}')
            print(f'Avg ZWNJ: {z/len(self.sents):.2f}%')

if __name__ == '__main__':
    print('='*70)
    print('🚀 Kurdish News Scraper v3.0 (Selenium)')
    print('='*70)
    print('\n📋 Target: 1500 quality sentences')
    print('   Quality: 10-25 words, >70% Kurdish purity')
    print('   Method: Selenium + Chromium (JavaScript rendering)\n')
    
    sc = Scraper()
    try:
        sc.scrapek()
        sc.scraper()
        sc.save()
        sc.stats()
        
        print(f"\n{'='*70}")
        if len(sc.sents) >= 1000:
            print(f'✅ SUCCESS! Collected {len(sc.sents)} sentences')
            print('\n📋 Next steps:')
            print('  1. Quality check: python3 tools/corpus_quality_checker.py corpus/kurdish_news_batch2.txt')
            print('  2. Combine with Phase 4 corpus')
            print('  3. Train Batch 2 models')
        else:
            print(f'⚠️  Only collected {len(sc.sents)} sentences (need 1000+)')
            print('   Run scraper again to collect more')
        print('='*70)
    
    except KeyboardInterrupt:
        print('\n\n⚠️  Interrupted by user')
        sc.save()
        sc.stats()
    finally:
        sc.close()
