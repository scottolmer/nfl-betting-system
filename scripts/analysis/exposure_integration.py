"""
Integration layer for agent exposure tracking into parlay builder workflow
Hooks into the parlay building process to detect and report portfolio concentration risk
"""

from typing import Dict, List, Tuple
from .agent_exposure_tracker import AgentExposureTracker, AgentExposureLimiter
from .models import Parlay
import logging

logger = logging.getLogger(__name__)


class ExposureIntegrationManager:
    """
    Main integration point for exposure tracking in the parlay building workflow
    """
    
    def __init__(self):
        self.exposure_limiter = AgentExposureLimiter()
        self.last_report = None
    
    def analyze_and_report(self, parlays_by_type: Dict[str, List[Parlay]]) -> Dict:
        """
        Main entry point: analyze parlays for concentration risk and generate report
        Returns detailed report that can be printed or used for rebuilding decisions
        """
        logger.info("📊 Analyzing agent exposure across portfolio...")
        
        report = self.exposure_limiter.get_exposure_report(parlays_by_type)
        self.last_report = report
        
        return report
    
    def should_rebuild(self) -> Tuple[bool, str]:
        """
        Check if portfolio needs rebuilding due to concentration risk
        Returns (should_rebuild, reason)
        """
        if self.last_report is None:
            return False, "No portfolio analyzed yet"
        
        if self.last_report.get('over_exposed_agents'):
            reasons = [
                f"{agent.upper()} at {pct:.0%}"
                for agent, pct in self.last_report['over_exposed_agents'].items()
            ]
            return True, f"Over-exposure: {', '.join(reasons)}"
        
        return False, ""
    
    def print_full_report(self):
        """Print formatted portfolio risk report"""
        self.exposure_limiter.print_report()
    
    def get_summary_line(self) -> str:
        """Get one-liner summary for quick reference"""
        if self.last_report is None:
            return "❌ No portfolio analyzed"
        
        risk_level = self.last_report.get('risk_level', 'UNKNOWN')
        risk_emoji = {
            'CRITICAL': '🔴',
            'HIGH': '🟠',
            'ELEVATED': '🟡',
            'MODERATE': '🟡',
            'LOW': '🟢',
            'UNKNOWN': '⚪'
        }.get(risk_level, '⚪')
        
        primary_drivers = self.last_report.get('primary_drivers', [])
        if not primary_drivers:
            return f"{risk_emoji} Portfolio Risk: {risk_level} (No drivers identified)"
        
        top_agent = primary_drivers[0][0]
        top_pct = primary_drivers[0][1]
        
        return f"{risk_emoji} Portfolio Risk: {risk_level} | Top Driver: {top_agent} ({top_pct:.0%})"


