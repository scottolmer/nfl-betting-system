"""
Agent Calibration - Weekly performance tracking and Claude-powered agent weighting
"""

import os
from anthropic import Anthropic
from typing import Dict, List
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentCalibrator:
    """Tracks agent accuracy and recommends weight adjustments"""
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = "claude-sonnet-4-20250514"
    
    def analyze_agent_performance(self, performance_data: Dict[str, List[Dict]]) -> Dict:
        """
        Analyze which agents performed best/worst this week
        
        Args:
            performance_data: {
                'agent_name': [
                    {'confidence': 65, 'prediction': 'OVER', 'actual': 'OVER', 'hit': True, 'line': 250, 'actual_value': 275},
                    ...
                ]
            }
        
        Returns:
            {
                'accuracy': {agent: accuracy%},
                'top_agents': [agents],
                'struggling_agents': [agents],
                'weight_recommendations': {agent: new_weight},
                'analysis': str
            }
        """
        prompt = f"""Analyze NFL betting agent performance data.

PERFORMANCE DATA:
{json.dumps(performance_data, indent=2)[:2000]}

Analyze:
1. Accuracy % for each agent (correct predictions / total)
2. Hit rate on high-confidence predictions (>65%)
3. Which agent predictions correlate best with wins
4. Which agents are over/under-confident

Return JSON:
{{
  "accuracy": {{"DVOA": 0.65, "Matchup": 0.62, ...}},
  "top_performers": ["agent1", "agent2"],
  "needs_improvement": ["agent3"],
  "confidence_calibration": {{"DVOA": "overconfident", "Matchup": "well_calibrated"}},
  "weight_recommendations": {{"DVOA": 1.5, "Matchup": 1.2, ...}},
  "key_finding": "<1-2 sentences about this week's trends>",
  "recommendation": "<action to improve next week>"
}}

Current weights are all 1.0. Recommend 0.5-2.0 based on accuracy.
Higher weight = agent more accurate.

RESPOND ONLY WITH JSON."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(response_text)
            logger.info(f"Agent calibration analysis complete")
            return result
            
        except Exception as e:
            logger.error(f"Agent performance analysis failed: {e}")
            return {
                'accuracy': {},
                'top_performers': [],
                'needs_improvement': [],
                'weight_recommendations': {},
                'recommendation': f'Could not analyze: {str(e)}'
            }
    
    def generate_weekly_calibration_report(self, week: int, performance_summary: Dict) -> str:
        """
        Generate human-readable weekly calibration report
        
        Returns formatted report with agent rankings and recommendations
        """
        prompt = f"""Generate a weekly betting system calibration report.

WEEK: {week}
SUMMARY:
{json.dumps(performance_summary, indent=2)[:1500]}

Write a 3-4 paragraph report covering:
1. Top performing agents and why
2. Struggling agents and suspected causes
3. Recommended weight adjustments
4. Strategy adjustments for next week

Be specific and actionable. Format as markdown.
No JSON in response - just the report text."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            
            report = response.content[0].text.strip()
            logger.info(f"Generated calibration report for week {week}")
            return report
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return f"Could not generate report: {str(e)}"
    
    def compare_to_historical(self, current_week: int, historical_performance: Dict[int, Dict]) -> Dict:
        """
        Compare current week to historical trends
        
        Returns insights on seasonal patterns
        """
        prompt = f"""Analyze NFL betting system trends across season.

CURRENT WEEK: {current_week}
HISTORICAL DATA (weeks 1-{current_week-1}):
{json.dumps(historical_performance, indent=2)[:2000]}

Return JSON:
{{
  "seasonal_trend": "<improving/declining/stable>",
  "best_agents_historically": ["agent1", "agent2"],
  "most_volatile_agent": "agent_name",
  "accuracy_trend": "<getting better or worse over time>",
  "week_{current_week}_prediction": "<expected accuracy range>",
  "recommendation": "<strategic adjustment for rest of season>"
}}

RESPOND ONLY WITH JSON."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(response_text)
            return result
            
        except Exception as e:
            logger.error(f"Historical comparison failed: {e}")
            return {'seasonal_trend': 'unknown', 'recommendation': f'Error: {str(e)}'}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    calibrator = AgentCalibrator()
    
    # Test with sample performance data
    sample_performance = {
        'DVOA': [
            {'confidence': 70, 'prediction': 'OVER', 'actual': 'OVER', 'hit': True},
            {'confidence': 65, 'prediction': 'UNDER', 'actual': 'OVER', 'hit': False},
            {'confidence': 75, 'prediction': 'OVER', 'actual': 'OVER', 'hit': True},
        ],
        'Matchup': [
            {'confidence': 60, 'prediction': 'OVER', 'actual': 'OVER', 'hit': True},
            {'confidence': 55, 'prediction': 'UNDER', 'actual': 'UNDER', 'hit': True},
        ],
    }
    
    analysis = calibrator.analyze_agent_performance(sample_performance)
    print("Agent Analysis:", json.dumps(analysis, indent=2))
