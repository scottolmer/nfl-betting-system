# ⚡ Parlay Builder + Tracker - Complete Specification

**Date:** 2026-01-10
**Status:** Technical Specification
**Feature Type:** Core Primary Feature (3-in-1)

---

## 📋 Overview

The **Parlay Builder + Tracker** is a unified system that serves three functions:
1. **Bet Planner** - Build parlays with confidence scores before placing
2. **Bet Tracker** - Save parlays to automatically track results
3. **Performance Analyzer** - Post-game analysis with auto-grading

**Key Innovation:** User builds parlay in app → saves it → places in their sportsbook → app auto-grades results

---

## 🎯 Why This Approach (vs OCR)

| Feature | OCR Photo Import | Parlay Builder Approach |
|---------|------------------|-------------------------|
| **Accuracy** | 70-80% (parsing errors) | 100% (user enters data) ✅ |
| **Books Supported** | Need to train for each book | All books (book-agnostic) ✅ |
| **User Effort** | Take photo + verify | Manual entry (1-2 min) |
| **Engagement** | After bet is placed | **Before bet is placed** ✅ |
| **Line Adjustment** | Hard to implement | Built-in naturally ✅ |
| **Development Time** | 4-6 weeks | 2-3 weeks ✅ |
| **Maintenance** | High (books change formats) | Low ✅ |
| **Cost** | $50-100/mo (OCR API) | $0 ✅ |
| **Workflow** | Place → Photo → Import | **Build → Place → Track** ✅ |

**Verdict:** Parlay Builder approach is simpler, more reliable, and creates better engagement.

---

## 🔄 COMPLETE USER WORKFLOW

### **Sunday Morning (Pre-Game)**

#### **Step 1: Create New Parlay**

```
┌─────────────────────────────────────────┐
│ NEW PARLAY                         [×]  │
├─────────────────────────────────────────┤
│                                         │
│ Parlay Name:                            │
│ [Sunday Morning Special________]        │
│                                         │
│ Sportsbook:                             │
│ [Select your book... ▼]                 │
│                                         │
│ YOUR BOOKS:                             │
│ • DraftKings Pick 6                     │
│ • FanDuel Pick 6                        │
│ • Underdog Fantasy                      │
│ • PrizePicks                            │
│                                         │
│ OTHER BOOKS:                            │
│ • BetMGM                                │
│ • Caesars                               │
│ • [+ Add Book]                          │
│                                         │
│ Bet Amount (optional):                  │
│ [$20____]                               │
│                                         │
│ [Next: Add Props]                       │
└─────────────────────────────────────────┘
```

#### **Step 2: Add Props with Filters**

