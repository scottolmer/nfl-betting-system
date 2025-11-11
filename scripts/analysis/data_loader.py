"""
NFL Data Loader - Loads DVOA, betting lines, injury data, and ROSTER data.
Uses roster data to accurately assign teams to players in betting lines.
Handles double headers in DVOA files.
"""

import pandas as pd
from pathlib import Path
import logging
import re
import csv
import io
from typing import Dict # <<< *** ADD THIS IMPORT *** <<<

logger = logging.getLogger(__name__)


# Helper function to normalize player names (used across loading/transforming)
def normalize_name(name):
    """Normalize player name to lowercase, remove periods"""
    if not name: return name
    name = str(name).strip().replace('.', '')
    name = re.sub(r'\s+', ' ', name)
    return name.lower()

def normalize_team_abbr(abbr):
    """Normalize team abbreviations to handle variations"""
    if not abbr: return abbr
    abbr = str(abbr).strip().upper()
    # Handle common variations
    team_map = {
        'JAX': 'JAC',  # Jacksonville
        'ARZ': 'ARI',  # Arizona
        'BLT': 'BAL',  # Baltimore (DVOA uses BLT)
        'CLV': 'CLE',  # Cleveland (DVOA uses CLV)
        'HST': 'HOU',  # Houston (DVOA uses HST)
    }
    return team_map.get(abbr, abbr)

# ====================================================================
#  ROSTER LOADING FUNCTION
# ====================================================================
def _load_roster_data(data_dir: Path) -> Dict[str, str]:
    """Loads the roster CSV and returns a player_name -> team_abbr map."""
    player_to_team_map = {}
    roster_file = data_dir / "NFL_roster - Sheet1.csv" # Specific filename
    if not roster_file.exists():
        logger.error(f"CRITICAL: Roster file not found at {roster_file}. Cannot accurately assign player teams.")
        return player_to_team_map # Return empty map

    try:
        df_roster = pd.read_csv(roster_file)
        # Ensure required columns exist
        if 'Player' not in df_roster.columns or 'Team' not in df_roster.columns:
             logger.error(f"Roster file {roster_file.name} is missing 'Player' or 'Team' column.")
             return player_to_team_map

        for _, row in df_roster.iterrows():
            player_name_raw = row.get('Player')
            team_abbr = row.get('Team')
            if player_name_raw and team_abbr and not pd.isna(player_name_raw) and not pd.isna(team_abbr):
                normalized_player = normalize_name(player_name_raw)
                player_to_team_map[normalized_player] = normalize_team_abbr(team_abbr) # Normalize team abbr

        logger.info(f"✓ Loaded roster data for {len(player_to_team_map)} players from {roster_file.name}")
    except Exception as e:
        logger.error(f"Error loading roster file {roster_file.name}: {e}", exc_info=True)

    return player_to_team_map


# ====================================================================
#  DATA TRANSFORMER FUNCTIONS
# ====================================================================

