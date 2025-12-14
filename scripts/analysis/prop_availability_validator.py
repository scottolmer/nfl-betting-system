"""
Prop Availability Validator - Hybrid rule-based and learned filtering system
Handles filtering props that aren't available on DraftKings Pick6
"""

from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
import sqlite3
import json
import logging
from .models import PropAnalysis, PlayerProp

logger = logging.getLogger(__name__)


@dataclass
class ValidationRule:
    """Represents an invalid prop combination rule"""
    rule_id: str
    description: str
    rule_type: str  # 'same_player_props', 'stat_correlation', 'platform_restriction'
    conditions: Dict  # Flexible dict for different rule types
    auto_applied: bool = True  # If False, only suggests rejection


class PropAvailabilityValidator:
    """
    Validates prop availability using both rules and learned patterns

    Features:
    1. Rule-based filtering (e.g., same player can't have UNDER completions + UNDER receptions)
    2. Learning from manual validations
    3. Interactive validation workflow
    4. Minimum threshold filtering (e.g., receptions must be > 2.5)
    """

    # Minimum thresholds for prop types (DraftKings typically doesn't offer props below these values)
    MINIMUM_THRESHOLDS = {
        "Receptions": 2.5,
        "Rush Att": 3.5,
        "Completions": 14.5,
        "Pass Att": 19.5,
        "Rec Yds": 19.5,
        "Rush Yds": 19.5,
        "Pass Yds": 149.5,
    }

    def __init__(self, db_path: str = "bets.db", min_thresholds: Dict[str, float] = None):
        self.db_path = db_path
        # Allow custom thresholds to be passed in, otherwise use defaults
        if min_thresholds:
            self.min_thresholds = {**self.MINIMUM_THRESHOLDS, **min_thresholds}
        else:
            self.min_thresholds = self.MINIMUM_THRESHOLDS.copy()
        self._init_database()
        self._load_default_rules()

    def _init_database(self):
        """Initialize validation database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Table: Validation rules (both default and learned)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prop_validation_rules (
                rule_id TEXT PRIMARY KEY,
                description TEXT,
                rule_type TEXT,
                conditions TEXT,
                auto_applied INTEGER DEFAULT 1,
                created_date TEXT,
                times_triggered INTEGER DEFAULT 0
            )
        """)

        # Table: Prop availability tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prop_availability (
                prop_signature TEXT PRIMARY KEY,
                player_name TEXT,
                prop_type TEXT,
                bet_type TEXT,
                is_available INTEGER,
                last_validated TEXT,
                validation_source TEXT,
                notes TEXT
            )
        """)

        # Table: Parlay validation history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parlay_validation_history (
                validation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                parlay_signature TEXT,
                props_json TEXT,
                is_valid INTEGER,
                invalid_reason TEXT,
                validated_date TEXT,
                week INTEGER
            )
        """)

        conn.commit()
        conn.close()

    def _load_default_rules(self):
        """Load default rules into database if not already present"""
        default_rules = [
            ValidationRule(
                rule_id="same_player_under_completions_receptions",
                description="Same player: UNDER completions + UNDER receptions (QB/WR/TE correlation)",
                rule_type="same_player_props",
                conditions={
                    "player": "same",
                    "bet_types": ["UNDER", "UNDER"],
                    "prop_types": ["Completions", "Receptions"]
                },
                auto_applied=True
            ),
            ValidationRule(
                rule_id="same_player_under_passing_completions",
                description="Same player: UNDER passing yards + UNDER completions",
                rule_type="same_player_props",
                conditions={
                    "player": "same",
                    "bet_types": ["UNDER", "UNDER"],
                    "prop_types": ["Pass Yds", "Completions"]
                },
                auto_applied=True
            ),
            ValidationRule(
                rule_id="same_player_under_rushing_attempts",
                description="Same player: UNDER rushing yards + UNDER rushing attempts",
                rule_type="same_player_props",
                conditions={
                    "player": "same",
                    "bet_types": ["UNDER", "UNDER"],
                    "prop_types": ["Rush Yds", "Rush Att"]
                },
                auto_applied=True
            ),
            ValidationRule(
                rule_id="same_player_under_receiving_receptions",
                description="Same player: UNDER receiving yards + UNDER receptions",
                rule_type="same_player_props",
                conditions={
                    "player": "same",
                    "bet_types": ["UNDER", "UNDER"],
                    "prop_types": ["Rec Yds", "Receptions"]
                },
                auto_applied=True
            ),
        ]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for rule in default_rules:
            cursor.execute("""
                INSERT OR IGNORE INTO prop_validation_rules
                (rule_id, description, rule_type, conditions, auto_applied, created_date)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, (
                rule.rule_id,
                rule.description,
                rule.rule_type,
                json.dumps(rule.conditions),
                1 if rule.auto_applied else 0
            ))

        conn.commit()
        conn.close()

    def validate_parlay_props(self, props: List[PropAnalysis]) -> Tuple[bool, List[str]]:
        """
        Validate if all props in a parlay are available

        Args:
            props: List of PropAnalysis objects

        Returns:
            Tuple of (is_valid, list of violation reasons)
        """
        violations = []

        # Check against rules
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT rule_id, description, rule_type, conditions, auto_applied FROM prop_validation_rules")
        rules = cursor.fetchall()
        conn.close()

        for rule_id, description, rule_type, conditions_json, auto_applied in rules:
            if not auto_applied:
                continue

            conditions = json.loads(conditions_json)

            if rule_type == "same_player_props":
                violation = self._check_same_player_rule(props, conditions, description)
                if violation:
                    violations.append(violation)

        return (len(violations) == 0, violations)

    def _check_same_player_rule(self, props: List[PropAnalysis], conditions: Dict, description: str) -> Optional[str]:
        """Check if props violate a same-player rule"""
        if conditions.get("player") != "same":
            return None

        # Group props by player
        player_props: Dict[str, List[PropAnalysis]] = {}
        for prop_analysis in props:
            player = prop_analysis.prop.player_name
            if player not in player_props:
                player_props[player] = []
            player_props[player].append(prop_analysis)

        # Check each player's props
        for player, player_prop_list in player_props.items():
            if len(player_prop_list) < 2:
                continue

            # Get prop types and bet types
            prop_types = conditions.get("prop_types", [])
            bet_types = conditions.get("bet_types", [])

            # Check if this player has the forbidden combination
            found_props = []
            for target_prop_type in prop_types:
                for prop_analysis in player_prop_list:
                    if self._normalize_prop_type(prop_analysis.prop.stat_type) == self._normalize_prop_type(target_prop_type):
                        found_props.append(prop_analysis)
                        break

            if len(found_props) == len(prop_types):
                # Check bet types match
                actual_bet_types = [p.prop.bet_type for p in found_props]
                if self._bet_types_match(actual_bet_types, bet_types):
                    prop_desc = " + ".join([f"{p.prop.stat_type} {p.prop.bet_type}" for p in found_props])
                    return f"❌ {player}: {prop_desc} ({description})"

        return None

    def _normalize_prop_type(self, prop_type: str) -> str:
        """Normalize prop type for comparison"""
        # Handle variations like "Pass Yds", "Passing Yards", "PassingYards"
        normalized = prop_type.lower().replace(" ", "").replace("_", "")

        # Map common variations
        mappings = {
            "passyds": "passingyards",
            "passyards": "passingyards",
            "rushyds": "rushingyards",
            "rushyards": "rushingyards",
            "recyds": "receivingyards",
            "recyards": "receivingyards",
            "receivingyds": "receivingyards",
            "rushatt": "rushingattempts",
            "rushattempts": "rushingattempts",
        }

        return mappings.get(normalized, normalized)

    def _bet_types_match(self, actual: List[str], expected: List[str]) -> bool:
        """Check if bet types match (allowing for order independence)"""
        if len(actual) != len(expected):
            return False

        # Sort both lists for comparison
        return sorted([b.upper() for b in actual]) == sorted([b.upper() for b in expected])

    def mark_prop_available(self, prop: PlayerProp, is_available: bool, notes: str = ""):
        """Manually mark a prop as available or not"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        prop_signature = self._get_prop_signature(prop)

        cursor.execute("""
            INSERT OR REPLACE INTO prop_availability
            (prop_signature, player_name, prop_type, bet_type, is_available, last_validated, validation_source, notes)
            VALUES (?, ?, ?, ?, ?, datetime('now'), 'manual', ?)
        """, (
            prop_signature,
            prop.player_name,
            prop.stat_type,
            prop.bet_type,
            1 if is_available else 0,
            notes
        ))

        conn.commit()
        conn.close()

    def add_custom_rule(self, description: str, rule_type: str, conditions: Dict, auto_applied: bool = True):
        """Add a new validation rule based on manual observation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Generate rule ID
        rule_id = f"custom_{rule_type}_{len(description.split())}"

        cursor.execute("""
            INSERT INTO prop_validation_rules
            (rule_id, description, rule_type, conditions, auto_applied, created_date)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (
            rule_id,
            description,
            rule_type,
            json.dumps(conditions),
            1 if auto_applied else 0
        ))

        conn.commit()
        conn.close()

        logger.info(f"✅ Added custom rule: {description}")

    def _get_prop_signature(self, prop: PlayerProp) -> str:
        """Generate unique signature for a prop"""
        return f"{prop.player_name}|{prop.stat_type}|{prop.bet_type}|{prop.line}"

    def filter_available_props(self, props: List[PropAnalysis]) -> List[PropAnalysis]:
        """
        Filter props based on known availability

        Returns only props that haven't been marked as unavailable
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        available_props = []
        for prop_analysis in props:
            prop_signature = self._get_prop_signature(prop_analysis.prop)

            cursor.execute("""
                SELECT is_available FROM prop_availability
                WHERE prop_signature = ?
            """, (prop_signature,))

            result = cursor.fetchone()
            if result is None:
                # Unknown availability - include it
                available_props.append(prop_analysis)
            elif result[0] == 1:
                # Marked as available
                available_props.append(prop_analysis)
            # else: marked as unavailable, skip it

        conn.close()
        return available_props

    def filter_by_minimum_thresholds(self, props: List[PropAnalysis], verbose: bool = True) -> List[PropAnalysis]:
        """
        Filter props that don't meet minimum thresholds for their stat type

        Args:
            props: List of PropAnalysis objects
            verbose: Whether to print filtering information

        Returns:
            List of props that meet minimum threshold requirements
        """
        filtered_props = []
        filtered_count = 0
        filtered_details = []

        for prop_analysis in props:
            prop = prop_analysis.prop
            stat_type = prop.stat_type
            line = prop.line

            # Check if this stat type has a minimum threshold
            if stat_type in self.min_thresholds:
                min_threshold = self.min_thresholds[stat_type]

                if line < min_threshold:
                    filtered_count += 1
                    filtered_details.append(
                        f"  ❌ {prop.player_name} - {stat_type} {prop.line} "
                        f"(below minimum {min_threshold})"
                    )
                    continue  # Skip this prop

            # Prop meets threshold or has no threshold requirement
            filtered_props.append(prop_analysis)

        if verbose and filtered_count > 0:
            logger.info(f"\n🔍 Filtered {filtered_count} props below minimum thresholds:")
            for detail in filtered_details[:10]:  # Show first 10
                logger.info(detail)
            if len(filtered_details) > 10:
                logger.info(f"  ... and {len(filtered_details) - 10} more")
            logger.info(f"✅ {len(filtered_props)} props remaining after threshold filter\n")

        return filtered_props

    def get_validation_stats(self) -> Dict:
        """Get statistics about validation rules and history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM prop_validation_rules")
        total_rules = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM prop_availability WHERE is_available = 1")
        available_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM prop_availability WHERE is_available = 0")
        unavailable_count = cursor.fetchone()[0]

        conn.close()

        return {
            "total_rules": total_rules,
            "props_marked_available": available_count,
            "props_marked_unavailable": unavailable_count
        }