```
┌─────────────────────────────────────────┐
│ BUILDING: Sunday Morning Special        │
│ DraftKings Pick 6                  [△]  │ ← Tap to collapse
├─────────────────────────────────────────┤
│                                         │
│ FILTERS                            [△]  │
├─────────────────────────────────────────┤
│                                         │
│ 🏈 TEAMS (multi-select)                 │
│ [All] [KC] [BUF] [PHI] [SF] [LAC] ...  │
│                                         │
│ 👤 POSITIONS                            │
│ [All] [QB] [RB] [WR] [TE]               │
│                                         │
│ 📊 MIN CONFIDENCE                       │
│ ●────────●──────  [75+]                 │
│ 60   70   80   90                       │
│                                         │
│ 🎯 PROP TYPES                           │
│ [All] [Yds] [Rec] [TD] [Rush]           │
│                                         │
│ 🎲 PARLAY STYLE                         │
│ ○ Any Games                             │
│ ○ Same Game                             │
│ ○ Max Diversity                         │
│                                         │
│ [Apply Filters]                         │
│                                         │
├─────────────────────────────────────────┤
│ QUICK PRESETS                           │
├─────────────────────────────────────────┤
│ [🔥 Elite Only] [🎯 Shootouts]          │
│ [🏃 RB Heavy] [⭐ WR1s]                  │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ AVAILABLE PROPS (23 matches)            │
├─────────────────────────────────────────┤
│                                         │
│ ┌─────────────────────────────────┐    │
│ │ 🔥 85  Patrick Mahomes (KC)     │[+] │
│ │ Pass Yds OVER 275.5 | vs BUF   │    │
│ │                                 │    │
│ │ DK Props: 275.5                 │    │
│ │ Pick 6: [275.5] [✏️ Edit]       │    │
│ │                                 │    │
│ │ • KC +18% Pass DVOA             │    │
│ │ • Elite matchup vs BUF          │    │
│ └─────────────────────────────────┘    │
│                                         │
│ ┌─────────────────────────────────┐    │
│ │ ⭐ 78  Travis Kelce (KC)        │[+] │
│ │ Rec Yds OVER 58.5 | vs BUF     │    │
│ │                                 │    │
│ │ DK Props: 56.5                  │    │
│ │ Pick 6: [58.5] [✏️ Edit]        │    │
│ │                                 │    │
│ │ • High volume: 25% targets      │    │
│ └─────────────────────────────────┘    │
│                                         │
│ [Load More Props]                       │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ YOUR PARLAY (2 legs)         [Clear All]│
├─────────────────────────────────────────┤
│                                         │
│ 1. Mahomes Pass Yds OVER 275.5 (KC)[×] │
│    Confidence: 85                      │
│                                         │
│ 2. Kelce Rec Yds OVER 58.5 (KC)    [×] │
│    Confidence: 78                      │
│                                         │
├─────────────────────────────────────────┤
│ Combined Confidence: 81 🔥              │
│ Risk Level: MODERATE ⚠️                 │
│ Games: KC (1 game - same game stack)   │
│ Correlation: +3 boost (Mahomes+Kelce)  │
│                                         │
│ 💡 SUGGESTION                           │
│ High correlation = higher risk.        │
│ Consider adding prop from different game│
│                                         │
│ [💾 Save Parlay] [➕ Add More Props]   │
└─────────────────────────────────────────┘
```

#### **Line Adjustment Modal**

```
When user taps [✏️ Edit] on a prop:

┌─────────────────────────────────────────┐
│ ADJUST LINE                        [×]  │
├─────────────────────────────────────────┤
│ Travis Kelce Rec Yds OVER               │
│                                         │
│ DraftKings Props Line:                  │
│ [  56.5  ] (System analysis baseline)   │
│                                         │
│ Pick 6 Line:                            │
│ [  58.5  ] [+] [-]                      │
│                                         │
│ ┌─────────────────────────────────┐    │
│ │ RE-SCORED CONFIDENCE              │    │
│ ├─────────────────────────────────┤    │
│ │ Original: ⭐ 80                   │    │
│ │ Adjusted: ✅ 75  (-5)             │    │
│ │                                   │    │
│ │ Change: Line 2 yards tighter      │    │
│ │ ⚠️ Reduced margin vs projection   │    │
│ └─────────────────────────────────┘    │
│                                         │
│ Projection: 65 yards                   │
│ Original cushion: 8.5 yds (13%)        │
│ Pick 6 cushion: 6.5 yds (10%)          │
│                                         │
│ Still playable but reduced edge.       │
│                                         │
│ [Apply Change] [Cancel]                 │
└─────────────────────────────────────────┘
```

#### **Step 3: Save & Export**

