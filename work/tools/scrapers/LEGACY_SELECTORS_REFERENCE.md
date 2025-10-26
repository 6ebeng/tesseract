# Legacy Scrapers - Working Selectors Reference

This document extracts all **PROVEN WORKING** selectors from legacy scrapers for migration to YAML configs.

---

## 1. Kurdsat TV

**Legacy File:** `kurdsat_scraper.py`

### Article List (Collection)

```python
articles = driver.find_elements(By.CSS_SELECTOR, "a[href*='/ckb/news/']")
```

### Article Detail Page

```python
# Primary selector
paragraphs = driver.find_elements(By.CSS_SELECTOR, ".article-body p")

# Fallback 1
paragraphs = driver.find_elements(By.CSS_SELECTOR, ".content p")

# Fallback 2
paragraphs = driver.find_elements(By.TAG_NAME, "p")
```

### Load More Button (for news page)

```python
button = driver.find_element(By.XPATH, "//button[contains(text(),'زیاتر ببینە')]")
```

### Category URLs (Specialized)

```python
categories = [
    ('Health', 'https://kurdsat.tv/ckb/categories/8'),
    ('Science', 'https://kurdsat.tv/ckb/categories/16'),
    ('Technology', 'https://kurdsat.tv/ckb/categories/9'),
    ('Opinion', 'https://news.kurdsat.tv/ckb/opinions')
]
```

---

## 2. Rudaw

**Legacy File:** `rudaw_scraper.py`

### Article List (Collection)

```python
articles = driver.find_elements(By.CSS_SELECTOR, "a[href*='/sorani/']")

# Filter for actual articles (must end with number)
if link and '/sorani/' in link and re.search(r'/\d+$', link):
    article_urls.append(link)
```

### Article Detail Page

```python
content_divs = driver.find_elements(By.CSS_SELECTOR, ".content div")

# Split content into sentences
sents = re.split(r'[.؟!،]\s*', text)
```

### Pagination Method

- **Type:** Infinite Scroll
- **Scrolls:** 20 (political), 15 (specialized)

### Category URLs

```python
categories = [
    ('Political', 'https://www.rudaw.net/sorani/kurdistan'),
    ('Economy', 'https://www.rudaw.net/sorani/business'),
    ('Health', 'https://www.rudaw.net/sorani/news?CategoryID=412631'),
    ('Sport', 'https://www.rudaw.net/sorani/news?CategoryID=412632'),
    ('Culture', 'https://www.rudaw.net/sorani/culture'),
    ('Interview', 'https://www.rudaw.net/sorani/news?CategoryID=412627')
]
```

---

## 3. GovKrd

**Legacy File:** `govkrd_scraper.py`

### Article List (Collection)

```python
article_items = driver.find_elements(By.CSS_SELECTOR, "div.item a[href*='/ka/activities/']")
```

### Article Detail Page

```python
# Title
title_elem = driver.find_element(By.CSS_SELECTOR, "h1.heading.main")

# Content paragraphs
paragraphs = driver.find_elements(By.CSS_SELECTOR, "div.right-col p")

# Split into sentences
sentences = re.split(r'[.؟!]\s+', text)
```

### Pagination Method

- **Type:** Standard pagination with page parameter
- **Pages:** 5
- **URL Pattern:** `https://gov.krd/ka/activities/?page={page}`

---

## 4. Sekokurd

**Legacy File:** `sekokurd_scraper.py`

### Article List (Collection)

```python
titles = driver.find_elements(By.CSS_SELECTOR, '.anwp-pg-post-teaser__title a')
```

### Load More Button

```python
load_more = driver.find_elements(By.CSS_SELECTOR, '.anwp-pg-load-more__btn')
```

### Article Detail Page

```python
# Title
title_elem = driver.find_element(By.CSS_SELECTOR, '.wpr-post-title')

# Content
content_elem = driver.find_element(By.CSS_SELECTOR, '.wpr-post-content')
```

### Pagination Method

- **Type:** Click Load More
- **Clicks:** 10

### Category URLs

```python
categories = [
    ('Articles', 'https://sekokurd.org/?page_id=874'),
    ('Culture', 'https://sekokurd.org/?page_id=1614')
]
```

---

## 5. Sharpress

**Legacy File:** `sharpress_scraper.py`

### Article List (Collection)

```python
# News items in list view
items = driver.find_elements(By.CSS_SELECTOR, "div.news-item a")
# OR
titles = driver.find_elements(By.CSS_SELECTOR, "h3.hawal-title a")
```

### Article Detail Page

