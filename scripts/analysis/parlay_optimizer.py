"""Parlay Optimizer - Rebuilds parlays to minimize dependency risk"""
import logging
from typing import List, Dict, Tuple, Set
from .models import PropAnalysis, Parlay
from .dependency_analyzer import DependencyAnalyzer
from .prop_availability_validator import PropAvailabilityValidator

logger = logging.getLogger(__name__)


class ParlayOptimizer:
    """Optimizes parlay construction to minimize correlations"""

    def __init__(self, api_key: str = None, db_path: str = "bets.db"):
        self.dep_analyzer = DependencyAnalyzer(api_key=api_key)
        self.validator = PropAvailabilityValidator(db_path=db_path)

    def rebuild_parlays_low_correlation(
        self,
        all_analyses: List[PropAnalysis],
        target_parlays: int = 10,
        min_confidence: int = 65,
        max_player_exposure: float = 1.0,
        teams: List[str] = None
    ) -> Dict[str, List[Parlay]]:
        """
        Rebuild parlays optimizing for low dependency risk

        Strategy:
        1. Score each prop for "independence" - how uncorrelated it is from others
        2. Build parlays preferring independent props
        3. Validate each parlay's dependency score
        4. Stop when target is reached

        Args:
            all_analyses: List of prop analyses
            target_parlays: Number of parlays to generate
            min_confidence: Minimum confidence threshold
            max_player_exposure: Maximum player exposure (0.0-1.0)
            teams: Optional list of team abbreviations to filter to (e.g., ['GB', 'DET', 'KC'])
        """

        print("\n" + "="*70)
        print("🔄 REBUILDING PARLAYS - LOW CORRELATION OPTIMIZATION")
        print("="*70)

        # Filter by teams if specified
        if teams:
            all_analyses = [a for a in all_analyses if a.prop.team in teams]
            print(f"\n📌 Filtered to teams: {', '.join(teams)} ({len(all_analyses)} props)")

        # Filter eligible props
        eligible = sorted(
            [p for p in all_analyses if p.final_confidence >= min_confidence],
            key=lambda x: x.final_confidence,
            reverse=True
        )

        # Filter by minimum thresholds (remove props with lines too small for DraftKings)
        eligible = self.validator.filter_by_minimum_thresholds(eligible, verbose=True)

        # Filter out defense/ST props
        eligible = self.validator.filter_defense_props(eligible, verbose=True)

        print(f"\n📊 Starting with {len(eligible)} props (confidence {min_confidence}+)")
        
        # Score props for independence
        independence_scores = self._score_independence(eligible)
        
        # Build diverse parlays
        optimized_parlays = self._build_optimized_parlays(
            eligible, 
            independence_scores,
            target_parlays,
            max_player_exposure
        )
        
        # Validate with dependency analyzer
        print("\n🔍 Validating with dependency analysis...\n")
        analyzed = self.dep_analyzer.analyze_all_parlays(optimized_parlays)
        
        # Report
        self._print_optimization_report(analyzed)
        
        return optimized_parlays

    def _score_independence(self, props: List[PropAnalysis]) -> Dict:
        """Score each prop for how independent it is"""
        scores = {}
        
        # Count occurrences of each player/team combo
        player_counts = {}
        team_counts = {}
        stat_counts = {}
        
        for prop in props:
            player_key = prop.prop.player_name
            team_key = f"{prop.prop.team} vs {prop.prop.opponent}"
            stat_key = f"{prop.prop.stat_type}-{prop.prop.position}"
            
            player_counts[player_key] = player_counts.get(player_key, 0) + 1
            team_counts[team_key] = team_counts.get(team_key, 0) + 1
            stat_counts[stat_key] = stat_counts.get(stat_key, 0) + 1
        
        # Score: lower counts = more independent
        for prop in props:
            player_key = prop.prop.player_name
            team_key = f"{prop.prop.team} vs {prop.prop.opponent}"
            stat_key = f"{prop.prop.stat_type}-{prop.prop.position}"
            
            # Inverse scoring - fewer duplicates = higher independence
            player_penalty = 1.0 / (1 + player_counts[player_key])
            team_penalty = 1.0 / (1 + team_counts[team_key])
            stat_bonus = 1.0 / (1 + stat_counts[stat_key])
            
            independence = (player_penalty * 0.4 + team_penalty * 0.4 + stat_bonus * 0.2)
            scores[id(prop)] = independence
        
        return scores

    def _build_optimized_parlays(
        self,
        eligible: List[PropAnalysis],
        independence_scores: Dict,
        target_total: int,
        max_player_exposure: float = 1.0
    ) -> Dict[str, List[Parlay]]:
        """Build parlays - ONE PLAYER PER PARLAY (maximum diversification)"""
        
        result = {'2-leg': [], '3-leg': [], '4-leg': [], '5-leg': []}
        player_usage_count: Dict[str, int] = {}
        all_used_players: Set[str] = set()  # CONSTRAINT: Each player in exactly ONE parlay
        built_parlay_signatures: Set[str] = set()  # DUPLICATE DETECTION
        
        # Dynamically distribute target parlays across leg types
        if target_total <= 5:
            targets = {
                '2-leg': max(1, target_total // 3),
                '3-leg': max(1, target_total // 3),
                '4-leg': max(1, target_total - (2 * (target_total // 3))),
                '5-leg': 0
            }
        elif target_total <= 10:
            targets = {
                '2-leg': max(2, int(target_total * 0.40)),
                '3-leg': max(2, int(target_total * 0.40)),
                '4-leg': max(1, int(target_total * 0.20)),
                '5-leg': 0
            }
        else:
            targets = {
                '2-leg': int(target_total * 0.35),
                '3-leg': int(target_total * 0.35),
                '4-leg': int(target_total * 0.20),
                '5-leg': int(target_total * 0.10)
            }
        
        # Adjust to ensure we hit target_total exactly
        total_assigned = sum(targets.values())
        if total_assigned < target_total:
            targets['2-leg'] += (target_total - total_assigned)
        
        print(f"\n📊 Target Distribution for {target_total} parlays:")
        print(f"   2-leg: {targets['2-leg']} | 3-leg: {targets['3-leg']} | 4-leg: {targets['4-leg']} | 5-leg: {targets['5-leg']}")
        print(f"📊 CONSTRAINT: One player per parlay (maximum diversification)\n")
        
        for leg_type in ['2-leg', '3-leg', '4-leg', '5-leg']:
            num_legs = int(leg_type.split('-')[0])
            target_count = targets[leg_type]
            
            built = 0
            attempt = 0
            max_attempts = 200  # Very generous attempts
            
            while built < target_count and attempt < max_attempts:
                attempt += 1
                
                # PROGRESSIVE CONFIDENCE RELAXATION
                relaxation_factor = min(1.0, (attempt - 1) / 30)  # Full relax by attempt 31
                
                if num_legs == 5:
                    base_threshold = 62
                elif num_legs == 4:
                    base_threshold = 64
                elif num_legs == 3:
                    base_threshold = 66
                else:  # 2-leg
                    base_threshold = 68
                
                # Relax by up to 15 points
                relaxed_threshold = base_threshold - (relaxation_factor * 15)
                
                # Build candidate list
                candidates = [p for p in eligible if p.final_confidence >= relaxed_threshold]
                
                # Sort by CONFIDENCE FIRST (80%), independence SECOND (20%)
                candidates.sort(
                    key=lambda p: (
                        p.final_confidence * 0.8 +
                        independence_scores[id(p)] * 100 * 0.2
                    ),
                    reverse=True
                )
                
                # Build parlay - MUST use ONLY UNUSED PLAYERS
                parlay_legs = []
                players_used = set()
                games_used = set()
                
                for candidate in candidates:
                    if len(parlay_legs) >= num_legs:
                        break
                    
                    player = candidate.prop.player_name
                    
                    # HARD CONSTRAINT: Player cannot be in any other parlay
                    if player in all_used_players:
                        continue  # Skip - player already locked in another parlay
                    
                    if player in players_used:
                        continue  # Skip - already in this parlay
                    
                    game = f"{candidate.prop.team} vs {candidate.prop.opponent}"
                    
                    # Allow up to 2 props from same game
                    max_same_game = 2
                    same_game_count = sum(1 for leg in parlay_legs 
                                         if f"{leg.prop.team} vs {leg.prop.opponent}" == game)
                    if same_game_count >= max_same_game:
                        continue
                    
                    parlay_legs.append(candidate)
                    players_used.add(player)
                    games_used.add(game)
                
                # Only accept parlay if we got all legs with completely new players
                if len(parlay_legs) == num_legs:
                    # CREATE PARLAY SIGNATURE for duplicate detection
                    parlay_signature = "|".join(sorted([
                        f"{leg.prop.player_name}_{leg.prop.stat_type}_{leg.prop.line}" 
                        for leg in parlay_legs
                    ]))
                    
                    # SKIP IF DUPLICATE
                    if parlay_signature in built_parlay_signatures:
                        continue
                    
                    built_parlay_signatures.add(parlay_signature)
                    
                    avg_conf = sum(p.final_confidence for p in parlay_legs) / num_legs
                    parlay = Parlay(
                        legs=parlay_legs,
                        parlay_type=leg_type,
                        risk_level="MODERATE",
                        rationale=f"✅ {len(games_used)} games, avg conf: {avg_conf:.0f}%"
                    )
                    result[leg_type].append(parlay)
                    
                    # Update tracking - lock ALL players to this parlay
                    for leg in parlay_legs:
                        player_name = leg.prop.player_name
                        player_usage_count[player_name] = 1  # Always 1 (one per parlay)
                        all_used_players.add(player_name)  # LOCK player globally
                    
                    built += 1
                    print(f"  ✓ Built {leg_type} Parlay #{built} (Avg Conf: {avg_conf:.0f}%)")
            
            if built < target_count:
                print(f"  ⚠️ Only built {built}/{target_count} {leg_type} parlays")
        
        # Generate exposure report
        self._print_exposure_report(player_usage_count, target_total)
        
        return result
    
    def _print_exposure_report(self, player_usage_count: Dict[str, int], total_parlays: int):
        """Print player exposure report showing concentration risk"""
        
        if not player_usage_count:
            return
        
        print("\n" + "="*70)
        print("📊 PLAYER EXPOSURE REPORT")
        print("="*70)
        
        sorted_players = sorted(player_usage_count.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\n🟢 ALL PLAYERS (1 appearance each):")
        for i, (player, count) in enumerate(sorted_players):
            if i < 30:  # Show first 30
                print(f"  ✓ {player:25s} | {count}/{total_parlays} parlay")
        
        if len(sorted_players) > 30:
            print(f"  ... and {len(sorted_players) - 30} more players")
        
        # Summary stats
        total_unique_players = len(player_usage_count)
        
        print("\n" + "-"*70)
        print(f"Total Unique Players: {total_unique_players}")
        print(f"Average Parlays per Player: 1.0 (ONE-PER-PARLAY CONSTRAINT)")
        print(f"Coverage: {total_unique_players} unique players across {total_parlays} parlays")
        print(f"Diversification: {(total_unique_players / total_parlays):.1%}")
        print("="*70)

    def _print_optimization_report(self, analyzed_parlays: Dict):
        """Print optimization results"""
        
        print("\n" + "="*70)
        print("📊 OPTIMIZATION RESULTS")
        print("="*70)
        
        total_parlays = 0
        accepts = 0
        modifies = 0
        avoids = 0
        
        for ptype in ['2-leg', '3-leg', '4-leg', '5-leg']:
            items = analyzed_parlays.get(ptype, [])
            if not items:
                continue
            
            print(f"\n{ptype.upper()} ({len(items)} parlays)")
            print("-" * 70)
            
            for i, item in enumerate(items, 1):
                analysis = item['dependency_analysis']
                adj_conf = analysis.get('adjusted_confidence', 50)
                rec = analysis.get('recommendation', 'REVIEW')
                
                if rec == "ACCEPT":
                    emoji = "✅"
                    accepts += 1
                elif rec == "MODIFY":
                    emoji = "⚠️"
                    modifies += 1
                else:
                    emoji = "❌"
                    avoids += 1
                
                print(f"  {emoji} Parlay {i}: {rec} - Adjusted Confidence: {adj_conf}%")
            
            total_parlays += len(items)
        
        print("\n" + "="*70)
        print(f"Total: {total_parlays} parlays")
        print(f"  ✅ ACCEPT: {accepts}")
        print(f"  ⚠️ MODIFY: {modifies}")
        print(f"  ❌ AVOID: {avoids}")
        print("="*70)

    def get_best_parlays(
        self, 
        analyzed_parlays: Dict,
        exclude_avoid: bool = True
    ) -> List[Dict]:
        """Extract only the best parlays"""
        
        best = []
        
        for ptype in ['2-leg', '3-leg', '4-leg', '5-leg']:
            for item in analyzed_parlays.get(ptype, []):
                analysis = item['dependency_analysis']
                rec = analysis.get('recommendation')
                
                if exclude_avoid and rec == "AVOID":
                    continue
                
                best.append({
                    'parlay': item['parlay'],
                    'adjusted_confidence': analysis.get('adjusted_confidence'),
                    'recommendation': rec,
                    'adjustment': analysis.get('correlation_adjustment', {}).get('adjustment_value', 0)
                })
        
        # Sort by confidence descending
        best.sort(key=lambda x: x['adjusted_confidence'], reverse=True)
        
        return best

    def format_best_parlays(self, best_parlays: List[Dict]) -> str:
        """Format best parlays for display"""
        
        lines = [
            "\n" + "="*70,
            "🎯 OPTIMIZED PARLAYS (LOW CORRELATION)",
            "="*70,
            ""
        ]
        
        total_units = 0
        
        for i, item in enumerate(best_parlays, 1):
            parlay = item['parlay']
            conf = item['adjusted_confidence']
            rec = item['recommendation']
            adj = item['adjustment']
            
            emoji = "✅" if rec == "ACCEPT" else "⚠️"
            
            # Adjust units based on recommendation
            if rec == "AVOID":
                units = 0
            elif rec == "MODIFY":
                units = max(0.5, parlay.recommended_units * 0.75)
            else:
                units = parlay.recommended_units
            
            total_units += units
            
            lines.append(f"{emoji} PARLAY {i} ({parlay.parlay_type})")
            lines.append(f"   Confidence: {conf}% ({adj:+d})")
            lines.append(f"   Bet: {units:.2f} units (${units*10:.0f})")
            
            for j, leg in enumerate(parlay.legs, 1):
                bet_type = getattr(leg.prop, 'bet_type', 'OVER')
                lines.append(f"     {j}. {leg.prop.player_name} - {leg.prop.stat_type} {bet_type} {leg.prop.line}")
            
            lines.append("")
        
        lines.append("="*70)
        lines.append(f"Total: {len(best_parlays)} parlays | {total_units:.1f} units | ${total_units*10:.0f}")
        lines.append("="*70)
        
        return "\n".join(lines)
    
    def _create_under_variation(self, over_analysis):
        """Deprecated: Use orchestrator._create_complementary_bet instead"""
        pass