```
After tapping [💾 Save Parlay]:

┌─────────────────────────────────────────┐
│ ✅ PARLAY SAVED                         │
├─────────────────────────────────────────┤
│ Sunday Morning Special                  │
│ DraftKings Pick 6                       │
│                                         │
│ 2 LEGS:                                 │
│ • Mahomes Pass Yds OVER 275.5 (85)     │
│ • Kelce Rec Yds OVER 58.5 (78)         │
│                                         │
│ Combined Confidence: 81 🔥              │
│ Risk: MODERATE (same game stack)       │
│ Recommended Bet: $20 (2 units)          │
│                                         │
│ ═══════════════════════════════════     │
│ NEXT STEPS:                             │
│                                         │
│ 1. Open DraftKings Pick 6               │
│ 2. Enter these 2 props                  │
│ 3. Place your bet                       │
│ 4. Return here to mark as "Placed"     │
│                                         │
│ [📋 Copy Props to Clipboard]            │
│ [📱 Open DraftKings App]                │
│ [✅ Mark as Placed]                     │
│ [🏠 Back to Home]                       │
└─────────────────────────────────────────┘
```

**Copy to Clipboard Format:**
```
DraftKings Pick 6 - 2 legs (81 confidence)

1. Patrick Mahomes Pass Yds OVER 275.5
2. Travis Kelce Rec Yds OVER 58.5

Recommended bet: $20
Risk: MODERATE
```

#### **Step 4: Mark as Placed**

```
When user returns after placing bet:

┌─────────────────────────────────────────┐
│ MARK AS PLACED                     [×]  │
├─────────────────────────────────────────┤
│ Sunday Morning Special                  │
│ DraftKings Pick 6                       │
│                                         │
│ Did you place this bet?                 │
│                                         │
│ Bet Amount:                             │
│ [$20____] (optional)                    │
│                                         │
│ Actual Book Used:                       │
│ [DraftKings Pick 6 ▼]                  │
│                                         │
│ Notes (optional):                       │
│ [Using this for SNF_______]            │
│                                         │
│ [✅ Yes, I Placed It]                   │
│ [Not Yet]                               │
└─────────────────────────────────────────┘

After marking placed, parlay status updates:
Status: Placed ($20) ✅
Waiting for results...
```

---

## 📚 MY PARLAYS LIBRARY

### **Main View**

```
┌─────────────────────────────────────────┐
│ ⚡ BUILD                      [+ New]    │
├─────────────────────────────────────────┤
│                                         │
│ 📚 MY PARLAYS (2/3 used) 🔓            │ ← Free tier
│                                         │
│ [All] [Draft] [Placed] [Graded]        │ ← Filters
│                                         │
│ ┌─────────────────────────────────┐    │
│ │ 📝 Sunday Morning Special       │    │
│ │ 2 legs • 81 confidence          │    │
│ │ DraftKings Pick 6 • $20         │    │
│ │ Status: Placed ✅               │    │
│ │ Game starts in 45 minutes       │    │
│ │                                 │    │
│ │ [View Details] [Track Results]  │    │
│ └─────────────────────────────────┘    │
│                                         │
│ ┌─────────────────────────────────┐    │
│ │ 📝 Chiefs Stack                 │    │
│ │ 3 legs • 78 confidence          │    │
│ │ FanDuel Pick 6 • Not placed     │    │
│ │ Status: Draft                   │    │
│ │                                 │    │
│ │ [Edit] [Place Bet] [Delete]     │    │
│ └─────────────────────────────────┘    │
│                                         │
│ [+ Create New Parlay]                   │
│     ↓ (if at limit)                     │
│ ┌─────────────────────────────────┐    │
│ │ 🔒 PARLAY LIMIT REACHED         │    │
│ ├─────────────────────────────────┤    │
│ │ Free tier: 3 parlays max        │    │
│ │                                 │    │
│ │ Options:                        │    │
│ │ • Delete an existing parlay     │    │
│ │ • Wait for results (auto-archive)│   │
│ │ • Upgrade to Premium (unlimited)│    │
│ │                                 │    │
│ │ [Delete Parlay]                 │    │
│ │ [Upgrade - $9.99/mo]            │    │
│ └─────────────────────────────────┘    │
│                                         │
├─────────────────────────────────────────┤
│ QUICK BUILD                             │
├─────────────────────────────────────────┤
│ [🔍 Browse Props] [💡 System Picks]     │
└─────────────────────────────────────────┘
```

