"""
Injury Agent - Analyzes player injury status impact
UPDATED to parse CSV format with headers: Player,Team,Pos,Injury,Status,Est. Return
Includes explicit logger initialization and BOM handling.
"""

from typing import Dict, List, Tuple
from .base_agent import BaseAgent
import csv
import io
import re
import logging # Import logging

# Helper function to normalize player names
def normalize_player_name(name: str) -> str:
    if not name: return name
    name = str(name).strip().replace('.', '')
    name = re.sub(r'\s+', ' ', name)
    return name.lower()

class InjuryAgent(BaseAgent):
    """Analyzes player injury status from a CSV report"""

    def __init__(self):
        super().__init__(weight=1.5)
        # Ensure logger exists, unconditionally initialize if needed
        if not hasattr(self, 'logger') or self.logger is None:
             self.logger = logging.getLogger(self.__class__.__name__)
        self.injury_data = {} # Cache for parsed injury data


    def _parse_injury_report(self, injury_report_text: str):
        """Parses the CSV injury report text into a dictionary."""
        self.injury_data = {}
        if not injury_report_text:
            self.logger.warning("Injury report text empty, skipping parse.")
            return

        try:
            csvfile = io.StringIO(injury_report_text)
            reader = csv.DictReader(csvfile)
            expected_headers = ['Player', 'Team', 'Pos', 'Injury', 'Status', 'Est. Return']
            actual_headers = reader.fieldnames
            if not actual_headers:
                 self.logger.error("Injury report CSV empty or no header row.")
                 return

            # --- *** BOM HANDLING FIX *** ---
            # Check the FIRST header specifically, removing potential BOM before comparison
            clean_first_header = actual_headers[0].lstrip('\ufeff')
            headers_match = (
                clean_first_header == expected_headers[0] and
                all(exp_h in actual_headers for exp_h in expected_headers[1:])
            )
            # --- *** END BOM HANDLING FIX *** ---

            if not headers_match:
                # Log the cleaned headers for clarity
                logged_headers = [clean_first_header] + actual_headers[1:]
                self.logger.error(f"Injury report CSV headers mismatch!")
                self.logger.error(f"Expected something like: {expected_headers}")
                self.logger.error(f"Got: {logged_headers}")
                return

            player_count = 0
            # Define the key for the player name column, accounting for BOM
            player_key = actual_headers[0] # Use the actual first header name found

            for row in reader:
                player_name_raw = row.get(player_key) # Use the potentially BOM'd key
                status_raw = row.get('Status', '')
                status = status_raw.strip().lower() if status_raw else ''
                if player_name_raw and status:
                    normalized_name = normalize_player_name(player_name_raw)
                    self.injury_data[normalized_name] = status
                    player_count += 1
            self.logger.info(f"Parsed injury data for {player_count} players.")

        except csv.Error as e: self.logger.error(f"CSV Error parsing injury report: {e}")
        except Exception as e: self.logger.error(f"Error parsing injury report: {e}", exc_info=False)


    def analyze(self, prop, context: Dict) -> Tuple[float, str, List[str]]:
        """Analyzes injury status for the prop player"""
        if not hasattr(self, 'logger'): return (50, "AVOID", ["⚠️ Agent Error"]) # Safety check

        rationale = []; score = 50
        injury_text = context.get('injuries')

        if not self.injury_data and injury_text:
            self._parse_injury_report(injury_text)

        player_name_norm = normalize_player_name(prop.player_name)
        status = self.injury_data.get(player_name_norm)

        if status:
            self.logger.debug(f"Injury Status for {player_name_norm}: {status}")
            if status in ['out', 'ir', 'pup-r', 'pup-nr', 'nfi-r', 'nfi-nr', 'reserve-ret']:
                score = 0; rationale.append(f"🚨 PLAYER OUT ({status.upper()})")
            elif status == 'doubtful':
                score = 20; rationale.append(f"⚠️ PLAYER DOUBTFUL")
            elif status == 'questionable':
                score = 40; rationale.append(f"🟡 PLAYER QUESTIONABLE")
            else: score = 50 # Healthy/Active
        else: score = 50 # Assume healthy if not listed

        direction = "AVOID" if score < 30 else ("UNDER" if score < 50 else "OVER")
        final_rationale = rationale if score != 50 else []

        return (score, direction, final_rationale)