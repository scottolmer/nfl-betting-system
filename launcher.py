#!/usr/bin/env python
"""
NFL Betting System Launcher - Desktop GUI (FILE-BASED OUTPUT CAPTURE)
Tkinter-based launcher for running parlay generation and prop analysis
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import os
import sys
import tempfile
from pathlib import Path
from datetime import datetime
import pyperclip

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"


class FileValidator:
    """Validates required data files"""
    
    CRITICAL_FILES = {
        'offensive_dvoa': 'wk{week}_offensive_DVOA.csv',
        'defensive_dvoa': 'wk{week}_defensive_DVOA.csv',
        'betting_lines': 'wk{week}_betting_lines_draftkings.csv',
        'injuries': 'wk{week}-injury-report.csv',
    }
    
    @classmethod
    def validate(cls, week):
        """Validate that required files exist for the week"""
        missing_critical = []
        missing_optional = []
        
        for key, filename_pattern in cls.CRITICAL_FILES.items():
            filename = filename_pattern.format(week=week)
            if not (DATA_DIR / filename).exists():
                missing_critical.append((key, filename))
        
        is_valid = len(missing_critical) == 0
        return is_valid, missing_critical, missing_optional


class ResultsPreviewWindow:
    """Resizable results preview window"""
    
    def __init__(self, parent, content_markdown):
        self.window = tk.Toplevel(parent)
        self.window.title("Parlay Results Preview")
        self.window.geometry("1200x700")
        self.content = content_markdown
        
        button_frame = ttk.Frame(self.window)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Copy to Clipboard", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        
        text_frame = ttk.Frame(self.window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=("Courier", 9))
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        self.text_widget.insert(tk.END, self.content)
        self.text_widget.config(state=tk.DISABLED)
        self.window.focus()
    
    def copy_to_clipboard(self):
        """Copy content to clipboard"""
        try:
            pyperclip.copy(self.content)
            messagebox.showinfo("Success", "Results copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy: {e}")


class ProgressWindow:
    """Modal progress window with real-time updates"""
    
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Analysis in Progress")
        self.window.geometry("650x500")
        self.window.resizable(False, False)
        
        self.window.transient(parent)
        self.window.grab_set()
        
        title = ttk.Label(self.window, text="Processing Analysis...", font=("Arial", 12, "bold"))
        title.pack(pady=10)
        
        self.text_widget = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, font=("Courier", 8), height=25, width=75)
        self.text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.text_widget.config(state=tk.DISABLED)
        
        self.status_label = ttk.Label(self.window, text="Starting...", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        self.window.update()
    
    def add_progress(self, text):
        """Add line to progress display"""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, text + "\n")
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)
        self.window.update()
    
    def set_status(self, status):
        """Update status bar"""
        self.status_label.config(text=status)
        self.window.update()
    
    def close(self):
        """Close the progress window"""
        self.window.destroy()


class SubprocessRunner:
    """Manages running subprocesses"""
    
    def __init__(self, progress_window):
        self.progress_window = progress_window
        self.traditional_output = []
        self.enhanced_output = []
        self.top_props_output = []
    
    def run_command(self, command, output_list, label):
        """Run subprocess and capture output via temp file"""
        try:
            self.progress_window.set_status(f"Running: {label}...")
            self.progress_window.add_progress(f"\n{'='*70}")
            self.progress_window.add_progress(f"Starting: {label}")
            self.progress_window.add_progress(f"{'='*70}\n")
            
            # Create temp file for output
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt', encoding='utf-8') as f:
                temp_file = f.name
            
            try:
                # Run process with output redirected to file
                with open(temp_file, 'w', encoding='utf-8') as f:
                    process = subprocess.Popen(
                        command,
                        stdout=f,
                        stderr=subprocess.STDOUT,
                        text=True,
                        cwd=str(PROJECT_ROOT)
                    )
                    process.wait()
                
                # Read captured output
                with open(temp_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.rstrip('\n\r')
                        if line:
                            output_list.append(line)
                            if any(x in line for x in ['Built', 'Parlay', 'PARLAY', 'Total', 'Confidence']):
                                self.progress_window.add_progress(f"  {line}")
                
                self.progress_window.add_progress(f"\n✅ {label} completed")
            
            finally:
                # Clean up temp file
                if os.path.exists(temp_file):
                    os.remove(temp_file)
        
        except Exception as e:
            self.progress_window.add_progress(f"❌ Error running {label}: {e}")
            import traceback
            self.progress_window.add_progress(traceback.format_exc())
    
    def run_parlays_parallel(self, week, bankroll):
        """Run traditional and enhanced parlays in parallel"""
        
        self.progress_window.add_progress("=" * 70)
        self.progress_window.add_progress(f"🎯 WEEK {week} PARLAY ANALYSIS")
        self.progress_window.add_progress(f"💰 Bankroll: ${bankroll}")
        self.progress_window.add_progress("=" * 70)
        
        trad_cmd = [sys.executable, "run.py", "build-parlays", "week", str(week)]
        enh_cmd = [sys.executable, "run.py", "build-parlays-optimized", str(week)]
        
        trad_thread = threading.Thread(target=self.run_command, args=(trad_cmd, self.traditional_output, "Traditional Parlays"))
        enh_thread = threading.Thread(target=self.run_command, args=(enh_cmd, self.enhanced_output, "Enhanced Parlays"))
        
        trad_thread.start()
        enh_thread.start()
        trad_thread.join()
        enh_thread.join()
        
        self.progress_window.add_progress("\n" + "=" * 70)
        self.progress_window.add_progress("✅ ALL ANALYSIS COMPLETE")
        self.progress_window.add_progress("=" * 70)
        self.progress_window.set_status("Complete. Preparing results...")
    
    def run_top_props(self, week):
        """Run top props analysis"""
        
        self.progress_window.add_progress("=" * 70)
        self.progress_window.add_progress(f"🎯 TOP 20 PROPS - WEEK {week}")
        self.progress_window.add_progress("=" * 70)
        
        cmd = [sys.executable, "run.py", "analyze", "week", str(week)]
        self.run_command(cmd, self.top_props_output, "Top Props Analysis")
        
        self.progress_window.add_progress("\n" + "=" * 70)
        self.progress_window.add_progress("✅ ANALYSIS COMPLETE")
        self.progress_window.add_progress("=" * 70)
        self.progress_window.set_status("Complete. Preparing results...")
    
    def combine_parlay_results(self, bankroll):
        """Combine results into markdown"""
        
        trad_text = "\n".join(self.traditional_output)
        enh_text = "\n".join(self.enhanced_output)
        
        combined = f"""# NFL BETTING SYSTEM ANALYSIS
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Bankroll: ${bankroll}

