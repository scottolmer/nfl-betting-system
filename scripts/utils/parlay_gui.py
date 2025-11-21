"""Parlay GUI Display - Shows parlays in a nice popup window"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import pyperclip
from datetime import datetime
from typing import List, Dict


class ParlayDisplayWindow:
    """Display parlays in a nice GUI window"""
    
    def __init__(self, content_markdown: str, title: str = "Parlay Results"):
        """
        Create and show a parlay display window
        
        Args:
            content_markdown: The formatted parlay content to display
            title: Window title
        """
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("1200x700")
        self.content = content_markdown
        
        # Button frame at top
        button_frame = ttk.Frame(self.root)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="📋 Copy to Clipboard", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✅ Close", command=self.root.destroy).pack(side=tk.LEFT, padx=5)
        
        # Text display area
        text_frame = ttk.Frame(self.root)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.text_widget = scrolledtext.ScrolledText(
            text_frame, 
            wrap=tk.WORD, 
            font=("Courier New", 10),
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="#d4d4d4"
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Insert content
        self.text_widget.insert(tk.END, self.content)
        self.text_widget.config(state=tk.DISABLED)
        
        # Center window on screen
        self.center_window()
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def copy_to_clipboard(self):
        """Copy content to clipboard"""
        try:
            pyperclip.copy(self.content)
            messagebox.showinfo("✅ Success", "Results copied to clipboard!")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Failed to copy: {e}")
    
    def show(self):
        """Show the window and start mainloop"""
        # Make sure window can be closed with Ctrl+C
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.root.mainloop()


def format_parlays_for_display(parlays: Dict, optimized: bool = False, week: int = None) -> str:
    """
    Format parlays into a nice markdown display
    
    Args:
        parlays: Dictionary of parlays by type (2-leg, 3-leg, etc.)
        optimized: Whether these are optimized parlays
        week: NFL week number
        
    Returns:
        Formatted markdown string
    """
    lines = []
    
    # Header
    lines.append("=" * 80)
    parlay_type_str = "OPTIMIZED LOW-CORRELATION PARLAYS" if optimized else "TRADITIONAL PARLAYS"
    lines.append(f"🏈 {parlay_type_str}")
    if week:
        lines.append(f"📅 Week {week}")
    lines.append(f"🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 80)
    lines.append("")
    
    total_parlays = sum(len(v) for v in parlays.values())
    lines.append(f"📊 Total Parlays: {total_parlays}")
    lines.append("")
    
    # Display each parlay type
    for leg_type in ['2-leg', '3-leg', '4-leg', '5-leg']:
        leg_parlays = parlays.get(leg_type, [])
        if not leg_parlays:
            continue
            
        lines.append("")
        lines.append("=" * 80)
        lines.append(f"🎯 {leg_type.upper()} PARLAYS ({len(leg_parlays)} total)")
        lines.append("=" * 80)
        lines.append("")
        
        for i, parlay in enumerate(leg_parlays, 1):
            # Parlay header
            conf = parlay.combined_confidence
            lines.append(f"┌─ PARLAY #{i} ─────────────────────────────────────────")
            lines.append(f"│ Combined Confidence: {conf:.1f}%")
            lines.append(f"│ Number of Legs: {len(parlay.legs)}")
            lines.append("├───────────────────────────────────────────────────────")
            
            # Display each leg
            for j, leg in enumerate(parlay.legs, 1):
                prop = leg.prop
                bet_type = getattr(prop, 'bet_type', 'OVER')
                lines.append(f"│ LEG {j}:")
                lines.append(f"│   Player: {prop.player_name} ({prop.team} vs {prop.opponent})")
                lines.append(f"│   Prop: {prop.stat_type} {bet_type} {prop.line}")
                lines.append(f"│   Confidence: {leg.final_confidence:.1f}%")
                if j < len(parlay.legs):
                    lines.append("│")
            
            lines.append("└───────────────────────────────────────────────────────")
            lines.append("")
    
    # Footer
    lines.append("")
    lines.append("=" * 80)
    lines.append("💡 TIP: Use these parlays as a starting point for your betting decisions")
    lines.append("⚠️  Always verify odds and player status before placing bets")
    lines.append("=" * 80)
    
    return "\n".join(lines)


def show_parlays_gui(parlays: Dict, optimized: bool = False, week: int = None):
    """
    Show parlays in a GUI window (non-blocking)
    
    Args:
        parlays: Dictionary of parlays by type
        optimized: Whether these are optimized parlays  
        week: NFL week number
    """
    import threading
    import time
    
    def show_window():
        try:
            title = "Optimized Parlays" if optimized else "Traditional Parlays"
            if week:
                title += f" - Week {week}"
            
            content = format_parlays_for_display(parlays, optimized, week)
            window = ParlayDisplayWindow(content, title)
            window.show()
        except Exception as e:
            print(f"\nGUI Error: {e}")
            print("Continuing without GUI...\n")
    
    # Run in background thread so CLI doesn't block
    thread = threading.Thread(target=show_window, daemon=True)
    thread.start()
    
    # Give it a moment to start, then return control to CLI
    time.sleep(0.5)