def transform_betting_lines_to_props(betting_lines_df, week, player_roster_map: Dict[str, str]):
    """
    Transform betting lines DataFrame into props format.
    Uses the player_roster_map to assign correct teams.
    """

    def infer_position(stat_type):
        stat_lower = str(stat_type).lower()
        if 'pass' in stat_lower: return 'QB'
        if 'rush' in stat_lower: return 'RB'
        if 'rec' in stat_lower: return 'WR'
        return 'UNK'

    TEAM_FULL_NAME_TO_ABBR = { # Used if home/away columns contain full names
        'Arizona Cardinals': 'ARI', 'Atlanta Falcons': 'ATL', 'Baltimore Ravens': 'BAL',
        'Buffalo Bills': 'BUF', 'Carolina Panthers': 'CAR', 'Chicago Bears': 'CHI',
        'Cincinnati Bengals': 'CIN', 'Cleveland Browns': 'CLE', 'Dallas Cowboys': 'DAL',
        'Denver Broncos': 'DEN', 'Detroit Lions': 'DET', 'Green Bay Packers': 'GB',
        'Houston Texans': 'HOU', 'Indianapolis Colts': 'IND', 'Jacksonville Jaguars': 'JAC',
        'Kansas City Chiefs': 'KC', 'Las Vegas Raiders': 'LV', 'Los Angeles Chargers': 'LAC',
        'Los Angeles Rams': 'LAR', 'Miami Dolphins': 'MIA', 'Minnesota Vikings': 'MIN',
        'New England Patriots': 'NE', 'New Orleans Saints': 'NO', 'New York Giants': 'NYG',
        'New York Jets': 'NYJ', 'Philadelphia Eagles': 'PHI', 'Pittsburgh Steelers': 'PIT',
        'San Francisco 49ers': 'SF', 'Seattle Seahawks': 'SEA', 'Tampa Bay Buccaneers': 'TB',
        'Tennessee Titans': 'TEN', 'Washington Commanders': 'WAS',
        'Washington Football Team': 'WAS','LA Chargers': 'LAC', 'LA Rams': 'LAR',
    }
    def is_abbr(team_name):
        return isinstance(team_name, str) and len(team_name) <= 3 and team_name.isupper()

    def get_abbr(team_name):
         if not team_name or pd.isna(team_name): return ''
         team_name_str = str(team_name).strip()
         if is_abbr(team_name_str): return normalize_team_abbr(team_name_str)
         abbr = TEAM_FULL_NAME_TO_ABBR.get(team_name_str)
         if abbr: return normalize_team_abbr(abbr)
         return normalize_team_abbr(team_name_str)

    props = []
    if betting_lines_df is None: logger.warning("Betting lines DF is None."); return props
    if not player_roster_map: logger.error("Player roster map is empty. Cannot accurately assign teams."); # Don't return, try anyway but log error

    # Check for TRANSFORMED format
    if 'Player' in betting_lines_df.columns and 'Team' in betting_lines_df.columns and 'Opponent' in betting_lines_df.columns:
        logger.info("Detected TRANSFORMED betting lines.")
        for _, row in betting_lines_df.iterrows():
            player_name_norm = normalize_name(row['Player'])
            # Verify team from roster if possible
            roster_team = player_roster_map.get(player_name_norm)
            csv_team = get_abbr(row['Team'])
            if roster_team and csv_team != roster_team:
                logger.warning(f"Team mismatch for {player_name_norm}: CSV='{csv_team}', Roster='{roster_team}'. Using CSV team.")
                player_team_abbr = csv_team # Trust CSV if transformed? Or override with roster? Decide policy.
            else:
                 player_team_abbr = roster_team if roster_team else csv_team # Use roster if available, else CSV

            opponent_abbr = get_abbr(row['Opponent'])

            stat_type = row['Stat_Type']
            prop = {
                'player_name': player_name_norm, 'team': player_team_abbr, 'opponent': opponent_abbr,
                'position': row.get('Position', infer_position(stat_type)),
                'stat_type': stat_type, 'line': float(row.get('Line', 0)), # Use .get for safety
                'game_total': row.get('Game_Total'), 'spread': row.get('Spread'),
                'is_home': row.get('Is_Home', True), 'week': week,
            }
            props.append(prop)

    # Check for DraftKings/API format
    elif 'home_team' in betting_lines_df.columns and 'away_team' in betting_lines_df.columns:
        logger.info("Detected home_team/away_team betting lines. Using roster for team assignment.")
        stat_map = {
            'player_pass_yds': 'Pass Yds', 'player_pass_tds': 'Pass TDs',
            'player_pass_completions': 'Pass Completions', 'player_rush_yds': 'Rush Yds',
            'player_rush_attempts': 'Rush Attempts', 'player_reception_yds': 'Rec Yds',
            'player_receiving_yds': 'Rec Yds', 'player_receptions': 'Receptions',
             'player_rush_reception_yds': 'Rush+Rec Yds',
        }
        name_col = 'description' if 'description' in betting_lines_df.columns else 'player_name'
        if name_col not in betting_lines_df.columns:
             logger.error(f"Missing player name column ('{name_col}')"); return props

        processed_ids = set()
        skipped_roster_lookup = 0
        for _, row in betting_lines_df.iterrows():
            market = row.get('market', ''); stat_type = stat_map.get(market, market)
            if not stat_type or (stat_type == market and not market.startswith('player_')): continue

            player_name_raw = row.get(name_col, ''); player_name_norm = normalize_name(player_name_raw)
            line = float(row.get('point', 0)); label = row.get('label', 'Over')

            prop_unique_id = (player_name_norm, stat_type, line, label)
            if prop_unique_id in processed_ids: continue
            processed_ids.add(prop_unique_id)

            home_team_abbr = get_abbr(row.get('home_team'))
            away_team_abbr = get_abbr(row.get('away_team'))
            if not home_team_abbr or not away_team_abbr: continue

            # --- *** Use Roster Lookup with Better Fallback *** ---
            player_team_abbr = player_roster_map.get(player_name_norm)
            opponent_abbr = None
            is_home = None

            if player_team_abbr:
                # Player found in roster - check if team matches game
                if player_team_abbr == home_team_abbr:
                    opponent_abbr = away_team_abbr
                    is_home = True
                elif player_team_abbr == away_team_abbr:
                    opponent_abbr = home_team_abbr
                    is_home = False
                else:
                    # Team mismatch - this shouldn't happen if roster/game data match
                    # Log as debug, not warning, since it's expected in edge cases
                    logger.debug(f"Roster team '{player_team_abbr}' for {player_name_norm} doesn't match game teams ({home_team_abbr}/{away_team_abbr}). Skipping.")
                    continue
            else:
                # Player not found in roster file
                # This is an ERROR that needs attention - missing players means props get skipped
                logger.warning(f"Player '{player_name_norm}' NOT IN ROSTER - cannot assign team/opponent. Skipping prop.")
                skipped_roster_lookup += 1
                continue
            # --- *** End Roster Lookup with Better Fallback *** ---

            position = infer_position(stat_type)

            if label == 'Over':
                prop = {
                    'player_name': player_name_norm, 'team': player_team_abbr, 'opponent': opponent_abbr,
                    'position': position, 'stat_type': stat_type, 'line': line,
                    'game_total': 44.5,  # Default reasonable NFL game total
                    'spread': 0.0,  # Default neutral (ideally from separate moneyline data)
                    'is_home': is_home, 'week': week,
                }
                props.append(prop)
    else: logger.error("Betting lines CSV format unrecognized.")

    if skipped_roster_lookup > 0:
         logger.warning(f"Skipped {skipped_roster_lookup} props because player was not found in the roster file.")
    logger.info(f"Total props transformed after roster lookup: {len(props)}")
    if not props: logger.error("No props were transformed.")
    return props