```python
# Title
title = driver.find_element(By.CSS_SELECTOR, "h1.hawal-title, h1")

# Content
paragraphs = driver.find_elements(By.CSS_SELECTOR, ".hawal-text p, .content p")
```

### Pagination Method

- **Type:** Standard pagination
- **Pages:** 5 (political), 3 (specialized)
- **URL Pattern:** `?page={page}`

### Category URLs (Specialized)

```python
categories = [
    ('Economy', 'https://www.sharpress.net/all-hawal.aspx?Cor=abwri&Nawnishan=%D8%A6%D8%A7%D8%A8%D9%88%D8%B1%DB%8C'),
    ('Sport', 'https://www.sharpress.net/all-hawal.aspx?Cor=Werziş&Nawnishan=%D9%88%DB%95%D8%B1%D8%B2%D8%B4'),
    ('Culture', 'https://www.sharpress.net/all-hawal.aspx?Cor=Kültür&Nawnishan=%DA%A9%D9%88%D9%84%D8%AA%D9%88%D9%88%D8%B1'),
    ('Health', 'https://www.sharpress.net/all-hawal.aspx?Cor=tandrwsti&Nawnishan=%D8%AA%DB%95%D9%86%D8%AF%D8%B1%D9%88%D8%B3%D8%AA%DB%8C'),
    ('Opinion', 'https://www.sharpress.net/opinion.aspx?Cor=Birura&Nawnishan=%D8%A8%DB%8C%D8%B1%D9%88%DA%95%D8%A7')
]
```

---

## 6. Awene

**Legacy File:** `awene_scraper.py`

### Article List (Collection)

```python
# List page titles
titles = driver.find_elements(By.CSS_SELECTOR, ".newstopsumbtitle a")

# Get title from attribute
text = title.get_attribute('title')
```

### Article Detail Page

```python
# Content
paragraphs = driver.find_elements(By.CSS_SELECTOR, ".viewdesc p")
```

### Pagination Method

- **Type:** Standard pagination
- **Pages:** 10 (political), varies (specialized)
- **URL Pattern:** `?section=2&page={page}` OR `/culture`, `/economy`, etc.

### Article URL Patterns

```python
# Political
'detail?article=' in href

# Articles section
'article?no=' in href
```

### Category URLs

```python
categories = [
    ('Political', 'https://www.awene.com/part?section=2'),
    ('Articles', 'https://www.awene.com/articles'),
    ('Culture', 'https://www.awene.com/culture'),
    ('Economy', 'https://www.awene.com/aburi'),
    ('Health', 'https://www.awene.com/health'),
    ('Multimedia', 'https://www.awene.com/multimedia')
]
```

---

## 7. Khak TV

**Legacy File:** `khak_scraper.py`

### Article List (Collection)

```python
links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/article/']")
```

### Article Detail Page

```python
# Modern structure - content in <main> without <p> tags
main_content = driver.find_element(By.TAG_NAME, "main")
text = main_content.text.strip()

# Fallback to paragraphs
paragraphs = driver.find_elements(By.CSS_SELECTOR, ".html-content p, .content p, p")
```

### Pagination Method

- **Type:** Standard pagination
- **Pages:** 10
- **URL Pattern:** `?group=5&page={page}`

---

## 8. Kurdistan24

**Legacy File:** `kurdistan24_scraper.py`

**NOTE:** Requires FlareSolverr for Cloudflare bypass

### Article List (Collection)

```python
# Uses BeautifulSoup after FlareSolverr
soup.find_all('div', class_='views-row')
link_elem = row.find('a', href=True)
```

### Article Detail Page

```python
# Title
title = soup.find('h1', class_='text-black')

# Content
content_div = soup.find('div', class_='content')
paragraphs = content_div.find_all('p')
```

### Pagination Method

- **Type:** Standard pagination
- **Pages:** 10
- **URL Pattern:** `?page={page}`

---

## 9. Xendan

**Legacy File:** `xendan_scraper.py`

### Article List (Collection)

```python
# Article cards
cards = driver.find_elements(By.CSS_SELECTOR, '.card-small')

# Get link from parent
link_elem = card.find_element(By.XPATH, '..')
link = link_elem.get_attribute('href')

# Get title
title_elem = card.find_element(By.CSS_SELECTOR, 'h2')
```

### Article Detail Page

```python
# Title
title_elem = driver.find_element(By.CSS_SELECTOR, '.detail-top h1')

# Content
paragraphs = driver.find_elements(By.CSS_SELECTOR, '.detail-big-text-p p')
```

