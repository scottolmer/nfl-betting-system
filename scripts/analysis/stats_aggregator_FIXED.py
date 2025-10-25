"""
Fixed Stats Aggregator - Normalizes player names to match betting lines
"""

import logging
import re

logger = logging.getLogger(__name__)


def normalize_player_name(name: str) -> str:
    """
    Normalize player names to match betting lines format.
    
    CSV format: "Justin  Jefferson" (double space)
    Betting format: "justin jefferson" (lowercase, single space)
    
    This function:
    1. Strips leading/trailing whitespace
    2. Collapses multiple spaces to single space
    3. Converts to lowercase
    """
    if not name or not isinstance(name, str):
        return ""
    
    # Strip, collapse spaces, and lowercase
    normalized = re.sub(r'\s+', ' ', name.strip()).lower()
    
    return normalized


def extract_usage_stats(df, stat_type="receiving"):
    """Extract usage stats from DataFrame"""
    usage_stats = {}
    
    if df is None or df.empty:
        return usage_stats
    
    # Find the Player column
    player_col = None
    for col in df.columns:
        if 'Player' in str(col):
            player_col = col
            break
    
    if player_col is None:
        logger.warning(f"No Player column found in {stat_type} usage DataFrame")
        return usage_stats
    
    for _, row in df.iterrows():
        player = row.get(player_col, "")
        if not player or player == "Player":  # Skip header rows
            continue
        
        # CRITICAL FIX: Normalize player name
        player = normalize_player_name(player)
        
        if stat_type == "receiving":
            try:
                snap_pct = row[("USAGE", "SNP%")] if ("USAGE", "SNP%") in row.index else 0
                tar_pct = row[("USAGE", "TAR%")] if ("USAGE", "TAR%") in row.index else 0
                rt_pct = row[("USAGE", "RT%")] if ("USAGE", "RT%") in row.index else 0
                
                usage_stats[player] = {
                    "snap_share_pct": float(snap_pct or 0),
                    "target_share_pct": float(tar_pct or 0),
                    "route_share_pct": float(rt_pct or 0),
                }
            except (KeyError, ValueError, TypeError):
                usage_stats[player] = {
                    "snap_share_pct": 0.0,
                    "target_share_pct": 0.0,
                    "route_share_pct": 0.0,
                }
        elif stat_type == "rushing":
            try:
                snap_pct = row[("USAGE", "SNP%")] if ("USAGE", "SNP%") in row.index else 0
                att_pct = row[("USAGE", "ATT%")] if ("USAGE", "ATT%") in row.index else 0
                
                usage_stats[player] = {
                    "snap_share_pct": float(snap_pct or 0),
                    "carry_share_pct": float(att_pct or 0),
                }
            except (KeyError, ValueError, TypeError):
                usage_stats[player] = {
                    "snap_share_pct": 0.0,
                    "carry_share_pct": 0.0,
                }
    
    return usage_stats


def extract_base_stats(df, stat_type="receiving"):
    """Extract base stats from DataFrame"""
    base_stats = {}
    
    if df is None or df.empty:
        return base_stats
    
    player_col = None
    for col in df.columns:
        if 'Player' in str(col):
            player_col = col
            break
    
    if player_col is None:
        logger.warning(f"No Player column found in {stat_type} base DataFrame")
        return base_stats
    
    for _, row in df.iterrows():
        player = row.get(player_col, "")
        if not player or player == "Player":
            continue
        
        # CRITICAL FIX: Normalize player name
        player = normalize_player_name(player)
        
        if stat_type == "receiving":
            base_stats[player] = {
                "rec_yds": float(row.get(("BASE", "YDS"), 0) or 0),
                "receptions": float(row.get(("BASE", "REC"), 0) or 0),
                "targets": float(row.get(("BASE", "TAR"), 0) or 0),
                "rec_tds": float(row.get(("BASE", "TD"), 0) or 0),
            }
        elif stat_type == "rushing":
            base_stats[player] = {
                "rush_yds": float(row.get(("BASE", "YDS"), 0) or 0),
                "rush_att": float(row.get(("BASE", "ATT"), 0) or 0),
                "rush_tds": float(row.get(("BASE", "TD"), 0) or 0),
            }
        elif stat_type == "passing":
            base_stats[player] = {
                "pass_yds": float(row.get(("BASE", "YDS"), 0) or 0),
                "pass_att": float(row.get(("BASE", "ATT"), 0) or 0),
                "pass_cmp": float(row.get(("BASE", "CMP"), 0) or 0),
                "pass_tds": float(row.get(("BASE", "TD"), 0) or 0),
                "ints": float(row.get(("BASE", "INT"), 0) or 0),
            }
    
    return base_stats


