"""
Conversation Manager for Betting Assistant
Handles session state, context tracking, and intent detection
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)


class Intent(Enum):
    """User intent classification"""
    ANALYZE_PROPS = "analyze_props"
    BUILD_PARLAY = "build_parlay"
    REFINE_PARLAY = "refine_parlay"
    EXCLUDE_PLAYER = "exclude_player"
    EXPLAIN_PROP = "explain_prop"
    HISTORICAL_QUERY = "historical_query"
    COMPARE_PARLAYS = "compare_parlays"
    DATA_STATUS = "data_status"
    GENERAL_QUESTION = "general_question"
    UPLOAD_DATA = "upload_data"


class ConversationManager:
    """Manages conversation state and context for betting assistant"""

    def __init__(self, db_path: str = "bets.db", user_id: str = "default"):
        self.db_path = db_path
        self.user_id = user_id
        self.session_id = str(uuid.uuid4())
        self.context_window = []  # Last 10 messages
        self.max_context = 10
        self.current_week = None
        self.current_props = None
        self.current_parlays = None
        self.excluded_players = set()
        self.platform_constraints = {}  # Platform-specific constraints

    def detect_intent(self, user_message: str) -> Tuple[Intent, Dict]:
        """
        Detect user intent from message

        Returns:
            (intent, parameters) tuple
        """
        message_lower = user_message.lower().strip()

        # Extract parameters
        params = {}

        # Detect week mentions
        if 'week ' in message_lower:
            import re
            match = re.search(r'week\s+(\d+)', message_lower)
            if match:
                params['week'] = int(match.group(1))

        # Intent detection patterns
        if any(word in message_lower for word in ['exclude', 'remove', 'not available']):
            # Extract player names (simple heuristic)
            if 'mahomes' in message_lower:
                params['player'] = 'Patrick Mahomes'
            return Intent.EXCLUDE_PLAYER, params

        if any(word in message_lower for word in ['best parlay', 'build parlay', 'make parlay']):
            return Intent.BUILD_PARLAY, params

        if any(word in message_lower for word in ['analyze', 'analysis', 'what are']):
            if 'prop' in message_lower or 'bet' in message_lower:
                return Intent.ANALYZE_PROPS, params

        if any(word in message_lower for word in ['refine', 'update', 'change', 'modify']):
            if 'parlay' in message_lower:
                return Intent.REFINE_PARLAY, params

        if any(word in message_lower for word in ['why', 'explain', 'how', 'what makes']):
            return Intent.EXPLAIN_PROP, params

        if any(word in message_lower for word in ['how did', 'performance', 'results', 'last week']):
            return Intent.HISTORICAL_QUERY, params

        if any(word in message_lower for word in ['compare', 'vs', 'versus', 'difference']):
            if 'parlay' in message_lower:
                return Intent.COMPARE_PARLAYS, params

        if any(word in message_lower for word in ['status', 'loaded', 'data', 'files']):
            return Intent.DATA_STATUS, params

        if any(word in message_lower for word in ['upload', 'load', 'csv']):
            return Intent.UPLOAD_DATA, params

        # Default to general question
        return Intent.GENERAL_QUESTION, params

    def add_message(self, user_message: str, assistant_response: str,
                    intent: Intent, actions: List[str] = None):
        """Add message to conversation history"""
        timestamp = datetime.now().isoformat()

        # Add to context window
        self.context_window.append({
            'timestamp': timestamp,
            'user_message': user_message,
            'assistant_response': assistant_response,
            'intent': intent.value,
        })

        # Keep only last max_context messages
        if len(self.context_window) > self.max_context:
            self.context_window.pop(0)

        # Store in database
        self._save_to_db(timestamp, user_message, assistant_response, intent, actions)

    def _save_to_db(self, timestamp: str, user_message: str,
                    assistant_response: str, intent: Intent, actions: List[str] = None):
        """Save conversation to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO conversation_history
                (session_id, user_id, timestamp, user_message, assistant_response,
                 intent_detected, actions_taken)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                self.session_id,
                self.user_id,
                timestamp,
                user_message,
                assistant_response,
                intent.value,
                json.dumps(actions) if actions else None
            ))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to save conversation to DB: {e}")

    def get_user_preferences(self) -> Dict:
        """Load user preferences from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT default_platform, default_confidence_threshold,
                       preferred_prop_types, auto_apply_constraints
                FROM user_preferences
                WHERE user_id = ?
            """, (self.user_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    'platform': row[0],
                    'confidence_threshold': row[1],
                    'preferred_prop_types': json.loads(row[2]) if row[2] else [],
                    'auto_apply_constraints': bool(row[3])
                }
        except Exception as e:
            logger.error(f"Failed to load user preferences: {e}")

        # Return defaults
        return {
            'platform': 'pick6',
            'confidence_threshold': 65,
            'preferred_prop_types': [],
            'auto_apply_constraints': True
        }

    def update_user_preference(self, key: str, value):
        """Update a user preference"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Map key to column
            column_map = {
                'platform': 'default_platform',
                'confidence_threshold': 'default_confidence_threshold',
                'preferred_prop_types': 'preferred_prop_types',
                'auto_apply_constraints': 'auto_apply_constraints'
            }

            if key not in column_map:
                logger.warning(f"Unknown preference key: {key}")
                return

            column = column_map[key]

            # JSON encode if needed
            if key == 'preferred_prop_types' and isinstance(value, list):
                value = json.dumps(value)

            cursor.execute(f"""
                UPDATE user_preferences
                SET {column} = ?, last_updated = ?
                WHERE user_id = ?
            """, (value, datetime.now().isoformat(), self.user_id))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to update user preference: {e}")

    def set_current_week(self, week: int):
        """Set the current week context"""
        self.current_week = week

    def set_current_props(self, props: List[Dict]):
        """Set the current props context"""
        self.current_props = props

    def set_current_parlays(self, parlays: Dict):
        """Set the current parlays context"""
        self.current_parlays = parlays

    def add_excluded_player(self, player_name: str):
        """Add a player to exclusion list"""
        self.excluded_players.add(player_name.strip())

    def get_excluded_players(self) -> List[str]:
        """Get list of excluded players"""
        return list(self.excluded_players)

    def clear_excluded_players(self):
        """Clear exclusion list"""
        self.excluded_players.clear()

    def add_platform_constraint(self, platform: str, constraint_type: str, value):
        """Add a platform-specific constraint"""
        if platform not in self.platform_constraints:
            self.platform_constraints[platform] = {}
        self.platform_constraints[platform][constraint_type] = value

    def get_platform_constraints(self, platform: str) -> Dict:
        """Get constraints for a specific platform"""
        return self.platform_constraints.get(platform, {})

    def get_context_summary(self) -> str:
        """Get a summary of current conversation context"""
        lines = []

        if self.current_week:
            lines.append(f"Week: {self.current_week}")

        if self.current_props:
            lines.append(f"Props loaded: {len(self.current_props)}")

        if self.current_parlays:
            total_parlays = sum(len(p) for p in self.current_parlays.values())
            lines.append(f"Parlays generated: {total_parlays}")

        if self.excluded_players:
            lines.append(f"Excluded players: {', '.join(self.excluded_players)}")

        if not lines:
            return "No active context"

        return " | ".join(lines)

    def get_recent_history(self, limit: int = 5) -> List[Dict]:
        """Get recent conversation history"""
        return self.context_window[-limit:]


if __name__ == "__main__":
    # Test conversation manager
    logging.basicConfig(level=logging.INFO)

    manager = ConversationManager()

    test_messages = [
        "What are the best parlays for week 15?",
        "Exclude Mahomes - not available in Pick6",
        "Focus on WR3 receiving yards",
        "How did week 14 perform?",
        "Compare these to system recommendations"
    ]

    for msg in test_messages:
        intent, params = manager.detect_intent(msg)
        print(f"\nMessage: {msg}")
        print(f"Intent: {intent.value}")
        print(f"Params: {params}")