# --- DVOA Transformation Functions (Using Positional Access) ---
# (These remain unchanged from the previous version)
def transform_dvoa_offensive(dvoa_df):
    if dvoa_df is None: return {}
    result = {}
    expected_cols_len = 9
    if len(dvoa_df.columns) != expected_cols_len: logger.warning(f"DVOA Off cols mismatch! Exp {expected_cols_len}, Got {len(dvoa_df.columns)}.")
    for idx, row in dvoa_df.iterrows():
         try:
            team_abbr = str(row.iloc[1]).strip();
            if team_abbr == 'Tm': continue
            team_abbr = normalize_team_abbr(team_abbr)  # Normalize
            if not team_abbr or pd.isna(team_abbr): continue
            result[team_abbr] = {
                'offense_dvoa': float(str(row.get('DVOA', 0)).replace('%','')),
                'passing_dvoa': float(str(row.get('Passing DVOA', 0)).replace('%','')),
                'rushing_dvoa': float(str(row.get('Rushing DVOA', 0)).replace('%','')),
            }
         except (IndexError, ValueError, TypeError) as e: logger.warning(f"DVOA Off - Skip row {idx}: {e}")
    if not result: logger.error("DVOA Offensive dictionary empty!")
    return result

def transform_dvoa_defensive(dvoa_df):
    if dvoa_df is None: return {}
    result = {}
    expected_cols_len = 9
    if len(dvoa_df.columns) != expected_cols_len: logger.warning(f"DVOA Def cols mismatch! Exp {expected_cols_len}, Got {len(dvoa_df.columns)}.")
    for idx, row in dvoa_df.iterrows():
         try:
            team_abbr = str(row.iloc[1]).strip();
            if team_abbr == 'Tm': continue
            team_abbr = normalize_team_abbr(team_abbr)  # Normalize
            if not team_abbr or pd.isna(team_abbr): continue
            result[team_abbr] = {
                'defense_dvoa': float(str(row.get('DVOA', 0)).replace('%','')),
                'pass_defense_dvoa': float(str(row.get('Passing DVOA', 0)).replace('%','')),
                'rush_defense_dvoa': float(str(row.get('Rushing DVOA', 0)).replace('%','')),
            }
         except (IndexError, ValueError, TypeError) as e: logger.warning(f"DVOA Def - Skip row {idx}: {e}")
    if not result: logger.error("DVOA Defensive dictionary empty!")
    return result

