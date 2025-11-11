"""
RotoWire Injury Report Scraper
Fetches NFL injury data from https://www.rotowire.com/football/injury-report.php
Automatically updates your injury report CSV

Uses Selenium to click the "Export to CSV" button and download the file directly
"""

import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
import time
import os
import shutil

logger = logging.getLogger(__name__)

# Try importing Selenium - if not available, provide helpful error
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.action_chains import ActionChains
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("Selenium not installed. Run: pip install selenium webdriver-manager")


class RotoWireInjuryScraper:
    """Scrapes injury data from RotoWire by clicking the export CSV button"""
    
    def __init__(self):
        self.url = "https://www.rotowire.com/football/injury-report.php"
    
    def fetch_injuries(self, download_dir: str = None) -> str:
        """
        Fetch injury data from RotoWire by clicking export button
        
        Returns:
            Path to downloaded CSV file
        """
        if not SELENIUM_AVAILABLE:
            logger.error("Selenium not available. Install: pip install selenium webdriver-manager")
            return None
        
        # Set up download directory
        if download_dir is None:
            download_dir = str(Path.home() / "Downloads")
        
        Path(download_dir).mkdir(parents=True, exist_ok=True)
        
        driver = None
        try:
            logger.info("Fetching injuries from RotoWire...")
            
            # Set up Chrome options with download directory
            options = webdriver.ChromeOptions()
            options.add_argument('--start-maximized')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Configure download directory
            prefs = {
                "download.default_directory": download_dir,
                "download.prompt_for_download": False,
                "profile.default_content_settings.popups": 0
            }
            options.add_experimental_option("prefs", prefs)
            
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            
            # Load the page
            logger.info("Loading RotoWire injury report page...")
            driver.get(self.url)
            
            # Wait for the page to load
            logger.info("Waiting for page to load...")
            wait = WebDriverWait(driver, 30)
            
            try:
                # Wait for table to appear first
                wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'table')))
                logger.info("Table loaded, waiting additional time for buttons to render...")
                time.sleep(3)
                
            except Exception as e:
                logger.warning(f"Table not found: {e}")
                return None
            
            # Scroll down to find export button
            logger.info("Scrolling to find export button...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Try multiple ways to find and click export button
            export_button = None
            button_selectors = [
                "//button[@class='export-button is-csv']",
                "//button[contains(@class, 'export-button')]",
                "//button[contains(@class, 'is-csv')]",
                "//button[contains(text(), 'Export')]",
                "//button[contains(text(), 'export')]",
                "//button[contains(., 'Export')]",
                "//a[contains(text(), 'Export')]",
                "//a[contains(text(), 'export')]",
                "//*[contains(@class, 'export')]",
                "//button[@title*='Export']",
                "//button[@title*='export']",
            ]
            
            for selector in button_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    if elements:
                        export_button = elements[0]
                        logger.info(f"✅ Found export button using selector: {selector}")
                        logger.info(f"   Button text: {export_button.text}")
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            if not export_button:
                # Try finding ALL buttons and log them for debugging
                logger.warning("Could not find export button, listing all buttons on page:")
                all_buttons = driver.find_elements(By.TAG_NAME, "button")
                logger.info(f"Found {len(all_buttons)} buttons total:")
                for i, btn in enumerate(all_buttons):
                    text = btn.text[:50] if btn.text else "(no text)"
                    classes = btn.get_attribute("class") or "(no classes)"
                    logger.info(f"  Button {i}: text='{text}' class='{classes}'")
                
                # Also check for links
                all_links = driver.find_elements(By.TAG_NAME, "a")
                logger.info(f"\nFound {len(all_links)} links total:")
                for i, link in enumerate(all_links[:10]):  # Show first 10
                    text = link.text[:50] if link.text else "(no text)"
                    href = link.get_attribute("href") or "(no href)"
                    logger.info(f"  Link {i}: text='{text}' href='{href[:50]}'")
                
                return None
            
            # Click the export button
            try:
                logger.info("Clicking export button...")
                # Use ActionChains to ensure the button is visible and clickable
                actions = ActionChains(driver)
                actions.move_to_element(export_button).click().perform()
                
                # Wait for file to download
                logger.info("Waiting for file to download...")
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"Failed to click export button: {e}")
                logger.info("Trying alternative click method...")
                try:
                    driver.execute_script("arguments[0].click();", export_button)
                    time.sleep(3)
                except Exception as e2:
                    logger.error(f"Alternative click also failed: {e2}")
                    return None
            
            # Find the downloaded CSV file
            logger.info(f"Looking for downloaded file in {download_dir}...")
            
            # Wait a bit more for file to fully download
            max_wait = 10
            downloaded_file = None
            
            for attempt in range(max_wait):
                csv_files = list(Path(download_dir).glob("*.csv"))
                
                if csv_files:
                    # Get the most recently modified file
                    downloaded_file = max(csv_files, key=lambda p: p.stat().st_mtime)
                    logger.info(f"✅ Downloaded file found: {downloaded_file.name}")
                    break
                
                logger.debug(f"Waiting for download... ({attempt + 1}/{max_wait})")
                time.sleep(1)
            
            if not downloaded_file:
                logger.error("No CSV file found in downloads directory")
                logger.info(f"Files in {download_dir}:")
                for f in Path(download_dir).iterdir():
                    logger.info(f"  - {f.name}")
                return None
            
            return str(downloaded_file)
        
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
        
        finally:
            if driver:
                driver.quit()
                logger.info("Browser closed")
    
    def save_to_final_location(self, source_csv: str, output_path: str) -> bool:
        """Copy the downloaded CSV to the desired output location"""
        try:
            if not os.path.exists(source_csv):
                logger.error(f"Source file not found: {source_csv}")
                return False
            
            # Create output directory if needed
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_csv, output_path)
            logger.info(f"✅ Saved injuries to {output_path}")
            
            # Read and log summary
            df = pd.read_csv(output_path)
            logger.info(f"✅ File contains {len(df)} injuries")
            
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save file: {e}")
            return False


