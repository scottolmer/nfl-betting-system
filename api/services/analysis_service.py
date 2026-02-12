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
        pure wrapper around PropAnalyzer.
        """
        # Check cache first
        cache_key = f"props_week_{week}_conf_{min_confidence}"
        cached_data = await cache_get(cache_key)

        analyses_responses = []

        if cached_data:
            logger.info(f"✓ Cache HIT for week {week}, min_confidence {min_confidence}")
            try:
                # Deserialize cached JSON list of dicts into Pydantic models
                analyses_responses = [PropAnalysisResponse(**item) for item in json.loads(cached_data)]
            except Exception as e:
                logger.error(f"Cache deserialization failed: {e}")
                cached_data = None # Force re-analysis

        if not cached_data:
            logger.info(f"Cache MISS - analyzing props for week {week}...")

            # Load data using EXISTING loader
            logger.info(f"Loading data for week {week}...")
            context = self.loader.load_all_data(week=week)

            # Analyze using EXISTING analyzer
            logger.info(f"Analyzing props with min_confidence={min_confidence}...")
            analyses = self.analyzer.analyze_all_props(context, min_confidence=min_confidence)

            # Convert to responses
            analyses_responses = [self._to_response(a) for a in analyses]

            # Cache the responses
            cache_data = json.dumps([r.model_dump() for r in analyses_responses])
            await cache_set(cache_key, cache_data, expire=settings.cache_ttl_seconds)
            logger.info(f"✓ Cached {len(analyses_responses)} props for week {week}")

        # --- Filtering ---
        filtered = analyses_responses

        # Confidence range
        if max_confidence is not None:
            filtered = [a for a in filtered if a.confidence <= max_confidence]

        # Team filtering
        if teams:
            team_list = [t.strip().upper() for t in teams.split(',')]
            filtered = [a for a in filtered if a.team.upper() in team_list]
        elif team:
            filtered = [a for a in filtered if a.team.upper() == team.upper()]

        # Position filtering
        if positions:
            position_list = [p.strip().upper() for p in positions.split(',')]
            filtered = [a for a in filtered if a.position.upper() in position_list]
        elif position:
            filtered = [a for a in filtered if a.position == position]

        # Other filters
        if stat_type:
            if stat_type == 'TDs':
                # Fuzzy match for TDs (Pass TDs, Rush TDs, Rec TDs)
                filtered = [a for a in filtered if 'TD' in a.stat_type]
                logger.info(f"After TD filter: {len(filtered)} matches")
                if not filtered:
                    # DEBUG: Exfiltrate available stat types via error
                    available = list(set([a.stat_type for a in analyses_responses]))
                    raise ValueError(f"DEBUG: Found 0 matches for TDs. Available types: {available}")
            else:
                # Try strict match first, then fuzzy match if no results
                strict_matches = [a for a in filtered if a.stat_type == stat_type]
                if strict_matches:
                    filtered = strict_matches
                else:
                    # Fuzzy match (e.g. "Pass Yds" matches "player_pass_yds")
                    filtered = [a for a in filtered if stat_type.lower().replace(' ', '') in a.stat_type.lower().replace('_', '').replace(' ', '')]
        if bet_type:
            filtered = [a for a in filtered if a.bet_type.upper() == bet_type.upper()]

        # Sort by confidence descending
        filtered.sort(key=lambda a: a.confidence, reverse=True)

        # Apply limit
        if limit:
            filtered = filtered[:limit]

        logger.info(f"✓ Returning {len(filtered)} props after filters")
        return filtered

    async def get_raw_analyses_for_week(
        self,
        week: int,
        min_confidence: int = 60,
        team: Optional[str] = None
    ) -> List[PropAnalysis]:
        """
        Get raw PropAnalysis objects (not converted to API responses).
        Used by parlay generation which needs the full PropAnalysis objects.
        """
        logger.info(f"Getting raw analyses for week {week}...")

        # Load data using EXISTING loader
        context = self.loader.load_all_data(week=week)

        # Analyze using EXISTING analyzer - returns List[PropAnalysis]
        analyses = self.analyzer.analyze_all_props(context, min_confidence=min_confidence)

        # Apply team filter if provided
        if team:
            analyses = [a for a in analyses if a.team.upper() == team.upper()]

        logger.info(f"✓ Returning {len(analyses)} raw PropAnalysis objects")
        return analyses

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

    def get_player_odds(self, week: int, player_name: str, stat_type: str) -> List[dict]:
        """
        Get odds for a specific player and stat type from the raw betting lines.
        Returns a list of odds entries (one per book/line).
        """
        # Load data (this is cached by the loader logic or we rely on OS caching)
        context = self.loader.load_all_data(week=week)
        
        df = context.get('betting_lines_raw')
        if df is None or df.empty:
            return []

        # Filter by player and stat_type
        from scripts.analysis.data_loader import normalize_name
        target_name = normalize_name(player_name)
        
        results = []
        
        for _, row in df.iterrows():
            # Handle variable column names
            p_name = row.get('player_name') or row.get('description')
            row_player = normalize_name(str(p_name or ''))
            
            if not row_player or target_name not in row_player: 
                # Use "in" check for "Patrick Mahomes II" vs "Patrick Mahomes"
                if row_player not in target_name: 
                     continue
                
            s_type = row.get('stat_type') or row.get('market')
            row_stat = str(s_type or '')
            
            # Simple normalization: remove spaces, lowercase, underscores
            rs_norm = row_stat.lower().replace(' ', '').replace('_', '')
            st_norm = stat_type.lower().replace(' ', '').replace('_', '')
            
            # Check for match (e.g. 'playerpassyds' vs 'passyds')
            match = False
            if rs_norm == st_norm:
                match = True
            elif f"player{st_norm}" == rs_norm:
                match = True
            elif st_norm in rs_norm and len(st_norm) > 3: # loose match
                match = True
                
            if not match:
                continue

            # Extract values with fallbacks
            line = row.get('line') if row.get('line') is not None else row.get('point')
            price = row.get('odds') if row.get('odds') is not None else row.get('price')
            side = row.get('direction') or row.get('label')
            
            if line is None or price is None:
                continue

            results.append({
                "book": row.get('bookmaker', 'Unknown'),
                "line": float(line),
                "price": int(float(price)), 
                "side": str(side).lower(), # 'Over' or 'Under'
                "timestamp": str(row.get('fetch_time', '') or row.get('last_update', ''))
            })
            
        return results