### **Parlay Detail View**

```
┌─────────────────────────────────────────┐
│ ← Sunday Morning Special           [⋮]  │
├─────────────────────────────────────────┤
│ DraftKings Pick 6                       │
│ Status: Placed ✅ • $20 bet             │
│ Game starts in 45 minutes               │
│                                         │
│ LEGS (2)                                │
│                                         │
│ ┌─────────────────────────────────┐    │
│ │ 1. Patrick Mahomes (KC)         │    │
│ │    Pass Yds OVER 275.5          │    │
│ │    Confidence: 85 🔥            │    │
│ │                                 │    │
│ │    WHY THIS IS GOOD:            │    │
│ │    • KC +18% Pass DVOA          │    │
│ │    • Elite matchup vs BUF       │    │
│ │    • Projection: 295 yards      │    │
│ └─────────────────────────────────┘    │
│                                         │
│ ┌─────────────────────────────────┐    │
│ │ 2. Travis Kelce (KC)            │    │
│ │    Rec Yds OVER 58.5            │    │
│ │    Confidence: 78 ⭐            │    │
│ │                                 │    │
│ │    WHY THIS IS GOOD:            │    │
│ │    • High volume: 25% targets   │    │
│ │    • Projection: 67 yards       │    │
│ │    • 8.5 yard cushion           │    │
│ └─────────────────────────────────┘    │
│                                         │
├─────────────────────────────────────────┤
│ PARLAY ANALYSIS                         │
├─────────────────────────────────────────┤
│ Combined Confidence: 81 🔥              │
│ Risk: MODERATE (same game stack)       │
│ Correlation: +3 boost                  │
│                                         │
│ If both hit: $40 payout (+$20)         │
│                                         │
│ [Edit Parlay] [Share] [Delete]          │
└─────────────────────────────────────────┘
```

---

## 🏈 POST-GAME AUTO-GRADING

### **Sunday Evening (Games Complete)**

**Backend Process:**
```
ESPN API polls every 5 minutes
    ↓
Detects game STATUS_FINAL
    ↓
Fetches box score (player stats)
    ↓
Finds all "Placed" parlays for this game
    ↓
For each parlay leg:
  - Compare actual stat vs line
  - Mark HIT/MISS
    ↓
Calculate parlay result (all legs must hit)
    ↓
Update parlay status
    ↓
Trigger post-game analysis
    ↓
Send push notification
```

**Push Notification:**
```
🏈 Game final! Chiefs 27, Bills 24

Your parlay results:
✅ Sunday Morning Special - HIT! (+$20)

Tap to see breakdown →
```

**Results Screen:**
```
┌─────────────────────────────────────────┐
│ 📊 MY BETS → Results                    │
├─────────────────────────────────────────┤
│                                         │
│ ✅ SUNDAY MORNING SPECIAL - WON!        │
│ DraftKings Pick 6 • $20 bet            │
│ Payout: $40 (+$20 profit) 💰           │
│ Graded: 4:23 PM                        │
│                                         │
│ LEGS (2/2 HIT) ✅✅                     │
│                                         │
│ ┌─────────────────────────────────┐    │
│ │ ✅ Patrick Mahomes              │    │
│ │ Pass Yds 315/275.5 (+39.5) ✓    │    │
│ │ Confidence: 85 (Accurate!)      │    │
│ │                                 │    │
│ │ WHY IT HIT:                     │    │
│ │ • DVOA Agent was right (90 score)│   │
│ │ • Matchup Agent was right (85)  │    │
│ │ • Elite offense delivered       │    │
│ └─────────────────────────────────┘    │
│                                         │
│ ┌─────────────────────────────────┐    │
│ │ ✅ Travis Kelce                 │    │
│ │ Rec Yds 73/58.5 (+14.5) ✓       │    │
│ │ Confidence: 78 (Accurate!)      │    │
│ │                                 │    │
│ │ WHY IT HIT:                     │    │
│ │ • Volume Agent was right (80)   │    │
│ │ • High target share delivered   │    │
│ │ • 9 targets, 7 catches          │    │
│ └─────────────────────────────────┘    │
│                                         │
├─────────────────────────────────────────┤
│ SYSTEM ACCURACY                         │
├─────────────────────────────────────────┤
│ Combined Confidence: 81                 │
│ Actual Hit Rate: 100% ✅                │
│                                         │
│ System was accurate! Trust these       │
│ confidence scores going forward.       │
│                                         │
│ [View Full Analysis] [Share Win 🎉]    │
└─────────────────────────────────────────┘
```

