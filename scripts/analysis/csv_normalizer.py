"""
CSV Normalizer - Claude API integration for data cleanup and validation
"""

import os
from anthropic import Anthropic
from typing import Dict, List, Any
import json
import logging

logger = logging.getLogger(__name__)


class CSVNormalizer:
    """Cleans and normalizes CSV data using Claude API"""
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = "claude-sonnet-4-20250514"
    
    def normalize_player_names(self, player_list: List[str]) -> Dict[str, str]:
        """
        Normalize player names across all data files
        
        Returns mapping: {original_name: normalized_name}
        """
        if not player_list or len(player_list) == 0:
            return {}
        
        prompt = f"""Normalize these NFL player names to standard format.

NAMES:
{json.dumps(player_list[:50])}

Return JSON mapping of original -> normalized:
{{
  "mapping": {{
    "original_name": "Normalized Name",
    ...
  }}
}}

Rules:
- Full name format: "First Last" (e.g., "Jordan Love", not "J.Love" or "love, jordan")
- Consistent capitalization
- Remove middle initials unless needed to distinguish duplicates
- Fix common misspellings
- Consolidate variations (e.g., "Jalen" vs "Jalen")

RESPOND ONLY WITH JSON."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(response_text)
            logger.info(f"Normalized {len(result.get('mapping', {}))} player names")
            return result.get('mapping', {})
            
        except Exception as e:
            logger.error(f"Player name normalization failed: {e}")
            return {}
    
    def validate_stat_types(self, stat_list: List[str]) -> Dict[str, Any]:
        """
        Validate and standardize stat type names
        
        Returns: {
            'standardized': {original: standard},
            'issues': [list of detected issues],
            'mappings': {category: [valid_stats]}
        }
        """
        prompt = f"""Validate and standardize NFL stat types.

STATS:
{json.dumps(stat_list[:30])}

Return JSON:
{{
  "standardized": {{"Rec Yds": "Receiving Yards", ...}},
  "issues": ["Stat1 - reason", ...],
  "categories": {{
    "passing": ["Pass Yds", "Pass TDs", ...],
    "rushing": ["Rush Yds", "Rush Att", ...],
    "receiving": ["Receptions", "Rec Yds", "Rec TDs"]
  }}
}}

Standard names:
- Passing: Pass Yds, Pass TDs, Pass Comp, Pass Att, Pass Int
- Rushing: Rush Yds, Rush Att, Rush TDs
- Receiving: Receptions, Rec Yds, Rec TDs, Rec Targets
- Defense: Sacks, Tackles, Interceptions, Pass Deflections

RESPOND ONLY WITH JSON."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(response_text)
            logger.info(f"Validated stats. Issues found: {len(result.get('issues', []))}")
            return result
            
        except Exception as e:
            logger.error(f"Stat validation failed: {e}")
            return {'standardized': {}, 'issues': [str(e)], 'categories': {}}
    
    def detect_data_outliers(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect outliers and anomalies in betting/DVOA data
        
        Returns: {
            'outliers': [{player, stat, value, reason}, ...],
            'suspicious_patterns': [patterns],
            'recommendations': [recommendations]
        }
        """
        if not data or len(data) == 0:
            return {'outliers': [], 'suspicious_patterns': [], 'recommendations': []}
        
        # Prepare sample data
        sample = json.dumps(data[:20])
        
        prompt = f"""Analyze this betting/stat data for outliers and errors.

SAMPLE DATA:
{sample}

Return JSON:
{{
  "outliers": [
    {{"player": "name", "stat": "Pass Yds", "value": 500, "issue": "reason", "severity": "high/medium/low"}},
    ...
  ],
  "suspicious_patterns": [
    "Pattern1 - explanation",
    ...
  ],
  "recommendations": [
    "Action1",
    ...
  ]
}}

Look for:
- Values outside typical ranges (QB >600 pass yds, RB >300 rush yds)
- Missing data or nulls
- Inconsistent formatting
- Duplicate players
- Negative values where impossible
- Zero values indicating missing data

RESPOND ONLY WITH JSON."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(response_text)
            logger.warning(f"Data analysis found {len(result.get('outliers', []))} outliers")
            return result
            
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            return {'outliers': [], 'suspicious_patterns': [], 'recommendations': []}
    
    def infer_missing_values(self, player_name: str, stat_type: str, 
                            team: str, position: str, context: Dict) -> Dict[str, float]:
        """
        Infer reasonable values for missing usage/stat data
        
        Returns: {
            'snap_share_pct': value,
            'target_share_pct': value,
            'pass_attempts': value,
            'confidence': 0-100 (how confident in inference)
        }
        """
        prompt = f"""Generate reasonable estimates for missing NFL player stats.

PLAYER: {player_name}
POSITION: {position}
TEAM: {team}
STAT TYPE: {stat_type}

Return JSON:
{{
  "snap_share_pct": <estimated snap % for position>,
  "target_share_pct": <if WR/TE>,
  "pass_attempts": <if QB>,
  "rush_attempts": <if RB>,
  "confidence": <50-95, how confident in estimates>,
  "reasoning": "<why these estimates make sense>"
}}

Base estimates on:
- {position} typical snap shares: QB 100%, WR1 90%, WR2 75%, WR3 50%, RB 60%, TE 70%
- Team offensive pace and philosophy
- Player role context

RESPOND ONLY WITH JSON."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(response_text)
            result['confidence'] = max(50, min(95, result.get('confidence', 70)))
            
            logger.info(f"Inferred stats for {player_name}: {result.get('confidence')}% confidence")
            return result
            
        except Exception as e:
            logger.error(f"Value inference failed: {e}")
            return {'snap_share_pct': 60, 'confidence': 50}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    normalizer = CSVNormalizer()
    
    # Test player name normalization
    players = ["jordan love", "J.Love", "Love, Jordan", "Tyreek Hill", "T. Hill"]
    mappings = normalizer.normalize_player_names(players)
    print("Player mappings:", mappings)
    
    # Test stat validation
    stats = ["Pass Yds", "PassYards", "pass yards", "Rush Yards", "rec_yds"]
    validation = normalizer.validate_stat_types(stats)
    print("\nStat validation:", validation)
