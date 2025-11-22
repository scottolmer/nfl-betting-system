"""
Natural Language Query Interface for NFL Betting System
Uses Claude Haiku to translate natural language queries into system commands.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from .parlay_tracker import ParlayTracker
from .export_parlays import export_weekly_parlays, preview_weekly_parlays
from .data_loader import NFLDataLoader
from .orchestrator import PropAnalyzer
from .models import PropAnalysis

logger = logging.getLogger(__name__)


# System prompt for Claude Haiku
SYSTEM_PROMPT = """You are a query parser for an NFL betting analysis system.
Your job is to translate natural language queries into structured JSON function calls.

Available functions and their parameters:

1. list_weeks() - Show available weeks with parlays
   Returns: List of weeks

2. get_parlays(week, position, min_confidence, max_confidence, sort_by, limit)
   - week: int (required)
   - position: str (QB, RB, WR, TE) (optional)
   - min_confidence: int (0-100) (optional)
   - max_confidence: int (0-100) (optional)
   - sort_by: str ("confidence", "correlation", "week") (optional, default "confidence")
   - limit: int (optional, default 10)
   Returns: List of parlays matching filters

3. get_all_props(week, position, stat_type, direction, min_confidence, sort_by, limit)
   - week: int (required)
   - position: str (QB, RB, WR, TE) (optional)
   - stat_type: str ("Pass Yards", "Rush Yards", "Receiving Yards", etc.) (optional)
   - direction: str ("OVER", "UNDER") (optional) - filter by bet direction
   - min_confidence: int (0-100) (optional, default 50)
   - sort_by: str ("confidence", "player") (optional, default "confidence")
   - limit: int (optional)
   Returns: List of analyzed props

4. explain_parlay(parlay_id)
   - parlay_id: str (required) - The parlay identifier
   Returns: Detailed breakdown of parlay with correlation analysis

5. show_agent_breakdown(player_name, stat_type)
   - player_name: str (required)
   - stat_type: str (optional) - specific prop type
   Returns: Agent scores and reasoning for player props

6. export_parlays(week, preview)
   - week: int (required)
   - preview: bool (optional, default False) - preview without saving
   Returns: Export status or preview

7. help() - Show available commands and examples
   Returns: Help text

System context:
- 8 agents analyze each prop: DVOA, Matchup, Volume, Injury, Trend, GameScript, Variance, Weather
- Prop types: Pass Yards, Pass TDs, Rush Yards, Rush TDs, Receptions, Receiving Yards, Receiving TDs
- Positions: QB, RB, WR, TE, K
- Bet directions: OVER and UNDER (both are fully supported and tracked)
  * OVER bets: Predict player will go OVER the line
  * UNDER bets: Predict player will stay UNDER the line
  * Confidence scores work the same for both (0-100, typically 60-75 for good bets)
  * System tracks and analyzes UNDER bets just like OVER bets
- Parlays: 2-6 leg combinations with correlation-adjusted confidence
- Parlay types: "traditional", "enhanced", "custom", "generated"
- IMPORTANT: Users can filter by bet direction (OVER, UNDER, or both)

Instructions:
1. Parse the user's query and return a JSON object with "function" and "params" keys
2. If query is ambiguous, return a JSON with "clarification" key asking for details
3. For follow-up queries referring to previous results, use context from conversation history
4. If user asks for help or doesn't know what to do, return help() function
5. Always return valid JSON only, no extra text