**When Parlay Misses:**
```
┌─────────────────────────────────────────┐
│ ❌ CHIEFS STACK - LOST                  │
│ FanDuel Pick 6 • $15 bet               │
│ Lost: -$15                             │
│                                         │
│ LEGS (2/3 HIT) ✅✅❌                   │
│                                         │
│ ✅ Mahomes Pass Yds 315/275.5 ✓        │
│ ✅ Kelce Rec Yds 73/58.5 ✓             │
│ ❌ Hill Rec Yds 58/65.5 ✗              │
│    • Close call (89% of line)          │
│    • Needed 8 more yards               │
│                                         │
│ WHY IT MISSED:                          │
│ GameScript shifted - Chiefs led big in │
│ 2nd half and went run-heavy. Hill saw  │
│ only 2 targets after halftime.         │
│                                         │
│ 💡 LESSON                               │
│ Avoid WR2s in blowout games. When team │
│ leads big, they reduce passing volume. │
│                                         │
│ GameScript Agent was overconfident (75).│
│ Consider lowering its weight.          │
│                                         │
│ [View Full Analysis] [Try Again]        │
└─────────────────────────────────────────┘
```

---

## ⚙️ SPORTSBOOK MANAGEMENT

### **Settings → Sportsbooks**

```
┌─────────────────────────────────────────┐
│ ⚙️ SETTINGS → Sportsbooks               │
├─────────────────────────────────────────┤
│                                         │
│ 📱 YOUR SPORTSBOOKS                     │
│                                         │
│ Select which books you use:             │
│                                         │
│ ☑️ DraftKings Pick 6                    │
│ ☑️ FanDuel Pick 6                       │
│ ☑️ Underdog Fantasy                     │
│ ☑️ PrizePicks                           │
│ ☐ BetMGM                                │
│ ☐ Caesars                               │
│ ☐ FanDuel Sportsbook                   │
│ ☐ DraftKings Sportsbook                │
│ ☐ ESPN Bet                              │
│                                         │
│ Default book:                           │
│ [DraftKings Pick 6 ▼]                  │
│                                         │
│ ℹ️ Your selected books will appear first│
│    when creating parlays.               │
│                                         │
│ [Save Changes]                          │
└─────────────────────────────────────────┘
```

### **Supported Sportsbooks (Book-Agnostic Design)**

**Daily Fantasy / Pick'em:**
- DraftKings Pick 6
- FanDuel Pick 6
- Underdog Fantasy
- PrizePicks
- Sleeper Fantasy

**Traditional Sportsbooks:**
- DraftKings Sportsbook
- FanDuel Sportsbook
- BetMGM
- Caesars
- ESPN Bet
- PointsBet
- BetRivers

**Future:** Allow custom book entry

---

## 💾 DATABASE SCHEMA

