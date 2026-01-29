# 🏈 ESPN API Post-Game Auto-Grading System

**Date:** 2026-01-10
**Status:** Technical Specification

---

## 📋 Overview

Automatically grade prop bets after games complete using ESPN's hidden API. Provides immediate results (Sunday night) instead of waiting for Tuesday CSV uploads.

**Key Benefit:** Users get results Sunday night with post-game analysis, not Tuesday.

---

## 🎯 Core Concept

### **Two-Source Data Strategy**

```
PRE-GAME DATA (Tuesday-Saturday)
├─ Manual CSV Uploads
│  ├─ DVOA rankings
│  ├─ Player projections
│  ├─ Injury reports
│  └─ Defensive matchups
└─ Used for: Confidence scoring & recommendations

POST-GAME DATA (Sunday night)
├─ ESPN API (Automated)
│  ├─ Final player stats
│  ├─ Game scores
│  └─ Box scores
└─ Used for: W/L grading & post-game analysis
```

**Why this works:**
- Pre-game analysis uses uploaded data (accurate, curated)
- Post-game grading uses API (automated, immediate)
- Best of both worlds

---

## 🚫 What This Is NOT

**NOT Live Tracking** ❌
- We're NOT tracking props during games
- We're NOT showing real-time progress bars
- We're NOT competing with DraftKings live features

**What This IS** ✅
- Automatic grading AFTER games end
- Immediate results (Sunday night vs Tuesday)
- Post-game analysis ("why did it hit/miss?")
- Learning system (which agents were accurate?)

---

## 📡 ESPN Hidden API

### **Base Endpoint**
```
https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard
```

**Authentication:** None required (public API)

**Rate Limits:** Unknown (unofficial API)
- Use respectfully: 5-minute intervals
- Only ~50 calls per week total

### **Game Status Check**

**Request:**
```bash
GET https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard
```

**Response (abbreviated):**
```json
{
  "events": [
    {
      "id": "401547417",
      "name": "Kansas City Chiefs at Buffalo Bills",
      "date": "2024-01-21T18:30Z",
      "status": {
        "type": {
          "name": "STATUS_FINAL",
          "completed": true
        }
      },
      "competitions": [{
        "competitors": [
          {
            "team": {"displayName": "Kansas City Chiefs"},
            "score": "27"
          },
          {
            "team": {"displayName": "Buffalo Bills"},
            "score": "24"
          }
        ]
      }]
    }
  ]
}
```

**Game Status Values:**
- `STATUS_SCHEDULED` - Not started
- `STATUS_IN_PROGRESS` - Currently playing
- `STATUS_FINAL` - Completed ✅
- `STATUS_POSTPONED` - Delayed

### **Game Box Score**

**Request:**
```bash
GET https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event=401547417
```

**Response (player stats):**
```json
{
  "boxscore": {
    "players": [
      {
        "team": {"displayName": "Kansas City Chiefs"},
        "statistics": [
          {
            "name": "passing",
            "athletes": [
              {
                "athlete": {
                  "displayName": "Patrick Mahomes",
                  "id": "3139477"
                },
                "stats": [
                  "23/35",  // Completions/Attempts
                  "315",    // Yards
                  "3",      // TDs
                  "0"       // INTs
                ]
              }
            ]
          },
          {
            "name": "receiving",
            "athletes": [
              {
                "athlete": {"displayName": "Travis Kelce"},
                "stats": [
                  "7",   // Receptions
                  "73",  // Yards
                  "1"    // TDs
                ]
              },
              {
                "athlete": {"displayName": "Tyreek Hill"},
                "stats": ["5", "62", "1"]
              }
            ]
          },
          {
            "name": "rushing",
            "athletes": [
              {
                "athlete": {"displayName": "Isiah Pacheco"},
                "stats": [
                  "18",  // Attempts
                  "89",  // Yards
                  "1"    // TDs
                ]
              }
            ]
          }
        ]
      }
    ]
  }
}
```

---

## 🔧 Backend Architecture

### **Core Components**

