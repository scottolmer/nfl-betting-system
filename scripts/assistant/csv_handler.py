"""
CSV Handler for Betting Assistant
Processes file uploads and integrates with NFLDataLoader
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader

logger = logging.getLogger(__name__)


class CSVHandler:
    """Handles CSV file uploads and data validation for conversational interface"""

    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or str(project_root / "data")
        self.loader = NFLDataLoader(data_dir=self.data_dir)
        self.last_context = None
        self.last_week = None

    def process_files(self, week: int, file_paths: List[str] = None) -> Tuple[bool, str, Dict]:
        """
        Process CSV files for a given week

        Args:
            week: NFL week number
            file_paths: Optional list of file paths to process (for upload detection)

        Returns:
            (success, message, context) tuple
        """
        logger.info(f"Processing data for Week {week}")

        try:
            # Load all data using existing NFLDataLoader
            context = self.loader.load_all_data(week=week)
            self.last_context = context
            self.last_week = week

            # Get validation status
            validation = self.loader.get_validation_status(context)

            # Build user-friendly message
            message = self._build_status_message(validation)

            return validation['success'], message, context

        except Exception as e:
            error_msg = f"Error loading data for Week {week}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg, {}

    def _build_status_message(self, validation: Dict) -> str:
        """Build conversational status message"""
        lines = []
        week = validation['week']

        if validation['success']:
            lines.append(f"Loaded Week {week} data successfully:")
            lines.append(f"  [CHECK] {validation['props_count']} betting props")
            lines.append(f"  [CHECK] {validation['dvoa_teams']} team DVOA rankings")

            if validation['injuries_loaded']:
                lines.append(f"  [CHECK] Injury reports loaded")

            lines.append(f"  [CHECK] Source: {validation['betting_lines_source']}")

            if validation['warnings']:
                lines.append("\nWarnings:")
                for warning in validation['warnings']:
                    lines.append(f"  [WARNING] {warning}")

            lines.append("\nReady for analysis. What would you like to know?")
        else:
            lines.append(f"Failed to load Week {week} data:")
            for error in validation['errors']:
                lines.append(f"  [ERROR] {error}")

            if validation['warnings']:
                lines.append("\nAdditional warnings:")
                for warning in validation['warnings']:
                    lines.append(f"  [WARNING] {warning}")

        return "\n".join(lines)

    def get_files_loaded_summary(self, context: Dict = None) -> str:
        """Get summary of loaded files for display"""
        ctx = context or self.last_context
        if not ctx:
            return "No data loaded yet"

        files = ctx.get('loaded_files', [])
        if not files:
            return "No files loaded"

        return "\n".join([f"  - {f}" for f in files])

    def validate_data_quality(self, context: Dict = None) -> Tuple[bool, List[str]]:
        """
        Validate data quality for analysis

        Returns:
            (is_valid, issues) tuple
        """
        ctx = context or self.last_context
        if not ctx:
            return False, ["No data loaded"]

        issues = []

        # Check props exist
        props = ctx.get('props', [])
        if not props:
            issues.append("No props found in betting lines")

        # Check DVOA data
        if not ctx.get('dvoa_offensive'):
            issues.append("Missing DVOA offensive data")
        if not ctx.get('dvoa_defensive'):
            issues.append("Missing DVOA defensive data")

        # Check for props with missing data
        if props:
            missing_team_count = sum(1 for p in props if not p.get('team'))
            missing_opponent_count = sum(1 for p in props if not p.get('opponent'))

            if missing_team_count > 0:
                issues.append(f"{missing_team_count} props missing team assignment")
            if missing_opponent_count > 0:
                issues.append(f"{missing_opponent_count} props missing opponent")

        return len(issues) == 0, issues

    def detect_uploaded_files(self, file_paths: List[str]) -> Dict[str, str]:
        """
        Detect file types from uploaded paths

        Returns:
            Dict mapping file_type -> file_path
        """
        file_map = {}

        for path in file_paths:
            path_lower = path.lower()
            filename = Path(path).name.lower()

            # Detect file type
            if 'betting_lines' in filename or 'draftkings' in filename:
                file_map['betting_lines'] = path
            elif 'offensive_dvoa' in filename or 'dvoa_off' in filename:
                file_map['dvoa_offensive'] = path
            elif 'defensive_dvoa' in filename or 'dvoa_def' in filename:
                file_map['dvoa_defensive'] = path
            elif 'def_v_wr' in filename or 'def_vs_wr' in filename:
                file_map['def_vs_receiver'] = path
            elif 'injury' in filename:
                file_map['injuries'] = path
            elif 'roster' in filename:
                file_map['roster'] = path

        return file_map

    def get_week_from_context(self) -> Optional[int]:
        """Get the current week from loaded context"""
        if self.last_context:
            return self.last_context.get('week')
        return None


if __name__ == "__main__":
    # Test CSV handler
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--week', type=int, default=15)
    args = parser.parse_args()

    handler = CSVHandler()
    success, message, context = handler.process_files(week=args.week)

    print("\n" + "="*70)
    print(message)
    print("="*70)

    if success:
        is_valid, issues = handler.validate_data_quality(context)
        print(f"\nData Quality: {'VALID' if is_valid else 'ISSUES FOUND'}")
        if issues:
            print("Issues:")
            for issue in issues:
                print(f"  - {issue}")
