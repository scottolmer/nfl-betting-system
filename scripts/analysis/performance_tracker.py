"""Performance tracking and bet outcome logging for calibration"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

class PerformanceTracker:
    def __init__(self, db_path="bets.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.create_tables()
        print(f"✅ Performance tracker initialized at {self.db_path}")
    
    def create_tables(self):
        """Create database schema"""
        cursor = self.conn.cursor()
        
        # Parlays table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parlays (
                parlay_id TEXT PRIMARY KEY,
                created_date TEXT,
                week INTEGER,
                confidence_score REAL,
                odds REAL,
                parlay_type TEXT,
                status TEXT DEFAULT 'pending',
                agent_breakdown TEXT,
                dependencies TEXT,
                created_timestamp REAL
            )
        """)
        
        # Legs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS legs (
                leg_id TEXT PRIMARY KEY,
                parlay_id TEXT,
                player TEXT,
                team TEXT,
                prop_type TEXT,
                bet_type TEXT,
                line REAL,
                agent_scores TEXT,
                result INTEGER DEFAULT NULL,
                FOREIGN KEY(parlay_id) REFERENCES parlays(parlay_id)
            )
        """)
        
        # Analysis table for calibration
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calibration_results (
                id INTEGER PRIMARY KEY,
                parlay_id TEXT,
                confidence_predicted REAL,
                confidence_actual REAL,
                calibration_error REAL,
                notes TEXT,
                FOREIGN KEY(parlay_id) REFERENCES parlays(parlay_id)
            )
        """)
        
        self.conn.commit()
    
    def log_parlay(self, parlay, week, parlay_type="standard"):
        """
        Log a parlay at bet time
        
        parlay = {
            'confidence': 0.76,
            'odds': -110,
            'legs': [
                {
                    'player': 'Mahomes',
                    'team': 'KC',
                    'prop_type': 'pass_yards',
                    'bet_type': 'OVER',
                    'line': 250,
                    'agent_scores': {'DVOA': 58, 'Matchup': 42, ...}
                },
                ...
            ]
        }
        """
        cursor = self.conn.cursor()
        parlay_id = f"parlay_{int(datetime.now().timestamp() * 1000)}"
        
        try:
            # Log parlay
            cursor.execute("""
                INSERT INTO parlays 
                (parlay_id, created_date, week, confidence_score, odds, parlay_type, agent_breakdown, created_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                parlay_id,
                datetime.now().isoformat(),
                week,
                parlay['confidence'],
                parlay.get('odds'),
                parlay_type,
                json.dumps(parlay.get('agent_scores', {})),
                datetime.now().timestamp()
            ))
            
            # Log legs
            leg_count = 0
            for leg in parlay.get('legs', []):
                leg_id = f"{parlay_id}_leg_{leg_count}"
                cursor.execute("""
                    INSERT INTO legs
                    (leg_id, parlay_id, player, team, prop_type, bet_type, line, agent_scores)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    leg_id,
                    parlay_id,
                    leg.get('player'),
                    leg.get('team'),
                    leg.get('prop_type'),
                    leg.get('bet_type', 'OVER'),
                    leg.get('line'),
                    json.dumps(leg.get('agent_scores', {}))
                ))
                leg_count += 1
            
            self.conn.commit()
            print(f"   ✅ Logged parlay {parlay_id} ({len(parlay.get('legs', []))} legs, {parlay['confidence']:.1f}% confidence)")
            return parlay_id
        
        except Exception as e:
            print(f"   ❌ Error logging parlay: {e}")
            return None
    
    def log_results(self, parlay_id, leg_results):
        """
        Log results after games complete
        
        leg_results = {
            'leg_0': True,   # hit
            'leg_1': False,  # missed
            ...
        }
        """
        cursor = self.conn.cursor()
        
        try:
            parlay_won = all(leg_results.values())
            
            # Update parlay status
            cursor.execute("UPDATE parlays SET status = ? WHERE parlay_id = ?",
                          ('won' if parlay_won else 'lost', parlay_id))
            
            # Update leg results
            for leg_key, hit in leg_results.items():
                leg_id = f"{parlay_id}_{leg_key}"
                cursor.execute("UPDATE legs SET result = ? WHERE leg_id = ?",
                              (int(hit), leg_id))
            
            self.conn.commit()
            hit_count = sum(1 for hit in leg_results.values() if hit)
            total_legs = len(leg_results)
            print(f"✅ Logged results for {parlay_id}: {hit_count}/{total_legs} legs hit")
        
        except Exception as e:
            print(f"❌ Error logging results: {e}")
    
    def get_all_results(self):
        """Get all completed parlays with their agent breakdown for calibration analysis"""
        cursor = self.conn.cursor()
        
        try:
            query = """
                SELECT 
                    parlay_id, week, confidence_score, status, agent_breakdown,
                    (SELECT COUNT(*) FROM legs WHERE parlay_id = parlays.parlay_id) as leg_count
                FROM parlays
                WHERE status IN ('won', 'lost')
                ORDER BY created_timestamp DESC
            """
            
            results = cursor.execute(query).fetchall()
            
            parsed_results = []
            for parlay_id, week, conf, status, agent_breakdown_json, leg_count in results:
                try:
                    agent_breakdown = json.loads(agent_breakdown_json) if agent_breakdown_json else {}
                except:
                    agent_breakdown = {}
                
                parsed_results.append({
                    "parlay_id": parlay_id,
                    "week": week,
                    "confidence_score": conf,
                    "result": "HIT" if status == "won" else "MISS",
                    "agent_breakdown": agent_breakdown,
                    "leg_count": leg_count,
                })
            
            return parsed_results
        
        except Exception as e:
            print(f"❌ Error getting all results: {e}")
            return []
    
    def get_week_results(self, week):
        """Get all completed parlays for a specific week with agent breakdown"""
        cursor = self.conn.cursor()
        
        try:
            query = """
                SELECT 
                    parlay_id, week, confidence_score, status, agent_breakdown,
                    (SELECT COUNT(*) FROM legs WHERE parlay_id = parlays.parlay_id) as leg_count
                FROM parlays
                WHERE week = ? AND status IN ('won', 'lost')
                ORDER BY created_timestamp DESC
            """
            
            results = cursor.execute(query, (week,)).fetchall()
            
            parsed_results = []
            for parlay_id, w, conf, status, agent_breakdown_json, leg_count in results:
                try:
                    agent_breakdown = json.loads(agent_breakdown_json) if agent_breakdown_json else {}
                except:
                    agent_breakdown = {}
                
                parsed_results.append({
                    "parlay_id": parlay_id,
                    "week": w,
                    "confidence_score": conf,
                    "result": "HIT" if status == "won" else "MISS",
                    "agent_breakdown": agent_breakdown,
                    "leg_count": leg_count,
                })
            
            return parsed_results
        
        except Exception as e:
            print(f"❌ Error getting week results: {e}")
            return []
    
    def calibration_report(self, week=None):
        """Generate calibration report comparing predicted vs actual confidence"""
        cursor = self.conn.cursor()
        
        try:
            query = """
                SELECT 
                    ROUND(confidence_score * 20) / 20.0 as confidence_bin,
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) as wins,
                    ROUND(100.0 * SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) / COUNT(*), 1) as actual_hit_rate,
                    ROUND(AVG(confidence_score) * 100, 1) as avg_predicted
                FROM parlays
                WHERE status != 'pending'
            """
            
            if week:
                query += f" AND week = {week}"
            
            query += " GROUP BY confidence_bin ORDER BY confidence_bin DESC"
            
            results = cursor.execute(query).fetchall()
            
            if not results:
                print("\n❌ No completed parlays to analyze yet\n")
                return
            
            print("\n" + "="*80)
            print("📊 CALIBRATION REPORT - Predicted vs Actual Hit Rates")
            print("="*80)
            print(f"{'Conf Bin':<10} {'Total':<8} {'Wins':<8} {'Hit Rate':<12} {'Predicted':<12} {'Error':<10}")
            print("-"*80)
            
            total_all = 0
            wins_all = 0
            
            for bin_val, total, wins, hit_rate, avg_predicted in results:
                if total == 0:
                    continue
                
                error = hit_rate - avg_predicted
                error_sign = "+" if error >= 0 else ""
                
                print(f"{bin_val*100:5.0f}%    {total:<8} {wins:<8} {hit_rate:>6.1f}%     "
                      f"{avg_predicted:>6.1f}%        {error_sign}{error:6.1f}pp")
                
                total_all += total
                wins_all += wins
            
            print("-"*80)
            if total_all > 0:
                overall_rate = (wins_all / total_all) * 100
                print(f"{'OVERALL':<10} {total_all:<8} {wins_all:<8} {overall_rate:>6.1f}%")
            print("="*80)
            print("\n💡 INTERPRETATION:")
            print("  • Error = Actual - Predicted (negative = overconfident, positive = underconfident)")
            print("  • Goal: error ≈ 0 (predictions match reality)")
            print("  • Persistent negative error = system is too confident\n")
        
        except Exception as e:
            print(f"\n❌ Error generating report: {e}\n")
    
    def week_summary(self, week):
        """Show summary stats for a specific week"""
        cursor = self.conn.cursor()
        
        try:
            query = """
                SELECT 
                    COUNT(*) as total_parlays,
                    SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN status = 'lost' THEN 1 ELSE 0 END) as losses,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                    ROUND(AVG(confidence_score), 2) as avg_confidence
                FROM parlays
                WHERE week = ?
            """
            
            result = cursor.execute(query, (week,)).fetchone()
            
            if not result or result[0] == 0:
                print(f"\n❌ No parlays found for Week {week}\n")
                return
            
            total, wins, losses, pending, avg_conf = result
            
            print(f"\n📊 WEEK {week} SUMMARY")
            print("="*50)
            print(f"Total Parlays: {total}")
            print(f"  Won:     {wins} ({100*wins/total:.1f}%)")
            print(f"  Lost:    {losses} ({100*losses/total:.1f}%)")
            print(f"  Pending: {pending}")
            print(f"Average Confidence: {avg_conf:.1f}%")
            print("="*50 + "\n")
        
        except Exception as e:
            print(f"\n❌ Error getting summary: {e}\n")
    
    def list_recent_parlays(self, limit=10):
        """List recent parlays and their status"""
        cursor = self.conn.cursor()
        
        try:
            query = """
                SELECT 
                    parlay_id, week, confidence_score, status, 
                    (SELECT COUNT(*) FROM legs WHERE parlay_id = parlays.parlay_id) as leg_count
                FROM parlays
                ORDER BY created_timestamp DESC
                LIMIT ?
            """
            
            results = cursor.execute(query, (limit,)).fetchall()
            
            if not results:
                print("\n❌ No parlays logged yet\n")
                return
            
            print(f"\n📋 RECENT PARLAYS (Latest {len(results)})")
            print("="*80)
            print(f"{'Parlay ID':<25} {'Week':<6} {'Legs':<6} {'Confidence':<12} {'Status':<10}")
            print("-"*80)
            
            for parlay_id, week, conf, status, legs in results:
                status_emoji = "✅" if status == "won" else "❌" if status == "lost" else "⏳"
                print(f"{parlay_id:<25} {week:<6} {legs:<6} {conf:>6.1f}%      "
                      f"{status_emoji} {status:<8}")
            
            print("="*80 + "\n")
        
        except Exception as e:
            print(f"\n❌ Error listing parlays: {e}\n")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
