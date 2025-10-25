"""
Line Monitor - Quick Start
Run this to start monitoring betting lines
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.line_monitoring.line_monitor import LineMonitor

if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║        🚨  NFL LINE MOVEMENT MONITOR  🚨                   ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

Starting line movement monitoring...

This will:
- Check betting lines every hour
- Alert you when lines move 2+ points
- Track historical movements
- Detect sharp money indicators

Press Ctrl+C to stop.
""")
    
    monitor = LineMonitor()
    
    # Run continuously (checks every hour)
    monitor.run_continuously(interval_minutes=60)