def download_rotowire_injuries(output_dir: str = "data", week: int = None) -> str:
    """
    Download latest injuries from RotoWire by clicking export button
    
    Args:
        output_dir: Directory to save CSV
        week: NFL week (optional, for filename)
    
    Returns:
        Path to saved CSV file
    """
    logging.basicConfig(level=logging.INFO)
    
    scraper = RotoWireInjuryScraper()
    
    # Download the file (goes to temp location)
    downloaded_file = scraper.fetch_injuries()
    
    if not downloaded_file:
        logger.error("No injuries fetched. Check your internet connection or RotoWire website.")
        return None
    
    # Generate output filename
    if week:
        filename = f"wk{week}-injury-report.csv"
    else:
        filename = f"injury-report-{datetime.now().strftime('%Y%m%d')}.csv"
    
    output_path = Path(output_dir) / filename
    
    # Copy to final location
    if scraper.save_to_final_location(downloaded_file, str(output_path)):
        return str(output_path)
    else:
        return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch injuries from RotoWire")
    parser.add_argument('--output-dir', type=str, default='data', help='Output directory')
    parser.add_argument('--week', type=int, default=None, help='NFL week')
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("ROTOWIRE INJURY REPORT SCRAPER - EXPORT BUTTON METHOD")
    print("="*70)
    print()
    
    output_file = download_rotowire_injuries(
        output_dir=args.output_dir,
        week=args.week
    )
    
    if output_file:
        print(f"\n✅ Injuries saved to: {output_file}")
        
        # Show preview
        df = pd.read_csv(output_file)
        print(f"\nInjury Report Preview ({len(df)} total):")
        print("-"*70)
        print(df.head(10).to_string(index=False))
        if len(df) > 10:
            print(f"\n... and {len(df) - 10} more injuries")
    else:
        print("\n❌ Failed to fetch injuries")