```python
# backend/services/result_tracker.py

class GameResultTracker:
    """Tracks game completions and grades props"""

    def __init__(self):
        self.espn_api = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
        self.graded_games = set()

    def monitor_games(self, week):
        """Main loop - runs during game windows"""
        pass

    def check_completed_games(self):
        """Poll ESPN API for finished games"""
        pass

    def grade_game_props(self, game_id):
        """Grade all props for completed game"""
        pass

    def fetch_final_stats(self, game_id):
        """Get box score from ESPN"""
        pass

    def grade_single_prop(self, prop, stats):
        """Compare line vs actual result"""
        pass

    def trigger_post_game_analysis(self, game_id):
        """Generate insights"""
        pass

    def notify_users(self, game_id):
        """Send push notifications"""
        pass
```

### **Main Workflow**

```python
def monitor_games(week):
    """
    Runs on Sundays during game windows
    """
    games = get_week_games(week)

    while not all_games_complete(games):
        # Check every 5 minutes
        completed = check_completed_games(games)

        for game in completed:
            if game not in graded_games:
                # 1. Fetch final stats
                stats = fetch_final_stats(game)

                # 2. Grade all props for this game
                results = grade_game_props(game, stats)

                # 3. Analyze agent accuracy
                analysis = analyze_agents(results)

                # 4. Generate insights
                insights = generate_insights(results, analysis)

                # 5. Notify users
                notify_users_with_bets(game)

                graded_games.add(game)

        time.sleep(300)  # 5 minutes
```

### **Grading Logic**

```python
def grade_single_prop(prop, final_stats):
    """
    Determine if prop hit or missed
    """
    player = prop['player_name']
    stat_type = prop['stat_type']  # 'receiving_yards', etc.
    line = prop['line']
    direction = prop['direction']  # 'OVER' or 'UNDER'

    # Get player's actual stat
    actual = final_stats[player][stat_type]

    # Did it hit?
    if direction == 'OVER':
        hit = actual > line
    else:
        hit = actual < line

    return {
        'prop_id': prop['id'],
        'player': player,
        'line': line,
        'actual': actual,
        'difference': actual - line,
        'status': 'HIT' if hit else 'MISS',
        'confidence': prop['original_confidence']
    }
```

---

## 📊 API Usage Calculations

### **Weekly API Calls**

```
17 games per week (typical Sunday)

Checking for completion:
- Poll every 5 minutes during 3-hour window
- 36 checks per game window
- BUT: Single API call checks ALL games
- Total: 36 calls (not 36 × 17)

Fetching final stats:
- 1 call per completed game
- 17 games × 1 call = 17 calls

Total per week: 36 + 17 = 53 calls
Monthly: 53 × 4 weeks = 212 calls

COMPARED TO LIVE TRACKING:
- Live: 6,000+ calls/week
- Post-game: 53 calls/week
- 99% reduction! ✅
```

### **Smart Optimizations**

```python
# 1. Batch game checks (one API call)
response = requests.get(ESPN_API)
all_games = response.json()['events']

# 2. Cache completed games
if game_id in graded_games_cache:
    return cached_result

# 3. Smart polling schedule
if active_games_count() > 0:
    poll_interval = 300  # 5 min
else:
    poll_interval = 1800  # 30 min (off-hours)
```

---

## 💾 Database Schema

