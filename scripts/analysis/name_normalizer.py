"""
Player Name Normalizer - Standardizes player names for matching
"""

import re


def normalize_player_name(name: str) -> str:
    """
    Normalize player name for consistent matching
    
    Fixes:
    - "A.J.  Brown" -> "AJ Brown"
    - "DeVonta  Smith" -> "DeVonta Smith"
    - "Ja'Marr  Chase" -> "Ja'Marr Chase"
    """
    if not name:
        return name
    
    # Remove periods from initials (A.J. -> AJ)
    name = name.replace('.', '')
    
    # Replace multiple spaces with single space
    name = re.sub(r'\s+', ' ', name)
    
    # Strip leading/trailing whitespace
    name = name.strip()
    
    return name


def create_player_lookup(players_dict: dict) -> dict:
    """
    Create a lookup dictionary with normalized keys
    
    Returns both normalized->data and original->data mappings
    """
    lookup = {}
    
    for original_name, data in players_dict.items():
        normalized = normalize_player_name(original_name)
        lookup[normalized] = data
        # Also keep original for backwards compatibility
        lookup[original_name] = data
    
    return lookup
