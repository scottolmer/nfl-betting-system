"""
Post-Game Analysis Workflow
Completes validation forms, generates calibration reports, and tracks system performance
"""

import sys
from pathlib import Path
import logging
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.calibration_dashboard import generate_calibration_report

logger = logging.getLogger(__name__)


def find_latest_validation_form(week: int, data_dir: str = "data") -> Path:
    """
    Find the most recent validation form for a given week
    
    Looks in: data/betting_history/week_X/LATEST.txt
    """
    latest_file = Path(data_dir) / "betting_history" / f"week_{week}" / "LATEST.txt"
    
    if not latest_file.exists():
        logger.error(f"LATEST pointer not found: {latest_file}")
        return None
    
    # Read the LATEST.txt file to get the timestamp folder
    try:
        with open(latest_file, 'r') as f:
            for line in f:
                if line.startswith("Validation Form:"):
                    form_path = line.split(": ", 1)[1].strip()
                    return Path(form_path)
    except Exception as e:
        logger.error(f"Error reading LATEST pointer: {e}")
    
    return None


def generate_calibration_from_validation(week: int, validation_form_path: Path = None, 
                                        data_dir: str = "data") -> str:
    """
    Generate calibration report from a validation form
    
    Args:
        week: NFL week
        validation_form_path: Path to completed validation form (auto-finds if not provided)
        data_dir: Base data directory
    
    Returns:
        Path to generated calibration report
    """
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*100)
    print("📊 POST-GAME ANALYSIS - GENERATING CALIBRATION REPORT")
    print("="*100)
    print(f"Week: {week}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100)
    print()
    
    # Find validation form if not provided
    if validation_form_path is None:
        print("🔍 Finding latest validation form...")
        validation_form_path = find_latest_validation_form(week, data_dir)
        
        if validation_form_path is None:
            print("❌ Could not find validation form")
            print(f"   Expected path: {Path(data_dir) / 'betting_history' / f'week_{week}' / '*/validation_form.txt'}")
            return None
    
    validation_form_path = Path(validation_form_path)
    
    if not validation_form_path.exists():
        print(f"❌ Validation form not found: {validation_form_path}")
        return None
    
    print(f"✅ Found validation form: {validation_form_path}")
    print()
    
    # Generate calibration report
    print("🧮 Analyzing results and generating calibration report...")
    
    try:
        report_text = generate_calibration_report(week, validation_form_path, data_dir)
    except Exception as e:
        logger.error(f"Error generating calibration report: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None
    
    # Save report
    report_path = validation_form_path.parent / f"calibration_report.txt"
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"✅ Saved calibration report to: {report_path}")
        print()
        
    except Exception as e:
        logger.error(f"Error saving calibration report: {e}")
        return None
    
    # Print key sections of report to console
    print("="*100)
    print("REPORT PREVIEW")
    print("="*100)
    
    # Extract first few sections
    lines = report_text.split('\n')
    section_count = 0
    for i, line in enumerate(lines):
        if '=' in line and section_count < 3:  # Show first 3 sections
            section_count += 1
        
        if section_count <= 3:
            print(line)
        else:
            break
    
    print("\n[Full report saved to file - see above path]")
    print()
    
    # Final summary
    print("="*100)
    print("POST-GAME ANALYSIS COMPLETE!")
    print("="*100)
    print()
    print(f"Files generated:")
    print(f"  - Calibration Report: {report_path}")
    print()
    print("Next steps:")
    print("  1. Review the full calibration report for insights")
    print("  2. Identify underperforming agents/positions")
    print("  3. Adjust agent weights for next week")
    print("  4. Re-run analysis with updated weights")
    print()
    
    return str(report_path)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Post-Game Analysis and Calibration")
    parser.add_argument('--week', type=int, required=True, help='NFL week to analyze')
    parser.add_argument('--form', type=str, default=None, help='Path to validation form (auto-finds if not provided)')
    parser.add_argument('--data-dir', type=str, default='data', help='Data directory')
    
    args = parser.parse_args()
    
    report_path = generate_calibration_from_validation(
        week=args.week,
        validation_form_path=args.form,
        data_dir=args.data_dir
    )
    
    if report_path:
        print(f"✅ Analysis complete: {report_path}")
    else:
        print("❌ Analysis failed")
