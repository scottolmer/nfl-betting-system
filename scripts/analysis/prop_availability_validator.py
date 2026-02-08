"""
Prop Availability Validator - Hybrid rule-based and learned filtering system
Handles filtering props that aren't available on DraftKings Pick6
"""

from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
import json
import logging
from datetime import datetime
from sqlalchemy import func
from api.database import SessionLocal, PropAvailability, PropValidationRule, ParlayValidationHistory, init_db
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

    def __init__(self, db_path: str = None, min_thresholds: Dict[str, float] = None):
        # db_path is ignored now, using shared DB
        if min_thresholds:
            self.min_thresholds = {**self.MINIMUM_THRESHOLDS, **min_thresholds}
        else:
            self.min_thresholds = self.MINIMUM_THRESHOLDS.copy()
            
        init_db()  # Ensure tables exist
        self._load_default_rules()

    def get_session(self):
        return SessionLocal()

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

        session = self.get_session()
        try:
            for rule in default_rules:
                # Check if exists
                existing = session.query(PropValidationRule).filter_by(rule_id=rule.rule_id).first()
                if not existing:
                    new_rule = PropValidationRule(
                        rule_id=rule.rule_id,
                        description=rule.description,
                        rule_type=rule.rule_type,
                        conditions=rule.conditions, # SQLAlchemy handles JSON serialization
                        auto_applied=rule.auto_applied,
                        created_date=datetime.now()
                    )
                    session.add(new_rule)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error loading default rules: {e}")
        finally:
            session.close()

    def validate_parlay_props(self, props: List[PropAnalysis]) -> Tuple[bool, List[str]]:
        """
        Validate if all props in a parlay are available
        """
        violations = []
        session = self.get_session()
        
        try:
            # Check against rules
            rules = session.query(PropValidationRule).all()
            
            for rule in rules:
                if not rule.auto_applied:
                    continue

                if rule.rule_type == "same_player_props":
                    # rule.conditions is already a dict if using JSON type
                    conditions = rule.conditions if isinstance(rule.conditions, dict) else (json.loads(rule.conditions) if rule.conditions else {})
                    
                    violation = self._check_same_player_rule(props, conditions, rule.description)
                    if violation:
                        violations.append(violation)
                        
                        # Update times_triggered
                        rule.times_triggered += 1
                        session.add(rule)
            
            session.commit()
            return (len(violations) == 0, violations)
            
        except Exception as e:
            logger.error(f"Error validating parlay: {e}")
            return (True, []) # Default to valid on error to not block
        finally:
            session.close()

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
        session = self.get_session()
        try:
            prop_signature = self._get_prop_signature(prop)
            
            # Upsert logic
            existing = session.query(PropAvailability).filter_by(id=prop_signature).first()
            if existing:
                existing.is_available = is_available
                existing.last_updated = datetime.now()
                existing.validation_source = 'manual'
                existing.notes = notes
            else:
                new_prop = PropAvailability(
                    id=prop_signature,
                    player=prop.player_name,
                    prop_type=prop.stat_type,
                    bet_type=prop.bet_type,
                    line=prop.line,
                    is_available=is_available,
                    last_updated=datetime.now(),
                    validation_source='manual',
                    notes=notes
                )
                session.add(new_prop)
            
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error marking prop availability: {e}")
        finally:
            session.close()

    def add_custom_rule(self, description: str, rule_type: str, conditions: Dict, auto_applied: bool = True):
        """Add a new validation rule based on manual observation"""
        session = self.get_session()
        try:
            # Generate rule ID
            rule_id = f"custom_{rule_type}_{len(description.split())}"
            
            new_rule = PropValidationRule(
                rule_id=rule_id,
                description=description,
                rule_type=rule_type,
                conditions=conditions,
                auto_applied=auto_applied,
                created_date=datetime.now()
            )
            session.add(new_rule)
            session.commit()
            logger.info(f"✅ Added custom rule: {description}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding custom rule: {e}")
        finally:
            session.close()

    def _get_prop_signature(self, prop: PlayerProp) -> str:
        """Generate unique signature for a prop"""
        return f"{prop.player_name}|{prop.stat_type}|{prop.bet_type}|{prop.line}"

    def filter_available_props(self, props: List[PropAnalysis]) -> List[PropAnalysis]:
        """
        Filter props based on known availability
        Returns only props that haven't been marked as unavailable
        """
        session = self.get_session()
        try:
            # Get all unavailable signatures
            unavailable = session.query(PropAvailability.id).filter(PropAvailability.is_available == False).all()
            unavailable_sigs = {row[0] for row in unavailable}
            
            available_props = []
            for prop_analysis in props:
                prop_signature = self._get_prop_signature(prop_analysis.prop)
                if prop_signature not in unavailable_sigs:
                    available_props.append(prop_analysis)
            
            return available_props
        except Exception as e:
            logger.error(f"Error filtering available props: {e}")
            return props
        finally:
            session.close()

    def filter_by_minimum_thresholds(self, props: List[PropAnalysis], verbose: bool = True) -> List[PropAnalysis]:
        """
        Filter props that don't meet minimum thresholds for their stat type
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

    def filter_defense_props(self, props: List[PropAnalysis], verbose: bool = True) -> List[PropAnalysis]:
        """
        Filter out defense/special teams props
        """
        filtered_props = []
        defense_count = 0
        defense_details = []

        # Keywords that indicate defense/ST props
        defense_keywords = [
            'd/st', 'defense', 'dst', 'def',
            'steelers d', 'packers d', 'broncos d',
            'eagles d', 'ravens d', 'chiefs d',
            'bills d', 'cowboys d', 'lions d',
            '49ers d', 'dolphins d', 'seahawks d',
            'rams d', 'chargers d', 'bengals d',
            'browns d', 'colts d', 'giants d',
            'jets d', 'patriots d', 'raiders d',
            'saints d', 'panthers d', 'bears d',
            'vikings d', 'titans d', 'jaguars d',
            'texans d', 'commanders d', 'falcons d',
            'cardinals d', 'buccaneers d'
        ]

        for prop_analysis in props:
            prop = prop_analysis.prop
            player_name_lower = prop.player_name.lower()

            # Check if player name contains defense keywords
            is_defense = any(keyword in player_name_lower for keyword in defense_keywords)

            if is_defense:
                defense_count += 1
                defense_details.append(
                    f"  ❌ {prop.player_name} - {prop.stat_type} (defense/ST prop)"
                )
                continue  # Skip this prop

            # Not a defense prop - keep it
            filtered_props.append(prop_analysis)

        if verbose and defense_count > 0:
            logger.info(f"\n🛡️ Filtered {defense_count} defense/ST props:")
            for detail in defense_details[:10]:  # Show first 10
                logger.info(detail)
            if len(defense_details) > 10:
                logger.info(f"  ... and {len(defense_details) - 10} more")
            logger.info(f"✅ {len(filtered_props)} props remaining after defense filter\n")

        return filtered_props

    def get_validation_stats(self) -> Dict:
        """Get statistics about validation rules and history"""
        session = self.get_session()
        try:
            total_rules = session.query(func.count(PropValidationRule.rule_id)).scalar()
            available_count = session.query(func.count(PropAvailability.id)).filter(PropAvailability.is_available == True).scalar()
            unavailable_count = session.query(func.count(PropAvailability.id)).filter(PropAvailability.is_available == False).scalar()
            
            return {
                "total_rules": total_rules or 0,
                "props_marked_available": available_count or 0,
                "props_marked_unavailable": unavailable_count or 0
            }
        except Exception as e:
            logger.error(f"Error getting validation stats: {e}")
            return {"total_rules": 0, "props_marked_available": 0, "props_marked_unavailable": 0}
        finally:
            session.close()
