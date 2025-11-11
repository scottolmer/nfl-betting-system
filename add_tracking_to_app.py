#!/usr/bin/env python
"""Script to add tracking features to existing app.py"""

import sys
from pathlib import Path

def add_tracking_to_app():
    """Add tracking import and initialize tracker in app.py"""
    
    app_file = Path("ui/app.py")
    
    if not app_file.exists():
        print("❌ ui/app.py not found")
        return False
    
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already added
    if 'parlay_tracker' in content.lower():
        print("✅ Tracking already integrated")
        return True
    
    # Add import after DependencyAnalyzer import
    old_import = "from scripts.analysis.dependency_analyzer import DependencyAnalyzer"
    new_import = old_import + "\nfrom scripts.analysis.parlay_tracker import ParlayTracker"
    
    if old_import in content:
        content = content.replace(old_import, new_import)
    else:
        print("⚠️ Could not find DependencyAnalyzer import")
        return False
    
    # Add tracker initialization after session state setup
    tracker_init = """
# Initialize tracker
@st.cache_resource
def get_tracker():
    tracker_file = project_root / "parlay_tracking.json"
    return ParlayTracker(str(tracker_file))

tracker = get_tracker()
"""
    
    # Find where to insert (after selected_prop session state)
    insert_marker = "if 'selected_prop' not in st.session_state:\n    st.session_state.selected_prop = None"
    
    if insert_marker in content:
        content = content.replace(insert_marker, insert_marker + "\n" + tracker_init)
    else:
        print("⚠️ Could not find session state section")
        return False
    
    # Backup original
    backup_file = Path("ui/app_backup.py")
    if not backup_file.exists():
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(open(app_file, 'r', encoding='utf-8').read())
        print(f"✅ Backed up to {backup_file}")
    
    # Write updated content
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Added tracking import and initialization")
    print("\nNext: Add tracking tabs to your app manually, or:")
    print("  1. Keep using current app (tracking runs in background)")
    print("  2. Add Bet Tracking tab later when ready")
    print("\nTracker is now available as 'tracker' variable in app.py")
    
    return True

if __name__ == "__main__":
    success = add_tracking_to_app()
    sys.exit(0 if success else 1)
