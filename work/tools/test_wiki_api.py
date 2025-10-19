#!/usr/bin/env python3
import requests

# Test Wikipedia API
url = "https://ckb.wikipedia.org/w/api.php"
params = {
    'action': 'query',
    'format': 'json',
    'list': 'random',
    'rnnamespace': 0,
    'rnlimit': 5
}

print(f"Testing: {url}")
print(f"Params: {params}\n")

try:
    r = requests.get(url, params=params, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:500]}")
    
    if r.status_code == 200:
        data = r.json()
        if 'query' in data and 'random' in data['query']:
            articles = data['query']['random']
            print(f"\n✅ Got {len(articles)} random articles:")
            for art in articles:
                print(f"   - {art['title']}")
        else:
            print(f"\n⚠️  Response structure: {list(data.keys())}")
except Exception as e:
    print(f"❌ Error: {e}")
