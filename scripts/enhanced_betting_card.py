"""
Enhanced Betting Card Generator with Validation Form
Saves betting cards with timestamps and generates fillable forms for post-game validation
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class BettingCardFormatter:
    """Formats betting cards and generates validation forms"""
    
    @staticmethod
    def generate_validation_form(parlays: Dict, week: int, generated_at: datetime) -> str:
        """
        Generate a fillable validation form for post-game result tracking
        
        Form allows filling in actual results and calculating ROI
        """
        output = []
        total_parlays = sum(len(p) for p in parlays.values())
        
        output.append("="*80)
        output.append("🏈 NFL BETTING VALIDATION FORM - POST-GAME RESULTS")
        output.append("="*80)
        output.append("")
        
        # Header info
        output.append("PREDICTION DETAILS")
        output.append("-"*80)
        output.append(f"Week: {week}")
        output.append(f"Generated: {generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"Total Parlays: {total_parlays}")
        output.append("")
        
        # Instructions
        output.append("INSTRUCTIONS FOR VALIDATION")
        output.append("-"*80)
        output.append(f"1. After all games in Week {week} have concluded, fill in the 'ACTUAL' column")
        output.append("2. Enter 'HIT' if the prop went over the line, 'MISS' if it went under")
        output.append("3. The system will automatically calculate if each leg won/lost")
        output.append("4. Mark entire parlay as 'WON' only if ALL legs hit")
        output.append("")
        output.append("")
        
        parlay_counter = {'2': 0, '3': 0, '4': 0, '5': 0}
        total_units_recommended = 0
        
        for leg_count in [2, 3, 4, 5]:
            parlay_list = parlays.get(f'{leg_count}-leg', [])
            if not parlay_list:
                continue
            
            output.append("="*80)
            output.append(f"📊 {leg_count}-LEG PARLAYS")
            output.append("="*80)
            output.append("")
            
            for parlay_idx, parlay in enumerate(parlay_list, 1):
                parlay_counter[str(leg_count)] = parlay_idx
                recommended_units = parlay.recommended_units
                total_units_recommended += recommended_units
                
                output.append(f"┌─ PARLAY {leg_count}{parlay_idx} ─────────────────────────────────────────────────────┐")
                output.append(f"│ Risk Level: {parlay.risk_level:<8} | Confidence: {parlay.combined_confidence} | Units: {recommended_units:.1f}")
                output.append(f"│ Expected Value: +{parlay.expected_value:.1f}% | Potential Payout: ${recommended_units * (2 ** leg_count):.0f}")
                output.append("├─────────────────────────────────────────────────────────────────────────────┤")
                
                for leg_idx, leg in enumerate(parlay.legs, 1):
                    prop = leg.prop
                    output.append(f"│ Leg {leg_idx}/{leg_count}: {prop.player_name} ({prop.position}) - {prop.team}")
                    output.append(f"│   Bet Type: {prop.stat_type} OVER {prop.line} (vs {prop.opponent})")
                    output.append(f"│   Confidence: {leg.final_confidence}%")
                    output.append("│")
                    output.append(f"│   PREDICTION: {prop.stat_type} OVER {prop.line}")
                    output.append("│   ACTUAL RESULT: ________________  (Enter HIT or MISS)")
                    output.append("│   LEG RESULT: [ ]  (System calculates)")
                    output.append("│")
                
                output.append(f"├─ PARLAY RESULT ─────────────────────────────────────────────────────────────┤")
                output.append(f"│ All legs must HIT for parlay to WIN")
                output.append(f"│ PARLAY RESULT: [ ]  (System calculates: WON or LOST)")
                output.append(f"│ UNITS WON/LOST: ________________")
                output.append(f"└─────────────────────────────────────────────────────────────────────────────┘")
                output.append("")
                output.append("")
        
        # Summary section
        output.append("="*80)
        output.append("📊 VALIDATION SUMMARY")
        output.append("="*80)
        output.append("")
        output.append("OVERALL RESULTS")
        output.append("-"*80)
        output.append(f"Total Recommended Units: {total_units_recommended:.1f}")
        output.append(f"At $10/unit: ${total_units_recommended * 10:.0f}")
        output.append(f"At $25/unit: ${total_units_recommended * 25:.0f}")
        output.append("")
        output.append("RESULTS TO FILL IN:")
        output.append("-"*80)
        output.append(f"Total Parlays Placed: _____ / {total_parlays}")
        output.append(f"Parlays Won: _____")
        output.append(f"Parlays Lost: _____")
        output.append(f"Win Rate: ____% (Parlays Won / Parlays Placed)")
        output.append("")
        output.append(f"Total Units Wagered: _____ (should equal {total_units_recommended:.1f})")
        output.append(f"Total Units Won: _____")
        output.append(f"Total Units Lost: _____")
        output.append(f"Net Profit/Loss: _____ units")
        output.append(f"ROI: ____% (Net Profit / Units Wagered * 100)")
        output.append("")
        output.append("")
        
        # Calibration section
        output.append("="*80)
        output.append("📈 CALIBRATION NOTES")
        output.append("="*80)
        output.append("Use this section to track system performance and identify improvements:")
        output.append("")
        output.append("Which parlays performed better? (2-leg, 3-leg, 4-leg, 5-leg)")
        output.append("_" * 80)
        output.append("")
        output.append("Which positions/players underperformed?")
        output.append("_" * 80)
        output.append("")
        output.append("Any external factors that affected results? (injuries, weather, etc.)")
        output.append("_" * 80)
        output.append("")
        output.append("Confidence estimates accuracy (were high-confidence props more reliable?)")
        output.append("_" * 80)
        output.append("")
        output.append(f"Overall system assessment for Week {week}:")
        output.append("_" * 80)
        output.append("")
        output.append("="*80)
        
        return "\n".join(output)
    
    @staticmethod
    def format_betting_card_with_metadata(parlays: Dict, betting_card: str, week: int, 
                                          generated_at: datetime) -> str:
        """
        Add metadata header to betting card
        """
        output = []
        
        output.append("="*80)
        output.append("🏈 NFL BETTING ANALYSIS - WEEK {} PARLAYS".format(week))
        output.append("="*80)
        output.append("")
        output.append("METADATA")
        output.append("-"*80)
        output.append(f"Generated: {generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"System: NFL Betting Analysis AI")
        output.append(f"Week: {week}")
        output.append(f"Total Parlays: {sum(len(p) for p in parlays.values())}/10")
        output.append("")
        output.append("⚠️  DISCLAIMER: These are AI-generated predictions for educational and research purposes.")
        output.append("   Always gamble responsibly and only bet what you can afford to lose.")
        output.append("="*80)
        output.append("")
        
        # Add original betting card
        output.append(betting_card)
        
        return "\n".join(output)


def save_betting_card_with_timestamps(betting_card: str, parlays: Dict, week: int, 
                                      data_dir: str = "data") -> tuple:
    """
    Save betting card with timestamped folder structure
    
    Folder structure:
    data/
    └── betting_history/
        └── week_8/
            └── 2025-10-25_09-44-38/
                ├── betting_card.txt
                ├── validation_form.txt
                └── metadata.txt
    
    Args:
        betting_card: The formatted betting card text
        parlays: Dictionary of parlays
        week: NFL week number
        data_dir: Base data directory
    
    Returns:
        Tuple of (betting_card_path, validation_form_path, folder_path)
    """
    
    # Create timestamp
    now = datetime.now()
    timestamp_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    
    # Create folder structure
    base_path = Path(data_dir) / "betting_history" / f"week_{week}" / timestamp_str
    base_path.mkdir(parents=True, exist_ok=True)
    
    # Save betting card
    card_path = base_path / "betting_card.txt"
    formatter = BettingCardFormatter()
    card_with_metadata = formatter.format_betting_card_with_metadata(parlays, betting_card, week, now)
    
    with open(card_path, 'w', encoding='utf-8') as f:
        f.write(card_with_metadata)
    
    logger.info(f"✅ Saved betting card to: {card_path}")
    
    # Save validation form
    form_path = base_path / "validation_form.txt"
    validation_form = formatter.generate_validation_form(parlays, week, now)
    
    with open(form_path, 'w', encoding='utf-8') as f:
        f.write(validation_form)
    
    logger.info(f"✅ Saved validation form to: {form_path}")
    
    # Save metadata
    metadata_path = base_path / "metadata.txt"
    total_units = sum(parlay.recommended_units for parlays_list in parlays.values() for parlay in parlays_list)
    
    metadata = f"""BETTING CARD METADATA
Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}
Week: {week}
Total Parlays: {sum(len(p) for p in parlays.values())}/10