```sql
-- Store prop results
CREATE TABLE prop_results (
    id SERIAL PRIMARY KEY,
    prop_id INTEGER REFERENCES props(id),
    user_id INTEGER REFERENCES users(id),
    game_id VARCHAR(50),
    week INTEGER,

    -- Pre-game data
    player_name VARCHAR(100),
    prop_type VARCHAR(50),
    line DECIMAL(5,1),
    direction VARCHAR(10),  -- OVER/UNDER
    confidence INTEGER,

    -- Agent predictions (JSON)
    agent_scores JSONB,

    -- Post-game results
    actual_value DECIMAL(5,1),
    difference DECIMAL(5,1),
    status VARCHAR(20),  -- HIT, MISS, PUSH, ERROR

    -- Timestamps
    bet_placed_at TIMESTAMP,
    game_completed_at TIMESTAMP,
    graded_at TIMESTAMP,

    INDEX idx_user_week (user_id, week),
    INDEX idx_game (game_id),
    INDEX idx_status (status)
);

-- Store post-game analysis
CREATE TABLE post_game_analysis (
    id SERIAL PRIMARY KEY,
    game_id VARCHAR(50),
    week INTEGER,

    -- Summary
    total_props INTEGER,
    hits INTEGER,
    misses INTEGER,

    -- Agent performance (JSON)
    agent_accuracy JSONB,

    -- Insights (JSON)
    insights JSONB,

    generated_at TIMESTAMP,

    INDEX idx_week (week)
);

-- Track agent performance over time
CREATE TABLE agent_performance (
    id SERIAL PRIMARY KEY,
    week INTEGER,
    agent_name VARCHAR(50),

    -- Accuracy metrics
    total_predictions INTEGER,
    correct_predictions INTEGER,
    accuracy_pct DECIMAL(5,2),

    -- By confidence tier
    high_conf_accuracy DECIMAL(5,2),  -- 75+
    med_conf_accuracy DECIMAL(5,2),   -- 60-74

    updated_at TIMESTAMP,

    INDEX idx_week_agent (week, agent_name)
);
```

---

## 📱 Mobile App Experience

### **Sunday 4:15 PM - Early Games End**

**Push Notification:**
```
🏈 Early games complete!
Your props: 4/6 hit (67%)
+$85 profit
Tap to see results →
```

**App Screen:**
```
┌─────────────────────────────────────────┐
│ 🏈 SUNDAY RESULTS (Early Games)         │
├─────────────────────────────────────────┤
│ Your Record: 4-2 (67%)                  │
│ Profit: +$85                           │
│                                         │
│ HITS ✅                                 │
│                                         │
│ ✅ Patrick Mahomes                      │
│    Pass Yds 315/275.5 (+39.5)          │
│    Confidence: 82                      │
│    • DVOA Agent was right (85)         │
│    • Matchup Agent was right (90)      │
│                                         │
│ ✅ Travis Kelce                         │
│    Rec Yds 73/58.5 (+14.5)             │
│    Confidence: 75                      │
│    • Volume Agent was right (75)       │
│    • High target share delivered       │
│                                         │
│ ✅ Justin Jefferson                     │
│    Rec Yds 102/79.5 (+22.5) 🔥         │
│    Confidence: 78                      │
│    • Elite matchup paid off            │
│                                         │
│ MISSES ❌                               │
│                                         │
│ ❌ Tyreek Hill                          │
│    Rec Yds 58/65.5 (-7.5)              │
│    Confidence: 78                      │
│    • Close call (11% short)            │
│    • Game script shifted (Chiefs led)  │
│                                         │
│ WHY IT MISSED:                          │
│ GameScript Agent predicted shootout,   │
│ but Chiefs dominated time of possession.│
│ Hill saw fewer targets in 2nd half.    │
│                                         │
├─────────────────────────────────────────┤
│ 📊 AGENT PERFORMANCE (Today)            │
│                                         │
│ DVOA Agent: 80% accurate ████████       │
│ Matchup Agent: 75% accurate ███████     │
│ Volume Agent: 70% accurate ███████      │
│ GameScript: 50% accurate █████          │
│ Trend Agent: 50% accurate █████         │
│                                         │
│ 💡 LESSONS FOR NEXT WEEK                │
│                                         │
│ • Trust DVOA + Matchup agents          │
│ • GameScript was off today - weather?  │
│ • Avoid WR2s when team leads big       │
│                                         │
│ [View Late Game Props]                  │
└─────────────────────────────────────────┘
```

---

## 🤖 Post-Game Analysis Engine

### **Agent Accuracy Calculation**