Example responses:
{"function": "get_parlays", "params": {"week": 12, "position": "QB", "sort_by": "confidence", "limit": 5}}
{"function": "get_all_props", "params": {"week": 12, "min_confidence": 70}}
{"function": "get_all_props", "params": {"week": 12, "direction": "UNDER", "min_confidence": 60}}
{"function": "get_all_props", "params": {"week": 12, "position": "QB", "direction": "OVER"}}
{"function": "explain_parlay", "params": {"parlay_id": "TRAD_W12_abc123_v1"}}
{"clarification": "Which week would you like to see parlays for? (1-18)"}
{"function": "help", "params": {}}
"""


class NLQueryInterface:
    """Natural language query interface using Claude Haiku"""

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the query interface.

        Args:
            data_dir: Directory containing NFL data
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package required. Install with: pip install anthropic")

        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.conversation_history: List[Dict[str, str]] = []
        self.tracker = ParlayTracker()
        self.data_loader = NFLDataLoader(data_dir=data_dir)
        self.data_dir = Path(data_dir)

        # Cache for loaded data
        self.cached_week = None
        self.cached_props = None

    def translate_query(self, user_input: str) -> Dict:
        """
        Use Claude Haiku to translate natural language to structured command.

        Args:
            user_input: User's natural language query

        Returns:
            Dict with function name and parameters, or clarification request
        """
        # Build messages with conversation history
        messages = self.conversation_history + [
            {"role": "user", "content": user_input}
        ]

        try:
            response = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=500,
                system=SYSTEM_PROMPT,
                messages=messages
            )

            # Parse JSON from response
            response_text = response.content[0].text.strip()

            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            command = json.loads(response_text)
            return command

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Haiku response: {e}")
            return {"error": "Failed to understand query. Please rephrase."}
        except Exception as e:
            logger.error(f"Error translating query: {e}")
            return {"error": f"Translation error: {str(e)}"}

    def execute_command(self, command: Dict) -> str:
        """
        Execute the structured command on backend.

        Args:
            command: Parsed command with function and params

        Returns:
            Formatted result string
        """
        # Handle errors
        if "error" in command:
            return f"[ERROR] {command['error']}"

        # Handle clarification requests
        if "clarification" in command:
            return command["clarification"]

        function = command.get("function")
        params = command.get("params", {})

        try:
            if function == "list_weeks":
                return self._list_weeks()
            elif function == "get_parlays":
                return self._get_parlays(**params)
            elif function == "get_all_props":
                return self._get_all_props(**params)
            elif function == "explain_parlay":
                return self._explain_parlay(**params)
            elif function == "show_agent_breakdown":
                return self._show_agent_breakdown(**params)
            elif function == "export_parlays":
                return self._export_parlays(**params)
            elif function == "help":
                return self._show_help()
            else:
                return f"[ERROR] Unknown function: {function}"

        except Exception as e:
            logger.error(f"Error executing {function}: {e}")
            return f"[ERROR] {str(e)}"

    def _list_weeks(self) -> str:
        """List available weeks with parlays"""
        weeks = self.tracker.data.get('metadata', {}).get('weeks_tracked', [])
        if not weeks:
            return "No weeks with parlays found. Run analysis first."

        return f"Available weeks with parlays: {', '.join(map(str, sorted(weeks)))}"

    def _get_parlays(
        self,
        week: int,
        position: Optional[str] = None,
        min_confidence: Optional[int] = None,
        max_confidence: Optional[int] = None,
        sort_by: str = "confidence",
        limit: int = 10
    ) -> str:
        """Get parlays with filters"""
        parlays = self.tracker.get_parlays_by_week(week)

        if not parlays:
            return f"No parlays found for week {week}"

        # Apply filters
        filtered = parlays

        if position:
            # Filter parlays that have at least one prop of this position
            filtered = [
                p for p in filtered
                if any(prop.get('position', '').upper() == position.upper()
                      for prop in p.get('props', []))
            ]

        if min_confidence:
            filtered = [p for p in filtered if p.get('effective_confidence', 0) >= min_confidence]

        if max_confidence:
            filtered = [p for p in filtered if p.get('effective_confidence', 100) <= max_confidence]

        # Sort
        if sort_by == "confidence":
            filtered.sort(key=lambda p: p.get('effective_confidence', 0), reverse=True)
        elif sort_by == "week":
            filtered.sort(key=lambda p: p.get('week', 0))

        # Limit
        filtered = filtered[:limit]

        if not filtered:
            return f"No parlays match your filters for week {week}"

        # Format output
        lines = [f"\nFound {len(filtered)} parlays for week {week}:\n"]
        lines.append("=" * 80)

        for i, parlay in enumerate(filtered, 1):
            parlay_id = parlay.get('parlay_id', 'N/A')
            parlay_type = parlay.get('parlay_type', 'unknown')
            confidence = parlay.get('effective_confidence', 0)
            num_legs = len(parlay.get('props', []))
            was_bet = "[BET]" if parlay.get('bet_on', False) else ""

            lines.append(f"\n{i}. Parlay ID: {parlay_id} {was_bet}")
            lines.append(f"   Type: {parlay_type} | {num_legs} legs | Confidence: {confidence:.1f}%")

            # Show legs
            for j, prop in enumerate(parlay.get('props', [])[:3], 1):  # Show first 3 legs
                player = prop.get('player', 'Unknown')
                stat = prop.get('stat_type', 'Unknown')
                line = prop.get('line', 0)
                direction = prop.get('direction', 'OVER')
                lines.append(f"   Leg {j}: {player} {stat} {direction} {line}")

            if num_legs > 3:
                lines.append(f"   ... and {num_legs - 3} more legs")

        lines.append("\n" + "=" * 80)
        return "\n".join(lines)

    def _get_all_props(
        self,
        week: int,
        position: Optional[str] = None,
        stat_type: Optional[str] = None,
        direction: Optional[str] = None,
        min_confidence: int = 50,
        sort_by: str = "confidence",
        limit: Optional[int] = None
    ) -> str:
        """Get all analyzed props for a week"""
        # Load data if not cached
        if self.cached_week != week or self.cached_props is None:
            print(f"Loading props for week {week}...")
            context = self.data_loader.load_all_data(week=week)
            analyzer = PropAnalyzer()
            self.cached_props = analyzer.analyze_all_props(context, min_confidence=min_confidence)
            self.cached_week = week

        props = self.cached_props

        # Apply filters
        if position:
            props = [p for p in props if p.prop.position.upper() == position.upper()]

        if stat_type:
            props = [p for p in props if stat_type.lower() in p.prop.stat_type.lower()]

        if direction:
            props = [p for p in props if p.prop.direction.upper() == direction.upper()]

        # Sort
        if sort_by == "confidence":
            props.sort(key=lambda p: p.final_confidence, reverse=True)
        elif sort_by == "player":
            props.sort(key=lambda p: p.prop.player_name)

        # Limit
        if limit:
            props = props[:limit]

        if not props:
            return "No props match your filters"

        # Format output
        lines = [f"\nFound {len(props)} props:\n"]
        lines.append("=" * 80)

        for i, analysis in enumerate(props, 1):
            prop = analysis.prop
            lines.append(f"\n{i}. {prop.player_name} ({prop.position}) - {prop.team} vs {prop.opponent}")
            lines.append(f"   {prop.stat_type} {prop.direction} {prop.line} | Confidence: {analysis.final_confidence}%")
            lines.append(f"   Recommendation: {analysis.recommendation}")

        lines.append("\n" + "=" * 80)
        return "\n".join(lines)

    def _explain_parlay(self, parlay_id: str) -> str:
        """Explain a specific parlay"""
        parlay = self.tracker.get_parlay_by_id(parlay_id)

        if not parlay:
            return f"Parlay {parlay_id} not found"

        # Format detailed explanation
        lines = [f"\n{'=' * 80}"]
        lines.append(f"PARLAY ANALYSIS: {parlay_id}")
        lines.append(f"{'=' * 80}\n")

        lines.append(f"Type: {parlay.get('parlay_type', 'unknown')}")
        lines.append(f"Week: {parlay.get('week', 'N/A')}")
        lines.append(f"Raw Confidence: {parlay.get('raw_confidence', 0):.1f}%")
        lines.append(f"Effective Confidence: {parlay.get('effective_confidence', 0):.1f}%")
        lines.append(f"Was Bet On: {'Yes' if parlay.get('bet_on', False) else 'No'}")

        # Correlations
        correlations = parlay.get('correlations', [])
        if correlations:
            lines.append(f"\nCorrelation Adjustments:")
            for corr in correlations:
                adj = corr.get('adjustment', 0)
                reason = corr.get('reasoning', 'N/A')
                lines.append(f"  {adj:+.1f}: {reason}")

        # Legs
        lines.append(f"\nLegs ({len(parlay.get('props', []))}):")
        for i, prop in enumerate(parlay.get('props', []), 1):
            player = prop.get('player', 'Unknown')
            stat = prop.get('stat_type', 'Unknown')
            line = prop.get('line', 0)
            direction = prop.get('direction', 'OVER')
            conf = prop.get('confidence', 0)
            lines.append(f"\n  Leg {i}: {player}")
            lines.append(f"    {stat} {direction} {line}")
            lines.append(f"    Confidence: {conf}%")

        lines.append(f"\n{'=' * 80}")
        return "\n".join(lines)

    def _show_agent_breakdown(self, player_name: str, stat_type: Optional[str] = None) -> str:
        """Show agent breakdown for a player"""
        # Find player in cached props or load from tracker
        if not self.cached_props:
            return "No props loaded. Try searching for props first with 'get all props for week X'"

        # Find matching props
        matches = [
            p for p in self.cached_props
            if player_name.lower() in p.prop.player_name.lower()
        ]

        if stat_type:
            matches = [
                p for p in matches
                if stat_type.lower() in p.prop.stat_type.lower()
            ]

        if not matches:
            return f"No props found for {player_name}"

        # Show agent breakdown for first match
        analysis = matches[0]
        prop = analysis.prop

        lines = [f"\n{'=' * 80}"]
        lines.append(f"AGENT BREAKDOWN: {prop.player_name}")
        lines.append(f"{'=' * 80}\n")

        lines.append(f"Prop: {prop.stat_type} {prop.direction} {prop.line}")
        lines.append(f"Team: {prop.team} vs {prop.opponent}")
        lines.append(f"Final Confidence: {analysis.final_confidence}%")
        lines.append(f"Recommendation: {analysis.recommendation}\n")

        lines.append("Agent Scores:")
        lines.append("-" * 80)

        for agent_name, agent_data in analysis.agent_breakdown.items():
            score = agent_data.get('raw_score', 0)
            weight = agent_data.get('weight', 0)
            lines.append(f"  {agent_name:15s}: {score:3.0f}/100  (weight: {weight:.2f})")

        lines.append("\nTop Contributing Agents:")
        for agent_name, contribution in analysis.top_contributing_agents[:3]:
            lines.append(f"  {agent_name}: {contribution:.1f}% contribution")

        lines.append(f"\n{'=' * 80}")
        return "\n".join(lines)

    def _export_parlays(self, week: int, preview: bool = False) -> str:
        """Export parlays for a week"""
        if preview:
            preview_weekly_parlays(week)
            return f"Preview displayed for week {week}"
        else:
            filepath = export_weekly_parlays(week, overwrite=True)
            if filepath:
                return f"[SUCCESS] Exported to {filepath}"
            else:
                return "[ERROR] Export failed"

    def _show_help(self) -> str:
        """Show help text"""
        help_text = """
