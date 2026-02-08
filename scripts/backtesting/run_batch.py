
import subprocess
import sys
import logging
import argparse
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def run_batch(start_week, end_week, skip_backtest=False, skip_grading=False,
              run_calibration=False, apply_weights=False):
    """
    Run backtesting pipeline for a range of weeks.

    Args:
        start_week: First week to process
        end_week: Last week to process
        skip_backtest: Skip prediction generation (use existing predictions)
        skip_grading: Skip grading step (use existing graded results)
        run_calibration: Run calibration analysis after all weeks
        apply_weights: Apply weight adjustments (requires run_calibration)
    """
    project_root = Path(__file__).parent.parent.parent
    processed_weeks = []

    for week in range(start_week, end_week + 1):
        logger.info(f"\n{'='*50}")
        logger.info(f"🔄 PROCESSING WEEK {week}")
        logger.info(f"{'='*50}")

        # 1. Run Backtest Engine (generate predictions)
        if not skip_backtest:
            logger.info(f"▶️ Running Backtest Engine for Week {week}...")
            try:
                cmd = [sys.executable, "scripts/backtesting/backtest_engine.py", "--week", str(week)]
                subprocess.run(cmd, check=True, cwd=project_root)
            except subprocess.CalledProcessError:
                logger.error(f"❌ Backtest failed for Week {week}. Skipping grading.")
                continue
        else:
            logger.info(f"⏭️ Skipping backtest (using existing predictions)")

        # 2. Run Grader
        if not skip_grading:
            logger.info(f"▶️ Grading Results for Week {week}...")
            try:
                cmd = [sys.executable, "scripts/backtesting/grade_results.py", "--week", str(week)]
                subprocess.run(cmd, check=True, cwd=project_root)
                processed_weeks.append(week)
            except subprocess.CalledProcessError:
                logger.error(f"❌ Grading failed for Week {week}.")
                continue
        else:
            logger.info(f"⏭️ Skipping grading (using existing graded results)")
            processed_weeks.append(week)

    logger.info("\n✅ Batch processing complete.")

    # 3. Run Calibration Analysis (optional)
    if run_calibration and processed_weeks:
        logger.info(f"\n{'='*50}")
        logger.info(f"🧠 RUNNING CALIBRATION ANALYSIS")
        logger.info(f"{'='*50}")

        weeks_arg = f"{start_week}-{end_week}"
        cmd = [sys.executable, "scripts/backtesting/calibration_analyzer.py",
               "--weeks", weeks_arg]

        if apply_weights:
            cmd.append("--apply")
            logger.info("⚠️ Weight adjustments will be APPLIED")
        else:
            logger.info("📋 Running in dry-run mode (no changes)")

        try:
            subprocess.run(cmd, check=True, cwd=project_root)
        except subprocess.CalledProcessError:
            logger.error("❌ Calibration analysis failed.")

    return processed_weeks

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run backtesting batch processing')
    parser.add_argument('--start', type=int, default=11, help='Start week (default: 11)')
    parser.add_argument('--end', type=int, default=16, help='End week (default: 16)')
    parser.add_argument('--skip-backtest', action='store_true',
                        help='Skip prediction generation, use existing')
    parser.add_argument('--skip-grading', action='store_true',
                        help='Skip grading, use existing graded results')
    parser.add_argument('--calibrate', action='store_true',
                        help='Run calibration analysis after processing')
    parser.add_argument('--apply-weights', action='store_true',
                        help='Apply weight adjustments (use with --calibrate)')

    args = parser.parse_args()

    run_batch(
        start_week=args.start,
        end_week=args.end,
        skip_backtest=args.skip_backtest,
        skip_grading=args.skip_grading,
        run_calibration=args.calibrate,
        apply_weights=args.apply_weights
    )
