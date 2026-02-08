"""Performance tracking and bet outcome logging for calibration"""

import json
from datetime import datetime
from pathlib import Path
from sqlalchemy import func, desc
from api.database import SessionLocal, Parlay, Leg, CalibrationResult, init_db

class PerformanceTracker:
    def __init__(self, db_path=None):
        # db_path is legacy but kept for compatibility. 
        # The actual connection is handled by api.database.SessionLocal
        init_db()  # Ensure tables exist
        print(f"[OK] Performance tracker initialized (SQLAlchemy)")
    
    def get_session(self):
        return SessionLocal()

    def log_parlay(self, parlay_data, week, parlay_type="standard"):
        """
        Log a parlay at bet time.
        Uses SQLAlchemy ORM.
        """
        session = self.get_session()
        parlay_id = f"parlay_{int(datetime.now().timestamp() * 1000)}"
        
        try:
            # Create Parlay object
            # Note: SQLAlchemy JSON type handles serialization automatically
            new_parlay = Parlay(
                parlay_id=parlay_id,
                created_date=datetime.now().isoformat(),
                week=week,
                confidence_score=parlay_data['confidence'],
                odds=parlay_data.get('odds'),
                parlay_type=parlay_type,
                status="pending",
                agent_breakdown=parlay_data.get('agent_scores', {}),
                created_timestamp=datetime.now().timestamp()
            )
            session.add(new_parlay)
            
            # Create Leg objects
            leg_count = 0
            for leg_data in parlay_data.get('legs', []):
                leg_id = f"{parlay_id}_leg_{leg_count}"
                new_leg = Leg(
                    leg_id=leg_id,
                    parlay_id=parlay_id,
                    player=leg_data.get('player'),
                    team=leg_data.get('team'),
                    prop_type=leg_data.get('prop_type'),
                    bet_type=leg_data.get('bet_type', 'OVER'),
                    line=leg_data.get('line'),
                    agent_scores=leg_data.get('agent_scores', {})
                )
                session.add(new_leg)
                leg_count += 1
            
            session.commit()
            print(f"   [OK] Logged parlay {parlay_id} ({leg_count} legs, {parlay_data['confidence']:.1f}% confidence)")
            return parlay_id

        except Exception as e:
            session.rollback()
            print(f"   [ERROR] Error logging parlay: {e}")
            return None
        finally:
            session.close()
    
    def log_results(self, parlay_id, leg_results):
        """
        Log results after games complete
        
        leg_results = {
            'leg_0': True,   # hit
            'leg_1': False,  # missed
            ...
        }
        """
        session = self.get_session()
        
        try:
            parlay = session.query(Parlay).filter(Parlay.parlay_id == parlay_id).first()
            if not parlay:
                print(f"[ERROR] Parlay {parlay_id} not found")
                return

            parlay_won = all(leg_results.values())
            
            # Update parlay status
            parlay.status = 'won' if parlay_won else 'lost'
            
            # Update leg results
            # We need to map 'leg_0', 'leg_1' keys to our Leg objects
            for leg_key, hit in leg_results.items():
                # specific leg_id e.g. "parlay_123_leg_0"
                # If leg_key is "leg_0", we construct proper id
                full_leg_id = f"{parlay_id}_{leg_key}"
                
                leg = session.query(Leg).filter(Leg.leg_id == full_leg_id).first()
                if leg:
                    leg.result = int(hit)
            
            session.commit()
            
            hit_count = sum(1 for hit in leg_results.values() if hit)
            total_legs = len(leg_results)
            print(f"[OK] Logged results for {parlay_id}: {hit_count}/{total_legs} legs hit")

        except Exception as e:
            print(f"[ERROR] Error logging results: {e}")
            session.rollback()
        finally:
            session.close()
    
    def get_all_results(self):
        """Get all completed parlays with their agent breakdown for calibration analysis"""
        session = self.get_session()
        try:
            # Query parlays that are won or lost
            parlays = session.query(Parlay).filter(Parlay.status.in_(['won', 'lost'])).order_by(desc(Parlay.created_timestamp)).all()
            
            parsed_results = []
            for p in parlays:
                parsed_results.append({
                    "parlay_id": p.parlay_id,
                    "week": p.week,
                    "confidence_score": p.confidence_score,
                    "result": "HIT" if p.status == "won" else "MISS",
                    "agent_breakdown": p.agent_breakdown or {},
                    "leg_count": len(p.legs),
                })
            
            return parsed_results

        except Exception as e:
            print(f"[ERROR] Error getting all results: {e}")
            return []
        finally:
            session.close()
    
    def get_week_results(self, week):
        """Get all completed parlays for a specific week with agent breakdown"""
        session = self.get_session()
        try:
            parlays = session.query(Parlay).filter(
                Parlay.week == week,
                Parlay.status.in_(['won', 'lost'])
            ).order_by(desc(Parlay.created_timestamp)).all()
            
            parsed_results = []
            for p in parlays:
                parsed_results.append({
                    "parlay_id": p.parlay_id,
                    "week": p.week,
                    "confidence_score": p.confidence_score,
                    "result": "HIT" if p.status == "won" else "MISS",
                    "agent_breakdown": p.agent_breakdown or {},
                    "leg_count": len(p.legs),
                })
            
            return parsed_results
        
        except Exception as e:
            print(f"[ERROR] Error getting week results: {e}")
            return []
        finally:
            session.close()
    
    def calibration_report(self, week=None):
        """Generate calibration report comparing predicted vs actual confidence"""
        session = self.get_session()
        try:
            # We can't easily do the complex binning SQL in ORM without func, 
            # so we'll fetch data and process in Python or use a raw query if needed for performance.
            # For simplicity and DB-independence, let's fetch and process in Python for now.
            # Or use query builder:
            
            query = session.query(Parlay).filter(Parlay.status != 'pending')
            if week:
                query = query.filter(Parlay.week == week)
                
            parlays = query.all()
            
            if not parlays:
                print("\n[ERROR] No completed parlays to analyze yet\n")
                return

            # Analyze in Python
            from collections import defaultdict
            bins = defaultdict(lambda: {'total': 0, 'wins': 0, 'confs': []})
            
            for p in parlays:
                # Bin to nearest 5% (0.05)
                # Matches original logic: ROUND(confidence_score * 20) / 20.0
                bin_val = round(p.confidence_score * 20) / 20.0
                bins[bin_val]['total'] += 1
                if p.status == 'won':
                    bins[bin_val]['wins'] += 1
                bins[bin_val]['confs'].append(p.confidence_score)
                
            print("\n" + "="*80)
            print("📊 CALIBRATION REPORT - Predicted vs Actual Hit Rates")
            print("="*80)
            print(f"{'Conf Bin':<10} {'Total':<8} {'Wins':<8} {'Hit Rate':<12} {'Predicted':<12} {'Error':<10}")
            print("-"*80)
            
            total_all = 0
            wins_all = 0
            
            # Sort by bin value descending
            for bin_val in sorted(bins.keys(), reverse=True):
                stats = bins[bin_val]
                total = stats['total']
                wins = stats['wins']
                hit_rate = (wins / total) * 100
                avg_predicted = sum(stats['confs']) / total  # Use actual avg for more precision? Or bin center? Original used avg
                
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
            
        except Exception as e:
            print(f"\n[ERROR] Error generating report: {e}\n")
        finally:
            session.close()
    
    def week_summary(self, week):
        """Show summary stats for a specific week"""
        session = self.get_session()
        try:
            # Query stats
            total = session.query(func.count(Parlay.parlay_id)).filter(Parlay.week == week).scalar()
            
            if total == 0:
                print(f"\n[ERROR] No parlays found for Week {week}\n")
                return

            wins = session.query(func.count(Parlay.parlay_id)).filter(Parlay.week == week, Parlay.status == 'won').scalar()
            losses = session.query(func.count(Parlay.parlay_id)).filter(Parlay.week == week, Parlay.status == 'lost').scalar()
            pending = session.query(func.count(Parlay.parlay_id)).filter(Parlay.week == week, Parlay.status == 'pending').scalar()
            avg_conf = session.query(func.avg(Parlay.confidence_score)).filter(Parlay.week == week).scalar() or 0
            
            print(f"\n📊 WEEK {week} SUMMARY")
            print("="*50)
            print(f"Total Parlays: {total}")
            print(f"  Won:     {wins} ({100*wins/total:.1f}%)")
            print(f"  Lost:    {losses} ({100*losses/total:.1f}%)")
            print(f"  Pending: {pending}")
            print(f"Average Confidence: {avg_conf:.1f}%")
            print("="*50 + "\n")
        
        except Exception as e:
            print(f"\n[ERROR] Error getting summary: {e}\n")
        finally:
            session.close()
    
    def list_recent_parlays(self, limit=10):
        """List recent parlays and their status"""
        session = self.get_session()
        try:
            parlays = session.query(Parlay).order_by(desc(Parlay.created_timestamp)).limit(limit).all()
            
            if not parlays:
                print("\n[ERROR] No parlays logged yet\n")
                return
            
            print(f"\n📋 RECENT PARLAYS (Latest {len(parlays)})")
            print("="*80)
            print(f"{'Parlay ID':<25} {'Week':<6} {'Legs':<6} {'Confidence':<12} {'Status':<10}")
            print("-"*80)
            
            for p in parlays:
                status_emoji = "[OK]" if p.status == "won" else "[ERROR]" if p.status == "lost" else "[PENDING]"
                print(f"{p.parlay_id:<25} {p.week:<6} {len(p.legs):<6} {p.confidence_score:>6.1f}%      "
                      f"{status_emoji} {p.status:<8}")
            
            print("="*80 + "\n")
        
        except Exception as e:
            print(f"\n[ERROR] Error listing parlays: {e}\n")
        finally:
            session.close()
    
    def close(self):
        """No-op for SQLAlchemy logic as sessions are closed per method"""
        pass
