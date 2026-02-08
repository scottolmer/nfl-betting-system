"""
Constraint Engine for Betting Assistant
Manages Pick6 availability tracking, constraint rules, and pattern learning
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import logging
import uuid

logger = logging.getLogger(__name__)


class ConstraintType:
    """Constraint rule types"""
    PLAYER_UNAVAILABLE = "player_unavailable"
    PROP_TYPE_EXCLUDED = "prop_type_excluded"
    PLATFORM_SPECIFIC = "platform_specific"
    MIN_LINE_THRESHOLD = "min_line_threshold"
    MAX_LINE_THRESHOLD = "max_line_threshold"


class ConstraintEngine:
    """Manages constraints and Pick6 availability learning"""

    def __init__(self, db_path: str = "bets.db"):
        self.db_path = db_path
        self.exclusion_cache = {}  # Platform -> set of player names
        self.rule_cache = {}  # Rule ID -> rule data
        self.pattern_history = defaultdict(list)  # Track user patterns

    def mark_player_unavailable(self, player_name: str, prop_type: str = None,
                                platform: str = "pick6", source: str = "user",
                                notes: str = None):
        """
        Mark a player/prop as unavailable on a platform

        Args:
            player_name: Player name
            prop_type: Specific prop type (e.g., "Pass Yds") or None for all props
            platform: Platform name (default: pick6)
            source: Source of information (user, scraper, pattern)
            notes: Additional notes
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Use wildcard for all prop types
            prop_type_key = prop_type or "*"

            cursor.execute("""
                INSERT OR REPLACE INTO pick6_availability
                (player_name, prop_type, platform, is_available, confidence,
                 last_updated, source, notes)
                VALUES (?, ?, ?, 0, 1.0, ?, ?, ?)
            """, (
                player_name.strip(),
                prop_type_key,
                platform,
                datetime.now().isoformat(),
                source,
                notes
            ))

            conn.commit()
            conn.close()

            # Update cache
            cache_key = platform
            if cache_key not in self.exclusion_cache:
                self.exclusion_cache[cache_key] = set()
            self.exclusion_cache[cache_key].add(player_name.strip())

            logger.info(f"Marked {player_name} as unavailable on {platform}")

        except Exception as e:
            logger.error(f"Failed to mark player unavailable: {e}")

    def is_player_available(self, player_name: str, prop_type: str = None,
                           platform: str = "pick6") -> Tuple[bool, Optional[str]]:
        """
        Check if a player/prop is available on a platform

        Returns:
            (is_available, reason) tuple
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check exact match and wildcard
            cursor.execute("""
                SELECT is_available, source, notes
                FROM pick6_availability
                WHERE player_name = ? AND platform = ?
                  AND (prop_type = ? OR prop_type = '*')
                ORDER BY last_updated DESC
                LIMIT 1
            """, (player_name.strip(), platform, prop_type or "*"))

            row = cursor.fetchone()
            conn.close()

            if row:
                is_available = bool(row[0])
                reason = f"Marked unavailable by {row[1]}"
                if row[2]:
                    reason += f" ({row[2]})"
                return is_available, None if is_available else reason

        except Exception as e:
            logger.error(f"Failed to check player availability: {e}")

        # Default to available if no record
        return True, None

    def get_excluded_players(self, platform: str = "pick6") -> List[str]:
        """Get list of excluded players for a platform"""
        # Check cache first
        if platform in self.exclusion_cache:
            return list(self.exclusion_cache[platform])

        # Load from database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DISTINCT player_name
                FROM pick6_availability
                WHERE platform = ? AND is_available = 0
            """, (platform,))

            players = [row[0] for row in cursor.fetchall()]
            conn.close()

            # Update cache
            self.exclusion_cache[platform] = set(players)
            return players

        except Exception as e:
            logger.error(f"Failed to get excluded players: {e}")
            return []

    def create_constraint_rule(self, rule_type: str, rule_data: Dict,
                              platform: str = "pick6", auto_apply: bool = True) -> str:
        """
        Create a constraint rule

        Args:
            rule_type: Type of constraint (from ConstraintType)
            rule_data: Rule parameters (JSON-serializable dict)
            platform: Platform to apply rule to
            auto_apply: Whether to automatically apply this rule

        Returns:
            Rule ID
        """
        try:
            rule_id = str(uuid.uuid4())
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO constraint_rules
                (rule_id, rule_type, rule_data, platform, auto_apply, created_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                rule_id,
                rule_type,
                json.dumps(rule_data),
                platform,
                1 if auto_apply else 0,
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()

            # Update cache
            self.rule_cache[rule_id] = {
                'rule_type': rule_type,
                'rule_data': rule_data,
                'platform': platform,
                'auto_apply': auto_apply
            }

            logger.info(f"Created constraint rule: {rule_type} for {platform}")
            return rule_id

        except Exception as e:
            logger.error(f"Failed to create constraint rule: {e}")
            return None

    def get_active_rules(self, platform: str = "pick6") -> List[Dict]:
        """Get all active constraint rules for a platform"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT rule_id, rule_type, rule_data, times_applied
                FROM constraint_rules
                WHERE platform = ? AND auto_apply = 1
            """, (platform,))

            rules = []
            for row in cursor.fetchall():
                rules.append({
                    'rule_id': row[0],
                    'rule_type': row[1],
                    'rule_data': json.loads(row[2]),
                    'times_applied': row[3]
                })

            conn.close()
            return rules

        except Exception as e:
            logger.error(f"Failed to get active rules: {e}")
            return []

    def apply_constraints_to_props(self, props: List[Dict], platform: str = "pick6") -> Tuple[List[Dict], List[str]]:
        """
        Apply constraints to filter props

        Returns:
            (filtered_props, exclusion_reasons) tuple
        """
        filtered = []
        reasons = []

        # Get excluded players
        excluded_players = set(p.lower() for p in self.get_excluded_players(platform))

        # Get active rules
        active_rules = self.get_active_rules(platform)

        for prop in props:
            player_name = prop.get('player_name', '').strip()
            prop_type = prop.get('stat_type', '')
            line = prop.get('line', 0)

            # Check player exclusion
            if player_name.lower() in excluded_players:
                reasons.append(f"Excluded {player_name} (unavailable on {platform})")
                continue

            # Check rule constraints
            excluded = False
            for rule in active_rules:
                rule_type = rule['rule_type']
                rule_data = rule['rule_data']

                if rule_type == ConstraintType.PROP_TYPE_EXCLUDED:
                    if prop_type in rule_data.get('excluded_types', []):
                        reasons.append(f"Excluded {prop_type} (rule: {rule['rule_id'][:8]})")
                        excluded = True
                        break

                elif rule_type == ConstraintType.MIN_LINE_THRESHOLD:
                    min_line = rule_data.get('min_line', 0)
                    if line < min_line:
                        reasons.append(f"Excluded {player_name} {prop_type} (line {line} < {min_line})")
                        excluded = True
                        break

                elif rule_type == ConstraintType.MAX_LINE_THRESHOLD:
                    max_line = rule_data.get('max_line', 999)
                    if line > max_line:
                        reasons.append(f"Excluded {player_name} {prop_type} (line {line} > {max_line})")
                        excluded = True
                        break

            if not excluded:
                filtered.append(prop)

        return filtered, reasons

    def record_pattern(self, platform: str, pattern_type: str, data: Dict):
        """Record a user behavior pattern for learning"""
        self.pattern_history[platform].append({
            'timestamp': datetime.now().isoformat(),
            'pattern_type': pattern_type,
            'data': data
        })

    def detect_patterns(self, platform: str = "pick6", min_occurrences: int = 3) -> List[Dict]:
        """
        Detect recurring patterns in user behavior

        Returns:
            List of detected patterns with suggested rules
        """
        patterns = self.pattern_history.get(platform, [])
        if len(patterns) < min_occurrences:
            return []

        suggestions = []

        # Pattern 1: Repeatedly excluded prop types
        prop_type_exclusions = defaultdict(int)
        for pattern in patterns:
            if pattern['pattern_type'] == 'prop_type_exclusion':
                prop_type = pattern['data'].get('prop_type')
                if prop_type:
                    prop_type_exclusions[prop_type] += 1

        for prop_type, count in prop_type_exclusions.items():
            if count >= min_occurrences:
                suggestions.append({
                    'pattern': 'repeated_prop_type_exclusion',
                    'prop_type': prop_type,
                    'occurrences': count,
                    'suggested_rule': {
                        'rule_type': ConstraintType.PROP_TYPE_EXCLUDED,
                        'rule_data': {'excluded_types': [prop_type]},
                        'reason': f"You've excluded {prop_type} props {count} times"
                    }
                })

        # Pattern 2: Minimum line preferences
        line_exclusions = []
        for pattern in patterns:
            if pattern['pattern_type'] == 'line_exclusion':
                line = pattern['data'].get('line')
                if line:
                    line_exclusions.append(line)

        if len(line_exclusions) >= min_occurrences:
            min_excluded = min(line_exclusions)
            suggestions.append({
                'pattern': 'minimum_line_threshold',
                'min_line': min_excluded,
                'occurrences': len(line_exclusions),
                'suggested_rule': {
                    'rule_type': ConstraintType.MIN_LINE_THRESHOLD,
                    'rule_data': {'min_line': min_excluded},
                    'reason': f"You've excluded props with lines below {min_excluded}"
                }
            })

        return suggestions

    def get_exclusion_summary(self, platform: str = "pick6") -> Dict:
        """Get summary of exclusions for a platform"""
        excluded_players = self.get_excluded_players(platform)
        active_rules = self.get_active_rules(platform)

        return {
            'platform': platform,
            'excluded_players_count': len(excluded_players),
            'excluded_players': excluded_players,
            'active_rules_count': len(active_rules),
            'active_rules': active_rules
        }

    def calculate_pattern_confidence(self, pattern_data: Dict, total_interactions: int) -> float:
        """
        Calculate confidence score for a detected pattern

        Args:
            pattern_data: Pattern detection data
            total_interactions: Total number of user interactions

        Returns:
            Confidence score (0.0 to 1.0)
        """
        occurrences = pattern_data.get('occurrences', 0)
        pattern_type = pattern_data.get('pattern')

        # Base confidence on frequency
        frequency_ratio = occurrences / max(total_interactions, 1)

        # Weight different pattern types
        pattern_weights = {
            'repeated_prop_type_exclusion': 0.9,  # High confidence
            'minimum_line_threshold': 0.7,  # Medium confidence
            'position_preference': 0.6,  # Lower confidence
        }

        weight = pattern_weights.get(pattern_type, 0.5)

        # Calculate confidence
        confidence = min(1.0, frequency_ratio * 10 * weight)  # Scale up frequency

        # Boost if occurrences are high
        if occurrences >= 5:
            confidence = min(1.0, confidence * 1.2)

        return round(confidence, 2)

    def detect_position_preferences(self, platform: str = "pick6") -> List[Dict]:
        """
        Detect user preferences for specific positions

        Returns:
            List of position preference patterns
        """
        patterns = self.pattern_history.get(platform, [])
        if not patterns:
            return []

        position_counts = defaultdict(int)

        # Count position interactions
        for pattern in patterns:
            if pattern['pattern_type'] == 'position_focus':
                position = pattern['data'].get('position')
                if position:
                    position_counts[position] += 1

        # Find strong preferences (> 30% of interactions)
        total = sum(position_counts.values())
        preferences = []

        for position, count in position_counts.items():
            ratio = count / max(total, 1)
            if ratio > 0.3:  # 30% threshold
                preferences.append({
                    'pattern': 'position_preference',
                    'position': position,
                    'occurrences': count,
                    'preference_ratio': round(ratio, 2),
                    'confidence': round(ratio, 2)
                })

        return preferences

    def auto_apply_pattern_rule(self, pattern_data: Dict, platform: str = "pick6",
                                confidence_threshold: float = 0.8) -> Optional[str]:
        """
        Auto-apply a pattern as a constraint rule if confidence is high

        Args:
            pattern_data: Detected pattern data
            platform: Platform to apply rule to
            confidence_threshold: Minimum confidence to auto-apply

        Returns:
            Rule ID if created, None otherwise
        """
        # Calculate confidence
        confidence = pattern_data.get('confidence', 0.0)

        if confidence < confidence_threshold:
            logger.info(f"Pattern confidence {confidence} below threshold {confidence_threshold}")
            return None

        # Extract rule from pattern
        suggested_rule = pattern_data.get('suggested_rule')
        if not suggested_rule:
            return None

        # Create the rule
        rule_id = self.create_constraint_rule(
            rule_type=suggested_rule['rule_type'],
            rule_data=suggested_rule['rule_data'],
            platform=platform,
            auto_apply=True
        )

        logger.info(f"Auto-applied pattern rule: {rule_id}")
        return rule_id

    def analyze_exclusion_trends(self, platform: str = "pick6",
                                 time_window_days: int = 30) -> Dict:
        """
        Analyze exclusion trends over time

        Args:
            platform: Platform to analyze
            time_window_days: Number of days to analyze

        Returns:
            Trend analysis dict
        """
        from datetime import datetime, timedelta

        patterns = self.pattern_history.get(platform, [])
        if not patterns:
            return {'trend': 'no_data'}

        # Filter to time window
        cutoff = datetime.now() - timedelta(days=time_window_days)
        recent_patterns = [
            p for p in patterns
            if datetime.fromisoformat(p['timestamp']) > cutoff
        ]

        if not recent_patterns:
            return {'trend': 'no_recent_data'}

        # Analyze trends
        prop_type_exclusions = defaultdict(int)
        for p in recent_patterns:
            if p['pattern_type'] == 'prop_type_exclusion':
                prop_type = p['data'].get('prop_type')
                if prop_type:
                    prop_type_exclusions[prop_type] += 1

        # Determine trend
        total_exclusions = sum(prop_type_exclusions.values())
        avg_per_week = total_exclusions / max(time_window_days / 7, 1)

        return {
            'trend': 'increasing' if avg_per_week > 5 else 'stable',
            'total_exclusions': total_exclusions,
            'avg_per_week': round(avg_per_week, 1),
            'most_excluded': dict(sorted(prop_type_exclusions.items(),
                                        key=lambda x: x[1], reverse=True)[:3])
        }