BREAKDOWN:
- 2-leg parlays: {len(parlays.get('2-leg', []))}
- 3-leg parlays: {len(parlays.get('3-leg', []))}
- 4-leg parlays: {len(parlays.get('4-leg', []))}
- 5-leg parlays: {len(parlays.get('5-leg', []))}

INVESTMENT:
- Total units: {total_units:.1f}
- At $10/unit: ${total_units * 10:.0f}
- At $25/unit: ${total_units * 25:.0f}

FILES:
- betting_card.txt: Main betting recommendations
- validation_form.txt: Post-game result tracking and validation form
- metadata.txt: This file
"""
    
    with open(metadata_path, 'w', encoding='utf-8') as f:
        f.write(metadata)
    
    logger.info(f"✅ Saved metadata to: {metadata_path}")
    
    # Create a LATEST pointer file (works on Windows without admin)
    latest_pointer = Path(data_dir) / "betting_history" / f"week_{week}" / "LATEST.txt"
    try:
        with open(latest_pointer, 'w') as f:
            f.write(f"LATEST BETTING CARD: {timestamp_str}\n")
            f.write(f"Folder: {base_path}\n")
            f.write(f"Betting Card: {card_path}\n")
            f.write(f"Validation Form: {form_path}\n")
        logger.info(f"✅ Updated LATEST pointer to: {timestamp_str}")
    except Exception as e:
        logger.warning(f"Could not create LATEST pointer: {e}")
    
    return str(card_path), str(form_path), str(base_path)


if __name__ == "__main__":
    # Example usage
    print("Betting Card Enhancement Module - Import this in your main scripts")
