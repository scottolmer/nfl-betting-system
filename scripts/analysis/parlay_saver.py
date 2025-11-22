"""
Parlay Saver - Helper to save system-generated parlays to tracking system
Converts Parlay objects from ParlayBuilder to ParlayTracker format.
"""

import logging
from typing import Dict, List
from .models import Parlay
from .parlay_tracker import ParlayTracker

logger = logging.getLogger(__name__)


def save_parlays_to_tracker(
    parlays: Dict[str, List[Parlay]],
    week: int,
    year: int = 2024,
    parlay_type: str = "traditional",
    data_source: str = "orchestrator"
) -> List[str]:
    """
    Save system-generated parlays to the tracking system.

    Args:
        parlays: Dictionary of parlays by type (from ParlayBuilder.build_parlays())
        week: NFL week number
        year: Season year
        parlay_type: Type of parlay ("traditional" or "enhanced")
        data_source: Source of the data (e.g., "orchestrator", "csv_fallback")

    Returns:
        List of parlay IDs that were saved
    """
    tracker = ParlayTracker()
    saved_ids = []

    print(f"\n{'=' * 80}")
    print(f"💾 SAVING PARLAYS TO TRACKING SYSTEM")
    print(f"{'=' * 80}\n")

    # Process each parlay type (2-leg, 3-leg, 4-leg, 5-leg)
    for ptype, parlay_list in parlays.items():
        if not parlay_list:
            continue

        print(f"Saving {len(parlay_list)} {ptype} parlays...")

        for parlay in parlay_list:
            try:
                parlay_id = _save_single_parlay(
                    parlay=parlay,
                    tracker=tracker,
                    week=week,
                    year=year,
                    parlay_type=parlay_type,
                    data_source=data_source
                )
                saved_ids.append(parlay_id)
            except Exception as e:
                logger.error(f"Error saving parlay: {e}")
                print(f"  ❌ Failed to save one {ptype} parlay: {e}")

    print(f"\n✅ Saved {len(saved_ids)} parlays to tracking system")
    print(f"{'=' * 80}\n")

    return saved_ids


def _save_single_parlay(
    parlay: Parlay,
    tracker: ParlayTracker,
    week: int,
    year: int,
    parlay_type: str,
    data_source: str
) -> str:
    """
    Convert a single Parlay object and save to tracker.

    Args:
        parlay: Parlay object from ParlayBuilder
        tracker: ParlayTracker instance
        week: NFL week number
        year: Season year
        parlay_type: Type of parlay
        data_source: Data source

    Returns:
        parlay_id that was created
    """
    # Convert legs to props format
    props = []
    for leg in parlay.legs:
        prop = leg.prop
        props.append({
            'player': prop.player_name,
            'team': prop.team,
            'opponent': prop.opponent,
            'position': prop.position,
            'stat_type': prop.stat_type,
            'line': prop.line,
            'direction': prop.direction,
            'confidence': leg.final_confidence,
            'is_home': prop.is_home,
            'agent_scores': leg.agent_breakdown  # This has the full breakdown
        })

    # Calculate confidences
    raw_confidence = sum(leg.final_confidence for leg in parlay.legs) / len(parlay.legs)

    # Effective confidence includes correlation bonus
    effective_confidence = parlay.combined_confidence

    # Build correlations list
    correlations = []
    if parlay.correlation_bonus != 0:
        correlations.append({
            'type': 'same_game_bonus',
            'adjustment': parlay.correlation_bonus,
            'reasoning': f'{parlay.parlay_type} same-game correlation bonus'
        })

    # Extract aggregate agent breakdown (average across all legs)
    agent_breakdown = _calculate_aggregate_agent_breakdown(parlay.legs)

    # Calculate payout odds (approximate based on parlay size and confidence)
    num_legs = len(parlay.legs)
    payout_odds = _estimate_payout_odds(num_legs)

    # Calculate Kelly bet size
    kelly_bet_size = parlay.recommended_units

    # Save to tracker
    parlay_id = tracker.add_parlay(
        week=week,
        year=year,
        parlay_type=parlay_type,
        props=props,
        raw_confidence=raw_confidence,
        effective_confidence=effective_confidence,
        correlations=correlations,
        payout_odds=payout_odds,
        kelly_bet_size=kelly_bet_size,
        data_source=data_source,
        agent_breakdown=agent_breakdown
    )

    return parlay_id


def _calculate_aggregate_agent_breakdown(legs: List) -> Dict:
    """
    Calculate average agent breakdown across all legs in a parlay.

    Args:
        legs: List of PropAnalysis objects

    Returns:
        Dictionary with aggregate agent scores and weights
    """
    agent_totals = {}
    agent_counts = {}

    for leg in legs:
        for agent_name, agent_data in leg.agent_breakdown.items():
            if agent_name not in agent_totals:
                agent_totals[agent_name] = {
                    'raw_scores': [],
                    'weight': agent_data.get('weight', 0)
                }
            agent_totals[agent_name]['raw_scores'].append(agent_data.get('raw_score', 0))

    # Calculate averages
    agent_breakdown = {}
    for agent_name, data in agent_totals.items():
        avg_score = sum(data['raw_scores']) / len(data['raw_scores'])
        agent_breakdown[agent_name] = {
            'raw_score': avg_score,
            'weight': data['weight']
        }

    return agent_breakdown


def _estimate_payout_odds(num_legs: int) -> int:
    """
    Estimate payout odds based on number of legs.
    These are approximate American odds (+260 = $260 profit on $100 bet).

    Args:
        num_legs: Number of legs in the parlay

    Returns:
        Estimated payout odds (American format)
    """
    odds_map = {
        2: 260,   # 2.6x payout
        3: 600,   # 6x payout
        4: 1200,  # 12x payout
        5: 2500,  # 25x payout
        6: 4000,  # 40x payout
    }
    return odds_map.get(num_legs, 1000)


def save_parlays_after_analysis(
    parlays: Dict[str, List[Parlay]],
    week: int,
    year: int = 2024,
    parlay_type: str = "traditional"
) -> None:
    """
    Convenience function to save parlays with user-friendly output.
    Called from run_analysis.py after parlays are built.

    Args:
        parlays: Dictionary of parlays from ParlayBuilder
        week: NFL week number
        year: Season year
        parlay_type: Type of parlay
    """
    total_parlays = sum(len(p) for p in parlays.values())

    if total_parlays == 0:
        print("\n⚠️  No parlays to save to tracking system")
        return

    saved_ids = save_parlays_to_tracker(
        parlays=parlays,
        week=week,
        year=year,
        parlay_type=parlay_type,
        data_source="run_analysis"
    )

    if saved_ids:
        print(f"✅ Saved {len(saved_ids)} parlays to parlay_tracking.json")
        print(f"   You can now export them using: python scripts/export_parlays_cli.py --week {week}")
