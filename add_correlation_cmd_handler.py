#!/usr/bin/env python3
"""
Add build-parlays-correlation command to run.py
"""
import os

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
run_py_path = os.path.join(script_dir, "run.py")

# Read the file
with open(run_py_path, "r", encoding="utf-8") as f:
    content = f.read()

# The exact text to find
old_text = """            run_parlay_builder_optimized(week=week, quality_threshold=quality_threshold)
        
        else:
            print(f"❌ Unknown command: {command}")"""

# The replacement text
new_text = """            run_parlay_builder_optimized(week=week, quality_threshold=quality_threshold)
        
        elif command == 'build-parlays-correlation':
            week = None
            quality_threshold = None
            
            # Parse arguments
            i = 2
            while i < len(sys.argv):
                arg = sys.argv[i]
                
                if arg == '--quality' and i + 1 < len(sys.argv):
                    try:
                        quality_threshold = int(sys.argv[i + 1])
                        i += 2
                    except ValueError:
                        i += 1
                elif arg.lower() == 'week' and i + 1 < len(sys.argv):
                    try:
                        week = int(sys.argv[i + 1])
                        i += 2
                    except ValueError:
                        i += 1
                else:
                    try:
                        week = int(arg)
                    except ValueError:
                        pass
                    i += 1
            
            run_parlay_builder_with_correlation(week=week, quality_threshold=quality_threshold)
        
        else:
            print(f"❌ Unknown command: {command}")"""

# Check if this text exists
if old_text not in content:
    print("❌ ERROR: Could not find the text to replace!")
    print("This might mean:")
    print("  1. The function wasn't added to run.py yet")
    print("  2. The text format is different than expected")
    print("\nTrying alternative approach...")
    
    # Alternative: check if correlation function exists
    if "run_parlay_builder_with_correlation" in content:
        print("✅ Found: run_parlay_builder_with_correlation function exists")
        print("⚠️  The command handler needs to be added manually")
        print("\nPlease open run.py and add this code before the final 'else:' statement:")
        print("""
        elif command == 'build-parlays-correlation':
            week = None
            quality_threshold = None
            
            # Parse arguments
            i = 2
            while i < len(sys.argv):
                arg = sys.argv[i]
                
                if arg == '--quality' and i + 1 < len(sys.argv):
                    try:
                        quality_threshold = int(sys.argv[i + 1])
                        i += 2
                    except ValueError:
                        i += 1
                elif arg.lower() == 'week' and i + 1 < len(sys.argv):
                    try:
                        week = int(sys.argv[i + 1])
                        i += 2
                    except ValueError:
                        i += 1
                else:
                    try:
                        week = int(arg)
                    except ValueError:
                        pass
                    i += 1
            
            run_parlay_builder_with_correlation(week=week, quality_threshold=quality_threshold)
        """)
    exit(1)

# Replace it
updated_content = content.replace(old_text, new_text)

# Write back
with open(run_py_path, "w", encoding="utf-8") as f:
    f.write(updated_content)

print("✅ SUCCESS! Added 'build-parlays-correlation' command handler!")
print("\nYou can now use these commands:")
print("  python run build-parlays-correlation 8")
print("  python run build-parlays-correlation 8 --quality 50")
print("\nThe system will:")
print("  1. Build 10 optimized low-correlation parlays for Week 8")
print("  2. Apply correlation-adjusted confidence scoring")
print("  3. Show RAW vs ADJUSTED confidence for each parlay")
print("  4. Auto-size units based on correlation severity")
print("  5. Save all data to parlay_runs/wk8_correlation_adj/")
