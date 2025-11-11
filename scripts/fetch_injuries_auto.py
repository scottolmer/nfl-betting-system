#!/usr/bin/env python
"""Auto-fetch fresh injury data from RotoWire before analysis"""

import sys
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

def fetch_and_prepare_injuries(week: int, data_dir: Path = None):
    """Fetch fresh injuries from RotoWire, save as wk{week}-injury-report.csv"""
    
    if data_dir is None:
        data_dir = project_root / "data"
    
    data_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        from scripts.fetch_rotowire_injuries import RotoWireInjuryScraper
    except ImportError:
        logger.error("Could not import RotoWire scraper. Make sure Selenium is installed: pip install selenium webdriver-manager")
        return False
    
    scraper = RotoWireInjuryScraper()
    target_file = data_dir / f"wk{week}-injury-report.csv"
    
    logger.info(f"🔄 Fetching fresh injury data from RotoWire...")
    
    try:
        downloaded_path = scraper.fetch_injuries(download_dir=str(data_dir))
        
        if downloaded_path and Path(downloaded_path).exists():
            # RotoWire scraper returns path - move/rename to our standard format
            source = Path(downloaded_path)
            
            # Read and save with standard name
            with open(source, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✅ Saved fresh injury data to {target_file.name}")
            logger.info(f"📊 Injury data dated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return True
        else:
            logger.warning("Failed to download injury file from RotoWire")
            return False
            
    except Exception as e:
        logger.error(f"Error fetching injuries: {e}")
        logger.warning("Falling back to existing injury data if available")
        return False

if __name__ == "__main__":
    import os
    week = int(os.getenv('NFL_WEEK', 8))
    data_dir = Path(project_root) / "data"
    
    print(f"\n{'='*60}")
    print(f"🏥 INJURY DATA FETCHER - Week {week}")
    print(f"{'='*60}\n")
    
    success = fetch_and_prepare_injuries(week, data_dir)
    
    if success:
        print(f"\n✅ Ready for analysis with fresh injury data")
    else:
        print(f"\n⚠️  Using cached injury data (if available)")
    
    print(f"{'='*60}\n")
