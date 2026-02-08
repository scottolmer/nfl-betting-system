"""
Suggestion Engine for Betting Assistant
Generates contextual follow-up suggestions based on conversation state
"""

from typing import List, Dict, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SuggestionCategory(Enum):
    """Categories of suggestions"""
    ANALYSIS = "analysis"
    REFINEMENT = "refinement"
    HISTORICAL = "historical"
    EXPORT = "export"
    COMPARISON = "comparison"
    HELP = "help"


class SuggestionEngine:
    """Generates contextual follow-up suggestions"""

    def __init__(self):
        self.suggestion_templates = self._init_templates()

    def _init_templates(self) -> Dict:
        """Initialize suggestion templates"""
        return {
            # After data loaded
            'data_loaded': [
                ("Analyze props with default threshold", SuggestionCategory.ANALYSIS),
                ("Analyze props with 70% confidence threshold", SuggestionCategory.ANALYSIS),
                ("Check data quality", SuggestionCategory.ANALYSIS),
            ],

            # After props analyzed
            'props_analyzed': [
                ("Build parlays from these props", SuggestionCategory.ANALYSIS),
                ("Show top 10 props", SuggestionCategory.ANALYSIS),
                ("Explain why a specific prop is recommended", SuggestionCategory.ANALYSIS),
                ("Filter by position (QB, RB, WR, TE)", SuggestionCategory.REFINEMENT),
            ],

            # After parlays built
            'parlays_built': [
                ("Compare these to system recommendations", SuggestionCategory.COMPARISON),
                ("Show correlation analysis", SuggestionCategory.ANALYSIS),
                ("Check historical performance of similar parlays", SuggestionCategory.HISTORICAL),
                ("Export parlays to database", SuggestionCategory.EXPORT),
                ("Refine parlays (exclude players, adjust constraints)", SuggestionCategory.REFINEMENT),
            ],

            # After player excluded
            'player_excluded': [
                ("Rebuild parlays with this exclusion", SuggestionCategory.REFINEMENT),
                ("Show all excluded players for this platform", SuggestionCategory.ANALYSIS),
                ("Create a constraint rule for similar exclusions", SuggestionCategory.REFINEMENT),
            ],

            # After parlay explanation
            'parlay_explained': [
                ("Compare to other parlays", SuggestionCategory.COMPARISON),
                ("Check correlation risk", SuggestionCategory.ANALYSIS),
                ("See historical performance", SuggestionCategory.HISTORICAL),
            ],

            # General context-aware suggestions
            'has_week_context': [
                ("How did the previous week perform?", SuggestionCategory.HISTORICAL),
                ("Compare this week to previous week", SuggestionCategory.COMPARISON),
            ],
        }

    def generate_suggestions(self, conversation_state: Dict, max_suggestions: int = 3) -> List[Dict]:
        """
        Generate contextual suggestions based on conversation state

        Args:
            conversation_state: Dict containing:
                - has_props: bool
                - has_parlays: bool
                - has_week: bool
                - week: int
                - excluded_players_count: int
                - last_intent: str
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of suggestion dicts with 'text', 'category', 'priority'
        """
        suggestions = []

        # Determine context
        has_props = conversation_state.get('has_props', False)
        has_parlays = conversation_state.get('has_parlays', False)
        has_week = conversation_state.get('has_week', False)
        week = conversation_state.get('week')
        excluded_count = conversation_state.get('excluded_players_count', 0)
        last_intent = conversation_state.get('last_intent')

        # Generate suggestions based on state
        if has_parlays:
            suggestions.extend(self._generate_from_template('parlays_built', priority=10))
        elif has_props:
            suggestions.extend(self._generate_from_template('props_analyzed', priority=8))
        elif has_week:
            suggestions.extend(self._generate_from_template('data_loaded', priority=6))

        # Add intent-specific suggestions
        if last_intent == 'exclude_player':
            suggestions.extend(self._generate_from_template('player_excluded', priority=9))
        elif last_intent == 'explain_prop':
            suggestions.extend(self._generate_from_template('parlay_explained', priority=7))

        # Add week-aware suggestions
        if week and week > 1:
            suggestions.extend(self._generate_from_template('has_week_context', priority=5))

        # Add platform-specific suggestions
        if excluded_count > 0:
            suggestions.append({
                'text': f"Review {excluded_count} excluded players",
                'category': SuggestionCategory.REFINEMENT.value,
                'priority': 6
            })

        # Sort by priority (descending) and limit
        suggestions.sort(key=lambda x: x['priority'], reverse=True)
        return suggestions[:max_suggestions]

    def _generate_from_template(self, template_key: str, priority: int) -> List[Dict]:
        """Generate suggestions from a template"""
        templates = self.suggestion_templates.get(template_key, [])
        return [
            {
                'text': text,
                'category': category.value,
                'priority': priority
            }
            for text, category in templates
        ]

    def format_suggestions_for_display(self, suggestions: List[Dict]) -> str:
        """Format suggestions for conversational display"""
        if not suggestions:
            return ""

        lines = ["", "What would you like to do next?"]
        for i, sug in enumerate(suggestions, 1):
            lines.append(f"  {i}. {sug['text']}")

        return "\n".join(lines)

    def generate_proactive_insight(self, conversation_state: Dict) -> Optional[str]:
        """
        Generate proactive insights based on patterns

        Args:
            conversation_state: Current conversation state

        Returns:
            Insight string or None
        """
        has_parlays = conversation_state.get('has_parlays', False)
        parlay_count = conversation_state.get('parlay_count', 0)
        excluded_count = conversation_state.get('excluded_players_count', 0)
        platform = conversation_state.get('platform', 'pick6')

        insights = []

        # Insight 1: Multiple exclusions suggest pattern
        if excluded_count >= 3:
            insights.append(
                f"[INSIGHT] You've excluded {excluded_count} players for {platform}. "
                f"Consider creating a constraint rule to auto-apply these exclusions."
            )

        # Insight 2: High parlay count
        if parlay_count > 8:
            insights.append(
                f"[INSIGHT] You have {parlay_count} parlays. "
                f"Consider filtering to your highest-confidence picks to reduce decision fatigue."
            )

        # Insight 3: Correlation warning
        if has_parlays:
            insights.append(
                "[TIP] Check correlation risk before betting. "
                "Same-game parlays have higher variance."
            )

        # Return first insight
        return insights[0] if insights else None

    def suggest_pattern_rule(self, pattern_data: Dict) -> str:
        """
        Generate suggestion text for creating a pattern-based rule

        Args:
            pattern_data: Dict with 'pattern_type', 'occurrences', 'details'

        Returns:
            Suggestion text
        """
        pattern_type = pattern_data.get('pattern_type')
        occurrences = pattern_data.get('occurrences', 0)
        details = pattern_data.get('details', {})

        if pattern_type == 'repeated_prop_type_exclusion':
            prop_type = details.get('prop_type', 'Unknown')
            return (
                f"[PATTERN DETECTED] You've excluded {prop_type} props {occurrences} times. "
                f"Would you like to create a rule to auto-filter {prop_type} for future queries?"
            )

        elif pattern_type == 'minimum_line_threshold':
            min_line = details.get('min_line', 0)
            return (
                f"[PATTERN DETECTED] You've excluded props with lines below {min_line} "
                f"{occurrences} times. Create a minimum line threshold rule?"
            )

        elif pattern_type == 'position_preference':
            positions = details.get('positions', [])
            return (
                f"[PATTERN DETECTED] You prefer {', '.join(positions)} props. "
                f"Should I prioritize these positions by default?"
            )

        return "[PATTERN DETECTED] Would you like to create a constraint rule based on this pattern?"

    def generate_comparison_suggestions(self, parlay_count: int) -> List[str]:
        """Generate suggestions for comparing parlays"""
        suggestions = []

        if parlay_count > 1:
            suggestions.append("Compare 2-leg vs 3-leg vs 4-leg parlay performance")
            suggestions.append("Show parlays with highest expected value")
            suggestions.append("Compare correlation risk across all parlays")

        if parlay_count > 3:
            suggestions.append("Filter parlays by risk level (LOW/MODERATE/HIGH)")

        return suggestions

    def generate_historical_suggestions(self, week: int, has_parlays: bool) -> List[str]:
        """Generate suggestions for historical queries"""
        suggestions = []

        if week > 1:
            suggestions.append(f"How did Week {week - 1} parlays perform?")
            suggestions.append(f"Compare Week {week} props to Week {week - 1}")

        if has_parlays:
            suggestions.append("Check historical hit rate for similar parlays")
            suggestions.append("Show which agent predictions were most accurate")

        suggestions.append("What's the season ROI so far?")

        return suggestions

    def generate_export_suggestions(self, parlay_count: int) -> List[str]:
        """Generate suggestions for exporting results"""
        suggestions = []

        if parlay_count > 0:
            suggestions.append("Save parlays to database")
            suggestions.append("Export parlays as formatted text")
            suggestions.append("Generate betting card (PDF)")

        return suggestions

    def categorize_suggestions(self, suggestions: List[Dict]) -> Dict[str, List[Dict]]:
        """Group suggestions by category"""
        categorized = {}
        for sug in suggestions:
            category = sug['category']
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(sug)

        return categorized


