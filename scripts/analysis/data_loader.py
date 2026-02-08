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
from typing import Dict, Optional, Any
from api.database import SessionLocal, GameDataFile

logger = logging.getLogger(__name__)


# Helper function to normalize player names (used across loading/transforming)
def normalize_name(name):
    """Normalize player name to lowercase, remove periods"""
    if not name: return name
    name = str(name).strip().replace('.', '')
    name = re.sub(r'\s+', ' ', name)
    return name.lower()

def safe_float(val, default=0):
    """Convert value to float, handling commas, percentage signs, and dashes"""
    if pd.isna(val) or val == '' or val == '-':
        return default
    val_str = str(val).replace(',', '').replace('%', '').strip()
    try:
        return float(val_str)
    except (ValueError, TypeError):
        return default


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
        auto_assigned_players = set()  # Track which players we auto-assigned
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

            # --- *** Use Roster Lookup with Smart Fallback *** ---
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
                # Player not found in roster file - INFER from position
                # QBs are typically only 1-2 per game, so use heuristic:
                # If this is a QB stat, assume they're playing for one of the teams
                # For now, default to home team (can be improved with more logic)
                inferred_position = infer_position(stat_type)

                # Smart fallback: assume player is on home team by default
                # This works reasonably well since most betting lines are formatted
                # with home team first
                player_team_abbr = home_team_abbr
                opponent_abbr = away_team_abbr
                is_home = True

                # Auto-add to roster map so we remember for next props
                player_roster_map[player_name_norm] = player_team_abbr

                if player_name_norm not in auto_assigned_players:
                    logger.info(f"Auto-assigned '{player_name_raw}' to {player_team_abbr} (not in roster)")
                    auto_assigned_players.add(player_name_norm)
                    skipped_roster_lookup += 1
            # --- *** End Roster Lookup with Smart Fallback *** ---

            position = infer_position(stat_type)

            # Include both OVER and UNDER bets (not just Over)
            prop = {
                'player_name': player_name_norm, 'team': player_team_abbr, 'opponent': opponent_abbr,
                'position': position, 'stat_type': stat_type, 'line': line,
                'bet_type': label,  # Store 'Over' or 'Under' explicitly
                'game_total': 44.5,  # Default reasonable NFL game total
                'spread': 0.0,  # Default neutral (ideally from separate moneyline data)
                'is_home': is_home, 'week': week,
            }
            props.append(prop)
    else: logger.error("Betting lines CSV format unrecognized.")

    if skipped_roster_lookup > 0:
         logger.info(f"Auto-assigned {skipped_roster_lookup} players not in roster file (inferred from betting lines)")
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
        'vs_wr3_dvoa_col': actual_cols[10] if len(actual_cols) > 10 else 'DVOA.2',
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
                'vs_wr3_dvoa': clean_dvoa(row.get(col_map['vs_wr3_dvoa_col'], 0)),
                'vs_te_dvoa': clean_dvoa(row.get(col_map['vs_te_dvoa_col'], 0)),
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
        # Load roster data on init (Try DB first, then File)
        self.player_roster_map = self._load_roster_data_smart()

    def _load_from_db(self, week: int, file_type: str) -> Optional[str]:
        """Try to load file content from database"""
        session = SessionLocal()
        try:
            record = session.query(GameDataFile).filter_by(week=week, file_type=file_type).first()
            if record:
                logger.info(f"✓ Loaded {file_type} from Database (Week {week})")
                return record.content
            return None
        except Exception as e:
            logger.error(f"DB Load Error ({file_type}): {e}")
            return None
        finally:
            session.close()

    def _load_roster_data_smart(self) -> Dict[str, str]:
        """Load roster from DB or File"""
        # 1. Try DB
        content = self._load_from_db(week=0, file_type='roster') # Week 0 for global/roster
        if content:
            player_to_team_map = {}
            try:
                df_roster = pd.read_csv(io.StringIO(content))
                # reuse processing logic (copy-paste from _load_roster_data or helper)
                for _, row in df_roster.iterrows():
                    player_name_raw = row.get('Player')
                    team_abbr = row.get('Team')
                    if player_name_raw and team_abbr and not pd.isna(player_name_raw) and not pd.isna(team_abbr):
                        # ... verify normalize_name is available in scope or self ...
                        # It is defined in module scope, good.
                        normalized_player = normalize_name(player_name_raw)
                        player_to_team_map[normalized_player] = normalize_team_abbr(team_abbr)
                return player_to_team_map
            except Exception as e:
                logger.error(f"Error parsing roster from DB: {e}")

        # 2. Fallback to File
        return _load_roster_data(self.data_dir)

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
        
        # Helper to load CSV from DB or File
        def load_csv(file_type_key, file_patterns, header=0):
            # 1. DB Attempt
            db_content = self._load_from_db(week, file_type_key)
            if db_content:
                try:
                    df = pd.read_csv(io.StringIO(db_content), header=header)
                    file_name = f"DB:{file_type_key}"
                    return df, file_name, week # Return actual week found (DB uses exact week)
                except Exception as e:
                     logger.error(f"Failed to parse DB content for {file_type_key}: {e}")

            # 2. File Attempt (Fallback)
            fpath = None
            found_week = week
            for try_week in [week, week-1, week-2, week-3]:
                if try_week < 1: break
                for pattern in file_patterns:
                    fpath = next(self.data_dir.glob(pattern.format(week=try_week)), None)
                    if fpath: break
                if fpath: 
                    found_week = try_week
                    break
            
            if fpath and fpath.exists():
                return pd.read_csv(fpath, header=header), fpath.name, found_week
            return None, None, None

        # DVOA Offense
        dvoa_off_df, name, wk = load_csv(
            'dvoa_offensive', 
            ["wk{week}_offensive_DVOA.csv", "wk{week}_offensive_dvoa.csv", "DVOA_Off_wk_{week}.csv"], 
            header=1
        )
        if dvoa_off_df is not None:
             context['dvoa_off_raw'] = dvoa_off_df
             context['loaded_files'].append(f"DVOA Off: {name}")
             logger.info(f"✓ DVOA Off: {name}")
        else: logger.warning(f"⚠ DVOA Off missing")

        # DVOA Defense
        dvoa_def_df, name, wk = load_csv(
            'dvoa_defensive',
            ["wk{week}_defensive_DVOA.csv", "wk{week}_dvoa_defensive.csv", "DVOA_Def_wk_{week}.csv"],
            header=1
        )
        if dvoa_def_df is not None:
             context['dvoa_def_raw'] = dvoa_def_df
             context['loaded_files'].append(f"DVOA Def: {name}")
        else: logger.warning(f"⚠ DVOA Def missing")

        # Def vs WR
        def_vs_wr_df, name, wk = load_csv(
            'def_vs_wr',
            ["wk{week}_def_v_wr_DVOA.csv", "Def_vs_WR_wk_{week}.csv"],
            header=1
        )
        if def_vs_wr_df is not None:
             context['def_vs_wr_raw'] = def_vs_wr_df
             context['loaded_files'].append(f"Def vs WR: {name}")
        else: logger.warning(f"⚠ Def vs WR missing")

        # Betting Lines
        lines_df, name, wk = load_csv(
            'betting_lines',
            ["wk{week}_betting_lines_draftkings.csv", "betting_lines_wk_{week}_live.csv"],
            header=0
        )
        if lines_df is not None:
             context['betting_lines_raw'] = lines_df
             context['betting_lines_source'] = name
             context['loaded_files'].append(f"Betting Lines: {name}")
        else:
             context['betting_lines_source'] = "NO DATA"
             logger.warning(f"⚠ Betting lines missing")

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
        # Load BOTH receiving_usage AND rushing_usage for complete player data
        try:
            usage_dict = {}

            # 1. Load RECEIVING usage (WR, TE, pass-catching RB)
            recv_usage_file = None
            for try_week in [week-1, week-2, week-3]:
                if try_week < 1: break
                recv_usage_file = self.data_dir / f"wk{try_week}_receiving_usage.csv"
                if recv_usage_file.exists(): break

            if recv_usage_file and recv_usage_file.exists():
                recv_df = pd.read_csv(recv_usage_file, skiprows=1)
                for _, row in recv_df.iterrows():
                    player = normalize_name(row.get('Player', ''))
                    if player:
                        usage_dict[player] = {
                            'snap_share_pct': safe_float(row.get('SNP%')),
                            'target_share_pct': safe_float(row.get('TAR%')),
                            'targets': safe_float(row.get('TAR')),
                            'receptions': safe_float(row.get('REC')),
                            'receiving_yards': safe_float(row.get('YDS')),
                        }
                context['loaded_files'].append(f"Receiving Usage: {recv_usage_file.name}")
                logger.info(f"✓ Loaded receiving usage: {recv_usage_file.name} ({len(usage_dict)} players)")

            # 2. Load RUSHING usage (RB, rushing QB)
            rush_usage_file = None
            for try_week in [week-1, week-2, week-3]:
                if try_week < 1: break
                rush_usage_file = self.data_dir / f"wk{try_week}_rushing_usage.csv"
                if rush_usage_file.exists(): break

            if rush_usage_file and rush_usage_file.exists():
                rush_df = pd.read_csv(rush_usage_file, skiprows=1)
                rush_count = 0
                for _, row in rush_df.iterrows():
                    player = normalize_name(row.get('Player', ''))
                    if player:
                        snap_pct = safe_float(row.get('SNP%'))
                        attempt_pct = safe_float(row.get('ATT%'))
                        touch_pct = safe_float(row.get('TCH%'))

                        # Merge with existing data or create new entry
                        if player in usage_dict:
                            # Player already exists from receiving - add rushing data
                            usage_dict[player]['rush_attempts'] = safe_float(row.get('ATT'))
                            usage_dict[player]['rush_attempt_pct'] = attempt_pct
                            usage_dict[player]['touch_pct'] = touch_pct
                            usage_dict[player]['rushing_yards'] = safe_float(row.get('YDS'))
                            # Use higher snap share if rushing data has it
                            if snap_pct > usage_dict[player].get('snap_share_pct', 0):
                                usage_dict[player]['snap_share_pct'] = snap_pct
                        else:
                            # New player (RB without receiving data)
                            usage_dict[player] = {
                                'snap_share_pct': snap_pct,
                                'rush_attempts': safe_float(row.get('ATT')),
                                'rush_attempt_pct': attempt_pct,
                                'touch_pct': touch_pct,
                                'rushing_yards': safe_float(row.get('YDS')),
                            }
                        rush_count += 1
                context['loaded_files'].append(f"Rushing Usage: {rush_usage_file.name}")
                logger.info(f"✓ Loaded rushing usage: {rush_usage_file.name} ({rush_count} players)")

            context['usage'] = usage_dict
            if not usage_dict:
                logger.info(f"ℹ No usage data found for recent weeks")

        except Exception as e:
            logger.error(f"Error loading usage data: {e}")
            context['usage'] = {}

        # --- Load QB Analytics from passing_base ---
        try:
            qb_analytics = {}
            passing_file = None
            for try_week in [week-1, week-2, week-3]:
                if try_week < 1: break
                passing_file = self.data_dir / f"wk{try_week}_passing_base.csv"
                if passing_file.exists(): break

            if passing_file and passing_file.exists():
                pass_df = pd.read_csv(passing_file, skiprows=1)
                for _, row in pass_df.iterrows():
                    player = normalize_name(row.get('Player', ''))
                    if player:
                        qb_analytics[player] = {
                            'pass_attempts': safe_float(row.get('ATT')),
                            'completions': safe_float(row.get('COM')),
                            'completion_pct': safe_float(row.get('COM%')),
                            'passing_yards': safe_float(row.get('YDS')),
                            'yards_per_attempt': safe_float(row.get('YPA')),
                            'passing_tds': safe_float(row.get('TD')),
                            'interceptions': safe_float(row.get('INT')),
                            'passer_rating': safe_float(row.get('RTG')),
                            'epa': safe_float(row.get('EPA')),
                            'epa_per_dropback': safe_float(row.get('EPA/DB')),
                            'dvoa': safe_float(row.get('DVOA')),
                            'dyar': safe_float(row.get('DYAR')),
                            'snap_pct': safe_float(row.get('SNP%')),
                        }
                context['qb_analytics'] = qb_analytics
                context['loaded_files'].append(f"QB Analytics: {passing_file.name}")
                logger.info(f"✓ Loaded QB analytics: {passing_file.name} ({len(qb_analytics)} QBs)")
            else:
                context['qb_analytics'] = {}
                logger.info(f"ℹ No QB analytics data found")
        except Exception as e:
            logger.error(f"Error loading QB analytics: {e}")
            context['qb_analytics'] = {}

        # --- Load Receiver Alignment Data ---
        try:
            alignment_data = {}
            align_file = None
            for try_week in [week-1, week-2, week-3]:
                if try_week < 1: break
                align_file = self.data_dir / f"wk{try_week}_receiving_alignment.csv"
                if align_file.exists(): break

            if align_file and align_file.exists():
                align_df = pd.read_csv(align_file, skiprows=1)
                for _, row in align_df.iterrows():
                    player = normalize_name(row.get('Player', ''))
                    if player:
                        wide_pct = safe_float(row.get('OW%'))
                        slot_pct = safe_float(row.get('SLOT%'))

                        alignment_data[player] = {
                            'wide_pct': wide_pct,
                            'slot_pct': slot_pct,
                            'primary_alignment': 'SLOT' if slot_pct > wide_pct else 'WIDE',
                            'wide_yards_per_route': safe_float(row.get('WYPR')),
                            'slot_yards_per_route': safe_float(row.get('SYPR')),
                        }
                context['alignment'] = alignment_data
                context['loaded_files'].append(f"Receiver Alignment: {align_file.name}")
                logger.info(f"✓ Loaded alignment data: {align_file.name} ({len(alignment_data)} players)")
            else:
                context['alignment'] = {}
                logger.info(f"ℹ No alignment data found")
        except Exception as e:
            logger.error(f"Error loading alignment data: {e}")
            context['alignment'] = {}

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

    def get_validation_status(self, context: Dict) -> Dict:
        """Get user-friendly validation status for conversational interface"""
        status = {
            'success': True,
            'week': context.get('week'),
            'files_loaded': context.get('loaded_files', []),
            'props_count': len(context.get('props', [])),
            'dvoa_teams': len(context.get('dvoa_offensive', {})),
            'injuries_loaded': bool(context.get('injuries')),
            'betting_lines_source': context.get('betting_lines_source', 'Unknown'),
            'warnings': [],
            'errors': []
        }

        # Check for missing data
        if not context.get('dvoa_off_raw') is not None:
            status['warnings'].append('DVOA Offensive data missing')
        if not context.get('dvoa_def_raw') is not None:
            status['warnings'].append('DVOA Defensive data missing')
        if not context.get('betting_lines_raw') is not None:
            status['errors'].append('Betting lines missing - cannot analyze props')
            status['success'] = False
        if not context.get('props'):
            status['errors'].append('No props generated - check betting lines file')
            status['success'] = False
        if not context.get('injuries'):
            status['warnings'].append('No injury report found')

        return status


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