def aggregate_historical_stats(context: dict) -> dict:
    """
    Aggregate historical stats into agent-friendly format.
    
    Creates:
    - context['usage']: Player -> {snap_share_pct, target_share_pct, ...}
    - context['trends']: Player -> {weeks: {stat_name: [values]}}
    """
    
    historical = context.get('historical_stats', {})
    if not historical:
        logger.warning("No historical_stats found in context")
        return context
    
    weeks = sorted(historical.keys())
    logger.info(f"Processing historical weeks: {weeks}")
    
    usage_agg = {}
    trends_agg = {}
    
    for week in weeks:
        week_data = historical[week]
        
        # Process receiving usage
        if "receiving_usage" in week_data and week_data["receiving_usage"] is not None:
            usage_stats = extract_usage_stats(week_data["receiving_usage"], "receiving")
            for player, stats in usage_stats.items():
                if player not in usage_agg:
                    usage_agg[player] = {}
                usage_agg[player].update(stats)
                
                if player not in trends_agg:
                    trends_agg[player] = {"weeks": {}}
                if "snap_share_pct" not in trends_agg[player]["weeks"]:
                    trends_agg[player]["weeks"]["snap_share_pct"] = []
                trends_agg[player]["weeks"]["snap_share_pct"].append(stats.get("snap_share_pct", 0))
        
        # Process rushing usage
        if "rushing_usage" in week_data and week_data["rushing_usage"] is not None:
            usage_stats = extract_usage_stats(week_data["rushing_usage"], "rushing")
            for player, stats in usage_stats.items():
                if player not in usage_agg:
                    usage_agg[player] = {}
                usage_agg[player].update(stats)
                
                if player not in trends_agg:
                    trends_agg[player] = {"weeks": {}}
                if "snap_share_pct" not in trends_agg[player]["weeks"]:
                    trends_agg[player]["weeks"]["snap_share_pct"] = []
                trends_agg[player]["weeks"]["snap_share_pct"].append(stats.get("snap_share_pct", 0))
        
        # Process receiving base stats for trends
        if "receiving_base" in week_data and week_data["receiving_base"] is not None:
            base_stats = extract_base_stats(week_data["receiving_base"], "receiving")
            for player, stats in base_stats.items():
                if player not in trends_agg:
                    trends_agg[player] = {"weeks": {}}
                if "rec_yds" not in trends_agg[player]["weeks"]:
                    trends_agg[player]["weeks"]["rec_yds"] = []
                trends_agg[player]["weeks"]["rec_yds"].append(stats.get("rec_yds", 0))
        
        # Process rushing base stats for trends
        if "rushing_base" in week_data and week_data["rushing_base"] is not None:
            base_stats = extract_base_stats(week_data["rushing_base"], "rushing")
            for player, stats in base_stats.items():
                if player not in trends_agg:
                    trends_agg[player] = {"weeks": {}}
                if "rush_yds" not in trends_agg[player]["weeks"]:
                    trends_agg[player]["weeks"]["rush_yds"] = []
                trends_agg[player]["weeks"]["rush_yds"].append(stats.get("rush_yds", 0))
    
    # Calculate trends
    for player, week_data in trends_agg.items():
        weeks = week_data.get("weeks", {})
        for stat_name, values in weeks.items():
            if len(values) > 1:
                first_val = values[0]
                last_val = values[-1]
                if first_val != 0:
                    trend_pct = ((last_val - first_val) / first_val) * 100
                    if trend_pct > 10:
                        trends_agg[player][f"{stat_name}_trend"] = "increasing"
                    elif trend_pct < -10:
                        trends_agg[player][f"{stat_name}_trend"] = "decreasing"
                    else:
                        trends_agg[player][f"{stat_name}_trend"] = "stable"
    
    # Add trend to usage
    for player, trend_data in trends_agg.items():
        if player not in usage_agg:
            usage_agg[player] = {}
        if "target_share_pct_trend" in trend_data:
            usage_agg[player]["trend"] = trend_data.get("target_share_pct_trend", "stable")
        elif "snap_share_pct_trend" in trend_data:
            usage_agg[player]["trend"] = trend_data.get("snap_share_pct_trend", "stable")
        else:
            usage_agg[player]["trend"] = "stable"
    
    context["usage"] = usage_agg
    context["trends"] = trends_agg
    
    logger.info(f"✓ Aggregated stats for {len(usage_agg)} players")
    
    # Log a few sample players for debugging
    if usage_agg:
        sample_players = list(usage_agg.keys())[:3]
        logger.info(f"Sample player names: {sample_players}")
    
    return context