if __name__ == "__main__":
    # Test suggestion engine
    engine = SuggestionEngine()

    # Test scenario 1: Parlays built
    print("\n" + "="*70)
    print("TEST 1: After Building Parlays")
    print("="*70)
    state = {
        'has_props': True,
        'has_parlays': True,
        'has_week': True,
        'week': 15,
        'parlay_count': 8,
        'excluded_players_count': 2,
        'last_intent': 'build_parlay',
        'platform': 'pick6'
    }
    suggestions = engine.generate_suggestions(state, max_suggestions=5)
    print(engine.format_suggestions_for_display(suggestions))

    # Test scenario 2: Props analyzed
    print("\n" + "="*70)
    print("TEST 2: After Analyzing Props")
    print("="*70)
    state = {
        'has_props': True,
        'has_parlays': False,
        'has_week': True,
        'week': 15,
        'last_intent': 'analyze_props'
    }
    suggestions = engine.generate_suggestions(state, max_suggestions=4)
    print(engine.format_suggestions_for_display(suggestions))

    # Test scenario 3: Proactive insight
    print("\n" + "="*70)
    print("TEST 3: Proactive Insights")
    print("="*70)
    state = {
        'has_parlays': True,
        'parlay_count': 12,
        'excluded_players_count': 4,
        'platform': 'pick6'
    }
    insight = engine.generate_proactive_insight(state)
    if insight:
        print(insight)

    # Test scenario 4: Pattern rule suggestion
    print("\n" + "="*70)
    print("TEST 4: Pattern Rule Suggestion")
    print("="*70)
    pattern = {
        'pattern_type': 'repeated_prop_type_exclusion',
        'occurrences': 5,
        'details': {'prop_type': 'Pass TDs'}
    }
    suggestion = engine.suggest_pattern_rule(pattern)
    print(suggestion)

    print("\n" + "="*70)