def transform_def_vs_receiver(def_vs_wr_df):
    if def_vs_wr_df is None: return {}
    result = {}
    expected_cols_len = 19; actual_cols = list(def_vs_wr_df.columns)
    if len(actual_cols) != expected_cols_len: logger.warning(f"Def vs WR cols mismatch! Exp {expected_cols_len}, Got {len(actual_cols)}.")
    col_map = {
        'vs_wr1_dvoa_col': actual_cols[4] if len(actual_cols) > 4 else 'DVOA',
        'vs_wr2_dvoa_col': actual_cols[7] if len(actual_cols) > 7 else 'DVOA.1',
        'vs_te_dvoa_col': actual_cols[13] if len(actual_cols) > 13 else 'DVOA.3',
        'vs_rb_dvoa_col': actual_cols[16] if len(actual_cols) > 16 else 'DVOA.4',
    }
    for idx, row in def_vs_wr_df.iterrows():
         try:
            team_abbr = str(row.iloc[1]).strip();
            if team_abbr == 'Tm': continue
            team_abbr = normalize_team_abbr(team_abbr)  # Normalize
            if not team_abbr or pd.isna(team_abbr): continue
            def clean_dvoa(val):
                 val_str = str(val).strip()
                 if '%' in val_str: return float(val_str.replace('%', ''))
                 if pd.isna(val) or val_str == '-': return 0.0
                 try: return float(val_str)
                 except ValueError: return 0.0
            result[team_abbr] = {
                'vs_wr1_dvoa': clean_dvoa(row.get(col_map['vs_wr1_dvoa_col'], 0)),
                'vs_wr2_dvoa': clean_dvoa(row.get(col_map['vs_wr2_dvoa_col'], 0)),
                'vs_wr3_dvoa': 0.0, 'vs_te_dvoa': clean_dvoa(row.get(col_map['vs_te_dvoa_col'], 0)),
                'vs_rb_dvoa': clean_dvoa(row.get(col_map['vs_rb_dvoa_col'], 0)),
                'vs_wr1_yds_per_game': 0.0, 'vs_wr2_yds_per_game': 0.0,'vs_te_yds_per_game': 0.0,
            }
         except (IndexError, StopIteration, ValueError, TypeError) as e: logger.warning(f"Def vs WR - Skip row {idx}: {e}")
    if not result: logger.error("Defensive vs Receiver dictionary empty!")
    return result


# ====================================================================
#  DATA LOADER CLASS
# ====================================================================

