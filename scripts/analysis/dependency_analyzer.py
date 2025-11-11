"""Dependency Analyzer - Claude-powered correlation detection in parlays"""
import json
import logging
import os
from typing import List, Dict, Optional

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from .models import PropAnalysis, Parlay

logger = logging.getLogger(__name__)


class DependencyAnalyzer:
    """Analyzes parlay dependencies using Claude API - CONSERVATIVE approach"""

    def __init__(self, api_key: Optional[str] = None):
        if not ANTHROPIC_AVAILABLE:
            logger.warning("anthropic package not installed")
            self.client = None
            return
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"

    def analyze_parlay_dependencies(self, parlay: Parlay) -> Dict:
        """Analyze a single parlay for dependencies"""
        if not self.client:
            return {
                "adjusted_confidence": parlay.combined_confidence,
                "recommendation": "ACCEPT",
                "dependency_chains": [],
                "correlation_adjustment": {"adjustment_value": 0}
            }
        
        legs_context = self._build_legs_context(parlay)
        analysis_result = self._get_claude_analysis(parlay, legs_context)
        return self._parse_claude_response(analysis_result)

    def _build_legs_context(self, parlay: Parlay) -> str:
        """Build context about parlay legs"""
        context_lines = []
        for i, leg in enumerate(parlay.legs, 1):
            prop = leg.prop
            context_lines.append(f"Leg {i}: {prop.player_name}")
            context_lines.append(f"  Position: {prop.position}")
            context_lines.append(f"  {prop.stat_type} OVER {prop.line}")
            context_lines.append(f"  {prop.team} vs {prop.opponent}")
            context_lines.append(f"  Confidence: {leg.final_confidence}%")
        return "\n".join(context_lines)

    def _get_claude_analysis(self, parlay: Parlay, legs_context: str) -> str:
        """Get Claude analysis of dependencies - CONSERVATIVE SCORING"""
        prompt = f"""Analyze this NFL parlay for REAL correlations (not speculative ones).

Parlay Type: {parlay.parlay_type}
Combined Confidence: {parlay.combined_confidence}%

Legs:
{legs_context}

CRITICAL RULES - Be conservative:
- Do NOT penalize for different players in same game (they're independent)
- Do NOT penalize for "potential" game script effects (too speculative)
- DO penalize only for OBVIOUS dependencies:
  * SAME PLAYER in multiple legs = Correlation
  * Same QB + same target (even different stat type) = Minor correlation only
  * Same defense being targeted by multiple props = Minor correlation only

Adjustment guidelines:
- No real dependencies = ACCEPT, adjustment 0
- Minor/speculative correlations = ACCEPT, adjustment 0 (don't penalize speculation)
- Clear same-player dependencies = MODIFY, adjustment -2 to -3
- Multiple same-player dependencies = MODIFY, adjustment -3 to -5
- Parlays that break with one player failure = AVOID, adjustment -5

Return ONLY valid JSON:
{{"adjusted_confidence": 50-100, "recommendation": "ACCEPT/MODIFY/AVOID", "correlation_adjustment": {{"adjustment_value": -5 to 5, "reasoning": ""}}, "dependency_chains": [], "risk_flags": []}}"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return "{}"

    def _parse_claude_response(self, text: str) -> Dict:
        """Parse Claude JSON response with bounds checking"""
        try:
            text = text.strip()
            
            # Remove markdown code blocks if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            text = text.strip()
            data = json.loads(text)
            
            # Ensure required fields
            data.setdefault("adjusted_confidence", 50)
            data.setdefault("recommendation", "REVIEW")
            data.setdefault("dependency_chains", [])
            data.setdefault("correlation_adjustment", {"adjustment_value": 0})
            
            # BOUNDS CHECK: Ensure adjustments don't exceed -5 to +5 range
            adj_value = data["correlation_adjustment"].get("adjustment_value", 0)
            data["correlation_adjustment"]["adjustment_value"] = max(-5, min(5, adj_value))
            
            # BOUNDS CHECK: Ensure confidence is 0-100
            conf = data.get("adjusted_confidence", 50)
            data["adjusted_confidence"] = max(0, min(100, conf))
            
            return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return {
                "adjusted_confidence": 50,
                "recommendation": "REVIEW",
                "dependency_chains": [],
                "correlation_adjustment": {"adjustment_value": 0}
            }

    def analyze_all_parlays(self, parlays: Dict[str, List[Parlay]]) -> Dict:
        """Analyze all parlays for dependencies"""
        result = {"2-leg": [], "3-leg": [], "4-leg": [], "5-leg": []}
        
        for ptype in ["2-leg", "3-leg", "4-leg", "5-leg"]:
            for i, parlay in enumerate(parlays.get(ptype, []), 1):
                analysis = self.analyze_parlay_dependencies(parlay)
                result[ptype].append({
                    "parlay": parlay,
                    "dependency_analysis": analysis
                })
                
                rec = analysis.get('recommendation')
                print(f"  ✓ {ptype} Parlay {i}: {rec}")
        
        return result

    def generate_dependency_report(self, analyzed_parlays: Dict) -> str:
        """Generate summary report"""
        lines = ["", "=" * 70, "🔍 PARLAY DEPENDENCY ANALYSIS", "=" * 70, ""]
        
        for ptype in ["2-leg", "3-leg", "4-leg", "5-leg"]:
            items = analyzed_parlays.get(ptype, [])
            if not items:
                continue
            
            lines.append(f"\n{ptype.upper()} PARLAYS ({len(items)} total)")
            lines.append("-" * 70)
            
            for item in items:
                analysis = item["dependency_analysis"]
                adj = analysis.get("adjusted_confidence", 50)
                rec = analysis.get("recommendation", "REVIEW")
                emoji = "✅" if rec == "ACCEPT" else "⚠️" if rec == "MODIFY" else "❌"
                lines.append(f"  {emoji} {rec}: Confidence {adj}%")
        
        lines.append("")
        lines.append("=" * 70)
        return "\n".join(lines)
