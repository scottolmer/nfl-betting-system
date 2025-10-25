"""
Convert injury report to enhanced format
"""

import pandas as pd
from pathlib import Path

def classify_injury_type(injury: str) -> str:
    """Classify injury into categories"""
    injury_lower = str(injury).lower()
    
    if any(word in injury_lower for word in ['hamstring', 'groin', 'calf', 'quad']):
        return 'soft_tissue'
    elif any(word in injury_lower for word in ['ankle', 'foot', 'hand', 'finger']):
        return 'bone'
    elif 'concussion' in injury_lower:
        return 'concussion'
    elif any(word in injury_lower for word in ['knee', 'acl', 'mcl']):
        return 'knee'
    else:
        return 'other'


def estimate_games_missed(status: str, notes: str) -> int:
    """Estimate games missed from notes"""
    notes_lower = str(notes).lower()
    
    if 'out-ir' in status.lower() or 'out-season' in status.lower():
        return 4
    elif '4 weeks' in notes_lower or '4+ weeks' in notes_lower:
        return 4
    elif '3-week' in notes_lower:
        return 3
    elif '2-week' in notes_lower or '2+ weeks' in notes_lower:
        return 2
    elif status == 'OUT':
        return 1
    else:
        return 0


def is_returning(status: str, notes: str) -> bool:
    """Check if player is returning this week"""
    notes_lower = str(notes).lower()
    
    if status == 'ACTIVE' and any(word in notes_lower for word in ['back', 'return', 'debut', 'ready']):
        return True
    return False


def enhance_injury_file(input_file: Path, output_file: Path):
    """Add required columns to injury file"""
    
    print("📂 Loading injury report...")
    df = pd.read_csv(input_file)
    
    print(f"✅ Found {len(df)} injury entries")
    
    # Add new columns
    df['Games_Missed'] = df.apply(
        lambda row: estimate_games_missed(row['Status'], row.get('Notes', '')), 
        axis=1
    )
    
    df['Injury_Type'] = df['Injury'].apply(classify_injury_type)
    
    df['Returning_This_Week'] = df.apply(
        lambda row: is_returning(row['Status'], row.get('Notes', '')),
        axis=1
    )
    
    df['Weeks_Since_Return'] = 0  # Default to 0
    
    # Save
    df.to_csv(output_file, index=False)
    
    print(f"✅ Enhanced injury file saved: {output_file}")
    print(f"\n📊 Injury breakdown:")
    print(f"   OUT: {len(df[df['Status'] == 'OUT'])}")
    print(f"   DOUBTFUL: {len(df[df['Status'] == 'DOUBTFUL'])}")
    print(f"   QUESTIONABLE: {len(df[df['Status'] == 'QUESTIONABLE'])}")
    print(f"   ACTIVE (returning): {len(df[df['Returning_This_Week'] == True])}")
    
    return df


if __name__ == "__main__":
    project_root = Path(r"C:\Users\scott\Desktop\nfl-betting-system")
    
    input_file = project_root / "data" / "week7_injury_report.txt"
    output_file = project_root / "data" / "wk7_injuries.csv"
    
    print("🏥 Converting Injury Report to Enhanced Format")
    print("="*60)
    
    df = enhance_injury_file(input_file, output_file)
    
    print("\n" + "="*60)
    print("✅ Conversion complete!")
    print(f"\nFile saved: wk7_injuries.csv")
    print("\nNow run: python scripts\\test_week7.py")