class NFLDataLoader:
    """Loads and normalizes NFL data from CSV files"""

    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        # Load roster data on init
        self.player_roster_map = _load_roster_data(self.data_dir)

    def load_all_data(self, week):
        """Load all data needed for analysis"""
        logger.info(f"Loading data for Week {week}...")

        context = {
            'week': week,
            'dvoa_off_raw': None, 'dvoa_def_raw': None, 'def_vs_wr_raw': None,
            'betting_lines_raw': None, 'injuries': None,
            'player_roster_map': self.player_roster_map, # Pass roster map
            'loaded_files': ['Roster: NFL_roster - Sheet1.csv'] if self.player_roster_map else []  # Track loaded files for UI display
        }

        # --- Load RAW DataFrames ---
        # (Loading logic remains same as previous correct version)
        try: # DVOA Off - Fall back through recent weeks if current week missing
            fpath = None
            for try_week in [week, week-1, week-2, week-3]:
                if try_week < 1: break
                fpath = next(self.data_dir.glob(f"wk{try_week}_offensive_DVOA.csv"),
                           next(self.data_dir.glob(f"wk{try_week}_offensive_dvoa.csv"),
                           next(self.data_dir.glob(f"wk{try_week}_dvoa_offensive.csv"),
                           next(self.data_dir.glob(f"DVOA_Off_wk_{try_week}.csv"), None))))
                if fpath and fpath.exists(): break
            if fpath and fpath.exists(): 
                context['dvoa_off_raw'] = pd.read_csv(fpath, header=1)
                context['loaded_files'].append(f"DVOA Offensive: {fpath.name}")
                logger.info(f"✓ DVOA Off: {fpath.name} (using week {try_week} data)")
            else: logger.warning(f"⚠ DVOA Offensive: no data found for weeks {week} through {max(1,week-3)}")
        except Exception as e: logger.error(f"Error DVOA Off: {e}")

        try: # DVOA Def - Fall back through recent weeks if current week missing
            fpath = None
            for try_week in [week, week-1, week-2, week-3]:
                if try_week < 1: break
                fpath = next(self.data_dir.glob(f"wk{try_week}_defensive_DVOA.csv"),
                           next(self.data_dir.glob(f"wk{try_week}_dvoa_defensive.csv"),
                           next(self.data_dir.glob(f"w{try_week}_defensive_DVOA.csv"),
                           next(self.data_dir.glob(f"DVOA_Def_wk_{try_week}.csv"), None))))
                if fpath and fpath.exists(): break
            if fpath and fpath.exists(): 
                context['dvoa_def_raw'] = pd.read_csv(fpath, header=1)
                context['loaded_files'].append(f"DVOA Defensive: {fpath.name}")
                logger.info(f"✓ DVOA Def: {fpath.name} (using week {try_week} data)")
            else: logger.warning(f"⚠ DVOA Defensive: no data found for weeks {week} through {max(1,week-3)}")
        except Exception as e: logger.error(f"Error DVOA Def: {e}")

        try: # Def vs WR - Fall back through recent weeks if current week missing
            fpath = None
            for try_week in [week, week-1, week-2, week-3]:
                if try_week < 1: break
                fpath = next(self.data_dir.glob(f"wk{try_week}_def_v_wr_DVOA.csv"),
                           next(self.data_dir.glob(f"wk{try_week}_dvoa_defensive_vs_receiver.csv"),
                           next(self.data_dir.glob(f"Def_vs_WR_wk_{try_week}.csv"), None)))
                if fpath and fpath.exists(): break
            if fpath and fpath.exists(): 
                context['def_vs_wr_raw'] = pd.read_csv(fpath, header=1)
                context['loaded_files'].append(f"Def vs WR: {fpath.name}")
                logger.info(f"✓ Def vs WR: {fpath.name} (using week {try_week} data)")
            else: logger.warning(f"⚠ Def vs WR: no data found for weeks {week} through {max(1,week-3)}")
        except Exception as e: logger.error(f"Error Def vs WR: {e}")

        try: # Betting Lines
             fpath = next(self.data_dir.glob(f"wk{week}_betting_lines_draftkings.csv"),
                       next(self.data_dir.glob(f"wk{week}_betting_lines_TRANSFORMED.csv"),
                       next(self.data_dir.glob(f"betting_lines_wk_{week}_live.csv"), None)))
             if fpath and fpath.exists():
                context['betting_lines_raw'] = pd.read_csv(fpath)
                context['betting_lines_source'] = f"CSV ({fpath.name})"
                context['loaded_files'].append(f"Betting Lines: {fpath.name}")
                logger.info(f"✓ Betting Lines: {fpath.name} ({len(context['betting_lines_raw'])} rows)")
             else:
                context['betting_lines_source'] = "NO DATA"
                logger.warning(f"⚠ Betting lines wk{week} missing.")
        except Exception as e: logger.error(f"Error Betting Lines: {e}")

        try: # Injury Report
            user_csv_pattern = self.data_dir / f"wk{week}-injury-report.csv"
            alt_csv_pattern = self.data_dir / f"week{week}_injury_report.csv"
            txt_pattern = self.data_dir / f"week{week}_injury_report.txt"
            fpath = None
            if user_csv_pattern.exists(): fpath = user_csv_pattern
            elif alt_csv_pattern.exists(): fpath = alt_csv_pattern
            elif txt_pattern.exists(): fpath = txt_pattern
            if fpath:
                logger.info(f"Found injury report file: {fpath.name}")
                with open(fpath, 'r', encoding='utf-8') as f: context['injuries'] = f.read()
                context['loaded_files'].append(f"Injury Report: {fpath.name}")
                logger.info(f"✓ Loaded injury report content")
            else: logger.info(f"ℹ No injury report file found (tried patterns like wk{week}-injury-report.csv, ...).")
        except Exception as e: logger.warning(f"Injury report loading error: {e}")

        # --- Load Historical Stats ---
        context['historical_stats'] = {}
        loaded_hist_weeks = 0
        for hist_week in range(max(1, week-3), week):
             week_key = f"wk{hist_week}"; context['historical_stats'][week_key] = {}; has_data = False
             for st in ['receiving_base','receiving_usage','rushing_base','rushing_usage','passing_base','receiving_alignment']:
                 try:
                     fpath = self.data_dir / f"wk{hist_week}_{st}.csv"
                     if fpath.exists(): 
                         context['historical_stats'][week_key][st] = pd.read_csv(fpath, skiprows=1)
                         context['loaded_files'].append(f"Historical Stats: {fpath.name}")
                         has_data = True
                 except Exception as e: logger.debug(f"Hist stats wk{hist_week} {st}: {e}")
             if has_data: loaded_hist_weeks +=1
        logger.info(f"✓ Loaded historical stats for {loaded_hist_weeks} weeks")

        # --- Load Current Week Usage Data (Falls back to previous weeks) ---
        try:
            usage_file = None
            # Look backwards for usage data (week 10 uses week 9 data)
            for try_week in [week-1, week-2, week-3]:
                if try_week < 1: break
                usage_file = self.data_dir / f"wk{try_week}_receiving_usage.csv"
                if usage_file.exists(): break
            
            if usage_file and usage_file.exists():
                usage_df = pd.read_csv(usage_file, skiprows=1)
                usage_dict = {}
                for _, row in usage_df.iterrows():
                    player = normalize_name(row.get('Player', ''))
                    if player:
                        usage_dict[player] = {
                            'snap_share_pct': float(str(row.get('Snap Share %', 0)).replace('%', '')) if '%' in str(row.get('Snap Share %', '')) else 0,
                            'target_share_pct': float(str(row.get('Target Share %', 0)).replace('%', '')) if '%' in str(row.get('Target Share %', '')) else 0,
                            'targets': float(row.get('Tgt', 0)) if pd.notna(row.get('Tgt')) else 0,
                            'receptions': float(row.get('Rec', 0)) if pd.notna(row.get('Rec')) else 0,
                        }
                context['usage'] = usage_dict
                context['loaded_files'].append(f"Recent Usage Data: {usage_file.name}")
                logger.info(f"✓ Loaded usage data: {usage_file.name} ({len(usage_dict)} players)")
            else:
                logger.info(f"ℹ No usage data found for recent weeks")
                context['usage'] = {}
        except Exception as e:
            logger.error(f"Error loading usage data: {e}")
            context['usage'] = {}

        # --- Aggregate Historical Stats ---
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("stats_aggregator", str(Path(__file__).parent / "stats_aggregator.py"))
            stats_agg = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(stats_agg)
            context = stats_agg.aggregate_historical_stats(context); logger.info("✓ Aggregated historical stats.")
        except Exception as e:
            logger.error(f"FAIL Aggregation: {e}"); context['trends']={}; context['alignment']={}

        # ====================================================================
        #  TRANSFORM DATA FOR AGENTS (Now uses roster map)
        # ====================================================================
        logger.info("Transforming raw data for agents using roster map...")
        # Pass roster map loaded during __init__
        context['props'] = transform_betting_lines_to_props(
            context.get('betting_lines_raw'), week, self.player_roster_map
        )
        context['dvoa_offensive'] = transform_dvoa_offensive(context.get('dvoa_off_raw'))
        context['dvoa_defensive'] = transform_dvoa_defensive(context.get('dvoa_def_raw'))
        context['defensive_vs_receiver'] = transform_def_vs_receiver(context.get('def_vs_wr_raw'))

        logger.info(f"✓ Transformed {len(context.get('props', []))} props")
        logger.info(f"✓ Transformed {len(context.get('dvoa_offensive', {}))} offensive teams")
        logger.info(f"✓ Transformed {len(context.get('dvoa_defensive', {}))} defensive teams")
        logger.info(f"✓ Transformed {len(context.get('defensive_vs_receiver', {}))} defensive matchup teams")

        # Final checks
        if not context.get('props'): logger.critical("CRITICAL: No props transformed.")
        if not context.get('dvoa_offensive'): logger.error("ERROR: DVOA Offensive dict empty.")
        if not context.get('dvoa_defensive'): logger.error("ERROR: DVOA Defensive dict empty.")
        if not context.get('defensive_vs_receiver'): logger.error("ERROR: Def vs Receiver dict empty.")

        return context


