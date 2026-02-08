# NFL Betting Assistant - Natural Language Interface

## Overview

The Betting Assistant transforms the NFL betting system from script-based workflows into a conversational AI interface. Instead of memorizing commands and running scripts, you can now:

- Upload CSV files and get automatic validation
- Ask questions in natural language
- Get intelligent parlay recommendations
- Refine results interactively
- Automatically learn Pick6 constraints

## Quick Start

### Installation

Database schema is auto-created on first run. To manually initialize:

```bash
python scripts/assistant/init_db_schema.py
```

### Usage

**Via Skill (Recommended)**
```bash
/betting-assistant "What are the best parlays for week 15?"
/betting-assistant "Exclude Mahomes - not available in Pick6"
```

**Via Python**
```bash
python scripts/assistant/betting_assistant_agent.py --message "Your question here"
```

## Features

### Phase 1: Core Conversational Interface ✅

**Implemented:**
- Natural language query processing
- CSV file handling and validation
- Prop analysis invocation
- Parlay building
- Conversational responses

**Example:**
```
User: "What are the best parlays for week 15?"
Assistant: Analyzing 347 props with 9 agents... Done!
           Found 89 high-confidence props (>=65%).
           Built 8 optimized parlays. Here are the top 3:
           ...
```

### Phase 2: Constraint Handling & Pick6 Learning ✅

**Implemented:**
- Player exclusion tracking
- Pick6 availability database
- Constraint rules engine
- Pattern detection (foundation)
- Persistent constraints across sessions

**Example:**
```
User: "Exclude Mahomes - not available in Pick6"
Assistant: Excluded Patrick Mahomes from parlays.
           Recorded: Mahomes unavailable in Pick6
           Rebuilding parlays...
```

## Architecture

### Core Components

#### 1. BettingAssistantAgent (`betting_assistant_agent.py`)
Main conversational orchestrator that:
- Detects user intent from natural language
- Routes to appropriate handlers
- Executes analysis workflows
- Generates conversational responses

#### 2. ConversationManager (`conversation_manager.py`)
Manages conversation state:
- Session tracking
- Context retention (last 10 messages)
- Intent classification
- User preferences

#### 3. ConstraintEngine (`constraint_engine.py`)
Handles platform constraints:
- Pick6 availability tracking
- Constraint rule creation
- Pattern detection
- Automatic constraint application

#### 4. CSVHandler (`csv_handler.py`)
Processes data files:
- CSV validation
- Integration with NFLDataLoader
- User-friendly status reporting
- Data quality checks

### Database Schema

**New Tables:**
- `pick6_availability` - Player/prop availability per platform
- `constraint_rules` - User-defined constraint rules
- `conversation_history` - Conversation logs
- `user_preferences` - User settings (platform, thresholds, etc.)

### Integration with Existing System

The assistant **wraps** existing code without modification:
- Uses `PropAnalyzer` for prop analysis (unchanged)
- Uses `ParlayBuilder` for parlay generation (unchanged)
- Invokes existing skills as subsystems
- All existing 9 agents remain unchanged

## Supported Intents

### Data Loading
- "Load week 15 data"
- "What's the data status?"

### Prop Analysis
- "What are the best parlays for week 15?"
- "Analyze props with 70% confidence"

### Parlay Building
- "Build parlays"
- "Make me some parlays from these props"

### Constraints & Refinement
- "Exclude Mahomes - not available in Pick6"
- "Remove all QB passing TDs"
- "Filter props under 20 yards"

### Explanations
- "Why is this prop good?"
- "Explain the Mahomes OVER 287.5"

### Historical Queries
- "How did week 14 perform?"
- "Show me results from last week"

## Example Conversations

### Example 1: Basic Analysis
```
User: "What are the best parlays for week 15?"
Assistant: Analyzing 347 props with 9 agents... Done!
           Found 89 high-confidence props (>=65%).
           Built 8 optimized parlays.

           Top 3 parlays:
           PARLAY #1 (73% confidence, +550 odds)
           - Patrick Mahomes Pass Yds OVER 287.5 (75%)
           - Josh Allen Rush Yds OVER 28.5 (71%)
           - Christian McCaffrey Rush Yds OVER 85.5 (74%)
```

### Example 2: Pick6 Constraint Learning
```
User: "Exclude Mahomes - not available in Pick6"
Assistant: Excluded Patrick Mahomes from parlays.
           Recorded: Mahomes unavailable in Pick6
           Rebuilding parlays...

           NEW PARLAY #1 (72% confidence, +520 odds)
           - Josh Allen Pass Yds OVER 268.5 (73%)
           - Christian McCaffrey Rush Yds OVER 85.5 (74%)

           All props verified available in Pick6 ✓

[Next session, Week 16]
User: "Build Pick6 parlays for week 16"
Assistant: Building Pick6 parlays for Week 16...
           Auto-excluding Patrick Mahomes (Pick6 unavailable, learned from Week 15)
```

## Testing

Run component tests:
```bash
cd scripts/assistant
python test_assistant.py
```

Test individual components:
```bash
python csv_handler.py --week 15
python conversation_manager.py
python constraint_engine.py
python betting_assistant_agent.py --message "Your test message"
```

## Files Created

### Core Modules
- `betting_assistant_agent.py` (800 lines) - Main agent
- `conversation_manager.py` (400 lines) - Context tracking
- `constraint_engine.py` (600 lines) - Constraint management
- `csv_handler.py` (300 lines) - Data loading
- `init_db_schema.py` (110 lines) - Database setup

### Skill Definition
- `.claude/skills/betting-assistant/SKILL.md` - Skill invocation

### Tests
- `test_assistant.py` - Component integration tests

## Modifications to Existing Files

### orchestrator.py (+50 lines)
- Added `exclude_players` parameter to `analyze_all_props()`
- Added `prop_analysis_to_dict()` static method for JSON serialization

### parlay_builder.py (+40 lines)
- Added `parlay_to_dict()` static method
- Added `parlays_to_dict()` static method

### data_loader.py (+30 lines)
- Added `get_validation_status()` method for conversational reporting

## Next Steps (Phase 3 & 4)

### Phase 3: Intelligent Recommendations
- Suggestion engine for follow-up questions
- Enhanced pattern learning
- Skill integration (chat-query, performance-reporter)
- Historical performance queries

### Phase 4: Advanced Features
- Multi-turn complex conversations
- Session resume capability
- Export to multiple formats
- Mobile app API integration

## Notes

- All existing Python agents remain unchanged
- Existing 12 skills continue to work
- Assistant is purely additive - no breaking changes
- Pattern learning foundation in place for future enhancement
- Database schema is backward-compatible

## Troubleshooting

**Issue: "No data loaded"**
- Ensure CSV files exist in `data/` directory
- Check file naming: `wk15_betting_lines_draftkings.csv`, etc.

**Issue: "Database table not found"**
- Run `python scripts/assistant/init_db_schema.py`

**Issue: "No props analyzed"**
- Verify data quality with: `python scripts/assistant/csv_handler.py --week 15`

## Support

For issues or feature requests, refer to the main project documentation.
