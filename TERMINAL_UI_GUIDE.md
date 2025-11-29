# NFL Betting Terminal UI - Quick Start Guide

## Overview

The Terminal UI provides a CLI-style interface for the NFL Betting System with:
- **Dark terminal theme** with green monospace text
- **Natural language command input** (just like your CLI)
- **Instant results** that stream below commands
- **Command history** for quick reuse
- **Quick action buttons** for common operations

## Running the Terminal UI

```bash
# Quick start
run_terminal_ui.bat

# Or manually
streamlit run terminal_ui.py
```

## Quick Commands (Buttons)

- **📋 help** - Show all available commands and examples
- **📅 week X props** - Show all props for current week
- **🔥 top 20 props** - Display highest confidence props
- **🎲 standard parlays** - Build traditional 2, 3, 4-leg parlays
- **⚡ optimized parlays** - Build correlation-aware optimized parlays
- **🧹 clear** - Clear terminal output buffer

## Natural Language Commands

Type commands in plain English in the command input box:

### Viewing Props
```
show me props for week 12
top 20 QB props
show all props with confidence over 70
show under bets for week 12
filter to RB props
```

### Building Parlays
```
build 2-leg, 3-leg, and 4-leg parlays for week 12
create a 3-leg QB parlay
build optimized parlays for week 12
build optimized 2-leg and 3-leg parlays
make me a 4-leg parlay excluding teams BUF, HOU
```

### Analysis
```
explain parlay TRAD_W12_abc123
show agent breakdown for Patrick Mahomes
what are the correlation risks?
```

### Filtering
```
show only OVER bets
filter to UNDER bets only
show QB props with confidence > 70
filter to RBs and WRs
```

### Other
```
list available weeks
export parlays for week 12
preview export for week 11
```

## Features

### Standard Parlays vs Optimized Parlays

**Standard Parlays (`build parlay`):**
- Traditional parlay building
- Player diversity optimization
- No correlation detection

**Optimized Parlays (`build optimized parlays`):** ⚡ **RECOMMENDED**
- Detects correlation risks between props
- Penalizes overlapping agent signals
- Shows which agents are driving each prop
- Displays correlation warnings
- Shows penalty adjustments to confidence scores

Example output for optimized parlays:
```
OPTIMIZED PARLAY
Confidence: 65.2% (was 68.1%, -2.9% penalty applied)

⚠️ CORRELATION WARNINGS:
  • Same game correlation detected
  • Volume agent overlap between props

LEGS:
Leg 1: Patrick Mahomes (QB) - KC vs BUF
       Pass Yards OVER 275.5 | Confidence: 72.3%
       Driven by: Volume, GameScript
```

### Command History

The sidebar shows your last 10 commands. Click any command to re-run it instantly.

### Output Buffer

The terminal displays your last 20 command executions with:
- Timestamps
- Command inputs (green text with `$` prompt)
- Results (terminal-style output)
- Color-coded success/error messages

### Week Selector

Change the week in the sidebar to update all week-dependent quick commands.

## Tips

1. **Use optimized parlays** - They detect and penalize correlation risks
2. **Check command history** - Quickly reuse previous commands
3. **Start with help** - Type `help` to see all available examples
4. **Use quick buttons** - Faster than typing for common operations
5. **Natural language works** - Don't worry about exact syntax

## Color Coding

- **Green** (`#00ff00`): Success, normal output, command prompt
- **Red** (`#ff0000`): Errors, warnings
- **Yellow** (`#ffff00`): Important markers like `[BET]`
- **Gray** (`#666`): Secondary info, timestamps

## Troubleshooting

**Interface won't load:**
- Ensure `ANTHROPIC_API_KEY` is set in your environment
- Check that all required packages are installed

**Commands not working:**
- Try rephrasing in natural language
- Use the help command to see examples
- Check sidebar history to see if command was received

**Slow response:**
- Large queries (like analyzing all props) take time
- The "Processing..." spinner shows when working
- Consider narrowing your query (e.g., specific position or confidence range)

## Examples

### Typical Workflow

1. Start the UI: `run_terminal_ui.bat`
2. Click **"⚡ optimized parlays"** button
3. Wait for results to stream
4. Review correlation warnings and penalties
5. Type follow-up: `explain parlay TRAD_W12_abc123` to see details

### Research Workflow

1. Type: `show top 20 QB props`
2. Type: `show agent breakdown for Patrick Mahomes`
3. Type: `show only OVER bets`
4. Click history to re-run modified versions

## Architecture

The Terminal UI uses:
- **NLQueryInterface** from `chat_interface.py` for command parsing
- **Claude Haiku** for natural language understanding
- **Streamlit** for the web interface with custom CSS for terminal styling
- **EnhancedParlayBuilder** for optimized parlay generation
- **ParlayBuilder** for standard parlays

## Comparison with CLI

| Feature | CLI | Terminal UI |
|---------|-----|-------------|
| Speed | Fast | Moderate (web overhead) |
| Workflow | Command-based | Command-based |
| History | Limited | Full visual history |
| Visual | Text only | Color-coded, styled |
| Natural Language | No | Yes (via Haiku) |
| Setup | None | Requires browser |

**When to use CLI:**
- Quick operations
- Scripting/automation
- No browser available

**When to use Terminal UI:**
- Visual exploration
- Natural language queries
- Need to review history
- Prefer GUI interaction
