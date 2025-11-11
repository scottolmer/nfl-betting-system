#!/usr/bin/env python
"""Add tracking to parlay generation in app.py"""

from pathlib import Path

def add_parlay_tracking():
    """Add tracker.add_parlay() calls in the parlay generation sections"""
    
    app_file = Path("ui/app.py")
    
    with open(app_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified = False
    new_lines = []
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # After "parlay_builder.build_parlays" - add tracking for Traditional
        if 'parlay_builder.build_parlays(' in line and i < len(lines) - 10:
            # Check if tracking already added
            next_10_lines = ''.join(lines[i:i+10])
            if 'tracker.add_parlay' not in next_10_lines:
                # Find the closing of parlays dict assignment
                indent = "                    "
                tracking_code = f"""
{indent}# Track generated parlays
{indent}for leg_type, leg_parlays in parlays.items():
{indent}    for parlay in leg_parlays:
{indent}        props_data = []
{indent}        for leg in parlay.legs:
{indent}            props_data.append({{
{indent}                "player": leg.prop.player_name,
{indent}                "team": leg.prop.team,
{indent}                "opponent": leg.prop.opponent,
{indent}                "stat_type": leg.prop.stat_type,
{indent}                "line": leg.prop.line,
{indent}                "direction": leg.prop.direction,
{indent}                "confidence": leg.final_confidence,
{indent}                "agent_scores": leg.prop.agent_scores
{indent}            }})
{indent}        tracker.add_parlay(
{indent}            week=st.session_state.week,
{indent}            year=2024,
{indent}            parlay_type="traditional",
{indent}            props=props_data,
{indent}            raw_confidence=parlay.combined_confidence,
{indent}            effective_confidence=parlay.combined_confidence,
{indent}            correlations=[],
{indent}            payout_odds=450,
{indent}            kelly_bet_size=parlay.recommended_units * 10
{indent}        )
{indent}
{indent}st.success(f"✅ Generated and tracked {{len([p for parlays_dict in [parlays] for p in parlays_dict.get(lt, []) for lt in ['2-leg', '3-leg', '4-leg', '5-leg']])}}} parlays")
"""
                new_lines.append(tracking_code)
                modified = True
    
    if modified:
        with open(app_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print("✅ Added tracking to Traditional parlay generation")
        print("\nNote: Enhanced parlay tracking is more complex.")
        print("For now, Traditional parlays will be tracked automatically.")
        print("\nRun your app and generate Traditional parlays to test:")
        print("  cd ui")
        print("  streamlit run app.py")
        return True
    else:
        print("⚠️ Could not find parlay generation code or already modified")
        return False

if __name__ == "__main__":
    add_parlay_tracking()