```python
def analyze_agent_accuracy(results):
    """
    Determine which agents predicted correctly
    """
    agent_stats = {
        'dvoa': {'correct': 0, 'total': 0},
        'matchup': {'correct': 0, 'total': 0},
        'volume': {'correct': 0, 'total': 0},
        # ... etc
    }

    for result in results:
        agent_scores = result['agent_scores']

        for agent, score in agent_scores.items():
            # Agent was bullish (score > 60)
            if score > 60:
                agent_stats[agent]['total'] += 1
                if result['status'] == 'HIT':
                    agent_stats[agent]['correct'] += 1

            # Agent was bearish (score < 40)
            elif score < 40:
                agent_stats[agent]['total'] += 1
                if result['status'] == 'MISS':
                    agent_stats[agent]['correct'] += 1

    # Calculate percentages
    for agent in agent_stats:
        total = agent_stats[agent]['total']
        if total > 0:
            accuracy = agent_stats[agent]['correct'] / total * 100
            agent_stats[agent]['accuracy'] = round(accuracy, 1)

    return agent_stats
```

### **Insight Generation**

```python
def generate_insights(results, agent_accuracy):
    """
    Find interesting patterns
    """
    insights = []

    # 1. High confidence performance
    high_conf = [r for r in results if r['confidence'] >= 75]
    if high_conf:
        hit_rate = sum(1 for r in high_conf if r['status'] == 'HIT') / len(high_conf)
        insights.append({
            'type': 'confidence',
            'message': f"75+ confidence: {hit_rate*100:.0f}% ({len(high_conf)} props)",
            'good': hit_rate >= 0.65
        })

    # 2. Best agent today
    best = max(agent_accuracy.items(), key=lambda x: x[1]['accuracy'])
    insights.append({
        'type': 'best_agent',
        'message': f"{best[0].upper()} was most accurate: {best[1]['accuracy']:.0f}%",
        'agent': best[0]
    })

    # 3. Close calls (decided by ≤5 units)
    close = [r for r in results if abs(r['difference']) <= 5]
    if close:
        insights.append({
            'type': 'close_calls',
            'message': f"{len(close)} props decided by 5 or less",
            'props': [p['player'] for p in close]
        })

    # 4. Prop type performance
    rec_yds = [r for r in results if r['prop_type'] == 'receiving_yards']
    if rec_yds:
        hit_rate = sum(1 for r in rec_yds if r['status'] == 'HIT') / len(rec_yds)
        insights.append({
            'type': 'prop_type',
            'message': f"Rec Yds props: {hit_rate*100:.0f}% today",
            'good': hit_rate >= 0.60
        })

    return insights
```

---

## 🔄 Scheduling

### **APScheduler Setup**

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

# Sunday games (start monitoring 12:45pm ET)
scheduler.add_job(
    func=monitor_games,
    trigger='cron',
    day_of_week='sun',
    hour=12,
    minute=45,
    args=[current_week()]
)

# Thursday Night Football
scheduler.add_job(
    func=monitor_games,
    trigger='cron',
    day_of_week='thu',
    hour=19,
    minute=45,
    args=[current_week()]
)

# Monday Night Football
scheduler.add_job(
    func=monitor_games,
    trigger='cron',
    day_of_week='mon',
    hour=19,
    minute=45,
    args=[current_week()]
)

scheduler.start()
```

---

## 🚀 Implementation Phases

### **Phase 1: Basic Grading (Week 1)**
- ✅ Poll ESPN API for game status
- ✅ Fetch final box scores
- ✅ Grade props (HIT/MISS)
- ✅ Store results in database
- ✅ Show in mobile app

### **Phase 2: Notifications (Week 2)**
- ✅ Send push when games complete
- ✅ Show summary stats (4/6 hit)
- ✅ Link to detailed results

### **Phase 3: Post-Game Analysis (Week 3)**
- ✅ Agent accuracy calculation
- ✅ Generate insights
- ✅ "Why did it hit/miss?" explanations
- ✅ Weekly reports

### **Phase 4: Historical Tracking (Week 4)**
- ✅ Track agent performance over time
- ✅ Confidence tier validation
- ✅ Prop type trends
- ✅ System performance dashboard

---

## 💰 Cost Analysis

### **ESPN API Costs**
```
API: FREE (unofficial)
Risk: Could break if ESPN changes format
Mitigation: Monitor weekly, have backup plan