```sql
-- User parlays table
CREATE TABLE user_parlays (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),

    -- Parlay details
    name VARCHAR(100) NOT NULL,
    sportsbook VARCHAR(50) NOT NULL,  -- 'draftkings_pick6', 'fanduel_pick6', etc.

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    -- Values: 'draft', 'placed', 'won', 'lost', 'push', 'graded'

    -- Bet info
    bet_amount DECIMAL(10,2),
    potential_payout DECIMAL(10,2),
    actual_payout DECIMAL(10,2),

    -- Confidence
    combined_confidence INTEGER,
    risk_level VARCHAR(20),  -- 'LOW', 'MODERATE', 'HIGH'

    -- Correlation info
    correlation_type VARCHAR(50),  -- 'same_game', 'uncorrelated', 'mixed'
    correlation_boost INTEGER,  -- e.g., +3 for same-game

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    placed_at TIMESTAMP,
    graded_at TIMESTAMP,

    -- Metadata
    notes TEXT,

    INDEX idx_user_status (user_id, status),
    INDEX idx_created (created_at),
    INDEX idx_graded (graded_at)
);

-- Parlay legs table
CREATE TABLE parlay_legs (
    id SERIAL PRIMARY KEY,
    parlay_id INTEGER REFERENCES user_parlays(id) ON DELETE CASCADE,

    -- Prop details
    player_name VARCHAR(100) NOT NULL,
    team VARCHAR(10),
    opponent VARCHAR(10),
    prop_type VARCHAR(50) NOT NULL,  -- 'passing_yards', 'receiving_yards', etc.
    line DECIMAL(5,1) NOT NULL,
    direction VARCHAR(10) NOT NULL,  -- 'OVER' or 'UNDER'

    -- Pre-game analysis
    confidence INTEGER,
    projection DECIMAL(5,1),

    -- Agent scores (JSON)
    agent_scores JSONB,
    -- Example: {"dvoa": 85, "matchup": 90, "volume": 75, ...}

    -- Post-game results
    actual_value DECIMAL(5,1),
    difference DECIMAL(5,1),  -- actual - line
    result VARCHAR(20),  -- 'HIT', 'MISS', 'PUSH', 'PENDING'

    -- Order
    leg_order INTEGER NOT NULL,

    INDEX idx_parlay (parlay_id),
    INDEX idx_player (player_name),
    INDEX idx_result (result)
);

-- User sportsbooks preferences
CREATE TABLE user_sportsbooks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    sportsbook VARCHAR(50) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, sportsbook),
    INDEX idx_user (user_id)
);
```

---

## 🔌 API ENDPOINTS

### **Parlay CRUD**

```python
# Create new parlay
POST /api/parlays
{
    "name": "Sunday Morning Special",
    "sportsbook": "draftkings_pick6",
    "bet_amount": 20.00,
    "legs": [
        {
            "player_name": "Patrick Mahomes",
            "team": "KC",
            "opponent": "BUF",
            "prop_type": "passing_yards",
            "line": 275.5,
            "direction": "OVER",
            "confidence": 85,
            "projection": 295,
            "agent_scores": {
                "dvoa": 90,
                "matchup": 85,
                "volume": 80,
                ...
            }
        },
        {
            "player_name": "Travis Kelce",
            "team": "KC",
            "opponent": "BUF",
            "prop_type": "receiving_yards",
            "line": 58.5,
            "direction": "OVER",
            "confidence": 78,
            "projection": 67,
            "agent_scores": {...}
        }
    ]
}

Response:
{
    "parlay_id": 123,
    "name": "Sunday Morning Special",
    "status": "draft",
    "combined_confidence": 81,
    "risk_level": "MODERATE",
    "correlation_boost": 3,
    "created_at": "2024-11-10T10:30:00Z"
}

# Get user's parlays
GET /api/parlays
Query params:
  - status: 'draft', 'placed', 'graded'
  - limit: 10
  - offset: 0

Response:
{
    "parlays": [
        {
            "id": 123,
            "name": "Sunday Morning Special",
            "sportsbook": "draftkings_pick6",
            "status": "placed",
            "bet_amount": 20.00,
            "combined_confidence": 81,
            "risk_level": "MODERATE",
            "legs_count": 2,
            "legs": [...],
            "created_at": "2024-11-10T10:30:00Z",
            "placed_at": "2024-11-10T11:00:00Z"
        },
        ...
    ],
    "count": 2,
    "limit_reached": false  // Free tier: true if at 2-3 limit
}

# Update parlay (mark as placed, edit, etc.)
PATCH /api/parlays/{id}
{
    "status": "placed",
    "bet_amount": 20.00,
    "placed_at": "2024-11-10T11:00:00Z"
}

# Delete parlay
DELETE /api/parlays/{id}

# Grade parlay (internal - called by ESPN API cron)
POST /api/parlays/{id}/grade
{
    "legs": [
        {
            "leg_id": 1,
            "actual_value": 315,
            "result": "HIT"
        },
        {
            "leg_id": 2,
            "actual_value": 73,
            "result": "HIT"
        }
    ]
}

Response:
{
    "parlay_id": 123,
    "status": "won",
    "legs_hit": 2,
    "legs_total": 2,
    "actual_payout": 40.00,
    "profit": 20.00,
    "graded_at": "2024-11-10T16:30:00Z"
}
```

