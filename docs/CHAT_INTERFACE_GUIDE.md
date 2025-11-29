# Natural Language Chat Interface - User Guide

## Overview

The Natural Language Chat Interface lets you interact with the NFL betting system using conversational English instead of memorizing CLI commands. It uses Claude Haiku to translate your questions into system commands.

## Quick Start

### Start the Chat

```bash
python scripts/chat_cli.py
```

You'll see:
```
================================================================================
NFL BETTING SYSTEM - NATURAL LANGUAGE INTERFACE
================================================================================

Ask questions in plain English. Type 'help' for examples, 'exit' to quit.

You:
```

### Ask Questions

Just type naturally:

```
You: show me parlays for week 12
Thinking...

Found 111 parlays for week 12:
================================================================================

1. Parlay ID: TRAD_W12_abc123_v1
   Type: traditional | 6 legs | Confidence: 73.5%
   Leg 1: Josh Allen Pass Yards OVER 267.5
   Leg 2: CMC Rush Yards OVER 95.5
   ...

You: filter those to only QBs
Thinking...

Found 15 parlays for week 12:
...
```

## Example Queries

### Viewing Data

**See available weeks:**
```
You: what weeks are available?
You: list all weeks with parlays
```

**View parlays:**
```
You: show me parlays for week 12
You: get the top 5 parlays by confidence
You: show me QB parlays
You: what are the best parlays for week 11?
```

**View props:**
```
You: show all props for Josh Allen
You: get props with confidence over 70%
You: what RB props are available for week 12?
You: show receiving yard props
You: show me UNDER bets for week 12
You: what OVER bets do we have for QBs?
You: show high confidence UNDERs
```

### Filtering & Sorting

```
You: filter to only UNDER bets
You: show only OVER bets
You: filter to only home games
You: show only WRs and TEs
You: sort by correlation
You: filter to confidence between 65 and 75
You: show me the lowest confidence parlays
You: show QB UNDERs with confidence over 70
You: filter to RB OVER bets only
```

### Analysis & Details

```
You: explain parlay TRAD_W12_abc123_v1
You: why is this parlay rated 68%?
You: show agent breakdown for Patrick Mahomes
You: what are the correlation concerns?
You: show me the DVOA agent's opinion on this
```

### Actions

```
You: export parlays for week 12
You: preview export for week 11
You: create a 2-leg, 3-leg, and 4-leg parlay
You: build a 3-leg QB parlay for week 12
You: make me two parlays: one 2-leg and one 4-leg
```

### Follow-up Questions

The interface remembers context, so you can ask follow-ups:

```
You: show me QB parlays for week 12
... results shown ...

You: now filter those to only home games
... filtered results ...

You: what about confidence over 70?
... further filtered ...

You: show me details on the first one
... detailed breakdown ...
```

## UNDER Bets Are Fully Supported

**Important:** The system fully supports and tracks both OVER and UNDER bets!

- **OVER bets**: Predict the player will go OVER the line (e.g., Josh Allen OVER 267.5 Pass Yards)
- **UNDER bets**: Predict the player will stay UNDER the line (e.g., CMC UNDER 95.5 Rush Yards)

Both bet types:
- ✅ Are analyzed by all 8 agents
- ✅ Get confidence scores (0-100, same scale)
- ✅ Can be filtered and sorted
- ✅ Are included in parlays
- ✅ Are tracked in exports
- ✅ Work with correlation analysis

**Example queries for UNDER bets:**
```
You: show me all UNDER bets for week 12
You: filter to QB UNDERs with confidence over 65
You: what high confidence UNDER props do we have?
You: show only UNDER bets
```

## Features

### Conversation Context

The system remembers your last 10 exchanges, so you can:
- Refer to previous results ("filter those", "the first one", "that parlay")
- Build on previous queries
- Natural back-and-forth conversation

### Smart Query Parsing

Claude Haiku understands various ways to ask the same thing:
- "Show me parlays" = "Get parlays" = "What parlays are there?"
- "Filter to QBs" = "Only quarterbacks" = "Just show QBs"
- "Sort by confidence" = "Order by confidence" = "Highest confidence first"

### Error Handling