## TRADITIONAL PARLAYS
{trad_text}

## ENHANCED PARLAYS (LOW CORRELATION)
{enh_text}

---
*Note: Bankroll display assumes $10 per unit*
*Results saved to: parlay_runs folder*
"""
        return combined
    
    def get_top_props_markdown(self):
        """Get top props as markdown"""
        props_text = "\n".join(self.top_props_output)
        markdown = f"""# TOP 20 PROPS ANALYSIS
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{props_text}
"""
        return markdown


class NFLBettingLauncher:
    """Main launcher GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("NFL Betting System Launcher")
        self.root.geometry("650x450")
        self.root.resizable(False, False)
        
        style = ttk.Style()
        style.theme_use('clam')
        
        header = ttk.Label(root, text="🏈 NFL Betting System Launcher", font=("Arial", 14, "bold"))
        header.pack(pady=10)
        
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Select Action:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.action_var = tk.StringVar(value="parlays")
        ttk.Radiobutton(main_frame, text="Generate Parlays (Traditional + Enhanced)", variable=self.action_var, value="parlays").grid(row=1, column=0, sticky=tk.W, padx=20)
        ttk.Radiobutton(main_frame, text="View Top 20 Props", variable=self.action_var, value="props").grid(row=2, column=0, sticky=tk.W, padx=20, pady=(0, 10))
        
        ttk.Label(main_frame, text="Select Week:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=5)
        
        week_frame = ttk.Frame(main_frame)
        week_frame.grid(row=4, column=0, sticky=tk.W, padx=20, pady=(0, 10))
        
        self.week_var = tk.StringVar(value="9")
        ttk.Combobox(week_frame, textvariable=self.week_var, values=[str(i) for i in range(1, 18)], state="readonly", width=5).pack(side=tk.LEFT)
        ttk.Label(week_frame, text="(analyzes previous week)", font=("Arial", 9, "italic")).pack(side=tk.LEFT, padx=10)
        
        ttk.Label(main_frame, text="Bankroll (Required):", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky=tk.W, pady=5)
        
        bankroll_frame = ttk.Frame(main_frame)
        bankroll_frame.grid(row=6, column=0, sticky=tk.W, padx=20, pady=(0, 15))
        
        ttk.Label(bankroll_frame, text="$").pack(side=tk.LEFT)
        self.bankroll_var = tk.StringVar(value="100")
        ttk.Entry(bankroll_frame, textvariable=self.bankroll_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(bankroll_frame, text="(displayed at $10/unit)", font=("Arial", 9, "italic")).pack(side=tk.LEFT)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, sticky=tk.EW, pady=15)
        
        ttk.Button(button_frame, text="Run Analysis", command=self.run_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset", command=self.reset_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=root.quit).pack(side=tk.LEFT, padx=5)
        
        info_frame = ttk.LabelFrame(main_frame, text="Info", padding="10")
        info_frame.grid(row=8, column=0, sticky=tk.EW, pady=10)
        
        self.info_text = tk.Label(info_frame, text="Ready to analyze. Select action, week, and bankroll then click Run.", font=("Arial", 9), wraplength=550, justify=tk.LEFT)
        self.info_text.pack()
    
    def reset_form(self):
        """Reset form to defaults"""
        self.action_var.set("parlays")
        self.week_var.set("9")
        self.bankroll_var.set("100")
        self.info_text.config(text="Ready to analyze. Select action, week, and bankroll then click Run.")
    
    def run_analysis(self):
        """Run the selected analysis"""
        
        if not self.bankroll_var.get().strip():
            messagebox.showerror("Error", "Bankroll is required!")
            return
        
        try:
            bankroll = float(self.bankroll_var.get())
            if bankroll <= 0:
                raise ValueError("Bankroll must be positive")
        except ValueError:
            messagebox.showerror("Error", "Invalid bankroll amount!")
            return
        
        week_selected = int(self.week_var.get())
        week_to_analyze = week_selected - 1
        
        if week_to_analyze < 1:
            messagebox.showerror("Error", "Cannot analyze week 0. Select week 2 or higher.")
            return
        
        is_valid, missing_critical, missing_optional = FileValidator.validate(week_to_analyze)
        
        if not is_valid:
            error_msg = "❌ Missing Required Files:\n\n"
            for key, filename in missing_critical:
                error_msg += f"  • {filename}\n"
            error_msg += f"\n📁 Checked in: {DATA_DIR}\n\n"
            error_msg += "Possible naming issues:\n"
            error_msg += "  • Files should be in root data folder (not subfolders)\n"
            error_msg += "  • Check exact spelling and capitalization\n"
            error_msg += f"  • Expected format: wk{week_to_analyze}_[type].csv\n"
            error_msg += f"  • Injury file: wk{week_to_analyze}-injury-report.csv (note the hyphen)\n"
            messagebox.showerror("File Validation Error", error_msg)
            return
        
        action = self.action_var.get()
        thread = threading.Thread(target=self._run_analysis_thread, args=(action, week_to_analyze, bankroll))
        thread.start()
    
    def _run_analysis_thread(self, action, week, bankroll):
        """Background thread for running analysis"""
        try:
            progress = ProgressWindow(self.root)
            runner = SubprocessRunner(progress)
            
            if action == "parlays":
                runner.run_parlays_parallel(week, bankroll)
                results_markdown = runner.combine_parlay_results(bankroll)
            else:
                runner.run_top_props(week)
                results_markdown = runner.get_top_props_markdown()
            
            progress.close()
            
            results_window = ResultsPreviewWindow(self.root, results_markdown)
            
            try:
                pyperclip.copy(results_markdown)
                messagebox.showinfo("Success", "Results copied to clipboard!")
            except Exception as e:
                messagebox.showwarning("Copy Failed", f"Could not auto-copy to clipboard: {e}\n\nYou can still copy manually from the preview window.")
        
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = NFLBettingLauncher(root)
    root.mainloop()


if __name__ == "__main__":
    main()
