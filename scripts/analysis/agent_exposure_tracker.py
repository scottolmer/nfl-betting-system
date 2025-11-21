"""
Agent Exposure Tracker - Portfolio-level risk management
Detects when too many parlays are driven by the same agent(s)
This prevents "DVOA blackout risk" where a single analytical signal drives entire weekly portfolio
"""

from typing import Dict, List, Set, Tuple
from collections import defaultdict
from .models import Parlay, PropAnalysis
import logging

logger = logging.getLogger(__name__)

class AgentExposureTracker:
    """
    Tracks which agents drive each leg across all parlays.
    Ensures portfolio doesn't become overly dependent on single analytical signals.
    """
    
    # Maximum % of parlays that can be driven by a single agent
    MAX_AGENT_EXPOSURE = 0.40  # 40% = no more than 4/10 parlays heavily driven by one agent
    
    # Minimum threshold to count an agent as "driving" a leg (contribution %)
    AGENT_DRIVER_THRESHOLD = 0.20  # 20% = agent must contribute at least 20% to be counted
    
    def __init__(self, min_confidence: int = 58):
        self.min_confidence = min_confidence
        self.agent_exposure = defaultdict(int)
        self.parlay_agent_drivers = {}  # Maps parlay index -> set of driving agents
        self.portfolio_risk_report = {}
        
    def analyze_portfolio(self, parlays_by_type: Dict[str, List[Parlay]]) -> Dict:
        """
        Analyze entire portfolio's agent exposure
        Returns comprehensive risk report
        """
        self.agent_exposure = defaultdict(int)
        self.parlay_agent_drivers = {}
        all_parlays = []
        
        # Flatten all parlays
        for parlay_type, parlay_list in parlays_by_type.items():
            all_parlays.extend(parlay_list)
        
        total_parlays = len(all_parlays)
        
        if total_parlays == 0:
            return {
                'status': 'NO_PARLAYS',
                'message': 'No parlays to analyze',
                'agent_exposure': {},
                'risk_level': 'UNKNOWN'
            }
        
        # Analyze each parlay
        for parlay_idx, parlay in enumerate(all_parlays):
            driving_agents = self._get_driving_agents(parlay)
            self.parlay_agent_drivers[parlay_idx] = driving_agents
            
            # Increment exposure count for each driving agent
            for agent_name in driving_agents:
                self.agent_exposure[agent_name] += 1
        
        # Calculate exposure percentages
        exposure_percentages = {
            agent: (count / total_parlays) 
            for agent, count in self.agent_exposure.items()
        }
        
        # Identify over-exposed agents
        over_exposed = {
            agent: pct 
            for agent, pct in exposure_percentages.items() 
            if pct > self.MAX_AGENT_EXPOSURE
        }
        
        # Calculate portfolio risk level
        risk_level = self._assess_risk_level(exposure_percentages, total_parlays)
        
        # Build comprehensive report
        report = {
            'total_parlays': total_parlays,
            'agent_exposure': exposure_percentages,
            'agent_appearance_count': dict(self.agent_exposure),
            'over_exposed_agents': over_exposed,
            'risk_level': risk_level,
            'primary_drivers': self._get_primary_drivers(exposure_percentages),
            'portfolio_concentration_score': self._calculate_concentration_score(exposure_percentages),
            'recommendations': self._generate_recommendations(
                over_exposed, exposure_percentages, total_parlays
            )
        }
        
        self.portfolio_risk_report = report
        return report
    
    def _get_driving_agents(self, parlay: Parlay) -> Set[str]:
        """
        Identify which agents are 'driving' a parlay
        An agent drives a parlay if it significantly contributes to multiple legs
        """
        driving_agents = set()
        
        for leg in parlay.legs:
            # Get top contributing agents for this leg
            # top_contributing_agents = [(agent_name, contribution %), ...]
            if hasattr(leg, 'top_contributing_agents') and leg.top_contributing_agents:
                for agent_name, contribution_pct in leg.top_contributing_agents[:2]:  # Top 2 agents
                    if contribution_pct >= self.AGENT_DRIVER_THRESHOLD:
                        driving_agents.add(agent_name)
        
        return driving_agents
    
    def _assess_risk_level(self, exposure_pcts: Dict[str, float], total_parlays: int) -> str:
        """Assess portfolio concentration risk level"""
        
        # Count how many agents are above 30% exposure
        high_exposure_agents = sum(1 for pct in exposure_pcts.values() if pct >= 0.30)
        
        # Get max single agent exposure
        max_exposure = max(exposure_pcts.values()) if exposure_pcts else 0
        
        # If no agents, can't assess
        if not exposure_pcts:
            return 'UNKNOWN'
        
        # Concentration score: how much of portfolio is driven by top agent
        top_agent_exposure = max_exposure
        
        # Risk assessment logic
        if max_exposure > 0.50:
            return 'CRITICAL'  # One agent drives >50% of parlays
        elif max_exposure > 0.40:
            return 'HIGH'  # One agent drives >40% of parlays
        elif high_exposure_agents >= 2:
            return 'ELEVATED'  # Multiple agents at 30%+ (no diversity)
        elif top_agent_exposure >= 0.30:
            return 'MODERATE'  # Top agent at 30% but others more balanced
        else:
            return 'LOW'  # Well-diversified across agents
    
    def _calculate_concentration_score(self, exposure_pcts: Dict[str, float]) -> float:
        """
        Calculate Herfindahl-Hirschman Index (HHI) for agent concentration
        HHI = sum of (exposure_pct)^2
        0 = perfect diversification, 1 = complete concentration
        """
        if not exposure_pcts:
            return 0.0
        
        hhi = sum(pct ** 2 for pct in exposure_pcts.values())
        return round(hhi, 3)
    
    def _get_primary_drivers(self, exposure_pcts: Dict[str, float]) -> List[Tuple[str, float]]:
        """Get agents sorted by exposure percentage"""
        return sorted(
            exposure_pcts.items(),
            key=lambda x: x[1],
            reverse=True
        )
    
    def _generate_recommendations(self, over_exposed: Dict[str, float], 
                                 exposure_pcts: Dict[str, float], 
                                 total_parlays: int) -> List[str]:
        """Generate actionable recommendations based on exposure analysis"""
        recommendations = []
        
        if not over_exposed:
            recommendations.append("✅ Portfolio is well-diversified across analytical agents")
            return recommendations
        
        # Generate warnings for each over-exposed agent
        for agent, exposure_pct in sorted(over_exposed.items(), key=lambda x: x[1], reverse=True):
            count = int(exposure_pct * total_parlays)
            recommendations.append(
                f"⚠️  {agent.upper()} appears in {count}/{total_parlays} parlays ({exposure_pct:.0%}) - "
                f"REDUCE by building {int(count * 0.5)} parlays from independent signals"
            )
        
        # Strategic recommendations
        if len(over_exposed) > 0:
            recommendations.append("\n🎯 Rebuild Strategy:")
            
            # Identify underutilized agents
            underutilized = {
                agent: pct 
                for agent, pct in exposure_pcts.items() 
                if pct <= 0.15
            }
            
            if underutilized:
                agents_list = ", ".join(sorted(underutilized.keys()))
                recommendations.append(
                    f"   • Force next parlays to use {agents_list} as primary drivers"
                )
            
            recommendations.append(
                "   • Remove high-confidence legs driven by over-exposed agents"
            )
            recommendations.append(
                "   • Substitute with lower-confidence legs from independent agents"
            )
        
        return recommendations
    
    def print_portfolio_risk_report(self):
        """Pretty-print the portfolio risk assessment"""
        if not self.portfolio_risk_report:
            print("❌ No portfolio analysis available. Run analyze_portfolio() first.")
            return
        
        report = self.portfolio_risk_report
        
        print("\n" + "="*80)
        print("📊 PORTFOLIO AGENT EXPOSURE ANALYSIS")
        print("="*80)
        
        print(f"\n📈 Total Parlays Analyzed: {report['total_parlays']}")
        print(f"🎯 Risk Level: {self._risk_color(report['risk_level'])} {report['risk_level']}")
        print(f"📉 Concentration Score (HHI): {report['portfolio_concentration_score']} "
              f"({'Low' if report['portfolio_concentration_score'] < 0.3 else 'High'} concentration)")
        
        print("\n🔍 Agent Exposure Breakdown:")
        print("-" * 80)
        
        for agent, pct in report['primary_drivers']:
            count = report['agent_appearance_count'][agent]
            bar_length = int(pct * 40)  # 40-char bar
            bar = "█" * bar_length + "░" * (40 - bar_length)
            
            # Color code based on exposure
            if pct > self.MAX_AGENT_EXPOSURE:
                status = "🔴 OVER-EXPOSED"
            elif pct > 0.25:
                status = "🟡 ELEVATED"
            else:
                status = "🟢 HEALTHY"
            
            print(f"{agent:12} {status:20} {bar} {pct:6.0%} ({count}/{report['total_parlays']})")
        
        print("\n⚠️  Alerts:")
        print("-" * 80)
        if report['over_exposed_agents']:
            for agent, pct in sorted(report['over_exposed_agents'].items(), key=lambda x: x[1], reverse=True):
                excess = (pct - self.MAX_AGENT_EXPOSURE) * report['total_parlays']
                print(f"🔴 {agent.upper()}: {pct:.0%} exposure (MAX: {self.MAX_AGENT_EXPOSURE:.0%})")
                print(f"   Need to reduce by ~{excess:.0f} parlays")
        else:
            print("✅ No over-exposed agents detected")
        
        print("\n💡 Recommendations:")
        print("-" * 80)
        for rec in report['recommendations']:
            print(rec)
        
        print("\n" + "="*80 + "\n")
    
    @staticmethod
    def _risk_color(risk_level: str) -> str:
        """Return emoji indicator for risk level"""
        colors = {
            'CRITICAL': '🔴',
            'HIGH': '🟠',
            'ELEVATED': '🟡',
            'MODERATE': '🟡',
            'LOW': '🟢',
            'UNKNOWN': '⚪'
        }
        return colors.get(risk_level, '⚪')


class AgentExposureLimiter:
    """
    Constrains parlay building to respect agent exposure limits
    Used to rebuild parlays when concentration is too high
    """
    
    def __init__(self, max_exposure: float = 0.40):
        self.max_exposure = max_exposure
        self.exposure_tracker = AgentExposureTracker()
    
    def should_rebuild_parlays(self, parlays_by_type: Dict[str, List[Parlay]]) -> Tuple[bool, str]:
        """
        Determine if portfolio needs rebuilding
        Returns (should_rebuild, reason)
        """
        report = self.exposure_tracker.analyze_portfolio(parlays_by_type)
        
        if report['over_exposed_agents']:
            reasons = [
                f"{agent.upper()} at {pct:.0%}"
                for agent, pct in report['over_exposed_agents'].items()
            ]
            return True, f"Agent over-exposure detected: {', '.join(reasons)}"
        
        return False, ""
    
    def get_exposure_report(self, parlays_by_type: Dict[str, List[Parlay]]) -> Dict:
        """Get detailed exposure report"""
        return self.exposure_tracker.analyze_portfolio(parlays_by_type)
    
    def print_report(self):
        """Print formatted exposure report"""
        self.exposure_tracker.print_portfolio_risk_report()
