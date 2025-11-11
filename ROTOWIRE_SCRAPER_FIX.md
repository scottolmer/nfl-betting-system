# RotoWire Injury Scraper - JavaScript Issue & Fix

## Problem Identified

The original `fetch_rotowire_injuries.py` was failing because:

1. **RotoWire loads injury data via JavaScript** - The page shows "Loading NFL Injury Report" in the raw HTML
2. **BeautifulSoup can't execute JavaScript** - It only parses static HTML, so the table never appears
3. **Table class selectors didn't exist** - The specific `'tr-table scrollable'` class wasn't in the raw HTML either

When the script tried to find the table with BeautifulSoup, it couldn't find anything because the content hadn't been rendered yet.

## Solution: Use Selenium

Selenium is a browser automation tool that actually opens a Chrome browser, loads the page, waits for JavaScript to run, and *then* lets you scrape the rendered content.

### What Changed

**Before (didn't work):**
```python
import requests
from bs4 import BeautifulSoup

response = requests.get(url)  # Gets raw HTML only
soup = BeautifulSoup(response.content, 'html.parser')
table = soup.find('table', {'class': 'tr-table scrollable'})  # Not in raw HTML!
```

**After (works):**
```python
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()  # Opens real browser
driver.get(url)  # Loads page and runs JavaScript
wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'table')))  # Waits for table
tables = driver.find_elements(By.TAG_NAME, 'table')  # Now table exists!
```

## Installation

Install the required dependencies:

```bash
pip install selenium webdriver-manager
```

Or if updating requirements:
```bash
pip install -r requirements.txt
```

## How It Works

1. **Opens Chrome browser** (with anti-detection options)
2. **Loads RotoWire injury page** - JavaScript runs
3. **Waits up to 15 seconds** for the table to appear
4. **Extracts all table data** once rendered
5. **Closes browser** and returns DataFrame

## Running the Script

```bash
python scripts/fetch_rotowire_injuries.py --output-dir data --week 8
```

Or in code:
```python
from scripts.fetch_rotowire_injuries import download_rotowire_injuries

csv_path = download_rotowire_injuries(output_dir='data', week=8)
print(f"Injuries saved to: {csv_path}")
```

## What It Outputs

Returns a CSV with columns:
- **Player**: Player name
- **Team**: NFL team
- **Position**: QB, RB, WR, TE, etc.
- **Status**: Out, Questionable, Doubtful, Day-to-Day, etc.
- **Details**: Injury details (hamstring, knee, etc.)
- **Date**: When the report was pulled

## Benefits

✅ Actually works with JavaScript-rendered content
✅ Automatically handles waiting for page load
✅ Handles anti-bot detection
✅ More reliable than HTTP-based scraping
✅ Can extract any element visible on the rendered page

## Potential Issues & Fixes

**Issue: Chrome not found**
- Solution: `webdriver-manager` automatically downloads the right ChromeDriver version

**Issue: Takes too long**
- Currently waits 15 seconds max (configurable in code)
- Can uncomment `--headless` option to run browser in background (faster)

**Issue: Too much output**
- Comment out the logging lines or adjust logging level

## Future Improvements

1. Run headless by default (faster for production)
2. Add retry logic if table doesn't appear
3. Cache results to avoid repeated scrapes
4. Consider using other scraping libraries (Playwright) for parallel requests