class ParalayRebuildConstraints:
    """
    Constraints for rebuilding parlays to reduce agent concentration
    Used to guide next parlay generation when concentration is too high
    """
    
    def __init__(self, exposure_report: Dict):
        self.report = exposure_report
        self.over_exposed_agents = exposure_report.get('over_exposed_agents', {})
        self.underutilized_agents = self._identify_underutilized()
    
    def _identify_underutilized(self) -> Dict[str, float]:
        """Find agents that appear in <15% of parlays"""
        exposure_pcts = self.report.get('agent_exposure', {})
        return {
            agent: pct 
            for agent, pct in exposure_pcts.items() 
            if pct <= 0.15
        }
    
    def get_rebuild_strategy(self) -> Dict:
        """
        Generate strategy for rebuilding parlays to reduce concentration
        Returns actionable guidance for next parlay builder run
        """
        total_parlays = self.report.get('total_parlays', 10)
        
        strategy = {
            'status': 'REBUILD_REQUIRED' if self.over_exposed_agents else 'NO_REBUILD_NEEDED',
            'agents_to_reduce': {},
            'agents_to_increase': {},
            'total_parlays': total_parlays,
            'guidelines': []
        }
        
        if not self.over_exposed_agents:
            strategy['guidelines'].append("✅ Portfolio is well-diversified - no rebuild needed")
            return strategy
        
        # For each over-exposed agent, calculate reduction target
        for agent, current_pct in self.over_exposed_agents.items():
            current_count = int(current_pct * total_parlays)
            target_pct = 0.30  # Target 30% as max
            target_count = int(target_pct * total_parlays)
            reduction_needed = current_count - target_count
            
            strategy['agents_to_reduce'][agent] = {
                'current_count': current_count,
                'target_count': target_count,
                'reduction_needed': reduction_needed,
                'current_pct': current_pct,
                'target_pct': target_pct
            }
            
            strategy['guidelines'].append(
                f"🎯 {agent}: Reduce from {current_count} → {target_count} parlays"
            )
        
        # For each underutilized agent, suggest increased use
        for agent, current_pct in self.underutilized_agents.items():
            current_count = int(current_pct * total_parlays)
            target_pct = 0.25  # Target 25% for underutilized
            target_count = int(target_pct * total_parlays)
            
            strategy['agents_to_increase'][agent] = {
                'current_count': current_count,
                'target_count': target_count,
                'increase_needed': target_count - current_count,
                'current_pct': current_pct,
                'target_pct': target_pct
            }
            
            strategy['guidelines'].append(
                f"📈 {agent}: Increase from {current_count} → {target_count} parlays"
            )
        
        strategy['guidelines'].append(
            f"\n💡 Strategy: Build {sum(r['reduction_needed'] for r in strategy['agents_to_reduce'].values())} "
            f"new parlays prioritizing {', '.join(strategy['agents_to_increase'].keys())}"
        )
        
        return strategy
    
    def print_rebuild_strategy(self):
        """Print formatted rebuild strategy"""
        strategy = self.get_rebuild_strategy()
        
        print("\n" + "="*80)
        print("🛠️  PORTFOLIO REBUILD STRATEGY")
        print("="*80)
        print(f"\nStatus: {strategy['status']}")
        
        if strategy['status'] == 'NO_REBUILD_NEEDED':
            print("\n✅ Portfolio is well-diversified - keep current approach")
            return
        
        print(f"\nTotal Parlays: {strategy['total_parlays']}")
        
        if strategy['agents_to_reduce']:
            print("\n🔴 Agents to Reduce:")
            for agent, data in strategy['agents_to_reduce'].items():
                print(f"   {agent:12} {data['current_count']} → {data['target_count']} "
                      f"({data['current_pct']:.0%} → {data['target_pct']:.0%})")
        
        if strategy['agents_to_increase']:
            print("\n🟢 Agents to Increase:")
            for agent, data in strategy['agents_to_increase'].items():
                print(f"   {agent:12} {data['current_count']} → {data['target_count']} "
                      f"(+{data['increase_needed']} parlays)")
        
        print("\n📋 Implementation Guidelines:")
        for guideline in strategy['guidelines']:
            print(f"   {guideline}")
        
        print("\n" + "="*80 + "\n")


def integrate_exposure_tracking_into_run_py(parlay_optimizer_output: Dict) -> None:
    """
    Post-processing hook to run exposure tracking after parlay optimization
    Can be called after optimizer.rebuild_parlays_low_correlation() in run.py
    """
    
    # Extract parlays from optimizer output structure
    if 'parlays' in parlay_optimizer_output:
        # Format from optimizer.rebuild_parlays_low_correlation
        parlays_by_type = parlay_optimizer_output['parlays']
    else:
        logger.warning("Unable to extract parlays from optimizer output")
        return
    
    # Analyze exposure
    manager = ExposureIntegrationManager()
    report = manager.analyze_and_report(parlays_by_type)
    
    # Print summary
    print("\n" + manager.get_summary_line())
    
    # If over-exposed, print full analysis
    if report.get('over_exposed_agents'):
        manager.print_full_report()
        
        # Generate and print rebuild strategy
        constraints = ParalayRebuildConstraints(report)
        constraints.print_rebuild_strategy()


# Convenient export for use in run.py
__all__ = [
    'ExposureIntegrationManager',
    'ParalayRebuildConstraints',
    'integrate_exposure_tracking_into_run_py',
]
