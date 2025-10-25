"""
NFL Team Name Mapping - Convert between full names and abbreviations
"""

TEAM_NAME_TO_ABBREV = {
    # AFC East
    'Buffalo Bills': 'BUF',
    'Miami Dolphins': 'MIA',
    'New England Patriots': 'NE',
    'New York Jets': 'NYJ',
    
    # AFC North
    'Baltimore Ravens': 'BAL',
    'Cincinnati Bengals': 'CIN',
    'Cleveland Browns': 'CLE',
    'Pittsburgh Steelers': 'PIT',
    
    # AFC South
    'Houston Texans': 'HOU',
    'Indianapolis Colts': 'IND',
    'Jacksonville Jaguars': 'JAX',
    'Tennessee Titans': 'TEN',
    
    # AFC West
    'Denver Broncos': 'DEN',
    'Kansas City Chiefs': 'KC',
    'Las Vegas Raiders': 'LV',
    'Los Angeles Chargers': 'LAC',
    
    # NFC East
    'Dallas Cowboys': 'DAL',
    'New York Giants': 'NYG',
    'Philadelphia Eagles': 'PHI',
    'Washington Commanders': 'WAS',
    
    # NFC North
    'Chicago Bears': 'CHI',
    'Detroit Lions': 'DET',
    'Green Bay Packers': 'GB',
    'Minnesota Vikings': 'MIN',
    
    # NFC South
    'Atlanta Falcons': 'ATL',
    'Carolina Panthers': 'CAR',
    'New Orleans Saints': 'NO',
    'Tampa Bay Buccaneers': 'TB',
    
    # NFC West
    'Arizona Cardinals': 'ARI',
    'Los Angeles Rams': 'LA',
    'San Francisco 49ers': 'SF',
    'Seattle Seahawks': 'SEA',
}

ABBREV_TO_TEAM_NAME = {v: k for k, v in TEAM_NAME_TO_ABBREV.items()}


def normalize_team_name(team_name: str) -> str:
    """
    Convert any team name format to abbreviation
    
    Examples:
        'New England Patriots' -> 'NE'
        'NE' -> 'NE'
        'Patriots' -> 'NE'
    """
    # Already an abbreviation
    if team_name in ABBREV_TO_TEAM_NAME:
        return team_name
    
    # Full name
    if team_name in TEAM_NAME_TO_ABBREV:
        return TEAM_NAME_TO_ABBREV[team_name]
    
    # Partial match (e.g., "Patriots")
    for full_name, abbrev in TEAM_NAME_TO_ABBREV.items():
        if team_name.lower() in full_name.lower():
            return abbrev
    
    # No match - return original
    return team_name


def get_full_name(abbrev: str) -> str:
    """Convert abbreviation to full name"""
    return ABBREV_TO_TEAM_NAME.get(abbrev, abbrev)
