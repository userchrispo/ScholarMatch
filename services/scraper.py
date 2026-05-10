"""
Web scraper module for ScholarMatch.
Scrapes scholarship data from public sources that allow automated access.
Currently supports: yconic.com (robots.txt permits scraping of scholarship pages).
"""

import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as ET


HEADERS = {
    "User-Agent": "ScholarMatch/1.0 (Ontario Student Scholarship Finder; educational project)"
}

# Polite delay between requests (seconds)
REQUEST_DELAY = 1.5


def _get_page(url):
    """Fetch a URL with polite headers and delay."""
    time.sleep(REQUEST_DELAY)
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f"   [SCRAPER] Failed to fetch {url}: {e}")
        return None


def scrape_yconic_sitemap():
    """
    Parse yconic's scholarship sitemap to get all scholarship page URLs.
    Returns a list of URLs.
    """
    sitemap_url = "https://yconic.com/scholarships-sitemap.xml"
    response = _get_page(sitemap_url)
    
    if not response:
        return []
    
    urls = []
    try:
        root = ET.fromstring(response.content)
        namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        for url_elem in root.findall("ns:url", namespace):
            loc = url_elem.find("ns:loc", namespace)
            if loc is not None:
                urls.append(loc.text)
    except ET.ParseError as e:
        print(f"   [SCRAPER] Failed to parse sitemap XML: {e}")
    
    return urls


def scrape_yconic_scholarship(url):
    """
    Scrape a single yconic scholarship page.
    Extracts whatever structured data is available from the HTML.
    
    Returns a dict with scholarship data, or None if parsing fails.
    """
    response = _get_page(url)
    if not response:
        return None
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Extract the title (main scholarship name)
    title_tag = soup.find("h1")
    if not title_tag:
        return None
    
    name = title_tag.get_text(strip=True)
    
    # Extract meta description for the scholarship description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    description = meta_desc["content"] if meta_desc and meta_desc.get("content") else name
    
    # Extract og:description as fallback
    if description == name:
        og_desc = soup.find("meta", attrs={"property": "og:description"})
        description = og_desc["content"] if og_desc and og_desc.get("content") else name
    
    # Try to extract amount from the title (common pattern: "$X,XXX")
    amount = 0
    import re
    amount_match = re.search(r"\$(\d{1,3}(?:,\d{3})*)", name)
    if amount_match:
        amount = int(amount_match.group(1).replace(",", ""))
    
    if amount <= 0:
        amount = 1000  # Default if we can't parse amount
    
    # Build the scholarship record
    scholarship = {
        "name": name,
        "provider": "Yconic / Student Awards",
        "amount_min": amount,
        "amount_max": amount,
        "url": url,
        "description": description,
        # These can't be reliably extracted from yconic's light HTML
        # so we set sensible defaults
        "deadline": None,  # Will be filled during cleaning
        "eligibility": '{"education_level": ["university", "college"], "provinces": ["ontario"]}',
        "field_of_studys": '[]',
        "citizenship_requirement": "any"
    }
    
    return scholarship


def scrape_yconic():
    """
    Full yconic scraping pipeline.
    1. Get scholarship URLs from sitemap
    2. Scrape each page
    3. Return list of scholarship dicts
    """
    print("\n   [SCRAPER] Scraping yconic.com scholarships...")
    print("   [SCRAPER] Checking sitemap for scholarship URLs...")
    
    urls = scrape_yconic_sitemap()
    print(f"   [SCRAPER] Found {len(urls)} scholarship pages")
    
    scholarships = []
    for i, url in enumerate(urls):
        print(f"   [SCRAPER] Scraping ({i+1}/{len(urls)}): {url}")
        result = scrape_yconic_scholarship(url)
        if result:
            scholarships.append(result)
    
    print(f"   [SCRAPER] Successfully scraped {len(scholarships)} scholarships from yconic")
    return scholarships


def scrape_all():
    """
    Master scraping function. Calls all available scrapers.
    Returns combined list of scholarship dicts.
    
    Architecture note: New scrapers can be added here as additional
    source functions (e.g., scrape_scholarshipscanada(), scrape_universitystudy()).
    """
    all_scholarships = []
    
    # Yconic
    try:
        yconic_data = scrape_yconic()
        all_scholarships.extend(yconic_data)
    except Exception as e:
        print(f"   [SCRAPER] Yconic scraping failed: {e}")
    
    print(f"\n   [SCRAPER] Total scraped from all sources: {len(all_scholarships)}")
    return all_scholarships


if __name__ == "__main__":
    results = scrape_all()
    for r in results:
        print(f"  - {r['name']}: ${r['amount_max']}")
