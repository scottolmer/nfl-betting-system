"""Results logger - saves parlay recommendations to timestamped folders"""
import json
import os
from pathlib import Path
from datetime import datetime


class ResultsLogger:
    """Logs parlay results to organized folders"""
    
    def __init__(self, base_dir="results"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
    
    def get_session_dir(self, week):
        """Create timestamped session directory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = self.base_dir / f"week{week}" / timestamp
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir
    
    def save_standard_parlays(self, week, parlays_dict, analysis_summary):
        """Save standard parlays"""
        session_dir = self.get_session_dir(week)
        
        output = {
            "timestamp": datetime.now().isoformat(),
            "week": week,
            "type": "standard",
            "summary": analysis_summary,
            "parlays": self._format_parlays(parlays_dict)
        }
        
        filepath = session_dir / "standard_parlays.json"
        with open(filepath, "w") as f:
            json.dump(output, f, indent=2)
        
        return filepath
    
    def save_optimized_parlays(self, week, parlays_list, quality_threshold=None):
        """Save optimized parlays"""
        session_dir = self.get_session_dir(week)
        
        output = {
            "timestamp": datetime.now().isoformat(),
            "week": week,
            "type": "optimized",
            "quality_threshold": quality_threshold,
            "parlays": []
        }
        
        for parlay_data in parlays_list:
            parlay = parlay_data['parlay']
            output["parlays"].append({
                "type": parlay.parlay_type,
                "recommendation": parlay_data['recommendation'],
                "adjusted_confidence": parlay_data['adjusted_confidence'],
                "adjustment": parlay_data['adjustment'],
                "units": parlay.recommended_units,
                "legs": [
                    {
                        "player": leg.prop.player_name,
                        "team": leg.prop.team,
                        "stat": leg.prop.stat_type,
                        "line": leg.prop.line,
                        "confidence": leg.final_confidence
                    }
                    for leg in parlay.legs
                ]
            })
        
        filepath = session_dir / "optimized_parlays.json"
        with open(filepath, "w") as f:
            json.dump(output, f, indent=2)
        
        return filepath
    
    def _format_parlays(self, parlays_dict):
        """Format parlay dict for JSON"""
        result = {}
        for ptype in ['2-leg', '3-leg', '4-leg', '5-leg']:
            result[ptype] = []
            for parlay in parlays_dict.get(ptype, []):
                result[ptype].append({
                    "confidence": parlay.combined_confidence,
                    "risk_level": parlay.risk_level,
                    "units": parlay.recommended_units,
                    "legs": [
                        {
                            "player": leg.prop.player_name,
                            "team": leg.prop.team,
                            "stat": leg.prop.stat_type,
                            "line": leg.prop.line,
                            "confidence": leg.final_confidence
                        }
                        for leg in parlay.legs
                    ]
                })
        return result
    
    def save_session_summary(self, week, standard_path=None, optimized_path=None):
        """Create session summary file"""
        session_dir = self.get_session_dir(week)
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "week": week,
            "files": {}
        }
        
        if standard_path:
            summary["files"]["standard"] = str(standard_path)
        if optimized_path:
            summary["files"]["optimized"] = str(optimized_path)
        
        filepath = session_dir / "summary.json"
        with open(filepath, "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 Saved to: {session_dir}")
        return filepath
