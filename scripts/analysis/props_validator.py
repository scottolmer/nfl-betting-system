"""
Props Validator - Ensures all props are proper PlayerProp objects
Converts dicts to objects as needed

This module fixes the dict vs object issue by providing a validation layer
that automatically converts dictionary props to PlayerProp objects.
"""

from typing import Union, List, Optional
import logging

logger = logging.getLogger(__name__)


class PropsValidator:
    """Validates and converts props to proper object types"""
    
    @staticmethod
    def ensure_player_prop(prop: Union[dict, 'PlayerProp']) -> 'PlayerProp':
        """
        Ensure prop is a PlayerProp object, not a dict
        
        Safely converts dicts to PlayerProp objects while passing through
        objects unchanged. Returns a properly typed PlayerProp in either case.
        
        Args:
            prop: Either a dict or PlayerProp object
        
        Returns:
            PlayerProp: A PlayerProp object
        
        Raises:
            TypeError: If prop is neither dict nor PlayerProp
        
        Usage:
            prop = PropsValidator.ensure_player_prop(prop)  # Handle both dict and PlayerProp
            agent_result = agent.analyze(prop, context)     # Safe to call agent
        """
        # Import here to avoid circular imports
        from .models import PlayerProp
        
        if isinstance(prop, PlayerProp):
            return prop  # Already correct type
        
        if isinstance(prop, dict):
            # Convert dict to PlayerProp
            try:
                player_prop = PlayerProp(
                    player_name=prop.get('player_name', ''),
                    team=prop.get('team', ''),
                    opponent=prop.get('opponent', ''),
                    position=prop.get('position', ''),
                    stat_type=prop.get('stat_type', ''),
                    line=float(prop.get('line', 0)) if prop.get('line') is not None else 0,
                    game_total=float(prop.get('game_total')) if prop.get('game_total') is not None else None,
                    spread=float(prop.get('spread')) if prop.get('spread') is not None else None,
                    is_home=prop.get('is_home', True),
                    week=int(prop.get('week', 8)),
                    direction=prop.get('direction', 'OVER'),
                    bet_type=prop.get('bet_type', 'OVER'),
                )
                logger.debug(f"✓ Converted dict to PlayerProp: {player_prop.player_name}")
                return player_prop
            except Exception as e:
                logger.error(f"❌ Failed to convert dict to PlayerProp: {e}")
                raise
        
        raise TypeError(f"Cannot convert {type(prop)} to PlayerProp. Expected dict or PlayerProp.")
    
    @staticmethod
    def ensure_all_player_props(props: List[Union[dict, 'PlayerProp']]) -> List['PlayerProp']:
        """
        Ensure all props in a list are PlayerProp objects
        
        Converts any dicts in the list to PlayerProp objects.
        
        Args:
            props: List of dicts or PlayerProp objects
        
        Returns:
            List[PlayerProp]: List of properly typed PlayerProp objects
        
        Usage:
            props = PropsValidator.ensure_all_player_props(props)
        """
        return [PropsValidator.ensure_player_prop(p) for p in props]
    
    @staticmethod
    def validate_prop_analysis(analysis: 'PropAnalysis') -> 'PropAnalysis':
        """
        Validate that PropAnalysis.prop is a PlayerProp object
        Converts if needed
        
        Args:
            analysis: PropAnalysis object that might have dict prop
        
        Returns:
            PropAnalysis: Same analysis but with guaranteed PlayerProp object
        
        Usage:
            analysis = PropsValidator.validate_prop_analysis(analysis)
            assert isinstance(analysis.prop, PlayerProp)
        """
        from .models import PlayerProp, PropAnalysis
        
        if not isinstance(analysis.prop, PlayerProp):
            logger.debug(f"Converting PropAnalysis.prop from {type(analysis.prop).__name__} to PlayerProp")
            analysis.prop = PropsValidator.ensure_player_prop(analysis.prop)
        
        return analysis
    
    @staticmethod
    def validate_all_analyses(analyses: List['PropAnalysis']) -> List['PropAnalysis']:
        """
        Validate all PropAnalysis objects have PlayerProp props
        
        Ensures every PropAnalysis in the list has a proper PlayerProp object.
        
        Args:
            analyses: List of PropAnalysis objects
        
        Returns:
            List[PropAnalysis]: Same list but with all props validated
        
        Usage:
            results = PropsValidator.validate_all_analyses(results)
        """
        return [PropsValidator.validate_prop_analysis(a) for a in analyses]
    
    @staticmethod
    def validate_parlay_legs(parlay: 'Parlay') -> 'Parlay':
        """
        Validate all legs in a parlay have correct prop types
        
        Args:
            parlay: Parlay object
        
        Returns:
            Parlay: Same parlay but with all legs validated
        """
        if hasattr(parlay, 'legs'):
            parlay.legs = PropsValidator.validate_all_analyses(parlay.legs)
        return parlay
    
    @staticmethod
    def validate_all_parlays(parlays: dict) -> dict:
        """
        Validate all parlays in a parlays dict
        
        Args:
            parlays: Dict of parlay type -> list of Parlay objects
        
        Returns:
            dict: Same dict structure but with all parlays validated
        """
        for ptype in parlays:
            parlays[ptype] = [PropsValidator.validate_parlay_legs(p) for p in parlays[ptype]]
        return parlays


# Safety wrapper for agent input
def safe_agent_call(agent, prop: Union[dict, 'PlayerProp'], context: dict):
    """
    Safely call an agent with proper prop type
    Handles dict-to-object conversion automatically
    
    Use this instead of agent.analyze() directly for extra safety.
    
    Args:
        agent: Agent instance
        prop: Prop as dict or PlayerProp
        context: Context dict
    
    Returns:
        Tuple: (score, direction, rationale)
    
    Usage:
        result = safe_agent_call(dvoa_agent, prop_dict, context)
        score, direction, rationale = result
    """
    prop_obj = PropsValidator.ensure_player_prop(prop)
    return agent.analyze(prop_obj, context)