NFL BETTING SYSTEM - NATURAL LANGUAGE INTERFACE

You can ask questions in plain English. Here are some examples:

VIEWING DATA:
  - "Show me parlays for week 12"
  - "Get the top 5 QB parlays"
  - "What props are available for Josh Allen?"
  - "Show all props with confidence over 70%"
  - "Show me UNDER bets for week 12"
  - "What OVER bets do we have for RBs?"

FILTERING & SORTING:
  - "Show only UNDER bets"
  - "Filter to OVER bets only"
  - "Show only home games"
  - "Filter to RBs and WRs"
  - "Sort by correlation"
  - "Show me the best parlays"
  - "Show QB UNDERs with confidence over 65"

ANALYSIS:
  - "Why is parlay TRAD_W12_abc123 rated 68%?"
  - "Show agent breakdown for Patrick Mahomes"
  - "What are the correlation concerns?"
  - "Show me high confidence UNDER bets"

ACTIONS:
  - "Export parlays for week 12"
  - "Preview export for week 11"
  - "List available weeks"

FOLLOW-UP QUESTIONS:
  - "Now filter to only UNDER bets"
  - "What about OVER bets?"
  - "Show me details on that one"

IMPORTANT: Both OVER and UNDER bets are fully supported and tracked!
  - OVER bets predict player stats will go OVER the line
  - UNDER bets predict player stats will stay UNDER the line
  - Confidence scores work the same way for both (0-100)