Backup option: SportsData.io
- $99/mo for real-time stats
- Official, won't break
- Switch if ESPN API fails
```

### **Infrastructure Costs**
```
VPS (for background task): $20/mo
PostgreSQL (database): $25/mo
Push notifications (Firebase): $10/mo
Redis (caching): $15/mo

Total: $70/mo (vs $194/mo for live tracking)
```

### **Break-Even**
```
$70/mo ÷ $9.99 premium = 7 users
Very achievable!
```

---

## ⚠️ Edge Cases

### **1. Player Name Mismatches**
```python
# ESPN: "Patrick Mahomes II"
# Your DB: "Patrick Mahomes"

name_normalizer = {
    "Patrick Mahomes II": "Patrick Mahomes",
    "A.J. Brown": "AJ Brown",
    "D.K. Metcalf": "DK Metcalf",
    # etc...
}
```

### **2. Game Postponements**
```python
if game_status == 'STATUS_POSTPONED':
    notify_users("Game postponed - props will grade when rescheduled")
    mark_props_as_pending()
```

### **3. API Failures**
```python
try:
    stats = fetch_espn_stats(game_id)
except (Timeout, ConnectionError):
    # Retry with exponential backoff
    retry_with_backoff(fetch_espn_stats, game_id)
except Exception:
    # Fall back to manual grading
    queue_for_manual_review(game_id)
```

### **4. Stat Corrections**
```python
# ESPN sometimes corrects stats after initial report
# Re-check 1 hour after game ends

scheduler.add_job(
    func=recheck_stats,
    trigger='date',
    run_date=game_end_time + timedelta(hours=1),
    args=[game_id]
)
```

---

## 🎯 Success Metrics

### **System Reliability**
- 95%+ of games auto-graded successfully
- <1% stat mismatches requiring manual review
- <5 min average time from game end to results

### **User Engagement**
- 70%+ of users check results within 1 hour of notification
- 50%+ of users view post-game analysis
- 30%+ of users adjust strategy based on agent accuracy

### **API Stability**
- <1% API failure rate
- <30 sec average API response time
- Zero ESPN-related outages

---

## 📝 Testing Plan

### **Unit Tests**
```python
def test_grade_over_prop():
    prop = {'line': 65.5, 'direction': 'OVER'}
    actual = 73.0
    result = grade_prop(prop, actual)
    assert result['status'] == 'HIT'

def test_grade_under_prop():
    prop = {'line': 2.5, 'direction': 'UNDER'}
    actual = 1.0
    result = grade_prop(prop, actual)
    assert result['status'] == 'HIT'

def test_push():
    prop = {'line': 65.5, 'direction': 'OVER'}
    actual = 65.5
    result = grade_prop(prop, actual)
    assert result['status'] == 'PUSH'
```

### **Integration Tests**
```python
def test_espn_api_connection():
    response = requests.get(ESPN_API)
    assert response.status_code == 200
    assert 'events' in response.json()

def test_full_grading_flow():
    # Mock completed game
    game = create_mock_game()

    # Grade props
    results = grade_game_props(game)

    # Verify results saved
    assert db.get_prop_result(prop_id=1).status == 'HIT'

    # Verify notification sent
    assert notification_sent_to_user(user_id=1)
```

---

## 🎯 Summary

**This system provides:**
- ✅ Automatic prop grading (no manual work)
- ✅ Immediate results (Sunday night vs Tuesday)
- ✅ Post-game analysis (why it hit/miss)
- ✅ Agent accuracy tracking (continuous learning)
- ✅ Low cost (~$70/mo vs $194/mo for live tracking)
- ✅ Sustainable API usage (53 calls/week vs 6,000+)

**Better than live tracking because:**
- Users don't need live updates (DraftKings handles that)
- Post-game learning is more valuable than live watching
- Much simpler to build and maintain
- Way cheaper to operate

**Timeline:**
- Week 1: Basic grading
- Week 2: Notifications
- Week 3: Post-game analysis
- Week 4: Historical tracking
- **Total: 4 weeks vs 6 weeks for live tracking**

---

**Document Version:** 1.0
**Last Updated:** 2026-01-10
**Status:** Ready for implementation