if __name__ == "__main__":
    import os; from pathlib import Path
    logging.basicConfig(level=logging.INFO)
    project_root_dir = Path(__file__).parent.parent.parent
    data_dir = project_root_dir / "data"
    loader = NFLDataLoader(data_dir=str(data_dir)) # Loads roster on init
    week = int(os.getenv('NFL_WEEK', 8))
    print(f"\n{'='*60}\nTESTING DATA LOADER - WEEK {week}\n{'='*60}\n")
    context = loader.load_all_data(week=week)
    print(f"\n--- RAW ---")
    print(f"  Roster: {'✓' if loader.player_roster_map else '✗'} ({len(loader.player_roster_map)} players)") # Show roster status
    print(f"  DVOA Off Raw: {'✓' if context.get('dvoa_off_raw') is not None else '✗'}")
    print(f"  DVOA Def Raw: {'✓' if context.get('dvoa_def_raw') is not None else '✗'}")
    print(f"  Def vs WR Raw: {'✓' if context.get('def_vs_wr_raw') is not None else '✗'}")
    print(f"  Bet Lines Raw: {'✓' if context.get('betting_lines_raw') is not None else '✗'}")
    print(f"  Injuries: {'✓' if context.get('injuries') is not None else '✗'} ({'Loaded' if context.get('injuries') else 'Not Found/Loaded'})")
    print(f"--- TRANSFORMED ---")
    print(f"  Props: {len(context.get('props', []))}")
    print(f"  DVOA Off: {len(context.get('dvoa_offensive', {}))}")
    print(f"  DVOA Def: {len(context.get('dvoa_defensive', {}))}")
    print(f"  Def vs Rec: {len(context.get('defensive_vs_receiver', {}))}")
    print(f"  Usage: {len(context.get('usage', {}))}")
    if context.get('props'):
        print(f"\n--- SAMPLE PROPS (Check Team/Opponent) ---")
        for p in context['props'][:5]: print(f"  {p.get('player_name','?')} ({p.get('team','?')}) vs {p.get('opponent','?')}: {p.get('stat_type','?')} O{p.get('line','?')}")
    if context.get('dvoa_offensive'):
         print("\n--- SAMPLE DVOA OFF ---");
         for t, d in list(context['dvoa_offensive'].items())[:3]: print(f"  {t}: {d}")
    if context.get('defensive_vs_receiver'):
         print("\n--- SAMPLE DEF VS REC ---");
         for t, d in list(context['defensive_vs_receiver'].items())[:3]: print(f"  {t}: {d}")