"""
Claude Preprocessing Engine - Normalizes malformed NFL betting data
Handles: injury reports, betting odds, weekly stats with inconsistent headers/formats
"""

import json
import logging
import os
from typing import Dict, List, Any
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class ClaudePreprocessor:
    """Use Claude API to normalize messy NFL data"""
    
    def __init__(self):
        self.client = Anthropic()
        self.model = "claude-sonnet-4-20250514"
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def preprocess_injury_data(self, raw_injury_text: str) -> Dict[str, List[Dict]]:
        """Normalize injury report from any format to standard schema."""
        if not raw_injury_text or len(raw_injury_text.strip()) == 0:
            self.logger.warning("Empty injury data provided")
            return {'injuries': [], 'metadata': {'error': 'Empty input'}}
        
        prompt = f"""Parse this injury report data and normalize to JSON.

REQUIREMENTS:
1. Extract: player name, team (3-letter abbr), position, injury, status, return date
2. Normalize player names to lowercase, remove extra spaces/periods
3. Team abbreviations to 3-letter uppercase (JAX not JAX)
4. Status must be: 'out', 'doubtful', 'questionable', 'active', 'ir', 'pup-r', 'pup-nr'
5. Return ONLY valid JSON

INJURY DATA:
{raw_injury_text}

Return:
{{
  "injuries": [
    {{"player_name": "name", "team": "ABB", "position": "QB", "injury": "type", "status": "active", "est_return": "TBD"}}
  ],
  "metadata": {{"total_players": 0}}
}}"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = response.content[0].text
            result = json.loads(response_text)
            self.logger.info(f"✓ Preprocessed {len(result.get('injuries', []))} injury records")
            return result
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parse error: {e}")
            return {'injuries': [], 'metadata': {'error': 'JSON parse failed'}}
        except Exception as e:
            self.logger.error(f"Injury preprocessing failed: {e}")
            return {'injuries': [], 'metadata': {'error': str(e)}}
    
    def preprocess_odds_data(self, raw_odds_csv: str) -> Dict[str, List[Dict]]:
        """Normalize betting odds to standard schema."""
        if not raw_odds_csv or len(raw_odds_csv.strip()) == 0:
            self.logger.warning("Empty odds data provided")
            return {'props': [], 'metadata': {'error': 'Empty input'}}
        
        prompt = f"""Parse betting odds CSV and normalize to JSON.

REQUIREMENTS:
1. Extract player props only (ignore moneyline, spreads, totals)
2. Player prop markets: player_pass_yds, player_pass_tds, player_receptions, player_reception_yds, player_rush_yds
3. Normalize player names to lowercase with full first/last name
4. Convert markets: player_pass_yds → "Pass Yds", player_reception_yds → "Rec Yds"
5. Team abbreviations: 3-letter uppercase
6. Skip rows with missing data
7. Return ONLY valid JSON

ODDS DATA:
{raw_odds_csv}

Return:
{{
  "props": [
    {{"player_name": "name", "team": "ABB", "opponent": "ABB", "position": "QB", "stat_type": "Pass Yds", "line": 250.5, "is_home": true, "game_total": 44.5, "spread": -3.5}}
  ],
  "metadata": {{"total_props": 0, "games": 0}}
}}"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = response.content[0].text
            result = json.loads(response_text)
            self.logger.info(f"✓ Preprocessed {len(result.get('props', []))} prop records")
            return result
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parse error: {e}")
            return {'props': [], 'metadata': {'error': 'JSON parse failed'}}
        except Exception as e:
            self.logger.error(f"Odds preprocessing failed: {e}")
            return {'props': [], 'metadata': {'error': str(e)}}


def preprocess_injury_batch(raw_text: str) -> Dict:
    """One-off injury preprocessing"""
    preprocessor = ClaudePreprocessor()
    return preprocessor.preprocess_injury_data(raw_text)


def preprocess_odds_batch(raw_csv: str) -> Dict:
    """One-off odds preprocessing"""
    preprocessor = ClaudePreprocessor()
    return preprocessor.preprocess_odds_data(raw_csv)


if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    
    preprocessor = ClaudePreprocessor()
    
    sample_injury = """Player,Team,Pos,Injury,Status,Est. Return
Jordan Love,GB,QB,Shoulder,Active,N/A
Travis Kelce,KC,TE,Illness,Active,N/A"""
    
    print("\n=== TESTING INJURY PREPROCESSING ===")
    result = preprocessor.preprocess_injury_data(sample_injury)
    print(json.dumps(result, indent=2))