if __name__ == "__main__":
    # Test constraint engine
    logging.basicConfig(level=logging.INFO)

    engine = ConstraintEngine()

    # Test marking player unavailable
    engine.mark_player_unavailable("Patrick Mahomes", platform="pick6",
                                  source="user", notes="User feedback Week 15")

    # Test availability check
    is_avail, reason = engine.is_player_available("Patrick Mahomes", platform="pick6")
    print(f"\nPatrick Mahomes available: {is_avail}")
    if reason:
        print(f"Reason: {reason}")

    # Test getting excluded players
    excluded = engine.get_excluded_players("pick6")
    print(f"\nExcluded players: {excluded}")

    # Test constraint rule
    rule_id = engine.create_constraint_rule(
        rule_type=ConstraintType.PROP_TYPE_EXCLUDED,
        rule_data={'excluded_types': ['Pass TDs']},
        platform="pick6"
    )
    print(f"\nCreated rule: {rule_id}")

    # Test pattern detection
    engine.record_pattern("pick6", "prop_type_exclusion", {'prop_type': 'Pass TDs'})
    engine.record_pattern("pick6", "prop_type_exclusion", {'prop_type': 'Pass TDs'})
    engine.record_pattern("pick6", "prop_type_exclusion", {'prop_type': 'Pass TDs'})

    patterns = engine.detect_patterns("pick6", min_occurrences=3)
    print(f"\nDetected patterns: {len(patterns)}")
    for p in patterns:
        print(f"  - {p['pattern']}: {p.get('suggested_rule', {}).get('reason')}")
