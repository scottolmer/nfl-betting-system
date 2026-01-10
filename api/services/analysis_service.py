"""Analysis Service - Wraps existing PropAnalyzer for API use (100% code reuse)"""

from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.models import PropAnalysis
from api.schemas.props import PropAnalysisResponse
from api.core.cache import cache_get, cache_set
from api.config import settings
from typing import List, Optional
import logging
import json

logger = logging.getLogger(__name__)


class AnalysisService:
    """
    Service layer wrapping existing analysis engine.

    This class provides a thin wrapper around the existing PropAnalyzer
    and NFLDataLoader classes, achieving 100% code reuse of the analysis logic.
    No changes are made to the underlying agent system.
    """

    def __init__(self, data_dir: str = "data"):
        """Initialize service with existing analyzers"""
        self.analyzer = PropAnalyzer(use_dynamic_weights=True)
        self.loader = NFLDataLoader(data_dir=data_dir)
        logger.info("✓ AnalysisService initialized (reusing PropAnalyzer + NFLDataLoader)")

    async def analyze_props_for_week(
        self,
        week: int,
        min_confidence: int = 60,
        max_confidence: Optional[int] = None,
        team: Optional[str] = None,
        teams: Optional[str] = None,
        position: Optional[str] = None,
        positions: Optional[str] = None,
        stat_type: Optional[str] = None,
        bet_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[PropAnalysisResponse]:
        """
        Analyze props with filters using EXISTING analysis engine.

        NO CHANGES to PropAnalyzer or agents - pure wrapper.
        Uses existing 9-agent system:
        - DVOA (team efficiency)
        - Matchup (position-specific defense)
        - Volume (snap/target share)
        - GameScript (game total/spread)
        - Injury (health status)
        - Trend (recent performance)
        - Variance (prop reliability)
        - HitRate (historical accuracy)
        - Weather (disabled)

        Args:
            week: NFL week number (1-18)
            min_confidence: Minimum confidence threshold (0-100)
            max_confidence: Maximum confidence threshold (0-100), optional
            team: Filter by single team abbreviation (e.g., "KC")
            teams: Filter by multiple teams, comma-separated (e.g., "KC,BUF,DET")
            position: Filter by single position (QB, WR, RB, TE)
            positions: Filter by multiple positions, comma-separated (e.g., "QB,WR")
            stat_type: Filter by stat type (Pass Yds, Rush Yds, etc.)
            bet_type: Filter by OVER or UNDER
            limit: Maximum number of results to return

        Returns:
            List of PropAnalysisResponse objects
        """
        # Check cache first (cache key based on week and min_confidence)
        cache_key = f"props_week_{week}_conf_{min_confidence}"
        cached_data = await cache_get(cache_key)

        if cached_data:
            logger.info(f"✓ Cache HIT for week {week}, min_confidence {min_confidence}")
            analyses_data = json.loads(cached_data)
            # Reconstruct PropAnalysis objects from cached data (for filtering)
            # For now, we'll cache the final responses instead to avoid reconstruction
        else:
            logger.info(f"Cache MISS - analyzing props for week {week}...")

            # Load data using EXISTING loader (100% reuse)
            logger.info(f"Loading data for week {week}...")
            context = self.loader.load_all_data(week=week)

            # Analyze using EXISTING analyzer (100% reuse)
            logger.info(f"Analyzing props with min_confidence={min_confidence}...")
            analyses = self.analyzer.analyze_all_props(context, min_confidence=min_confidence)

            # Convert to responses before caching
            all_responses = [self._to_response(a) for a in analyses]

            # Cache the responses (serialized as JSON)
            cache_data = json.dumps([r.model_dump() for r in all_responses])
            await cache_set(cache_key, cache_data, expire=settings.cache_ttl_seconds)
            logger.info(f"✓ Cached {len(all_responses)} props for week {week}")

            # Set analyses variable for filtering below
            analyses_responses = all_responses

        # If we got cached data, deserialize it
        if cached_data:
            analyses_responses = [PropAnalysisResponse(**data) for data in analyses_data]

        # Apply filters
        filtered = analyses_responses

        # Confidence range filtering
        if max_confidence is not None:
            filtered = [a for a in filtered if a.confidence <= max_confidence]

        # Team filtering (single or multiple)
        if teams:
            # Multiple teams (comma-separated)
            team_list = [t.strip().upper() for t in teams.split(',')]
            filtered = [a for a in filtered if a.team.upper() in team_list]
        elif team:
            # Single team (backward compatibility)
            filtered = [a for a in filtered if a.team.upper() == team.upper()]

        # Position filtering (single or multiple)
        if positions:
            # Multiple positions (comma-separated)
            position_list = [p.strip().upper() for p in positions.split(',')]
            filtered = [a for a in filtered if a.position.upper() in position_list]
        elif position:
            # Single position (backward compatibility)
            filtered = [a for a in filtered if a.position == position]

        # Other filters (stat_type, bet_type)
        if stat_type:
            filtered = [a for a in filtered if a.stat_type == stat_type]
        if bet_type:
            filtered = [a for a in filtered if a.bet_type.upper() == bet_type.upper()]

        # Sort by confidence descending
        filtered.sort(key=lambda a: a.confidence, reverse=True)

        # Apply limit
        if limit:
            filtered = filtered[:limit]

        logger.info(f"✓ Returning {len(filtered)} props after filters")

        return filtered

    async def adjust_line_and_recalculate(
        self,
        week: int,
        player_name: str,
        stat_type: str,
        bet_type: str,
        original_line: float,
        new_line: float
    ) -> dict:
        """
        Adjust line for Pick 6 compatibility and recalculate confidence.

        This is critical for Pick 6 platforms where lines differ from regular props.
        Example: Kelce 56.5 yards (regular) vs 58.5 yards (Pick 6)

        Returns both original and adjusted confidence scores.
        """
        logger.info(f"Adjusting line for {player_name} {stat_type} from {original_line} to {new_line}")

        # Load data for the week
        context = self.loader.load_all_data(week=week)

        # Find the prop in the betting lines
        player_name_normalized = player_name.lower().strip()
        matching_props = [
            p for p in context.get('props', [])
            if p.get('player', '').lower().strip() == player_name_normalized
            and p.get('stat_type') == stat_type
            and p.get('bet_type', '').upper() == bet_type.upper()
        ]

        if not matching_props:
            raise ValueError(f"No prop found for {player_name} {stat_type} {bet_type} in week {week}")

        # Get the first matching prop
        prop_data = matching_props[0]

        # Analyze with original line
        original_prop_data = prop_data.copy()
        original_prop_data['line'] = original_line
        original_analysis = self.analyzer.analyze_prop(original_prop_data, context)

        # Analyze with adjusted line
        adjusted_prop_data = prop_data.copy()
        adjusted_prop_data['line'] = new_line
        adjusted_analysis = self.analyzer.analyze_prop(adjusted_prop_data, context)

        return {
            "player_name": original_analysis.prop.player_name,
            "team": original_analysis.prop.team,
            "stat_type": original_analysis.prop.stat_type,
            "bet_type": original_analysis.prop.bet_type,
            "original_line": original_line,
            "new_line": new_line,
            "original_confidence": original_analysis.final_confidence,
            "adjusted_confidence": adjusted_analysis.final_confidence,
            "confidence_change": adjusted_analysis.final_confidence - original_analysis.final_confidence,
            "recommendation": adjusted_analysis.recommendation
        }

    def _to_response(self, analysis: PropAnalysis) -> PropAnalysisResponse:
        """Convert PropAnalysis dataclass to Pydantic response schema"""
        return PropAnalysisResponse(
            player_name=analysis.prop.player_name,
            team=analysis.prop.team,
            opponent=analysis.prop.opponent,
            position=analysis.prop.position,
            stat_type=analysis.prop.stat_type,
            bet_type=analysis.prop.bet_type,
            line=analysis.prop.line,
            confidence=analysis.final_confidence,
            recommendation=analysis.recommendation,
            edge_explanation=analysis.edge_explanation,
            agent_breakdown={
                agent: {
                    "score": result["raw_score"],
                    "weight": result["weight"],
                    "direction": result["direction"]
                }
                for agent, result in analysis.agent_breakdown.items()
            }
        )
