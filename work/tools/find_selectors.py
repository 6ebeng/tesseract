#!/usr/bin/env python3
"""
Find correct selectors for Khak TV article pages.
"""

from bs4 import BeautifulSoup

# Read the saved HTML
with open('khak_article_clickthrough.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=" * 80)
print("FINDING ARTICLE TITLE SELECTORS")
print("=" * 80)

# Find h1 tags
h1_tags = soup.find_all('h1')
print(f"\nFound {len(h1_tags)} h1 tags:")
for i, tag in enumerate(h1_tags[:5]):
    text = tag.get_text(strip=True)[:100]
    classes = tag.get('class', [])
    print(f"  [{i}] Classes: {classes}")
    print(f"      Text: {text}")
    print()

# Find h2 tags
h2_tags = soup.find_all('h2')
print(f"\nFound {len(h2_tags)} h2 tags:")
for i, tag in enumerate(h2_tags[:5]):
    text = tag.get_text(strip=True)[:100]
    classes = tag.get('class', [])
    print(f"  [{i}] Classes: {classes}")
    print(f"      Text: {text}")
    print()

print("=" * 80)
print("FINDING ARTICLE BODY SELECTORS")
print("=" * 80)

# Find main content container
main_tag = soup.find('main')
if main_tag:
    print(f"\nFound <main> tag with classes: {main_tag.get('class', [])}")
    
# Find article tags
article_tags = soup.find_all('article')
print(f"\nFound {len(article_tags)} article tags:")
for i, tag in enumerate(article_tags[:3]):
    classes = tag.get('class', [])
    print(f"  [{i}] Classes: {classes}")

# Find divs with "content" in class
content_divs = soup.find_all('div', class_=lambda x: x and 'content' in str(x).lower())
print(f"\nFound {len(content_divs)} divs with 'content' in class:")
for i, tag in enumerate(content_divs[:5]):
    classes = tag.get('class', [])
    print(f"  [{i}] Classes: {classes}")

# Find all paragraphs
p_tags = soup.find_all('p')
print(f"\nFound {len(p_tags)} paragraph tags")
if p_tags:
    # Sample first paragraph
    first_p = p_tags[0]
    print(f"  First <p> parent chain:")
    parent = first_p.parent
    depth = 0
    while parent and depth < 5:
        classes = parent.get('class', [])
        print(f"    Level {depth}: <{parent.name}> classes={classes}")
        parent = parent.parent
        depth += 1

print("\n" + "=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)

# Suggest selectors
if h2_tags:
    best_h2 = h2_tags[0]
    h2_classes = ' '.join(best_h2.get('class', []))
    if h2_classes:
        print(f"\nSuggested title selector: h2.{h2_classes.replace(' ', '.')}")
    else:
        print(f"\nSuggested title selector: main h2 (or just h2)")

if p_tags:
    # Find common parent
    first_p_parent = p_tags[0].parent
    parent_classes = ' '.join(first_p_parent.get('class', []))
    if parent_classes:
        print(f"Suggested body selector: .{parent_classes.replace(' ', '.')} > p")
    else:
        print(f"Suggested body selector: {first_p_parent.name} > p (or just p)")