### **Line Adjustment**

```python
# Re-calculate confidence with adjusted line
POST /api/props/adjust-line
{
    "player_name": "Travis Kelce",
    "prop_type": "receiving_yards",
    "original_line": 56.5,
    "new_line": 58.5,
    "direction": "OVER"
}

Response:
{
    "original_confidence": 80,
    "new_confidence": 75,
    "adjustment": -5,
    "reason": "Line moved 2.0 yards tighter",
    "cushion_original": 8.5,
    "cushion_new": 6.5,
    "projection": 65.0,
    "recommendation": "Still playable but reduced edge"
}
```

### **Sportsbooks**

```python
# Get user's sportsbooks
GET /api/user/sportsbooks

Response:
{
    "sportsbooks": [
        {
            "name": "draftkings_pick6",
            "display_name": "DraftKings Pick 6",
            "is_default": true
        },
        {
            "name": "fanduel_pick6",
            "display_name": "FanDuel Pick 6",
            "is_default": false
        }
    ]
}

# Add sportsbook
POST /api/user/sportsbooks
{
    "sportsbook": "underdog_fantasy",
    "is_default": false
}

# Set default
PATCH /api/user/sportsbooks/{sportsbook}
{
    "is_default": true
}
```

---

## 🚀 IMPLEMENTATION PHASES

### **Phase 1: Basic Parlay CRUD (Week 1)**
- [ ] Create parlay (name, sportsbook, legs)
- [ ] Add/remove legs
- [ ] Calculate combined confidence
- [ ] Save parlay to database
- [ ] List user's parlays
- [ ] Delete parlay

**Deliverable:** Can create and save parlays

---

### **Phase 2: Filters & Props Selection (Week 1-2)**
- [ ] Build filter UI (teams, positions, confidence)
- [ ] Apply filters to prop list
- [ ] Add prop to parlay
- [ ] Remove prop from parlay
- [ ] Live confidence updates
- [ ] Quick filter presets

**Deliverable:** Full parlay builder with filters

---

### **Phase 3: Line Adjustment & Sportsbooks (Week 2)**
- [ ] Sportsbook selection dropdown
- [ ] User sportsbook preferences (settings)
- [ ] Line adjustment modal
- [ ] Re-calculate confidence for adjusted line
- [ ] Display original vs adjusted confidence
- [ ] Save adjusted line with leg

**Deliverable:** Book-agnostic with line adjustment

---

### **Phase 4: Status Management (Week 2-3)**
- [ ] Mark parlay as "placed"
- [ ] Enter bet amount
- [ ] Copy props to clipboard
- [ ] Deep link to sportsbook app (iOS/Android)
- [ ] Free tier limits (2-3 parlays)
- [ ] Premium upgrade prompt

**Deliverable:** Full workflow from build to place

---

