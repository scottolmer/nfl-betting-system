"""
Betting Assistant Agent - Main Conversational Interface
Natural language wrapper for NFL betting analysis system
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import json

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.assistant.conversation_manager import ConversationManager, Intent
from scripts.assistant.constraint_engine import ConstraintEngine
from scripts.assistant.csv_handler import CSVHandler
from scripts.assistant.suggestion_engine import SuggestionEngine
from scripts.assistant.skill_integrator import SkillIntegrator
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.parlay_builder import ParlayBuilder
from scripts.analysis.data_loader import NFLDataLoader

logger = logging.getLogger(__name__)


class BettingAssistantAgent:
    """Main conversational agent for NFL betting analysis"""

    def __init__(self, db_path: str = "bets.db", user_id: str = "default"):
        self.conversation = ConversationManager(db_path=db_path, user_id=user_id)
        self.constraints = ConstraintEngine(db_path=db_path)
        self.csv_handler = CSVHandler()
        self.suggestions = SuggestionEngine()  # NEW: Phase 3
        self.skills = SkillIntegrator()  # NEW: Phase 3
        self.db_path = db_path

        # Analysis components
        self.analyzer = None  # Initialized on-demand
        self.parlay_builder = ParlayBuilder()

        logger.info("Betting Assistant Agent initialized (Phase 3 enabled)")

    def process_message(self, user_message: str) -> str:
        """
        Process user message and return conversational response

        Args:
            user_message: User's input message

        Returns:
            Assistant's response text
        """
        # Detect intent
        intent, params = self.conversation.detect_intent(user_message)

        logger.info(f"Intent: {intent.value}, Params: {params}")

        # Route to appropriate handler
        if intent == Intent.UPLOAD_DATA:
            response = self._handle_upload_data(params)
        elif intent == Intent.DATA_STATUS:
            response = self._handle_data_status(params)
        elif intent == Intent.ANALYZE_PROPS:
            response = self._handle_analyze_props(params)
        elif intent == Intent.BUILD_PARLAY:
            response = self._handle_build_parlay(params)
        elif intent == Intent.EXCLUDE_PLAYER:
            response = self._handle_exclude_player(params, user_message)
        elif intent == Intent.REFINE_PARLAY:
            response = self._handle_refine_parlay(params)
        elif intent == Intent.EXPLAIN_PROP:
            response = self._handle_explain_prop(params, user_message)
        elif intent == Intent.HISTORICAL_QUERY:
            response = self._handle_historical_query(params, user_message)
        elif intent == Intent.COMPARE_PARLAYS:
            response = self._handle_compare_parlays(params)
        else:
            response = self._handle_general_question(user_message)

        # NEW: Phase 3 - Add proactive suggestions to response
        response = self._add_suggestions_to_response(response, intent)

        # Save conversation
        self.conversation.add_message(user_message, response, intent)

        return response

    def _handle_upload_data(self, params: Dict) -> str:
        """Handle data upload/loading"""
        week = params.get('week') or self.conversation.current_week

        if not week:
            return ("I'll need to know which week you want to analyze. "
                   "Please specify a week number (e.g., 'Load week 15 data')")

        # Process files
        success, message, context = self.csv_handler.process_files(week=week)

        if success:
            self.conversation.set_current_week(week)
            self.conversation.set_current_props(context.get('props', []))
            return message
        else:
            return f"Failed to load data:\n{message}"

    def _handle_data_status(self, params: Dict) -> str:
        """Handle data status query"""
        if not self.csv_handler.last_context:
            return "No data loaded yet. Upload CSV files or specify a week to analyze."

        context = self.csv_handler.last_context
        validation = self.csv_handler.loader.get_validation_status(context)

        lines = [
            f"Data Status for Week {validation['week']}:",
            f"  Props: {validation['props_count']}",
            f"  DVOA teams: {validation['dvoa_teams']}",
            f"  Injuries: {'Loaded' if validation['injuries_loaded'] else 'Not loaded'}",
            f"  Source: {validation['betting_lines_source']}"
        ]

        if validation['warnings']:
            lines.append("\nWarnings:")
            for warning in validation['warnings']:
                lines.append(f"  - {warning}")

        # Add constraint info
        if self.conversation.excluded_players:
            lines.append(f"\nExcluded players: {', '.join(self.conversation.get_excluded_players())}")

        return "\n".join(lines)

    def _handle_analyze_props(self, params: Dict) -> str:
        """Handle prop analysis request"""
        # Check if data is loaded
        if not self.csv_handler.last_context:
            week = params.get('week')
            if week:
                # Auto-load data
                success, message, context = self.csv_handler.process_files(week=week)
                if not success:
                    return f"Failed to load data for week {week}:\n{message}"
                self.conversation.set_current_week(week)
                self.conversation.set_current_props(context.get('props', []))
            else:
                return "No data loaded. Please specify a week to analyze or upload data first."

        context = self.csv_handler.last_context
        week = context.get('week')

        # Get user preferences
        prefs = self.conversation.get_user_preferences()
        threshold = params.get('confidence_threshold') or prefs['confidence_threshold']

        # Apply constraints
        props = context.get('props', [])
        platform = prefs.get('platform', 'pick6')

        # Get excluded players from conversation + constraints engine
        excluded_players = self.conversation.get_excluded_players()
        excluded_players.extend(self.constraints.get_excluded_players(platform))

        # Initialize analyzer
        self.analyzer = PropAnalyzer(db_path=self.db_path)

        # Analyze props
        logger.info(f"Analyzing {len(props)} props with threshold {threshold}%")
        analyses = self.analyzer.analyze_all_props(
            context=context,
            min_confidence=threshold,
            exclude_players=excluded_players
        )

        # Save to conversation
        self.conversation.set_current_props([
            PropAnalyzer.prop_analysis_to_dict(a) for a in analyses
        ])

        # Format response
        response_lines = [
            f"Analyzing {len(props)} props with 9 agents... Done!",
            f"Found {len(analyses)} high-confidence props (>={threshold}%).",
            ""
        ]

        if len(analyses) == 0:
            response_lines.append("No props met the confidence threshold.")
            response_lines.append("Try lowering the threshold or checking data quality.")
        else:
            response_lines.append("Top 5 props:")
            for i, analysis in enumerate(analyses[:5], 1):
                prop = analysis.prop
                bet_type = getattr(prop, 'bet_type', 'OVER')
                response_lines.append(
                    f"  {i}. {prop.player_name} ({prop.team}) - "
                    f"{prop.stat_type} {bet_type} {prop.line} - "
                    f"{analysis.final_confidence}% confidence"
                )

            response_lines.append("")
            response_lines.append("What would you like to do next?")
            response_lines.append("  - Build parlays from these props")
            response_lines.append("  - Exclude specific players")
            response_lines.append("  - See more details on a specific prop")

        return "\n".join(response_lines)

    def _handle_build_parlay(self, params: Dict) -> str:
        """Handle parlay building request"""
        # Check if props are analyzed
        if not self.conversation.current_props:
            return ("No props analyzed yet. Please analyze props first "
                   "(e.g., 'Analyze props for week 15')")

        # Get analyzed props from conversation
        prop_dicts = self.conversation.current_props

        # Need to reconstruct PropAnalysis objects
        # For simplicity, re-run analysis if needed
        if not self.csv_handler.last_context:
            return "Please re-analyze props before building parlays."

        context = self.csv_handler.last_context
        prefs = self.conversation.get_user_preferences()
        threshold = prefs['confidence_threshold']

        # Get excluded players
        platform = prefs.get('platform', 'pick6')
        excluded_players = self.conversation.get_excluded_players()
        excluded_players.extend(self.constraints.get_excluded_players(platform))

        # Re-analyze with exclusions
        if not self.analyzer:
            self.analyzer = PropAnalyzer(db_path=self.db_path)

        analyses = self.analyzer.analyze_all_props(
            context=context,
            min_confidence=threshold,
            exclude_players=excluded_players
        )

        if len(analyses) == 0:
            return "No props available to build parlays. Try lowering the confidence threshold."

        # Build parlays
        logger.info(f"Building parlays from {len(analyses)} props")
        parlays = self.parlay_builder.build_parlays(
            all_analyses=analyses,
            min_confidence=threshold
        )

        # Save to conversation
        self.conversation.set_current_parlays(
            ParlayBuilder.parlays_to_dict(parlays)
        )

        # Format response
        total_parlays = sum(len(p) for p in parlays.values())

        response_lines = [
            f"Built {total_parlays} optimized parlays from {len(analyses)} props:",
            ""
        ]

        # Show summary of each parlay type
        for leg_type, parlay_list in parlays.items():
            if parlay_list:
                response_lines.append(f"{leg_type} parlays: {len(parlay_list)}")

        response_lines.append("")

        # Show top 3 parlays
        all_parlays = []
        for leg_type in ['2-leg', '3-leg', '4-leg', '5-leg']:
            all_parlays.extend(parlays.get(leg_type, []))

        if all_parlays:
            response_lines.append("Top 3 parlays:")
            for i, parlay in enumerate(all_parlays[:3], 1):
                response_lines.append(
                    f"\nPARLAY #{i} ({parlay.parlay_type}, {parlay.combined_confidence}% confidence, {parlay.risk_level} risk)"
                )
                for j, leg in enumerate(parlay.legs, 1):
                    bet_type = getattr(leg.prop, 'bet_type', 'OVER')
                    response_lines.append(
                        f"  {j}. {leg.prop.player_name} {leg.prop.stat_type} "
                        f"{bet_type} {leg.prop.line} ({leg.final_confidence}%)"
                    )

        response_lines.append("")

        # Add Pick6 note if applicable
        if platform == 'pick6' and excluded_players:
            response_lines.append(
                f"[NOTE] Excluded {len(excluded_players)} players for Pick6 availability"
            )

        response_lines.append("")
        response_lines.append("What would you like to do next?")
        response_lines.append("  - Refine parlays (exclude players, change constraints)")
        response_lines.append("  - See detailed analysis for a specific parlay")
        response_lines.append("  - Save parlays to database")

        return "\n".join(response_lines)

    def _handle_exclude_player(self, params: Dict, user_message: str) -> str:
        """Handle player exclusion"""
        player_name = params.get('player')

        # Simple name extraction if not in params
        if not player_name:
            # Extract from message (basic heuristic)
            words = user_message.split()
            for i, word in enumerate(words):
                if word.lower() in ['exclude', 'remove', 'not']:
                    # Next 1-2 words might be player name
                    if i + 1 < len(words):
                        player_name = ' '.join(words[i+1:i+3])
                        break

        if not player_name:
            return "Please specify which player to exclude (e.g., 'Exclude Patrick Mahomes')"

        # Get platform
        prefs = self.conversation.get_user_preferences()
        platform = prefs.get('platform', 'pick6')

        # Check if Pick6 mentioned
        if 'pick6' in user_message.lower() or 'pick 6' in user_message.lower():
            platform = 'pick6'

        # Mark as unavailable
        self.constraints.mark_player_unavailable(
            player_name=player_name,
            platform=platform,
            source="user",
            notes=f"Excluded via conversation: {user_message[:100]}"
        )

        # Add to conversation context
        self.conversation.add_excluded_player(player_name)

        response_lines = [
            f"Excluded {player_name} from {platform} parlays.",
            f"[CHECK] Recorded: {player_name} unavailable in {platform}",
        ]

        # If parlays exist, offer to rebuild
        if self.conversation.current_parlays:
            response_lines.append("")
            response_lines.append("Would you like me to rebuild parlays with this exclusion?")

        return "\n".join(response_lines)

    def _handle_refine_parlay(self, params: Dict) -> str:
        """Handle parlay refinement"""
        if not self.conversation.current_parlays:
            return "No parlays to refine. Please build parlays first."

        # Rebuild parlays with current exclusions
        return self._handle_build_parlay(params)

    def _handle_explain_prop(self, params: Dict, user_message: str) -> str:
        """Handle explanation request for a prop"""
        if not self.conversation.current_props:
            return "No props analyzed yet. Please analyze props first."

        # Simple heuristic: try to find prop by player name in message
        props = self.conversation.current_props

        # Extract player name (basic)
        for prop in props:
            player = prop.get('player_name', '')
            if player.lower() in user_message.lower():
                # Found matching prop - NEW: Enhanced Phase 3 explanation
                response_lines = [
                    f"=== {player} ({prop.get('team')}) vs {prop.get('opponent')} ===",
                    f"{prop.get('stat_type')} {prop.get('bet_type')} {prop.get('line')}",
                    f"",
                    f"OVERALL CONFIDENCE: {prop.get('confidence')}%",
                    f"",
                    "WHY THIS PROP:",
                    prop.get('edge_explanation', 'No explanation available'),
                    "",
                    "AGENT BREAKDOWN:"
                ]

                # Enhanced agent breakdown with details
                agent_breakdown = prop.get('agent_breakdown', {})
                for agent, data in sorted(agent_breakdown.items(),
                                         key=lambda x: x[1].get('raw_score', 0), reverse=True)[:5]:
                    score = data.get('raw_score', 50)
                    weight = data.get('weight', 0)
                    direction = data.get('direction', 'neutral')

                    # Add interpretation
                    if score >= 70:
                        strength = "Strong"
                    elif score >= 60:
                        strength = "Good"
                    elif score >= 50:
                        strength = "Slight"
                    else:
                        strength = "Weak"

                    response_lines.append(
                        f"  {agent:12s}: {score}/100 (weight: {weight:.2f}) - "
                        f"{strength} {direction} signal"
                    )

                # Add rationale if available
                rationale = prop.get('rationale', [])
                if rationale:
                    response_lines.append("")
                    response_lines.append("KEY FACTORS:")
                    for i, reason in enumerate(rationale[:3], 1):
                        response_lines.append(f"  {i}. {reason}")

                return "\n".join(response_lines)

        return ("I couldn't find a specific prop to explain in your message. "
               "Try asking about a specific player (e.g., 'Why is Mahomes OVER 287.5 good?')")

    def _handle_historical_query(self, params: Dict, user_message: str) -> str:
        """Handle historical performance query"""
        # NEW: Phase 3 - Skill Integration
        week = params.get('week')

        # Detect query type
        if any(word in user_message.lower() for word in ['perform', 'results', 'outcome']):
            # Invoke performance reporter
            if week:
                result = self.skills.invoke_performance_reporter(week=week)
            else:
                result = self.skills.invoke_performance_reporter()
            return result
        else:
            # Invoke chat-query for general historical questions
            result = self.skills.invoke_chat_query(user_message)
            return result

    def _handle_compare_parlays(self, params: Dict) -> str:
        """Handle parlay comparison"""
        if not self.conversation.current_parlays:
            return "No parlays to compare. Please build parlays first."

        parlays_dict = self.conversation.current_parlays
        total = sum(len(p) for p in parlays_dict.values())

        response_lines = [
            f"Comparing {total} generated parlays:",
            "",
            "By leg count:"
        ]

        for leg_type in ['2-leg', '3-leg', '4-leg', '5-leg']:
            parlay_list = parlays_dict.get(leg_type, [])
            if parlay_list:
                avg_conf = sum(p['combined_confidence'] for p in parlay_list) / len(parlay_list)
                response_lines.append(
                    f"  {leg_type}: {len(parlay_list)} parlays, avg confidence: {avg_conf:.1f}%"
                )

        return "\n".join(response_lines)

    def _handle_general_question(self, user_message: str) -> str:
        """Handle general questions"""
        return (
            "I'm your NFL betting assistant. I can help you:\n"
            "  - Analyze props for a week\n"
            "  - Build optimized parlays\n"
            "  - Exclude players (e.g., for Pick6)\n"
            "  - Explain prop recommendations\n"
            "  - Check data status\n\n"
            "Try asking:\n"
            "  - 'What are the best parlays for week 15?'\n"
            "  - 'Exclude Mahomes - not available in Pick6'\n"
            "  - 'Why is this prop good?'"
        )

    def get_context_summary(self) -> str:
        """Get summary of current conversation context"""
        return self.conversation.get_context_summary()

    def _add_suggestions_to_response(self, response: str, intent: Intent) -> str:
        """
        Add proactive suggestions to response (Phase 3 feature)

        Args:
            response: Base response text
            intent: Intent that was just handled

        Returns:
            Response with suggestions appended
        """
        # Build conversation state for suggestion engine
        state = {
            'has_props': self.conversation.current_props is not None,
            'has_parlays': self.conversation.current_parlays is not None,
            'has_week': self.conversation.current_week is not None,
            'week': self.conversation.current_week,
            'parlay_count': sum(len(p) for p in self.conversation.current_parlays.values()) if self.conversation.current_parlays else 0,
            'excluded_players_count': len(self.conversation.get_excluded_players()),
            'last_intent': intent.value,
            'platform': self.conversation.get_user_preferences().get('platform', 'pick6')
        }

        # Generate suggestions
        suggestions = self.suggestions.generate_suggestions(state, max_suggestions=3)

        if suggestions:
            # Add suggestions to response
            suggestion_text = self.suggestions.format_suggestions_for_display(suggestions)
            response += "\n" + suggestion_text

        # Add proactive insight if applicable
        insight = self.suggestions.generate_proactive_insight(state)
        if insight:
            response += "\n\n" + insight

        return response


if __name__ == "__main__":
    # Test betting assistant
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--message', type=str, default="What are the best parlays for week 15?")
    args = parser.parse_args()

    assistant = BettingAssistantAgent()

    print("\n" + "="*70)
    print("NFL BETTING ASSISTANT - CONVERSATIONAL INTERFACE")
    print("="*70 + "\n")

    # Process message
    response = assistant.process_message(args.message)

    print(f"User: {args.message}")
    print(f"\nAssistant:\n{response}")
    print("\n" + "="*70)
