"""
Transform raw DraftKings API data to analysis engine format
"""

import pandas as pd
from pathlib import Path

def transform_betting_lines(input_file: str, output_file: str):
    """
    Transform raw API betting data to analysis format
    
    Input columns: game_id, home_team, away_team, market, label, description, point
    Output columns: Player, Team, Opponent, Position, Stat_Type, Line, Week, Home_Away, Game_Total, Spread
    """
    
    print("📂 Loading raw betting data...")
    df = pd.read_csv(input_file)
    
    # Filter for player props only
    player_markets = [
        'player_pass_yds', 'player_pass_tds', 'player_pass_attempts', 'player_pass_completions',
        'player_rush_yds', 'player_rush_attempts', 
        'player_receptions', 'player_reception_yds',
    ]
    
    player_props = df[df['market'].isin(player_markets)].copy()
    
    # Get game totals and spreads
    game_totals = df[df['market'] == 'totals'].groupby(['home_team', 'away_team']).first()
    game_spreads = df[df['market'] == 'spreads'].groupby(['home_team', 'away_team']).first()
    
    print(f"Found {len(player_props)} player props")
    
    # Transform to required format
    transformed = []
    
    for _, row in player_props.iterrows():
        player_name = row['description']
        home_team = row['home_team']
        away_team = row['away_team']
        market = row['market']
        direction = row['label']  # "Over" or "Under"
        line = row['point']
        
        # Skip if no line
        if pd.isna(line) or pd.isna(player_name):
            continue
        
        # Only take "Over" lines (we'll analyze Over vs Under)
        if direction != "Over":
            continue
        
        # Map market to stat type
        stat_type_map = {
            'player_pass_yds': 'Pass Yds',
            'player_pass_tds': 'Pass TDs',
            'player_pass_attempts': 'Pass Att',
            'player_pass_completions': 'Pass Comp',
            'player_rush_yds': 'Rush Yds',
            'player_rush_attempts': 'Rush Att',
            'player_receptions': 'Receptions',
            'player_reception_yds': 'Rec Yds',
        }
        
        stat_type = stat_type_map.get(market, market)
        
        # Get position from stat type
        if 'pass' in market.lower():
            position = 'QB'
        elif 'rush' in market.lower():
            position = 'RB'
        elif 'recep' in market.lower():
            position = 'WR'  # Could be WR/TE/RB, but we'll default to WR
        else:
            position = 'UNKNOWN'
        
        # Get game total and spread
        game_key = (home_team, away_team)
        game_total = game_totals.loc[game_key, 'point'] if game_key in game_totals.index else None
        spread = game_spreads.loc[game_key, 'point'] if game_key in game_spreads.index else None
        
        # Determine team and opponent (we don't know which team the player is on from this data)
        # For now, assume home team (you may need to manually correct this)
        team = home_team
        opponent = away_team
        is_home = True
        
        transformed.append({
            'Player': player_name,
            'Team': team,
            'Opponent': opponent,
            'Position': position,
            'Stat_Type': stat_type,
            'Line': line,
            'Week': 7,  # Hardcoded for Week 7
            'Home_Away': 'HOME' if is_home else 'AWAY',
            'Game_Total': game_total,
            'Spread': spread,
        })
    
    # Create DataFrame
    output_df = pd.DataFrame(transformed)
    
    # Save
    output_df.to_csv(output_file, index=False)
    
    print(f"✅ Transformed {len(output_df)} props")
    print(f"💾 Saved to: {output_file}")
    
    # Show sample
    print("\n📊 Sample of transformed data:")
    print(output_df.head(10).to_string(index=False))
    
    return output_df


if __name__ == "__main__":
    project_root = Path(r"C:\Users\scott\Desktop\nfl-betting-system")
    
    input_file = project_root / "data" / "wk7_betting_lines_draftkings.csv"
    output_file = project_root / "data" / "wk7_betting_lines_TRANSFORMED.csv"
    
    print("🔄 Transforming DraftKings betting data...")
    print("="*60)
    
    df = transform_betting_lines(str(input_file), str(output_file))
    
    print("\n" + "="*60)
    print("✅ Transformation complete!")
    print("\nNext step:")
    print("  1. Review the transformed file")
    print("  2. Manually correct any player team assignments if needed")
    print("  3. Update test_week7.py to use 'wk7_betting_lines_TRANSFORMED.csv'")