### Pagination Method

- **Type:** Next button click
- **Pages:** 10
- **Next Button:** `a.nextbutton` with text 'دواتر'

---

## 10. LvinPress

**Legacy File:** `lvinpress_scraper.py`

### Article List (Collection)

```python
# Elementor posts
article_elements = driver.find_elements(
    By.CSS_SELECTOR,
    "article.elementor-post h3.elementor-post__title a"
)

# Filter out video articles
if url and ('/news/' in url or '/birura/' in url) and '/video/' not in url:
    article_urls.append(url)
```

### Article Detail Page

```python
# Title - h1 first, h2 fallback
title_elem = driver.find_element(By.TAG_NAME, "h1")

# Content
paragraphs = driver.find_elements(By.CSS_SELECTOR, ".entry-content p")
```

### Pagination Method

- **Type:** Standard pagination
- **Pages:** 5 (political), 3 (specialized)
- **URL Pattern:** `/page/{page_num}`

### Category URLs

```python
categories = [
    ('Kurdistan News', 'https://lvinpress.com/category/news/kurdistan'),
    ('Social Media', 'https://lvinpress.com/category/socialmedia'),
    ('Opinion', 'https://lvinpress.com/category/birura')
]
```

---

## 11. Balinde

**Legacy File:** `balinde_scraper.py`

### Article List (Collection)

```python
# Card elements
article_elements = driver.find_elements(
    By.CSS_SELECTOR,
    "div.cards a.card"
)
```

### Article Detail Page

```python
# Content in poetry timeline
content = driver.find_element(By.CSS_SELECTOR, "div.poet-timeline")

# Also extract from paragraphs
paragraphs = driver.find_elements(By.CSS_SELECTOR, ".entry-content p")
```

### Pagination Method

- **Type:** Standard pagination
- **Pages:** 5
- **URL Pattern:** `/page/{page_num}/`

### Category URLs

```python
categories = [
    ('Kurdish Poetry', 'https://balinde.com/category/kurdishpoem'),
    ('Articles', 'https://balinde.com/category/wtar')
]
```

---

## Common Patterns Observed

### Fallback Chains for Content Extraction

Most scrapers use fallback chains:

```python
# Pattern 1: Specific to generic
paragraphs = driver.find_elements(By.CSS_SELECTOR, ".article-body p")
if not paragraphs:
    paragraphs = driver.find_elements(By.CSS_SELECTOR, ".content p")
if not paragraphs:
    paragraphs = driver.find_elements(By.TAG_NAME, "p")

# Pattern 2: Multiple selector attempt
content_divs = driver.find_elements(By.CSS_SELECTOR, ".content div")
```

### Sentence Splitting

Many scrapers split content into sentences:

```python
import re
sentences = re.split(r'[.؟!،]\s*', text)
```

### URL Filtering

Common patterns to identify actual articles:

```python
# Pattern 1: Must contain specific path
if '/ckb/news/' in link

# Pattern 2: Must end with number
if re.search(r'/\d+$', link)

# Pattern 3: Must contain keyword
if 'article=' in href or 'detail?article=' in href

# Pattern 4: Exclude patterns
if '/video/' not in url
```

---

## Selector Priority Recommendations

Based on legacy success rates:

### For Article Lists

1. **Specific CSS selector with href pattern** (most reliable)
   - `a[href*='/ckb/news/']`
   - `div.item a[href*='/activities/']`
2. **CSS class selectors**
   - `.card-small`, `.anwp-pg-post-teaser__title a`
3. **Generic with filter**
   - `a[href*='/sorani/']` + regex filter

### For Article Content

1. **Specific content class + p**
   - `.article-body p`, `.viewdesc p`, `.content p`
2. **Content div**
   - `.content div`, `div.right-col p`
3. **Generic fallback**
   - `p` (all paragraphs)
4. **Modern structure**
   - `main` (for sites without p tags like Khak)

### For Titles

1. **h1 with class**
   - `h1.heading.main`, `.detail-top h1`
2. **Generic h1**
   - `h1`, `h2`
3. **Title from link**
   - `title` attribute on `<a>` tags

---

## Migration Checklist

When updating YAML configs:

- ✅ Use exact selectors from legacy (proven working)
- ✅ Include fallback selectors as array
- ✅ Match pagination type (pagination/infinite_scroll/click_load_more)
- ✅ Match wait times (legacy used 2-3 seconds)
- ✅ Preserve URL patterns exactly
- ✅ Keep same click/scroll/page counts for consistency
- ✅ Test extraction with same article limits
