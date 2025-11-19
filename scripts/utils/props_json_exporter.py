"""
Props JSON Exporter - Export player props in structured JSON format for conversational analysis
Allows pasting props into Claude for natural language parlay generation
"""

import json
from typing import List, Optional, Tuple
from datetime import datetime
from scripts.analysis.models import PropAnalysis


class PropsJSONExporter:
    """Exports player props as structured JSON for Claude analysis"""

    def __init__(self):
        self.exported_props = []

    @staticmethod
    def export_props_to_json(props: List[PropAnalysis], num_props: Optional[int] = None) -> str:
        """
        Convert PropAnalysis objects to clean JSON format suitable for Claude
        
        Args:
            props: List of PropAnalysis objects (typically top props by confidence)
            num_props: Optional limit on number of props to export (default: all)
            
        Returns:
            JSON string ready for pasting into Claude
        """
        if num_props:
            props = props[:num_props]

        props_data = []
        for prop in props:
            prop_dict = {
                "player": prop.prop.player_name,
                "position": prop.prop.position,
                "team": prop.prop.team,
                "opponent": prop.prop.opponent,
                "stat_type": prop.prop.stat_type,
                "line": prop.prop.line,
                "bet_type": prop.prop.bet_type,
                "week": prop.prop.week,
                "game_total": prop.prop.game_total,
                "spread": prop.prop.spread,
                "is_home": prop.prop.is_home,
                "confidence": prop.final_confidence,
                "recommendation": prop.recommendation,
                "agent_breakdown": {
                    "DVOA": prop.agent_breakdown.get("DVOA", 50),
                    "Matchup": prop.agent_breakdown.get("Matchup", 50),
                    "Volume": prop.agent_breakdown.get("Volume", 50),
                    "Injury": prop.agent_breakdown.get("Injury", 50),
                    "Trend": prop.agent_breakdown.get("Trend", 50),
                    "GameScript": prop.agent_breakdown.get("GameScript", 50),
                    "Variance": prop.agent_breakdown.get("Variance", 50),
                    "Weather": prop.agent_breakdown.get("Weather", 50),
                },
                "rationale": prop.rationale,
                "edge_explanation": prop.edge_explanation,
            }
            props_data.append(prop_dict)

        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_props": len(props_data),
            "props": props_data,
        }

        return json.dumps(export_data, indent=2)

    @staticmethod
    def export_props_compact(props: List[PropAnalysis], num_props: Optional[int] = None) -> str:
        """
        Export props in compact format - one prop per line for easier scanning
        
        Args:
            props: List of PropAnalysis objects
            num_props: Optional limit on number of props
            
        Returns:
            Compact JSON string
        """
        if num_props:
            props = props[:num_props]

        props_data = []
        for i, prop in enumerate(props, 1):
            prop_dict = {
                "#": i,
                "player": f"{prop.prop.player_name} ({prop.prop.position})",
                "bet": f"{prop.prop.bet_type} {prop.prop.line}",
                "stat": prop.prop.stat_type,
                "matchup": f"{prop.prop.team} vs {prop.prop.opponent}",
                "confidence": f"{prop.final_confidence}%",
                "agents": {
                    "DVOA": prop.agent_breakdown.get("DVOA", 50),
                    "Matchup": prop.agent_breakdown.get("Matchup", 50),
                    "Volume": prop.agent_breakdown.get("Volume", 50),
                    "Injury": prop.agent_breakdown.get("Injury", 50),
                    "Trend": prop.agent_breakdown.get("Trend", 50),
                },
                "why": " | ".join(prop.rationale[:2]) if prop.rationale else "Good matchup",
            }
            props_data.append(prop_dict)

        return json.dumps(props_data, indent=2)

    @staticmethod
    def export_props_with_summary(props: List[PropAnalysis], num_props: Optional[int] = None) -> Tuple[str, str]:
        """
        Export props AND return a human-readable summary
        Useful for displaying what's being exported
        
        Args:
            props: List of PropAnalysis objects
            num_props: Optional limit
            
        Returns:
            Tuple of (JSON string, summary string)
        """
        if num_props:
            props = props[:num_props]

        summary_lines = [
            f"Exporting {len(props)} props for Claude analysis:\n",
            "Top Props by Confidence:",
            "-" * 60,
        ]

        for i, prop in enumerate(props, 1):
            summary = (
                f"{i:2d}. {prop.prop.player_name:20s} {prop.prop.bet_type} {prop.prop.line:6.1f} "
                f"({prop.prop.stat_type:15s}) | "
                f"Conf: {prop.final_confidence:3d}% | "
                f"{prop.prop.team} vs {prop.prop.opponent}"
            )
            summary_lines.append(summary)

        json_export = PropsJSONExporter.export_props_to_json(props, num_props)
        summary_text = "\n".join(summary_lines)

        return json_export, summary_text

    @staticmethod
    def export_by_stat_type(props: List[PropAnalysis], stat_type: str) -> str:
        """
        Export only props of a specific stat type
        
        Args:
            props: List of PropAnalysis objects
            stat_type: The stat type to filter (e.g., 'passing_yards', 'receiving_yards')
            
        Returns:
            JSON string of filtered props
        """
        filtered = [p for p in props if p.prop.stat_type.lower() == stat_type.lower()]
        return PropsJSONExporter.export_props_to_json(filtered)

    @staticmethod
    def export_by_position(props: List[PropAnalysis], position: str) -> str:
        """
        Export only props for a specific position
        
        Args:
            props: List of PropAnalysis objects
            position: Position code (QB, RB, WR, TE, etc.)
            
        Returns:
            JSON string of filtered props
        """
        filtered = [p for p in props if p.prop.position.upper() == position.upper()]
        return PropsJSONExporter.export_props_to_json(filtered)

    @staticmethod
    def export_high_confidence(props: List[PropAnalysis], min_confidence: int = 70) -> str:
        """
        Export only high-confidence props
        
        Args:
            props: List of PropAnalysis objects
            min_confidence: Minimum confidence threshold (default 70)
            
        Returns:
            JSON string of high-confidence props
        """
        filtered = [p for p in props if p.final_confidence >= min_confidence]
        return PropsJSONExporter.export_props_to_json(filtered)

    @staticmethod
    def format_for_display(props: List[PropAnalysis], num_props: int = None) -> str:
        """
        Format props as readable text for modal display
        
        Args:
            props: List of PropAnalysis objects
            num_props: Optional limit on number to display
            
        Returns:
            Formatted text string
        """
        if num_props:
            props = props[:num_props]

        lines = []
        lines.append("=" * 90)
        lines.append("📊 PLAYER PROPS EXPORT FOR CLAUDE ANALYSIS")
        lines.append("=" * 90)
        lines.append(f"🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"📈 Total Props: {len(props)}")
        lines.append("=" * 90)
        lines.append("")

        for i, prop_analysis in enumerate(props, 1):
            prop = prop_analysis.prop
            conf = prop_analysis.final_confidence

            # Color coding by confidence
            if conf >= 80:
                emoji = "🔥"
            elif conf >= 75:
                emoji = "⭐"
            elif conf >= 70:
                emoji = "✅"
            elif conf >= 65:
                emoji = "📊"
            else:
                emoji = "📈"

            lines.append(f"┌─ PROP #{i} {emoji} ─────────────────────────────────────────────────────")
            lines.append(f"│ Player: {prop.player_name:20s} | Position: {prop.position:3s} | Team: {prop.team:3s}")
            lines.append(f"│ Matchup: {prop.team} vs {prop.opponent}")
            lines.append(f"│")
            lines.append(f"│ Stat Type: {prop.stat_type}")
            lines.append(f"│ Bet Type: {prop.bet_type:6s} | Line: {prop.line:7.1f}")
            lines.append(f"│ Game Total: {str(prop.game_total) if prop.game_total else 'N/A':>6s} | Spread: {str(prop.spread) if prop.spread else 'N/A':>6s}")
            lines.append(f"│")
            lines.append(f"│ ⭐ CONFIDENCE: {conf:6.1f}%")
            lines.append(f"│ Recommendation: {prop_analysis.recommendation}")
            lines.append(f"│")
            lines.append(f"│ Agent Breakdown:")
            lines.append(f"│   DVOA:      {prop_analysis.agent_breakdown.get('DVOA', 50):3.0f}  │  Matchup:   {prop_analysis.agent_breakdown.get('Matchup', 50):3.0f}")
            lines.append(f"│   Volume:    {prop_analysis.agent_breakdown.get('Volume', 50):3.0f}  │  Injury:    {prop_analysis.agent_breakdown.get('Injury', 50):3.0f}")
            lines.append(f"│   Trend:     {prop_analysis.agent_breakdown.get('Trend', 50):3.0f}  │  GameScript:{prop_analysis.agent_breakdown.get('GameScript', 50):3.0f}")
            lines.append(f"│   Variance:  {prop_analysis.agent_breakdown.get('Variance', 50):3.0f}  │  Weather:   {prop_analysis.agent_breakdown.get('Weather', 50):3.0f}")
            lines.append(f"│")

            if prop_analysis.rationale:
                lines.append(f"│ Why This Prop:")
                for reason in prop_analysis.rationale[:3]:  # Show first 3 reasons
                    lines.append(f"│   • {reason}")

            lines.append(f"└" + "─" * 88)
            lines.append("")

        lines.append("=" * 90)
        lines.append("💡 COPY THE JSON AND PASTE INTO CLAUDE")
        lines.append("   Then ask Claude to create custom parlays from these props")
        lines.append("=" * 90)

        return "\n".join(lines)

    @staticmethod
    def show_modal_window(json_export: str, summary_text: str, display_text: str) -> None:
        """
        Display props in a modal window with copy functionality

        Args:
            json_export: JSON formatted props
            summary_text: Summary text display
            display_text: Formatted display text
        """
        try:
            import tkinter as tk
            from tkinter import ttk, scrolledtext, messagebox
            import threading
            import time

            def show_window():
                try:
                    root = tk.Tk()
                    root.title("📊 Props Export for Claude")
                    root.geometry("1200x800")

                    # Button frame
                    button_frame = ttk.Frame(root)
                    button_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

                    def copy_json():
                        try:
                            import pyperclip
                            pyperclip.copy(json_export)
                            messagebox.showinfo("✅ Success", "JSON copied to clipboard!\n\nPaste into Claude with Ctrl+V")
                        except ImportError:
                            messagebox.showerror("❌ Error", "pyperclip not installed.\n\nManually select and copy the JSON.")

                    ttk.Button(button_frame, text="📋 Copy JSON to Clipboard", command=copy_json).pack(side=tk.LEFT, padx=5)
                    ttk.Button(button_frame, text="❌ Close", command=root.destroy).pack(side=tk.LEFT, padx=5)

                    # Text display area with tabs
                    notebook = ttk.Notebook(root)
                    notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

                    # Display tab
                    display_frame = ttk.Frame(notebook)
                    notebook.add(display_frame, text="Props View")

                    display_text_widget = scrolledtext.ScrolledText(
                        display_frame,
                        wrap=tk.WORD,
                        font=("Courier New", 9),
                        bg="#1e1e1e",
                        fg="#d4d4d4",
                        insertbackground="#d4d4d4"
                    )
                    display_text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                    display_text_widget.insert(tk.END, display_text)
                    display_text_widget.config(state=tk.DISABLED)

                    # Summary tab
                    summary_frame = ttk.Frame(notebook)
                    notebook.add(summary_frame, text="Summary")

                    summary_text_widget = scrolledtext.ScrolledText(
                        summary_frame,
                        wrap=tk.WORD,
                        font=("Courier New", 9),
                        bg="#1e1e1e",
                        fg="#d4d4d4",
                        insertbackground="#d4d4d4"
                    )
                    summary_text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                    summary_text_widget.insert(tk.END, summary_text)
                    summary_text_widget.config(state=tk.DISABLED)

                    # JSON tab
                    json_frame = ttk.Frame(notebook)
                    notebook.add(json_frame, text="JSON Export")

                    json_text_widget = scrolledtext.ScrolledText(
                        json_frame,
                        wrap=tk.WORD,
                        font=("Courier New", 8),
                        bg="#1e1e1e",
                        fg="#00ff00",
                        insertbackground="#00ff00"
                    )
                    json_text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                    json_text_widget.insert(tk.END, json_export)
                    json_text_widget.config(state=tk.DISABLED)

                    # Center window
                    root.update_idletasks()
                    width = root.winfo_width()
                    height = root.winfo_height()
                    x = (root.winfo_screenwidth() // 2) - (width // 2)
                    y = (root.winfo_screenheight() // 2) - (height // 2)
                    root.geometry(f'{width}x{height}+{x}+{y}')

                    root.protocol("WM_DELETE_WINDOW", root.destroy)
                    root.mainloop()

                except Exception as e:
                    print(f"\n❌ Modal window error: {e}")
                    print("Continuing without GUI...")

            # Run in background thread
            thread = threading.Thread(target=show_window, daemon=True)
            thread.start()
            time.sleep(0.5)

        except ImportError:
            print("\n⚠️  tkinter not available for modal display")
            print("Displaying in terminal instead...")

    @staticmethod
    def copy_to_clipboard(json_string: str) -> None:
        """
        Copy JSON export to system clipboard (Windows/Linux/Mac)

        Args:
            json_string: The JSON string to copy
        """
        try:
            import pyperclip
            pyperclip.copy(json_string)
            print("\n✓ Props JSON copied to clipboard!")
            print("  Paste into Claude with: Ctrl+V")
        except ImportError:
            print("\n⚠ pyperclip not installed for clipboard access")
            print("  Install with: pip install pyperclip")
            print("\n  Or manually copy the JSON above")
