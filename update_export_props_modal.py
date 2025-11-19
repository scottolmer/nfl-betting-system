#!/usr/bin/env python
"""Quick updater for export-props modal window - run this to update betting_cli.py"""

def update_betting_cli():
    """Update the export_props_command to use modal window"""
    import os
    
    filepath = os.path.join(os.path.dirname(__file__), 'betting_cli.py')
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the export_props_command method
    old_start = 'def export_props_command(self, count_str="50"):'
    old_end = 'except ImportError:\n            print("\\n💡 Tip: Install pyperclip for auto-clipboard:")\n            print("   pip install pyperclip")\n            print("\\n   Or manually copy the JSON above and paste into Claude\\n")'
    
    new_method = '''def export_props_command(self, count_str="50"):
        """Export top props as JSON for conversational Claude analysis"""
        try:
            count = int(count_str)
        except ValueError:
            count = 50
        
        print(f"\\n🔄 Loading data for Week {self.week}...")
        context = self.loader.load_all_data(week=self.week)
        
        print(f"📊 Analyzing props...")
        all_analyses = self.analyzer.analyze_all_props(context, min_confidence=40)
        
        # Deduplicate: keep only highest confidence for each player+stat_type+bet_type
        seen = {}
        deduped_analyses = []
        
        for analysis in sorted(all_analyses, key=lambda x: x.final_confidence, reverse=True):
            prop = analysis.prop
            bet_type = getattr(prop, 'bet_type', 'OVER')
            key = (prop.player_name.lower(), prop.stat_type, bet_type)
            
            if key not in seen:
                seen[key] = True
                deduped_analyses.append(analysis)
                if len(deduped_analyses) >= count:
                    break
        
        top_props = deduped_analyses
        
        print(f"\\n📤 Exporting {len(top_props)} props to JSON...")
        
        # Generate exports
        json_export, summary = PropsJSONExporter.export_props_with_summary(top_props)
        display_text = PropsJSONExporter.format_for_display(top_props)
        
        print("\\n📋 Opening modal window...")
        
        # Show modal window with all three views (Props View, Summary, JSON)
        PropsJSONExporter.show_modal_window(json_export, summary, display_text)
        
        # Also print summary to console as fallback
        print(summary)
        print("\\n✅ Modal window opened!")
        print("   Ask Claude questions like:")
        print("   - 'Create a 3-leg parlay from high passing yards props'")
        print("   - 'Which players correlate most?'")
        print("   - 'Show me all TD props with bellcow RBs'\\n")'''
    
    # Find the old method
    start_idx = content.find('    def export_props_command(self, count_str="50"):')
    if start_idx == -1:
        print("❌ Could not find export_props_command method")
        return False
    
    # Find the end of the method (next method or end of class)
    next_def_idx = content.find('    def generate_parlays(self, min_conf_str="58"):', start_idx)
    if next_def_idx == -1:
        print("❌ Could not find end of method")
        return False
    
    # Replace the method
    new_content = content[:start_idx] + new_method + '\n    \n    ' + content[next_def_idx:]
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ betting_cli.py updated successfully!")
    print("\n📝 Changes:")
    print("   ✓ export-props now opens a modal window")
    print("   ✓ Modal has 3 tabs: Props View, Summary, JSON Export")
    print("   ✓ Copy to clipboard button in modal")
    print("   ✓ Non-blocking - CLI stays responsive")
    return True

if __name__ == "__main__":
    import sys
    if update_betting_cli():
        print("\n🎉 Ready to use! Try: export-props 50")
        sys.exit(0)
    else:
        sys.exit(1)
