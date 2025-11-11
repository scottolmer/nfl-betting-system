"""
Calibration Dashboard - Analyzes betting system performance
Reads validation forms and generates calibration reports
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List
import logging
import re
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class LegResult:
    player_name: str
    position: str
    team: str
    opponent: str
    stat_type: str
    line: float
    confidence: int
    actual_hit: bool = False


@dataclass
class ParlayResult:
    parlay_id: str
    num_legs: int
    legs: List[LegResult]
    risk_level: str
    combined_confidence: int
    units_wagered: float = 1.0
    units_won: float = 0.0
    actual_win: bool = False


class CalibrationAnalyzer:
    def __init__(self):
        self.week_results: Dict[int, List[ParlayResult]] = defaultdict(list)
    
    def parse_validation_form(self, form_path: Path, week: int) -> List[ParlayResult]:
        """Parse validation form using simple finditer approach"""
        parlays = []
        
        try:
            with open(form_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Reading file: {form_path}, size: {len(content)}")
            
            # Find all "PARLAY XX" markers
            parlay_pattern = r'PARLAY\s+(\d)(\d)'
            parlay_matches = list(re.finditer(parlay_pattern, content))
            
            logger.info(f"Found {len(parlay_matches)} PARLAY markers")
            
            for i, match in enumerate(parlay_matches):
                num_legs = int(match.group(1))
                parlay_num = int(match.group(2))
                
                # Extract content from this parlay to next (or end)
                parlay_start = match.start()
                parlay_end = parlay_matches[i + 1].start() if i + 1 < len(parlay_matches) else len(content)
                
                parlay_content = content[parlay_start:parlay_end]
                
                logger.debug(f"Parlay {num_legs}{parlay_num}: {len(parlay_content)} chars")
                
                # Parse this section
                parlay = self._parse_section(parlay_content, num_legs, parlay_num, week)
                if parlay and parlay.legs:
                    parlays.append(parlay)
                    logger.info(f"Parsed {parlay.parlay_id}: {len(parlay.legs)} legs, {'WON' if parlay.actual_win else 'LOST'}")
        
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
        
        return parlays
    
    def _parse_section(self, content: str, num_legs: int, parlay_num: int, week: int) -> ParlayResult:
        """Parse a single parlay section"""
        
        # Extract metadata
        risk_m = re.search(r'Risk Level:\s*(\w+)', content)
        conf_m = re.search(r'Confidence:\s*(\d+)', content)
        units_m = re.search(r'Units:\s*([\d.]+)', content)
        
        risk = risk_m.group(1) if risk_m else 'UNKNOWN'
        conf = int(conf_m.group(1)) if conf_m else 0
        units = float(units_m.group(1)) if units_m else 1.0
        
        # Parse legs
        legs = []
        leg_pattern = r'Leg\s+(\d+)/(\d+):\s+([^(]+)\((\w+)\)\s*-\s*(\w+)'
        
        for leg_m in re.finditer(leg_pattern, content):
            player = leg_m.group(3).strip()
            position = leg_m.group(4)
            team = leg_m.group(5)
            
            # Get section for this leg
            leg_start = leg_m.start()
            next_leg = re.search(r'Leg\s+\d+/\d+:', content[leg_m.end():])
            leg_end = leg_m.end() + next_leg.start() if next_leg else len(content)
            leg_content = content[leg_start:leg_end]
            
            # Extract bet type and line
            bet_m = re.search(r'Bet Type:\s+([A-Z\s]+?)\s+([\d.]+)\s*\(vs\s+(\w+)\)', leg_content)
            if not bet_m:
                continue
            
            stat_type = bet_m.group(1).strip()
            line = float(bet_m.group(2))
            opponent = bet_m.group(3)
            
            # Extract confidence and result
            leg_conf_m = re.search(r'Confidence:\s*(\d+)%', leg_content)
            leg_conf = int(leg_conf_m.group(1)) if leg_conf_m else conf
            
            result_m = re.search(r'ACTUAL RESULT:\s*(\w+)', leg_content)
            if not result_m:
                continue
            
            actual = result_m.group(1).upper()
            if actual not in ['HIT', 'MISS']:
                continue
            
            leg = LegResult(
                player_name=player,
                position=position,
                team=team,
                opponent=opponent,
                stat_type=stat_type,
                line=line,
                confidence=leg_conf,
                actual_hit=(actual == 'HIT')
            )
            legs.append(leg)
            logger.debug(f"  Leg: {player} - {stat_type} {line} - {actual}")
        
        if not legs:
            return None
        
        all_hit = all(leg.actual_hit for leg in legs)
        
        return ParlayResult(
            parlay_id=f"week{week}_p{num_legs}{parlay_num}",
            num_legs=num_legs,
            legs=legs,
            risk_level=risk,
            combined_confidence=conf,
            units_wagered=units,
            units_won=units * (2 ** num_legs) if all_hit else 0.0,
            actual_win=all_hit
        )
    
    def analyze_week(self, week: int, validation_form_path: Path) -> Dict:
        """Analyze week results"""
        parlays = self.parse_validation_form(validation_form_path, week)
        self.week_results[week].extend(parlays)
        
        if not parlays:
            return {}
        
        total = len(parlays)
        won = sum(1 for p in parlays if p.actual_win)
        win_rate = (won / total * 100) if total > 0 else 0
        
        total_legs = sum(len(p.legs) for p in parlays)
        hit_legs = sum(sum(1 for leg in p.legs if leg.actual_hit) for p in parlays)
        leg_rate = (hit_legs / total_legs * 100) if total_legs > 0 else 0
        
        total_units = sum(p.units_wagered for p in parlays)
        total_won = sum(p.units_won for p in parlays)
        roi = ((total_won - total_units) / total_units * 100) if total_units > 0 else 0
        
        return {
            'total_parlays': total,
            'parlays_won': won,
            'win_rate': win_rate,
            'total_legs': total_legs,
            'legs_hit': hit_legs,
            'leg_rate': leg_rate,
            'total_units': total_units,
            'total_won': total_won,
            'net': total_won - total_units,
            'roi': roi
        }


def generate_calibration_report(week: int, validation_form_path: Path, data_dir: str = "data") -> str:
    """Generate calibration report"""
    analyzer = CalibrationAnalyzer()
    stats = analyzer.analyze_week(week, validation_form_path)
    parlays = analyzer.week_results[week]
    
    if not parlays:
        return "No results to analyze."
    
    lines = []
    lines.append("="*100)
    lines.append("📊 NFL BETTING CALIBRATION REPORT")
    lines.append("="*100)
    lines.append(f"Week: {week}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    lines.append("OVERALL PERFORMANCE:")
    lines.append(f"  Parlays: {stats['total_parlays']} total, {stats['parlays_won']} won ({stats['win_rate']:.1f}%)")
    lines.append(f"  Legs: {stats['total_legs']} total, {stats['legs_hit']} hit ({stats['leg_rate']:.1f}%)")
    lines.append(f"  Units: {stats['total_units']:.1f} wagered, {stats['total_won']:.1f} won")
    lines.append(f"  ROI: {stats['roi']:+.1f}%")
    lines.append("")
    
    lines.append("="*100)
    return "\n".join(lines)


if __name__ == "__main__":
    print("Calibration Dashboard Module")
