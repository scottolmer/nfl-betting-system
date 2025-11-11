"""
Line Monitor - Quick Start
Run this to start monitoring betting lines with confidence scoring
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.line_monitoring.monitor_main_enhanced import EnhancedLineMonitorCLI

if __name__ == '__main__':
    monitor = EnhancedLineMonitorCLI()
    
    # Run continuously (checks every hour)
    monitor.run_continuously_enhanced(interval_minutes=60)
