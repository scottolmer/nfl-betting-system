"""
Main entry point for weekly analysis
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.core.config import Config

def main():
    """Main workflow"""
    Config.validate()
    print(f"NFL Betting System - Week {Config.NFL_WEEK}")
    print("Ready to analyze!")
    # TODO: Implement full workflow

if __name__ == "__main__":
    main()
