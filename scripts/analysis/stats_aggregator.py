import pandas as pd
import logging
from typing import Dict
import re

logger = logging.getLogger(__name__)

def normalize_player_name(name: str) -> str:
    if not name or pd.isna(name):
        return ""
    name = str(name).strip().replace(".", "")
    name = re.sub(r"\s+", " ", name)
    return name.lower()

def extract_usage_stats(usage_df: pd.DataFrame, position: str) -> Dict:
    if usage_df is None or usage_df.empty:
        return {}
    
    # Handle multi-level headers (first row contains headers)
    first_row_str = " ".join(str(v) for v in usage_df.iloc[0].tolist())
    if "Player" in first_row_str or "TAR%" in first_row_str:
        usage_df.columns = usage_df.iloc[0].tolist()
        usage_df = usage_df.iloc[1:].reset_index(drop=True)
    
    usage_dict = {}
    cols = usage_df.columns.tolist()
    
    for _, row in usage_df.iterrows():
        player_val = None
        for col in cols:
            if "Player" in str(col):
                player_val = row.get(col)
                break
        
        if player_val is None or pd.isna(player_val):
            continue
        
        player_name = normalize_player_name(player_val)
        if not player_name:
            continue
        
        player_stats = {}
        
        for col in cols:
            if "SNP%" in str(col):
                snap_val = row.get(col)
                if snap_val and not pd.isna(snap_val):
                    try:
                        player_stats["snap_share_pct"] = float(str(snap_val).replace("%", ""))
                    except:
                        pass
                break
        
        if position in ["WR", "TE"]:
            for col in cols:
                if "TAR%" in str(col):
                    tar_val = row.get(col)
                    if tar_val and not pd.isna(tar_val):
                        try:
                            player_stats["target_share_pct"] = float(str(tar_val).replace("%", ""))
                        except:
                            pass
                    break
        
        if player_stats:
            usage_dict[player_name] = player_stats
    
    return usage_dict

def extract_base_stats(base_df: pd.DataFrame, stat_type: str) -> Dict:
    if base_df is None or base_df.empty:
        return {}
    
    first_row_str = " ".join(str(v) for v in base_df.iloc[0].tolist())
    if "Player" in first_row_str or "REC" in first_row_str or "YDS" in first_row_str:
        base_df.columns = base_df.iloc[0].tolist()
        base_df = base_df.iloc[1:].reset_index(drop=True)
    
    base_dict = {}
    cols = base_df.columns.tolist()
    
    for _, row in base_df.iterrows():
        player_val = None
        for col in cols:
            if "Player" in str(col):
                player_val = row.get(col)
                break
        
        if player_val is None or pd.isna(player_val):
            continue
        
        player_name = normalize_player_name(player_val)
        if not player_name:
            continue
        
        player_stats = {}
        
        for col in cols:
            col_str = str(col).strip()
            try:
                if col_str == "REC" and stat_type == "receiving":
                    player_stats["receptions"] = float(row.get(col, 0))
                elif col_str == "YDS":
                    if stat_type == "receiving":
                        player_stats["rec_yds"] = float(row.get(col, 0))
                    elif stat_type == "rushing":
                        player_stats["rush_yds"] = float(row.get(col, 0))
                    elif stat_type == "passing":
                        player_stats["pass_yds"] = float(row.get(col, 0))
                elif col_str == "TD":
                    if stat_type == "receiving":
                        player_stats["rec_tds"] = float(row.get(col, 0))
                    elif stat_type == "rushing":
                        player_stats["rush_tds"] = float(row.get(col, 0))
                    elif stat_type == "passing":
                        player_stats["pass_tds"] = float(row.get(col, 0))
            except:
                pass
        
        if player_stats:
            base_dict[player_name] = player_stats
    
    return base_dict

def aggregate_historical_stats(context: Dict) -> Dict:
    if "historical_stats" not in context or not context["historical_stats"]:
        return context
    
    historical = context["historical_stats"]
    usage_agg = {}
    trends_agg = {}
    weeks_processed = sorted(list(historical.keys()))
    logger.info(f"Processing historical weeks: {weeks_processed}")
    
    for week_key in weeks_processed:
        week_data = historical[week_key]
        
        if "receiving_usage" in week_data and week_data["receiving_usage"] is not None:
            usage_stats = extract_usage_stats(week_data["receiving_usage"], "WR")
            for player, stats in usage_stats.items():
                if player not in usage_agg:
                    usage_agg[player] = {}
                usage_agg[player].update(stats)
                if player not in trends_agg:
                    trends_agg[player] = {"weeks": {}}
                if "target_share_pct" not in trends_agg[player]["weeks"]:
                    trends_agg[player]["weeks"]["target_share_pct"] = []
                trends_agg[player]["weeks"]["target_share_pct"].append(stats.get("target_share_pct", 0))
        
        if "receiving_base" in week_data and week_data["receiving_base"] is not None:
            base_stats = extract_base_stats(week_data["receiving_base"], "receiving")
            for player, stats in base_stats.items():
                if player not in trends_agg:
                    trends_agg[player] = {"weeks": {}}
                if "rec_yds" not in trends_agg[player]["weeks"]:
                    trends_agg[player]["weeks"]["rec_yds"] = []
                trends_agg[player]["weeks"]["rec_yds"].append(stats.get("rec_yds", 0))
        
        if "rushing_usage" in week_data and week_data["rushing_usage"] is not None:
            usage_stats = extract_usage_stats(week_data["rushing_usage"], "RB")
            for player, stats in usage_stats.items():
                if player not in usage_agg:
                    usage_agg[player] = {}
                usage_agg[player].update(stats)
                if player not in trends_agg:
                    trends_agg[player] = {"weeks": {}}
                if "snap_share_pct" not in trends_agg[player]["weeks"]:
                    trends_agg[player]["weeks"]["snap_share_pct"] = []
                trends_agg[player]["weeks"]["snap_share_pct"].append(stats.get("snap_share_pct", 0))
        
        if "rushing_base" in week_data and week_data["rushing_base"] is not None:
            base_stats = extract_base_stats(week_data["rushing_base"], "rushing")
            for player, stats in base_stats.items():
                if player not in trends_agg:
                    trends_agg[player] = {"weeks": {}}
                if "rush_yds" not in trends_agg[player]["weeks"]:
                    trends_agg[player]["weeks"]["rush_yds"] = []
                trends_agg[player]["weeks"]["rush_yds"].append(stats.get("rush_yds", 0))
    
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
    return context