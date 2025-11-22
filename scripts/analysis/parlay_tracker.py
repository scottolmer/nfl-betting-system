"""
Parlay Tracking System - Track parlay generation, betting, and results
Enhanced with agent breakdown storage for calibration analysis
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Literal
import logging

logger = logging.getLogger(__name__)


class ParlayTracker:
    """
    Tracks all generated parlays, betting decisions, and results.
    Enables system learning and performance analysis.
    Now captures agent breakdown for calibration.
    """
    
    def __init__(self, tracking_file: str = "parlay_tracking.json"):
        """Initialize the tracker with a JSON file for persistence"""
        self.tracking_file = Path(tracking_file)
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load existing tracking data or create new structure"""
        if self.tracking_file.exists():
            try:
                with open(self.tracking_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading tracking data: {e}")
                return self._create_empty_structure()
        return self._create_empty_structure()
    
    def _create_empty_structure(self) -> Dict:
        """Create empty tracking structure"""
        return {
            "parlays": [],
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": None,
                "weeks_tracked": [],
                "total_parlays_generated": 0,
                "total_parlays_bet": 0,
                "total_results_entered": 0
            }
        }
    
    def _save_data(self):
        """Save tracking data to file"""
        self.data["metadata"]["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.tracking_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving tracking data: {e}")
    
    def _generate_content_hash(self, props: List[Dict]) -> str:
        """
        Generate unique hash based on prop combination.
        Same props in different order = same hash.
        """
        prop_strings = []
        for prop in sorted(props, key=lambda x: f"{x['player']}_{x['stat_type']}"):
            prop_str = f"{prop['player']}_{prop['stat_type']}_{prop['line']}_{prop['direction']}"
            prop_strings.append(prop_str)
        
        combined = "|".join(prop_strings)
        return hashlib.md5(combined.encode()).hexdigest()[:8]
    
    def _get_next_version(self, content_hash: str, week: int, year: int, parlay_type: str) -> int:
        """Get next version number for this prop combination"""
        existing = [
            p for p in self.data["parlays"]
            if p["content_hash"] == content_hash
            and p["week"] == week
            and p["year"] == year
            and p["parlay_type"] == parlay_type
        ]
        return len(existing) + 1
    
    def add_parlay(
        self,
        week: int,
        year: int,
        parlay_type: Literal["traditional", "enhanced", "custom"],
        props: List[Dict],
        raw_confidence: float,
        effective_confidence: float,
        correlations: List[Dict],
        payout_odds: int,
        kelly_bet_size: float,
        data_source: str = "unknown",
        agent_breakdown: Dict = None
    ) -> str:
        """
        Add a newly generated parlay to tracking.

        Args:
            week: NFL week number
            year: Year
            parlay_type: "traditional", "enhanced", or "custom"
            props: List of prop dicts with player, stat_type, line, direction, confidence, etc.
            raw_confidence: Original confidence before correlation adjustment
            effective_confidence: Confidence after correlation adjustment (same as raw for traditional)
            correlations: List of detected correlations (empty for traditional)
            payout_odds: Parlay payout odds (e.g., 450 for +450)
            kelly_bet_size: Recommended bet size from Kelly Criterion
            data_source: Where the data came from (e.g., "live_api", "csv_fallback")
            agent_breakdown: Dict of agent scores/weights for calibration analysis
                Example: {'DVOA': {'raw_score': 78, 'weight': 0.20}, 'Matchup': {...}, ...}
        
        Returns:
            parlay_id: Unique identifier for this parlay
        """
        content_hash = self._generate_content_hash(props)
        version = self._get_next_version(content_hash, week, year, parlay_type)

        # Generate prefix: TRAD, ENHA, or CUST
        prefix = parlay_type.upper()[:4]
        parlay_id = f"{prefix}_W{week}_{content_hash}_v{version}"
        
        parlay = {
            "parlay_id": parlay_id,
            "week": week,
            "year": year,
            "parlay_type": parlay_type,
            "content_hash": content_hash,
            "version": version,
            "generated_timestamp": datetime.now().isoformat(),
            "data_source": data_source,
            "props": props,
            "raw_confidence": round(raw_confidence, 1),
            "effective_confidence": round(effective_confidence, 1),
            "correlations": correlations,
            "payout_odds": payout_odds,
            "kelly_bet_size": round(kelly_bet_size, 2),
            
            # Agent calibration data - CRITICAL for learning which agents work best
            "agent_breakdown": agent_breakdown or {},
            
            # Betting tracking
            "bet_on": False,
            "actual_bet_amount": None,
            "bet_timestamp": None,
            
            # Results tracking
            "result": None,  # "won" | "lost" | "pending" | None
            "result_entered_timestamp": None,
            "actual_payout": None,
            "prop_results": []
        }
        
        self.data["parlays"].append(parlay)
        self.data["metadata"]["total_parlays_generated"] += 1
        
        # Track weeks
        if week not in self.data["metadata"]["weeks_tracked"]:
            self.data["metadata"]["weeks_tracked"].append(week)
            self.data["metadata"]["weeks_tracked"].sort()
        
        self._save_data()
        logger.info(f"Added parlay: {parlay_id}")
        return parlay_id
    
    def mark_bet(self, parlay_id: str, bet_amount: float) -> bool:
        """Mark a parlay as actually bet on"""
        for parlay in self.data["parlays"]:
            if parlay["parlay_id"] == parlay_id:
                parlay["bet_on"] = True
                parlay["actual_bet_amount"] = round(bet_amount, 2)
                parlay["bet_timestamp"] = datetime.now().isoformat()
                
                if parlay["result"] is None:
                    parlay["result"] = "pending"
                
                self.data["metadata"]["total_parlays_bet"] += 1
                self._save_data()
                logger.info(f"Marked {parlay_id} as bet: ${bet_amount}")
                return True
        
        logger.warning(f"Parlay not found: {parlay_id}")
        return False
    
    def unmark_bet(self, parlay_id: str) -> bool:
        """Remove bet marking from a parlay"""
        for parlay in self.data["parlays"]:
            if parlay["parlay_id"] == parlay_id:
                if parlay["bet_on"]:
                    self.data["metadata"]["total_parlays_bet"] -= 1
                
                parlay["bet_on"] = False
                parlay["actual_bet_amount"] = None
                parlay["bet_timestamp"] = None
                
                self._save_data()
                logger.info(f"Unmarked {parlay_id} as bet")
                return True
        
        logger.warning(f"Parlay not found: {parlay_id}")
        return False
    
    def mark_result(
        self,
        parlay_id: str,
        result: Literal["won", "lost", "pending"],
        prop_results: Optional[List[Dict]] = None,
        actual_payout: Optional[float] = None
    ) -> bool:
        """
        Mark the result of a parlay (won/lost/pending).
        
        Args:
            parlay_id: The parlay identifier
            result: "won", "lost", or "pending"
            prop_results: Optional list of individual prop results
            actual_payout: Optional actual payout received (for won bets)
        
        Returns:
            True if successful, False if parlay not found
        """
        for parlay in self.data["parlays"]:
            if parlay["parlay_id"] == parlay_id:
                old_result = parlay["result"]
                parlay["result"] = result
                parlay["result_entered_timestamp"] = datetime.now().isoformat()
                
                if prop_results:
                    parlay["prop_results"] = prop_results
                
                if actual_payout is not None:
                    parlay["actual_payout"] = round(actual_payout, 2)
                elif result == "won" and parlay["bet_on"] and parlay["actual_bet_amount"]:
                    # Calculate payout if not provided
                    bet_amount = parlay["actual_bet_amount"]
                    odds = parlay["payout_odds"]
                    parlay["actual_payout"] = round(bet_amount * (odds / 100 + 1), 2)
                elif result == "lost":
                    parlay["actual_payout"] = 0
                
                # Update metadata count
                if old_result not in ["won", "lost"] and result in ["won", "lost"]:
                    self.data["metadata"]["total_results_entered"] += 1
                
                self._save_data()
                logger.info(f"Marked {parlay_id} as {result}")
                return True
        
        logger.warning(f"Parlay not found: {parlay_id}")
        return False
    
    def get_parlays_by_week(self, week: int, year: int = 2024) -> List[Dict]:
        """Get all parlays for a specific week"""
        return [
            p for p in self.data["parlays"]
            if p["week"] == week and p["year"] == year
        ]
    
    def get_pending_parlays(self, week: Optional[int] = None) -> List[Dict]:
        """Get all parlays that need results entered"""
        pending = [
            p for p in self.data["parlays"]
            if p["result"] is None or p["result"] == "pending"
        ]
        
        if week is not None:
            pending = [p for p in pending if p["week"] == week]
        
        return pending
    
    def get_parlay_by_id(self, parlay_id: str) -> Optional[Dict]:
        """Get a specific parlay by ID"""
        for parlay in self.data["parlays"]:
            if parlay["parlay_id"] == parlay_id:
                return parlay
        return None
    
    def get_completed_parlays(self, week: Optional[int] = None, year: int = 2024) -> List[Dict]:
        """
        Get all completed parlays (won or lost) for calibration analysis.
        
        Args:
            week: Optional specific week to filter
            year: Year to filter
        
        Returns:
            List of completed parlay dicts with agent_breakdown data
        """
        completed = [
            p for p in self.data["parlays"]
            if p["result"] in ["won", "lost"] and p["year"] == year
        ]
        
        if week is not None:
            completed = [p for p in completed if p["week"] == week]
        
        return completed
    
    def get_statistics(
        self,
        weeks: Optional[List[int]] = None,
        parlay_type: Optional[str] = None,
        bet_only: bool = False
    ) -> Optional[Dict]:
        """
        Calculate performance statistics.
        
        Args:
            weeks: Optional list of weeks to include
            parlay_type: Optional filter by "traditional" or "enhanced"
            bet_only: If True, only include parlays that were actually bet on
        
        Returns:
            Dictionary of statistics or None if no data
        """
        parlays = self.data["parlays"]
        
        # Filter by weeks
        if weeks:
            parlays = [p for p in parlays if p["week"] in weeks]
        
        # Filter by type
        if parlay_type:
            parlays = [p for p in parlays if p["parlay_type"] == parlay_type]
        
        # Filter by bet status
        if bet_only:
            parlays = [p for p in parlays if p["bet_on"]]
        
        # Only completed parlays
        completed = [p for p in parlays if p["result"] in ["won", "lost"]]
        
        if not completed:
            return None
        
        won = [p for p in completed if p["result"] == "won"]
        lost = [p for p in completed if p["result"] == "lost"]
        
        # Calculate financial stats
        bet_parlays = [p for p in completed if p["bet_on"]]
        total_bet = sum(p.get("actual_bet_amount", 0) for p in bet_parlays)
        total_payout = sum(p.get("actual_payout", 0) for p in won if p["bet_on"])
        
        # Calculate confidence calibration
        avg_predicted = sum(p["effective_confidence"] for p in completed) / len(completed)
        actual_win_rate = (len(won) / len(completed)) * 100
        
        return {
            "total_parlays": len(completed),
            "won": len(won),
            "lost": len(lost),
            "win_rate": round(actual_win_rate, 1),
            "avg_predicted_confidence": round(avg_predicted, 1),
            "calibration_error": round(avg_predicted - actual_win_rate, 1),
            "bet_parlays": len(bet_parlays),
            "total_risked": round(total_bet, 2),
            "total_return": round(total_payout, 2),
            "net_profit": round(total_payout - total_bet, 2),
            "roi": round((total_payout - total_bet) / total_bet * 100, 1) if total_bet > 0 else 0
        }
    
    def get_agent_performance(self, agent_name: str, min_score: int = 80) -> Optional[Dict]:
        """
        Analyze performance when a specific agent scores high.
        
        Args:
            agent_name: Name of the agent (e.g., "weather", "injury")
            min_score: Minimum agent score to consider
        
        Returns:
            Performance stats for props where this agent scored highly
        """
        completed = [p for p in self.data["parlays"] if p["result"] in ["won", "lost"]]
        
        if not completed:
            return None
        
        # Find props where this agent scored >= min_score
        relevant_parlays = []
        for parlay in completed:
            for prop in parlay["props"]:
                agent_scores = prop.get("agent_scores", {})
                if agent_scores.get(agent_name, 0) >= min_score:
                    relevant_parlays.append(parlay)
                    break  # Count parlay once
        
        if not relevant_parlays:
            return None
        
        won = [p for p in relevant_parlays if p["result"] == "won"]
        win_rate = (len(won) / len(relevant_parlays)) * 100
        
        return {
            "agent": agent_name,
            "min_score": min_score,
            "total_parlays": len(relevant_parlays),
            "won": len(won),
            "lost": len(relevant_parlays) - len(won),
            "win_rate": round(win_rate, 1),
            "prediction": f"Agent predicts high confidence ({min_score}+)",
            "actual": f"Actual win rate: {win_rate:.1f}%",
            "accurate": abs(win_rate - min_score) < 10
        }
    
    def export_to_csv(self, output_file: str):
        """Export all parlay data to CSV for external analysis"""
        import csv
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'parlay_id', 'week', 'year', 'parlay_type', 'version',
                'raw_confidence', 'effective_confidence', 'kelly_bet_size',
                'bet_on', 'actual_bet_amount', 'result', 'actual_payout',
                'num_props', 'payout_odds', 'data_source'
            ])
            writer.writeheader()
            
            for parlay in self.data["parlays"]:
                writer.writerow({
                    'parlay_id': parlay['parlay_id'],
                    'week': parlay['week'],
                    'year': parlay['year'],
                    'parlay_type': parlay['parlay_type'],
                    'version': parlay['version'],
                    'raw_confidence': parlay['raw_confidence'],
                    'effective_confidence': parlay['effective_confidence'],
                    'kelly_bet_size': parlay['kelly_bet_size'],
                    'bet_on': parlay['bet_on'],
                    'actual_bet_amount': parlay.get('actual_bet_amount'),
                    'result': parlay.get('result'),
                    'actual_payout': parlay.get('actual_payout'),
                    'num_props': len(parlay['props']),
                    'payout_odds': parlay['payout_odds'],
                    'data_source': parlay.get('data_source', 'unknown')
                })
        
        logger.info(f"Exported {len(self.data['parlays'])} parlays to {output_file}")
