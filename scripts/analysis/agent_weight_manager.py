"""
Agent Weight Manager - Automated Learning System

Manages agent weights dynamically based on historical performance.
Automatically adjusts weights after each week's calibration.
"""

import sqlite3
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json


class AgentWeightManager:
    """Manages automated agent weight adjustments based on performance."""

    # Default weights (fallback if database is empty)
    DEFAULT_WEIGHTS = {
        'DVOA': 2.5,
        'Matchup': 2.0,
        'Volume': 1.8,
        'Injury': 1.5,
        'Trend': 1.2,
        'GameScript': 1.0,
        'Variance': 0.8,
        'Weather': 0.5,
        'HitRate': 2.0
    }

    # Safety constraints
    MIN_WEIGHT = 0.1
    MAX_WEIGHT = 5.0
    MAX_ADJUSTMENT_PER_WEEK = 0.5  # Maximum change in one week
    MIN_SAMPLES_FOR_ADJUSTMENT = 10  # Minimum legs scored to adjust

    def __init__(self, db_path: str = "bets.db"):
        self.db_path = db_path
        self._ensure_tables_exist()

    def _ensure_tables_exist(self):
        """Create agent_weights and agent_weight_history tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Agent weights table (current active weights)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_weights (
                agent_name TEXT PRIMARY KEY,
                weight REAL NOT NULL,
                last_updated TEXT NOT NULL,
                total_legs_analyzed INTEGER DEFAULT 0,
                cumulative_accuracy REAL DEFAULT 0.0,
                notes TEXT
            )
        """)

        # Weight history table (audit trail)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_weight_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                old_weight REAL NOT NULL,
                new_weight REAL NOT NULL,
                adjustment_reason TEXT,
                week INTEGER,
                accuracy REAL,
                overconfidence REAL,
                sample_size INTEGER,
                timestamp TEXT NOT NULL
            )
        """)

        # Auto-learning config table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    def initialize_default_weights(self, force: bool = False):
        """Initialize agent weights with defaults if not already set."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for agent_name, weight in self.DEFAULT_WEIGHTS.items():
            if force:
                cursor.execute("""
                    INSERT OR REPLACE INTO agent_weights
                    (agent_name, weight, last_updated, notes)
                    VALUES (?, ?, ?, ?)
                """, (agent_name, weight, datetime.now().isoformat(), "Default initialization"))
            else:
                cursor.execute("""
                    INSERT OR IGNORE INTO agent_weights
                    (agent_name, weight, last_updated, notes)
                    VALUES (?, ?, ?, ?)
                """, (agent_name, weight, datetime.now().isoformat(), "Initial default"))

        conn.commit()
        conn.close()

    def get_current_weights(self) -> Dict[str, float]:
        """Get current active weights for all agents."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT agent_name, weight FROM agent_weights")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            # No weights in database, initialize with defaults
            self.initialize_default_weights()
            return self.DEFAULT_WEIGHTS.copy()

        return {agent_name: weight for agent_name, weight in rows}

    def get_weight(self, agent_name: str) -> float:
        """Get current weight for a specific agent."""
        weights = self.get_current_weights()
        return weights.get(agent_name, self.DEFAULT_WEIGHTS.get(agent_name, 1.0))

    def update_weight(
        self,
        agent_name: str,
        new_weight: float,
        reason: str,
        week: Optional[int] = None,
        accuracy: Optional[float] = None,
        overconfidence: Optional[float] = None,
        sample_size: Optional[int] = None
    ):
        """Update an agent's weight and log to history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get old weight
        cursor.execute("SELECT weight FROM agent_weights WHERE agent_name = ?", (agent_name,))
        row = cursor.fetchone()
        old_weight = row[0] if row else self.DEFAULT_WEIGHTS.get(agent_name, 1.0)

        # Apply safety constraints
        new_weight = max(self.MIN_WEIGHT, min(self.MAX_WEIGHT, new_weight))

        # Limit adjustment magnitude
        max_change = old_weight + self.MAX_ADJUSTMENT_PER_WEEK
        min_change = old_weight - self.MAX_ADJUSTMENT_PER_WEEK
        new_weight = max(min_change, min(max_change, new_weight))

        # Update current weight
        cursor.execute("""
            INSERT OR REPLACE INTO agent_weights
            (agent_name, weight, last_updated, notes)
            VALUES (?, ?, ?, ?)
        """, (agent_name, new_weight, datetime.now().isoformat(), reason))

        # Log to history
        cursor.execute("""
            INSERT INTO agent_weight_history
            (agent_name, old_weight, new_weight, adjustment_reason, week,
             accuracy, overconfidence, sample_size, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (agent_name, old_weight, new_weight, reason, week,
              accuracy, overconfidence, sample_size, datetime.now().isoformat()))

        conn.commit()
        conn.close()

        return old_weight, new_weight

    def auto_adjust_weights(
        self,
        agent_performance: Dict[str, Dict],
        week: int,
        dry_run: bool = False
    ) -> List[Dict]:
        """
        Automatically adjust agent weights based on performance.

        Args:
            agent_performance: Dict with agent stats (accuracy, overconfidence, sample_size)
            week: Week number for tracking
            dry_run: If True, calculate but don't apply adjustments

        Returns:
            List of adjustment records
        """
        adjustments = []

        for agent_name, stats in agent_performance.items():
            accuracy = stats.get('accuracy', 0.0)
            overconfidence = stats.get('overconfidence', 0.0)
            sample_size = stats.get('sample_size', 0)

            # Skip if not enough data
            if sample_size < self.MIN_SAMPLES_FOR_ADJUSTMENT:
                adjustments.append({
                    'agent': agent_name,
                    'action': 'SKIP',
                    'reason': f'Insufficient data ({sample_size} < {self.MIN_SAMPLES_FOR_ADJUSTMENT})',
                    'old_weight': self.get_weight(agent_name),
                    'new_weight': self.get_weight(agent_name)
                })
                continue

            # Calculate adjustment
            current_weight = self.get_weight(agent_name)

            # Adjustment formula:
            # - Overconfident agents get reduced weight
            # - Underconfident agents get increased weight
            # - Scale by magnitude of overconfidence and accuracy

            adjustment_factor = -overconfidence * 3.0  # Reduced from 5.0 for smoother learning

            # Bonus for high accuracy
            if accuracy > 0.70:
                accuracy_bonus = (accuracy - 0.70) * 2.0
                adjustment_factor += accuracy_bonus

            # Penalty for low accuracy
            if accuracy < 0.50:
                accuracy_penalty = (0.50 - accuracy) * 2.0
                adjustment_factor -= accuracy_penalty

            new_weight = current_weight + adjustment_factor

            # Determine reason
            if abs(overconfidence) < 0.02 and accuracy > 0.65:
                reason = "Well-calibrated (no adjustment needed)"
                new_weight = current_weight  # No change
            elif overconfidence > 0.05:
                reason = f"Overconfident (+{overconfidence:.1%}) - reducing weight"
            elif overconfidence < -0.05:
                reason = f"Underconfident ({overconfidence:.1%}) - increasing weight"
            elif accuracy > 0.70:
                reason = f"High accuracy ({accuracy:.1%}) - increasing weight"
            elif accuracy < 0.50:
                reason = f"Low accuracy ({accuracy:.1%}) - decreasing weight"
            else:
                reason = "Minor calibration adjustment"

            # Apply adjustment if not dry run
            if not dry_run and new_weight != current_weight:
                old_weight, final_weight = self.update_weight(
                    agent_name=agent_name,
                    new_weight=new_weight,
                    reason=reason,
                    week=week,
                    accuracy=accuracy,
                    overconfidence=overconfidence,
                    sample_size=sample_size
                )
            else:
                old_weight = current_weight
                final_weight = new_weight

            adjustments.append({
                'agent': agent_name,
                'action': 'ADJUSTED' if final_weight != old_weight else 'NO_CHANGE',
                'reason': reason,
                'old_weight': old_weight,
                'new_weight': final_weight,
                'adjustment': final_weight - old_weight,
                'accuracy': accuracy,
                'overconfidence': overconfidence,
                'sample_size': sample_size
            })

        return adjustments

    def get_weight_history(self, agent_name: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get weight adjustment history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if agent_name:
            cursor.execute("""
                SELECT agent_name, old_weight, new_weight, adjustment_reason,
                       week, accuracy, overconfidence, sample_size, timestamp
                FROM agent_weight_history
                WHERE agent_name = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (agent_name, limit))
        else:
            cursor.execute("""
                SELECT agent_name, old_weight, new_weight, adjustment_reason,
                       week, accuracy, overconfidence, sample_size, timestamp
                FROM agent_weight_history
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                'agent': row[0],
                'old_weight': row[1],
                'new_weight': row[2],
                'reason': row[3],
                'week': row[4],
                'accuracy': row[5],
                'overconfidence': row[6],
                'sample_size': row[7],
                'timestamp': row[8]
            }
            for row in rows
        ]

    def set_config(self, key: str, value: str):
        """Set a learning configuration value."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO learning_config (key, value, updated_at)
            VALUES (?, ?, ?)
        """, (key, value, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def get_config(self, key: str, default: str = None) -> Optional[str]:
        """Get a learning configuration value."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM learning_config WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()

        return row[0] if row else default

    def is_auto_learning_enabled(self) -> bool:
        """Check if auto-learning is enabled."""
        return self.get_config('auto_learning_enabled', 'true').lower() == 'true'

    def enable_auto_learning(self):
        """Enable automatic weight adjustments."""
        self.set_config('auto_learning_enabled', 'true')

    def disable_auto_learning(self):
        """Disable automatic weight adjustments."""
        self.set_config('auto_learning_enabled', 'false')

    def print_current_weights(self):
        """Print current agent weights in a formatted table."""
        weights = self.get_current_weights()

        print("\n" + "="*60)
        print("CURRENT AGENT WEIGHTS")
        print("="*60)

        # Sort by weight descending
        sorted_agents = sorted(weights.items(), key=lambda x: x[1], reverse=True)

        for agent_name, weight in sorted_agents:
            bar_length = int(weight * 10)
            bar = "█" * bar_length
            print(f"{agent_name:15s} {weight:5.2f}  {bar}")

        print("="*60)
        print(f"Auto-learning: {'ENABLED' if self.is_auto_learning_enabled() else 'DISABLED'}")
        print("="*60 + "\n")

    def print_adjustment_summary(self, adjustments: List[Dict]):
        """Print a summary of weight adjustments."""
        print("\n" + "="*80)
        print("AUTOMATED WEIGHT ADJUSTMENTS")
        print("="*80)

        for adj in adjustments:
            agent = adj['agent']
            action = adj['action']
            old = adj['old_weight']
            new = adj['new_weight']
            delta = adj.get('adjustment', 0)
            reason = adj['reason']

            if action == 'SKIP':
                symbol = '⏭️'
                change_str = f"{old:.2f} → {new:.2f} (no change)"
            elif delta > 0.1:
                symbol = '⬆️'
                change_str = f"{old:.2f} → {new:.2f} (+{delta:.2f})"
            elif delta < -0.1:
                symbol = '⬇️'
                change_str = f"{old:.2f} → {new:.2f} ({delta:.2f})"
            elif action == 'NO_CHANGE':
                symbol = '✅'
                change_str = f"{old:.2f} (no change)"
            else:
                symbol = '↔️'
                change_str = f"{old:.2f} → {new:.2f} ({delta:+.2f})"

            print(f"\n{symbol} {agent:15s} {change_str}")
            print(f"   Reason: {reason}")

            if 'accuracy' in adj and adj['accuracy'] is not None:
                print(f"   Stats: {adj['accuracy']:.1%} accuracy, " +
                      f"{adj['overconfidence']:+.1%} overconfidence, " +
                      f"{adj['sample_size']} samples")

        print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    # Test the manager
    manager = AgentWeightManager()
    manager.initialize_default_weights()
    manager.print_current_weights()
