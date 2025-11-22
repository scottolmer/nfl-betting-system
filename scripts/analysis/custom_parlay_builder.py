"""
Custom Parlay Builder - Manual parlay creation from analyzed props
Allows users to build custom 2-6 leg parlays when DraftKings lines don't match system parlays.
"""

import os
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from tabulate import tabulate
import anthropic

from .models import PropAnalysis, PlayerProp, Parlay
from .parlay_tracker import ParlayTracker
from .dependency_analyzer import DependencyAnalyzer

logger = logging.getLogger(__name__)


class CustomParlayBuilder:
    """Interactive CLI tool for building custom 2-6 leg parlays from analyzed props"""

    def __init__(self, analyzed_props: List[PropAnalysis], week: int, year: int = 2024):
        """
        Initialize the custom parlay builder.

        Args:
            analyzed_props: List of all props analyzed by orchestrator
            week: NFL week number
            year: Year (default 2024)
        """
        self.all_props = analyzed_props
        self.week = week
        self.year = year
        self.selected_legs: List[PropAnalysis] = []
        self.tracker = ParlayTracker()

        # Initialize dependency analyzer for correlation detection
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.dependency_analyzer = DependencyAnalyzer(api_key=api_key)

    def display_all_props(
        self,
        sort_by: str = "confidence",
        filter_position: Optional[str] = None,
        filter_stat_type: Optional[str] = None,
        filter_player: Optional[str] = None,
        min_confidence: int = 50,
        limit: Optional[int] = None
    ) -> None:
        """
        Display all analyzed props with sorting and filtering options.

        Args:
            sort_by: Sort method - "confidence" (default), "position", "player", "game"
            filter_position: Filter by position (e.g., "QB", "RB", "WR")
            filter_stat_type: Filter by stat type (e.g., "Pass Yds", "Rush Yds")
            filter_player: Filter by player name (partial match)
            min_confidence: Minimum confidence threshold (default 50)
            limit: Maximum number of props to display
        """
        # Apply filters
        filtered_props = self.all_props

        if filter_position:
            filtered_props = [p for p in filtered_props if p.prop.position.upper() == filter_position.upper()]

        if filter_stat_type:
            filtered_props = [p for p in filtered_props if filter_stat_type.lower() in p.prop.stat_type.lower()]

        if filter_player:
            filtered_props = [p for p in filtered_props if filter_player.lower() in p.prop.player_name.lower()]

        # Filter by minimum confidence
        filtered_props = [p for p in filtered_props if p.final_confidence >= min_confidence]

        # Sort props
        if sort_by == "confidence":
            filtered_props.sort(key=lambda p: p.final_confidence, reverse=True)
        elif sort_by == "position":
            filtered_props.sort(key=lambda p: (p.prop.position, -p.final_confidence))
        elif sort_by == "player":
            filtered_props.sort(key=lambda p: p.prop.player_name)
        elif sort_by == "game":
            filtered_props.sort(key=lambda p: (p.prop.team, p.prop.opponent, -p.final_confidence))

        # Apply limit
        if limit:
            filtered_props = filtered_props[:limit]

        # Build table for display
        table_data = []
        for i, analysis in enumerate(filtered_props, 1):
            prop = analysis.prop

            # Get top contributing agents
            top_agents = analysis.top_contributing_agents[:2] if analysis.top_contributing_agents else []
            top_agents_str = ", ".join([f"{name} ({contrib:.0f}%)" for name, contrib in top_agents])

            table_data.append([
                i,
                prop.player_name,
                prop.position,
                prop.stat_type,
                f"{prop.line:.1f}",
                prop.direction,
                f"{analysis.final_confidence}%",
                f"{prop.team} vs {prop.opponent}",
                top_agents_str
            ])

        # Display table
        headers = ["#", "Player", "Pos", "Stat Type", "Line", "Dir", "Conf", "Game", "Top Agents"]
        print("\n" + "=" * 120)
        print(f"📊 ANALYZED PROPS - Week {self.week} ({len(filtered_props)} props)")
        print("=" * 120)
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print(f"\nShowing {len(filtered_props)} of {len(self.all_props)} total props")
        print("=" * 120 + "\n")

    def select_leg_interactive(self) -> bool:
        """
        Interactive CLI for selecting a single leg.

        Returns:
            True if leg was added, False if cancelled
        """
        print("\n" + "=" * 80)
        print(f"🏈 SELECT LEG ({len(self.selected_legs)}/6 selected)")
        print("=" * 80)

        # Show currently selected legs
        if self.selected_legs:
            self._display_selected_legs()

        # Get selection method
        print("\nHow would you like to find a prop?")
        print("  1. Browse all props")
        print("  2. Search by player name")
        print("  3. Filter by position")
        print("  4. Filter by stat type")
        print("  5. Cancel / Go back")

        choice = input("\nEnter choice (1-5): ").strip()

        if choice == "1":
            return self._select_from_browse()
        elif choice == "2":
            return self._select_by_player()
        elif choice == "3":
            return self._select_by_position()
        elif choice == "4":
            return self._select_by_stat_type()
        else:
            print("❌ Selection cancelled")
            return False

    def _select_from_browse(self, filtered_props: Optional[List[PropAnalysis]] = None) -> bool:
        """Browse and select from list of props"""
        if filtered_props is None:
            filtered_props = self.all_props

        # Filter out already selected players
        available_props = self._filter_available_props(filtered_props)

        if not available_props:
            print("❌ No available props (all players already selected)")
            return False

        # Sort by confidence
        available_props.sort(key=lambda p: p.final_confidence, reverse=True)

        # Display props with numbers
        print("\n" + "-" * 100)
        print("Available Props (sorted by confidence):")
        print("-" * 100)

        # Show in pages of 20
        page_size = 20
        page = 0

        while True:
            start_idx = page * page_size
            end_idx = min(start_idx + page_size, len(available_props))

            table_data = []
            for i in range(start_idx, end_idx):
                analysis = available_props[i]
                prop = analysis.prop
                table_data.append([
                    i + 1,
                    prop.player_name,
                    prop.position,
                    prop.stat_type,
                    f"{prop.line:.1f}",
                    prop.direction,
                    f"{analysis.final_confidence}%",
                    f"{prop.team} vs {prop.opponent}"
                ])

            headers = ["#", "Player", "Pos", "Stat Type", "Line", "Dir", "Conf", "Game"]
            print(tabulate(table_data, headers=headers, tablefmt="simple"))

            print(f"\nShowing {start_idx + 1}-{end_idx} of {len(available_props)} props")

            # Get user input
            if end_idx < len(available_props):
                print("\nOptions: [number] to select, [n] next page, [p] prev page, [c] cancel")
            else:
                print("\nOptions: [number] to select, [p] prev page, [c] cancel")

            user_input = input("Enter choice: ").strip().lower()

            if user_input == 'c':
                return False
            elif user_input == 'n' and end_idx < len(available_props):
                page += 1
            elif user_input == 'p' and page > 0:
                page -= 1
            elif user_input.isdigit():
                idx = int(user_input) - 1
                if 0 <= idx < len(available_props):
                    selected_analysis = available_props[idx]
                    self.selected_legs.append(selected_analysis)
                    print(f"✅ Added: {selected_analysis.prop.player_name} {selected_analysis.prop.stat_type} {selected_analysis.prop.direction} {selected_analysis.prop.line}")
                    return True
                else:
                    print("❌ Invalid selection number")
            else:
                print("❌ Invalid input")

    def _select_by_player(self) -> bool:
        """Search and select by player name"""
        player_name = input("\nEnter player name (partial match): ").strip()

        if not player_name:
            print("❌ No player name entered")
            return False

        # Filter by player name
        filtered = [p for p in self.all_props if player_name.lower() in p.prop.player_name.lower()]

        if not filtered:
            print(f"❌ No props found for player matching '{player_name}'")
            return False

        print(f"\n✓ Found {len(filtered)} props matching '{player_name}'")
        return self._select_from_browse(filtered)

    def _select_by_position(self) -> bool:
        """Filter and select by position"""
        print("\nSelect position:")
        positions = ["QB", "RB", "WR", "TE", "K"]
        for i, pos in enumerate(positions, 1):
            print(f"  {i}. {pos}")

        choice = input("\nEnter position number (1-5): ").strip()

        if not choice.isdigit() or int(choice) < 1 or int(choice) > 5:
            print("❌ Invalid position selection")
            return False

        position = positions[int(choice) - 1]
        filtered = [p for p in self.all_props if p.prop.position == position]

        if not filtered:
            print(f"❌ No props found for position {position}")
            return False

        print(f"\n✓ Found {len(filtered)} {position} props")
        return self._select_from_browse(filtered)

    def _select_by_stat_type(self) -> bool:
        """Filter and select by stat type"""
        # Get unique stat types
        stat_types = sorted(list(set(p.prop.stat_type for p in self.all_props)))

        print("\nAvailable stat types:")
        for i, stat in enumerate(stat_types, 1):
            count = len([p for p in self.all_props if p.prop.stat_type == stat])
            print(f"  {i}. {stat} ({count} props)")

        choice = input(f"\nEnter stat type number (1-{len(stat_types)}): ").strip()

        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(stat_types):
            print("❌ Invalid stat type selection")
            return False

        stat_type = stat_types[int(choice) - 1]
        filtered = [p for p in self.all_props if p.prop.stat_type == stat_type]

        print(f"\n✓ Found {len(filtered)} {stat_type} props")
        return self._select_from_browse(filtered)

    def _filter_available_props(self, props: List[PropAnalysis]) -> List[PropAnalysis]:
        """Filter out props with players already selected"""
        selected_players = {leg.prop.player_name for leg in self.selected_legs}
        return [p for p in props if p.prop.player_name not in selected_players]

    def _display_selected_legs(self) -> None:
        """Display currently selected legs"""
        print("\n📋 Currently Selected Legs:")
        print("-" * 100)

        table_data = []
        for i, analysis in enumerate(self.selected_legs, 1):
            prop = analysis.prop
            table_data.append([
                i,
                prop.player_name,
                prop.position,
                prop.stat_type,
                f"{prop.line:.1f}",
                prop.direction,
                f"{analysis.final_confidence}%",
                f"{prop.team} vs {prop.opponent}"
            ])

        headers = ["#", "Player", "Pos", "Stat Type", "Line", "Dir", "Conf", "Game"]
        print(tabulate(table_data, headers=headers, tablefmt="simple"))
        print("-" * 100)

    def remove_leg(self, leg_index: int) -> bool:
        """
        Remove a selected leg by index.

        Args:
            leg_index: Index of leg to remove (1-based)

        Returns:
            True if removed, False if invalid index
        """
        if 0 < leg_index <= len(self.selected_legs):
            removed = self.selected_legs.pop(leg_index - 1)
            print(f"✅ Removed: {removed.prop.player_name} {removed.prop.stat_type}")
            return True
        else:
            print(f"❌ Invalid leg index: {leg_index}")
            return False

    def clear_selections(self) -> None:
        """Clear all selected legs"""
        count = len(self.selected_legs)
        self.selected_legs = []
        print(f"✅ Cleared {count} selected legs")

    def analyze_custom_parlay(self) -> Optional[Dict]:
        """
        Analyze the custom parlay using dependency analyzer.

        Returns:
            Analysis results dict with adjusted confidence and recommendation,
            or None if not enough legs selected
        """
        num_legs = len(self.selected_legs)
        if num_legs < 2:
            print(f"❌ Need at least 2 legs selected (currently have {num_legs})")
            return None

        # Create a Parlay object for correlation analysis
        custom_parlay = Parlay(
            legs=self.selected_legs,
            parlay_type=f"{num_legs}-leg",
            risk_level="CUSTOM",
            rationale="Custom user-built parlay",
            correlation_bonus=0
        )

        print("\n" + "=" * 80)
        print(f"🔍 ANALYZING {num_legs}-LEG CUSTOM PARLAY...")
        print("=" * 80)

        # Display selected legs
        self._display_selected_legs()

        # Calculate raw confidence (average of legs)
        raw_confidence = sum(leg.final_confidence for leg in self.selected_legs) / num_legs
        print(f"\n📊 Raw Confidence (average): {raw_confidence:.1f}%")

        # Run correlation analysis
        print("\n🤖 Running correlation analysis with Claude...")
        dependency_analysis = self.dependency_analyzer.analyze_parlay_dependencies(custom_parlay)

        # Extract results
        adjusted_confidence = dependency_analysis.get("adjusted_confidence", raw_confidence)
        correlation_adjustment = dependency_analysis.get("correlation_adjustment", {})
        adjustment_value = correlation_adjustment.get("adjustment_value", 0)
        reasoning = correlation_adjustment.get("reasoning", "No correlation detected")
        recommendation = dependency_analysis.get("recommendation", "REVIEW")

        # Display analysis results
        print("\n" + "=" * 80)
        print("📈 CORRELATION ANALYSIS RESULTS")
        print("=" * 80)
        print(f"Raw Confidence:        {raw_confidence:.1f}%")
        print(f"Correlation Adjust:    {adjustment_value:+.1f}")
        print(f"Adjusted Confidence:   {adjusted_confidence:.1f}%")
        print(f"Recommendation:        {recommendation}")
        print(f"\nReasoning: {reasoning}")
        print("=" * 80)

        # Get individual agent breakdowns
        print("\n" + "=" * 80)
        print("🎯 INDIVIDUAL LEG ANALYSIS")
        print("=" * 80)
        for i, leg in enumerate(self.selected_legs, 1):
            prop = leg.prop
            print(f"\nLeg {i}: {prop.player_name} - {prop.stat_type} {prop.direction} {prop.line}")
            print(f"  Confidence: {leg.final_confidence}%")
            print(f"  Recommendation: {leg.recommendation}")

            # Show top 3 contributing agents
            if leg.agent_breakdown:
                sorted_agents = sorted(
                    leg.agent_breakdown.items(),
                    key=lambda x: x[1].get('raw_score', 0) * x[1].get('weight', 0),
                    reverse=True
                )[:3]

                print("  Top Contributing Agents:")
                for agent_name, agent_data in sorted_agents:
                    score = agent_data.get('raw_score', 0)
                    weight = agent_data.get('weight', 0)
                    print(f"    - {agent_name}: {score:.0f} (weight: {weight:.2f})")

        print("\n" + "=" * 80)

        return {
            "raw_confidence": raw_confidence,
            "adjusted_confidence": adjusted_confidence,
            "correlation_adjustment": adjustment_value,
            "reasoning": reasoning,
            "recommendation": recommendation,
            "dependency_analysis": dependency_analysis
        }

    def save_custom_parlay(self, analysis_results: Dict, payout_odds: int = 1000) -> Optional[str]:
        """
        Save the custom parlay to tracking systems.

        Args:
            analysis_results: Results from analyze_custom_parlay()
            payout_odds: Payout odds for the parlay (varies by leg count)

        Returns:
            parlay_id if saved successfully, None otherwise
        """
        num_legs = len(self.selected_legs)
        if num_legs < 2:
            print(f"❌ Cannot save: need at least 2 legs (have {num_legs})")
            return None

        # Build props list for tracker
        props = []
        for leg in self.selected_legs:
            prop = leg.prop
            props.append({
                "player": prop.player_name,
                "team": prop.team,
                "opponent": prop.opponent,
                "position": prop.position,
                "stat_type": prop.stat_type,
                "line": prop.line,
                "direction": prop.direction,
                "confidence": leg.final_confidence,
                "agent_scores": leg.agent_breakdown
            })

        # Build aggregate agent breakdown for parlay
        # Average each agent's contribution across all legs
        aggregate_breakdown = {}
        for leg in self.selected_legs:
            for agent_name, agent_data in leg.agent_breakdown.items():
                if agent_name not in aggregate_breakdown:
                    aggregate_breakdown[agent_name] = {
                        "raw_scores": [],
                        "weight": agent_data.get('weight', 0)
                    }
                aggregate_breakdown[agent_name]["raw_scores"].append(agent_data.get('raw_score', 0))

        # Calculate average score for each agent
        final_breakdown = {}
        for agent_name, data in aggregate_breakdown.items():
            avg_score = sum(data["raw_scores"]) / len(data["raw_scores"])
            final_breakdown[agent_name] = {
                "raw_score": avg_score,
                "weight": data["weight"]
            }

        # Calculate Kelly bet size (simplified - user can adjust)
        raw_conf = analysis_results["raw_confidence"]
        adj_conf = analysis_results["adjusted_confidence"]
        kelly_bet_size = max(0.5, (adj_conf - 50) / 10)  # Simple Kelly approximation

        # Build correlations list
        correlations = [{
            "type": "custom_parlay_analysis",
            "adjustment": analysis_results["correlation_adjustment"],
            "reasoning": analysis_results["reasoning"]
        }]

        # Save to tracker
        try:
            parlay_id = self.tracker.add_parlay(
                week=self.week,
                year=self.year,
                parlay_type="custom",
                props=props,
                raw_confidence=raw_conf,
                effective_confidence=adj_conf,
                correlations=correlations,
                payout_odds=payout_odds,
                kelly_bet_size=kelly_bet_size,
                data_source="custom_builder",
                agent_breakdown=final_breakdown
            )

            print("\n" + "=" * 80)
            print("✅ CUSTOM PARLAY SAVED SUCCESSFULLY")
            print("=" * 80)
            print(f"Parlay ID: {parlay_id}")
            print(f"Week: {self.week}")
            print(f"Type: CUSTOM")
            print(f"Raw Confidence: {raw_conf:.1f}%")
            print(f"Adjusted Confidence: {adj_conf:.1f}%")
            print(f"Recommended Kelly Bet: {kelly_bet_size:.2f} units")
            print(f"Payout Odds: +{payout_odds}")
            print("=" * 80 + "\n")

            return parlay_id

        except Exception as e:
            logger.error(f"Error saving custom parlay: {e}")
            print(f"❌ Error saving parlay: {e}")
            return None

    def build_parlay_workflow(self) -> Optional[str]:
        """
        Complete workflow for building a custom parlay.

        Returns:
            parlay_id if successfully created and saved, None otherwise
        """
        print("\n" + "=" * 100)
        print(f"🏈 CUSTOM PARLAY BUILDER - Week {self.week}")
        print("=" * 100)
        print(f"Total Props Available: {len(self.all_props)}")
        print("=" * 100 + "\n")

        # Main workflow loop
        while True:
            print("\n" + "=" * 80)
            print(f"📊 PARLAY STATUS: {len(self.selected_legs)} legs selected (2-6 legs supported)")
            print("=" * 80)

            if self.selected_legs:
                self._display_selected_legs()

            # Show menu
            print("\nWhat would you like to do?")
            print("  1. Add leg to parlay")
            print("  2. Remove leg from parlay")
            print("  3. View all available props")
            print("  4. Clear all selections")
            if len(self.selected_legs) >= 2:
                print("  5. Analyze & save parlay (correlation analysis)")
            print("  0. Cancel and exit")

            choice = input("\nEnter choice: ").strip()

            if choice == "1":
                if len(self.selected_legs) >= 6:
                    print("❌ Maximum 6 legs reached. Remove a leg or analyze the parlay.")
                else:
                    self.select_leg_interactive()

            elif choice == "2":
                if not self.selected_legs:
                    print("❌ No legs to remove")
                else:
                    self._display_selected_legs()
                    leg_num = input("\nEnter leg number to remove (or 'c' to cancel): ").strip()
                    if leg_num.isdigit():
                        self.remove_leg(int(leg_num))

            elif choice == "3":
                # Show all props
                self.display_all_props(sort_by="confidence", limit=50)
                input("\nPress Enter to continue...")

            elif choice == "4":
                if self.selected_legs:
                    confirm = input(f"⚠️  Clear all {len(self.selected_legs)} selected legs? (y/n): ").strip().lower()
                    if confirm == 'y':
                        self.clear_selections()
                else:
                    print("❌ No legs to clear")

            elif choice == "5" and len(self.selected_legs) >= 2:
                # Analyze the parlay
                analysis_results = self.analyze_custom_parlay()

                if analysis_results:
                    # Ask if user wants to save
                    save_choice = input("\n💾 Save this custom parlay? (y/n): ").strip().lower()

                    if save_choice == 'y':
                        # Get payout odds with defaults based on leg count
                        num_legs = len(self.selected_legs)
                        default_odds = {2: 260, 3: 600, 4: 1200, 5: 2500, 6: 4000}.get(num_legs, 1000)
                        odds_input = input(f"Enter payout odds (default +{default_odds} for {num_legs}-leg): ").strip()
                        payout_odds = int(odds_input) if odds_input.isdigit() else default_odds

                        parlay_id = self.save_custom_parlay(analysis_results, payout_odds)

                        if parlay_id:
                            # Ask if user wants to build another
                            another = input("\n🔄 Build another custom parlay? (y/n): ").strip().lower()
                            if another != 'y':
                                return parlay_id
                            else:
                                self.clear_selections()
                        else:
                            print("❌ Failed to save parlay")
                    else:
                        print("❌ Parlay not saved")

            elif choice == "0":
                if self.selected_legs:
                    confirm = input("⚠️  Exit without saving? You have unsaved selections. (y/n): ").strip().lower()
                    if confirm == 'y':
                        print("👋 Exiting custom parlay builder...")
                        return None
                else:
                    print("👋 Exiting custom parlay builder...")
                    return None

            else:
                print("❌ Invalid choice")


def run_custom_parlay_builder(analyzed_props: List[PropAnalysis], week: int, year: int = 2024) -> Optional[str]:
    """
    Convenience function to run the custom parlay builder workflow.
    Supports building 2-6 leg custom parlays.

    Args:
        analyzed_props: List of all analyzed props from orchestrator
        week: NFL week number
        year: Year (default 2024)

    Returns:
        parlay_id if parlay was created and saved, None otherwise
    """
    builder = CustomParlayBuilder(analyzed_props, week, year)
    return builder.build_parlay_workflow()