### **Phase 5: Auto-Grading Integration (Week 3)**
- [ ] ESPN API grades completed games
- [ ] Update parlay leg results
- [ ] Calculate parlay win/loss
- [ ] Update parlay status
- [ ] Send push notification
- [ ] Display graded results

**Deliverable:** Automatic post-game grading

---

### **Phase 6: Post-Game Analysis (Week 4)**
- [ ] "Why it hit/miss" for each leg
- [ ] Agent accuracy analysis
- [ ] System performance validation
- [ ] Lessons/insights generation
- [ ] Archive graded parlays

**Deliverable:** Full post-game learning

---

### **Phase 7: Polish & Advanced Features (Week 4)**
- [ ] Auto-optimization suggestions
- [ ] Conflict detection
- [ ] Share parlays with friends
- [ ] Saved filter presets
- [ ] Parlay comparison
- [ ] Edit draft parlays

**Deliverable:** Production-ready feature

---

## 📊 FREEMIUM LIMITS

### **Free Tier**
```python
MAX_PARLAYS_FREE = 3

def can_create_parlay(user):
    active_parlays = Parlay.objects.filter(
        user=user,
        status__in=['draft', 'placed']
    ).count()

    if user.subscription == 'free':
        return active_parlays < MAX_PARLAYS_FREE

    return True  # Premium/Pro = unlimited
```

### **Archive Strategy**
```python
# Auto-archive graded parlays after 7 days (free tier only)
def archive_old_parlays():
    cutoff = datetime.now() - timedelta(days=7)

    Parlay.objects.filter(
        user__subscription='free',
        status='graded',
        graded_at__lt=cutoff
    ).update(status='archived')
```

---

## 🎯 SUCCESS METRICS

### **Engagement Metrics**
- **Parlay creation rate** - Avg parlays created per user per week
- **Placement rate** - % of created parlays actually placed
- **Return rate** - % of users who return to mark as placed
- **Free tier conversion** - % who hit 3-parlay limit and upgrade

### **Feature Usage**
- **Line adjustment usage** - % of legs with adjusted lines
- **Filter usage** - Which filters are most popular
- **Sportsbook distribution** - Which books are most used

### **Target Metrics**
- 70%+ of users create at least 1 parlay per week
- 60%+ placement rate (users actually place their parlays)
- 80%+ return rate (mark as placed after betting)
- 15%+ conversion when hitting free tier limit

---

## 💡 FUTURE ENHANCEMENTS

### **Phase 8+ (Post-Launch)**
- [ ] **Templates** - Save parlay as template for future weeks
- [ ] **Community Parlays** - See what top users are betting
- [ ] **Parlay Optimizer** - AI suggests best combination
- [ ] **Alternative Suggestions** - "Can't bet Kelce? Try Gray"
- [ ] **Bet Slip Photo** - Optional OCR for convenience
- [ ] **Multi-book comparison** - Show same prop across books
- [ ] **Parlay challenges** - Compete with friends
- [ ] **Streak tracking** - Track consecutive wins
- [ ] **Export to CSV** - Download bet history

---

## 🎯 SUMMARY

**This 3-in-1 feature provides:**
1. ✅ **Bet Planning** - Build parlays with confidence before placing
2. ✅ **Bet Tracking** - System knows what you bet (no manual entry friction)
3. ✅ **Performance Analysis** - Post-game learning with auto-grading

**Why it's better than alternatives:**
- **No OCR** - Simpler, more reliable, zero maintenance
- **Book-agnostic** - Works for any sportsbook
- **Natural workflow** - Build → Place → Track
- **High engagement** - 3 touchpoints per bet
- **Monetizable** - Free tier limit drives Premium upgrades

**Timeline:** 4 weeks for full implementation
**Cost:** $0 ongoing (no external APIs needed)
**Complexity:** Medium (CRUD + ESPN API integration)

---

**Document Version:** 1.0
**Last Updated:** 2026-01-10
**Status:** Ready for implementation
**Next:** Begin Phase 1 development