Type 'exit' or 'quit' to end the session.
"""
        return help_text

    def run(self):
        """Main chat loop"""
        print("\n" + "=" * 80)
        print("NFL BETTING SYSTEM - NATURAL LANGUAGE INTERFACE")
        print("=" * 80)
        print("\nAsk questions in plain English. Type 'help' for examples, 'exit' to quit.\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\nGoodbye!\n")
                    break

                # Translate query with Haiku
                print("Thinking...")
                command = self.translate_query(user_input)

                # Execute command
                result = self.execute_command(command)

                # Display result
                print(f"\n{result}\n")

                # Update conversation history (limit to last 10 exchanges)
                self.conversation_history.append({"role": "user", "content": user_input})
                self.conversation_history.append({"role": "assistant", "content": result})

                if len(self.conversation_history) > 20:  # Keep last 10 exchanges
                    self.conversation_history = self.conversation_history[-20:]

            except KeyboardInterrupt:
                print("\n\n[CANCELLED] Session ended by user\n")
                break
            except Exception as e:
                print(f"\n[ERROR] {e}\n")
                logger.error(f"Chat loop error: {e}")


def run_chat_interface(data_dir: str = "data"):
    """
    Convenience function to run the chat interface.

    Args:
        data_dir: Directory containing NFL data
    """
    interface = NLQueryInterface(data_dir=data_dir)
    interface.run()