If your query is ambiguous:
```
You: show me the good ones
Assistant: What would you like to see? Parlays, props, or specific player analysis?

You: show parlays with high confidence
```

If you make a mistake:
```
You: show parlays for week 25
Assistant: Week 25 doesn't exist. NFL weeks range from 1-18. Which week would you like?
```

## Available Functions

The interface can:

1. **list_weeks()** - Show which weeks have data
2. **get_parlays()** - View parlays with filters
3. **get_all_props()** - See analyzed props
4. **explain_parlay()** - Detailed parlay breakdown
5. **show_agent_breakdown()** - Agent scores for a player
6. **export_parlays()** - Export to CSV
7. **build_parlay()** - Build custom parlays with specified leg counts
8. **help()** - Show help and examples

## Cost & Performance

### API Costs

- **Translation (Haiku)**: ~$0.006 per 100 queries
- **Analysis (Sonnet)**: Only used for correlation analysis (existing usage)

The interface is designed to be cost-effective:
- Haiku is 3x cheaper than Sonnet for input
- Only used for query parsing, not complex reasoning
- Typical query: ~200 tokens = $0.0002

### Speed

- Query translation: ~0.5-1 second
- Total response time: 1-3 seconds depending on query complexity

## Tips for Best Results

### Be Specific When Needed

Good:
```
show me QB parlays for week 12 with confidence over 70%
```

Less good:
```
show me stuff
```

### Use Natural Language

You don't need to match exact keywords. These all work:
- "quarterbacks" / "QBs" / "QB"
- "confidence" / "conf" / "rating"
- "filter" / "only show" / "just" / "limit to"

### Leverage Context

Instead of repeating:
```
You: show parlays for week 12
You: show QB parlays for week 12 with confidence over 70
You: show home game QB parlays for week 12 with confidence over 70
```

Do this:
```
You: show parlays for week 12
You: filter to QBs
You: only show confidence over 70
You: just home games
```

### Ask for Help

```
You: help
You: what can you do?
You: show me examples
```

## Python API

You can also use the interface programmatically:

```python
from scripts.analysis import NLQueryInterface

# Create interface
interface = NLQueryInterface(data_dir="data")

# Translate query
command = interface.translate_query("show me QB parlays for week 12")

# Execute
result = interface.execute_command(command)

# Or run interactively
interface.run()
```

## Troubleshooting

### "ANTHROPIC_API_KEY environment variable not set"

Add to your `.env` file:
```
ANTHROPIC_API_KEY=sk-ant-...
```

### "anthropic package required"

Install:
```bash
pip install anthropic
```

### "Failed to understand query"

Try rephrasing:
```
You: show me things
Assistant: [ERROR] Failed to understand query. Please rephrase.

You: show me parlays for week 12
```

### Slow responses

- First query may be slow (loading data)
- Subsequent queries in same week are cached
- Check your internet connection

## Advanced Usage

### Chaining Queries

```python
from scripts.analysis import NLQueryInterface

interface = NLQueryInterface()

# Multiple queries with context
queries = [
    "show parlays for week 12",
    "filter to QBs",
    "only show top 3"
]

for query in queries:
    command = interface.translate_query(query)
    result = interface.execute_command(command)
    print(result)
```

### Custom Filters

```
You: show props where:
- confidence > 70
- position = QB or WR
- stat type = passing yards or receiving yards
- home games only
```

The interface will parse complex multi-condition queries.

## Limitations

Current version does NOT support:
- ❌ Placing actual bets
- ❌ Real-time odds fetching
- ❌ Multi-week comparisons
- ❌ Backtesting queries

Coming soon:
- ⏳ Historical performance queries
- ⏳ Agent calibration queries
- ⏳ Visual charts/graphs

## Security & Privacy

- All queries are sent to Anthropic Claude API
- No sensitive data is logged
- Conversation history stored in memory only (not persisted)
- API key required (never share your key)

## Support

For issues:
- Type `help` in the chat
- Check this guide
- Review error messages
- Create GitHub issue with "chat-interface" label

## Related Documentation

- [Custom Parlay Builder](CUSTOM_PARLAY_BUILDER.md)
- [Parlay Export Guide](PARLAY_EXPORT_GUIDE.md)
- [System Overview](../README.md)
