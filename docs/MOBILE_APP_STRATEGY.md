# 🏈 Mobile App Strategy & Architecture

**Date:** 2026-01-10
**Status:** Planning Phase

---

## 📋 Executive Summary

Converting the NFL Betting System to iOS/Android mobile apps using a **Backend API + Cross-Platform Mobile** approach (React Native or Flutter).

**Timeline:** 8-12 weeks for MVP
**Recommended Approach:** Option 2 - Keep Python backend as REST API, build mobile frontend

---

## 🎯 Conversion Approach

### **Recommended: Option 2 - Backend API + Native Mobile**

**Architecture:**
```
Mobile App (React Native/Flutter)
    ↓ HTTP/REST API
Python Backend (FastAPI)
    ↓ Analysis Engine
8 Agent System (existing Python code)
    ↓ Data Sources
PostgreSQL + External APIs
```

**Why this approach:**
- ✅ Reuse 90%+ of existing Python analysis code
- ✅ True native app experience
- ✅ Can distribute via App Store/Google Play
- ✅ Push notifications for line movements
- ✅ Offline caching
- ✅ Single codebase for iOS + Android

**Code Reuse:**
- Backend analysis: 95% reuse (convert to REST API)
- Frontend: 0% reuse (build new mobile UI)
- Database: 90% reuse (SQLite → PostgreSQL)

---

## 📱 Mobile App Structure

### **Bottom Navigation (5 tabs)**

```
┌─────────────────────────────────┐
│   BOTTOM NAV                    │
├─────────────────────────────────┤
│ 🏠 Home      │ Top props        │ PRIMARY
│ 🎰 Parlays   │ Pre-built        │ PRIMARY
│ ⚡ Build     │ Custom builder   │ PRIMARY (NEW!)
│ 📊 My Bets   │ Bet tracking     │ PRIMARY
│ ⚙️ More      │ Settings/Stats   │ SECONDARY
└─────────────────────────────────┘
```

---

## 🔥 PRIMARY FEATURES (Main Screens)

### **1. Home Screen: Today's Action**
- Top 10 props (sorted by confidence, live updated)
- Color-coded: 🔥 80+, ⭐ 75-79, ✅ 70-74
- Quick search bar
- Parlay of the Day
- Game schedule

### **2. Pre-Built Parlays**
- 6 ready-to-bet parlays (2-leg, 3-leg, 4-leg)
- Combined confidence scores
- Risk levels (LOW/MODERATE/HIGH)
- Unit recommendations
- One-tap "Copy to Clipboard" or "Export to DraftKings"
- Quick filters by risk, legs, games

### **3. ⚡ Parlay Builder + Tracker** (NEW! - 3-in-1 Feature)

**KEY INNOVATION:** The parlay builder IS the bet tracker. Users build parlays in the app, save them, then place in their preferred sportsbook. System auto-tracks and grades results.

**Workflow:**
```
Build in app → Get confidence → Place in book → Auto-graded results
```

#### **My Parlays Library**
```
📚 MY PARLAYS (2/3 used) 🔓  ← Free tier limit

┌─────────────────────────────────┐
│ 📝 Sunday Morning Special       │
│ 3 legs • 78 confidence          │
│ DraftKings Pick 6 • $20         │
│ Status: Placed ✅               │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ 📝 Chiefs Stack                 │
│ 4 legs • 82 confidence          │
│ FanDuel Pick 6 • Not placed     │
│ Status: Draft                   │
└─────────────────────────────────┘

[+ Create New Parlay] (Upgrade for unlimited)
```

#### **Sportsbook Selection**
- User selects their preferred book when creating parlay
- Supports: DraftKings Pick 6, FanDuel Pick 6, Underdog Fantasy, PrizePicks, BetMGM, Caesars, etc.
- Book-agnostic design (works for all platforms)
- Line adjustment built-in for Pick 6 variations

#### **Building a Parlay**

**Step 1: Create & Name**
- Name: "Sunday Morning Special"
- Sportsbook: [DraftKings Pick 6]
- Bet amount: $20 (optional)

**Step 2: Add Props (with filters)**

**Top: Filters (collapsible)**
- 🏈 Teams (multi-select)
- 👤 Positions (QB, RB, WR, TE)
- 📊 Min Confidence (slider: 60-90)
- 🎯 Prop Types (Yds, Rec, TD, Rush)
- 🎲 Parlay Style (Any Games, Same Game, Max Diversity)
- 🔢 Target Legs (2, 3, 4, 5, 6)

**Quick Filter Presets:**
- [🔥 Elite Only] - 80+ confidence
- [🎯 Shootouts] - High total games
- [🏃 RB Heavy] - Only RB props
- [⭐ WR1s] - Only team's top WR
- [🏠 Same Game] - One game only
- [🌎 Max Spread] - All different games

**Middle: Available Props (scrollable)**
```
🔥 85  Patrick Mahomes [+]
Pass Yds OVER 275.5 | vs BUF
Pick 6 Line: [275.5] [✏️ Edit]

⭐ 78  Travis Kelce [+]
Rec Yds OVER 58.5 | vs BUF
DK Props: 56.5 → Pick 6: 58.5 [✏️]
```

**Bottom: Your Parlay (live updates)**
```
1. Mahomes Pass Yds OVER 275.5 [×]
2. Kelce Rec Yds OVER 58.5 [×]

Combined Confidence: 81 🔥
Risk: LOW (2 legs, uncorrelated)

[💾 Save] [📋 Copy] [➕ Add More]
```

**Step 3: Save & Export**
```
✅ Parlay Saved!

NEXT STEPS:
1. Open DraftKings Pick 6
2. Enter these props
3. Return to mark as "Placed"

[📋 Copy Props to Clipboard]
[📱 Open DraftKings]
[✅ Mark as Placed]
```

**Step 4: Track & Grade**
- User marks parlay as "Placed" (optional: enter bet amount)
- After games end, ESPN API auto-grades props
- Push notification: "Your parlays are graded!"
- Detailed post-game analysis

#### **Smart Features:**
- **Auto-optimization suggestions** - "Swap Kelce for Hill (+4 confidence)"
- **Conflict detection** - "3 KC props = high correlation risk"
- **Line adjustment** - Adjust lines for Pick 6 differences
- **Save custom filters** - "WR Elite Shootouts" preset
- **Share parlays** - Send to friends (Premium)

#### **Why This Approach:**
- ✅ **No OCR needed** - User manually builds (simple, reliable)
- ✅ **Book-agnostic** - Works for all sportsbooks
- ✅ **Natural workflow** - Build first, then place
- ✅ **Engagement** - 3 touchpoints (build, place, results)
- ✅ **Monetizable** - Free tier limit drives upgrades

### **4. My Bets Screen**
- Active bets (post-game results, auto-graded)
- Pending bets (not started)
- Recent results (W/L last 7 days)
- Bankroll tracker (units won/lost)

### **5. Prop Search/Analysis**
- Search: "Jefferson receiving yards"
- Instant confidence score
- Top 3 reasons
- Compare lines (79.5 vs 82.5)
- Add to custom parlay

---

## ⚙️ SECONDARY FEATURES (Settings/Background)

### **Customization Screen**
- Agent weights (DVOA 2.0x → adjust)
- Minimum confidence thresholds
- Position filters
- Prop type filters
- Risk tolerance
- Unit size ($10, $25, $50)

### **Background Processes (Automated)**
- Data refresh (every 60 minutes)
- Weekly data updates (Wednesday/Thursday)
- Performance learning (after each game)
- Line movement monitoring (hourly)

### **Stats/History Screen**
- Performance dashboard
- Win rate by prop type
- Win rate by confidence tier
- Best agents
- ROI by parlay size
- Historical bets (last 50)
- Weekly reports

### **Notification Settings**
- Line movements (75+ confidence? 80+?)
- Daily digest (9am Sunday)
- Live bet updates (optional)
- Results (parlay won/lost)

---

## 🚫 FEATURES TO SKIP

### **Live Game Tracking - NOT NEEDED** ❌

**Why skip:**
- DraftKings already does this perfectly
- Users stay in DK app during games
- Your value is PRE-game analysis, not DURING game
- Would cost $100+/mo and 6 weeks dev time
- <10% of users would actually use it

**Better approach:**
- Let DraftKings handle live tracking
- Focus on post-game analysis instead (see below)

---

## 🎯 KEY FEATURE: LINE ADJUSTMENT FOR PICK 6

### **Problem:**
DraftKings Pick 6 lines often differ from sportsbook props:
- Kelce Rec Yds: 56.5 (props) vs 58.5 (Pick 6)
- Need to re-score confidence for Pick 6 lines

### **Solution: Manual Line Adjustment (FREE)**

**UI:**
```
Travis Kelce Rec Yds OVER
Original: 56.5 (Confidence: 80)
Pick 6: [58.5] [✏️ Edit]

Re-scored Confidence: 75 (-5)
⚠️ Line moved 2 yards tighter
Cushion: 8.5 → 6.5 yards (vs projection: 65)
Still playable but reduced edge
```

**Backend Logic:**
```python
# Every 1 yard tighter = -2 to -3 confidence points
cushion_diff = new_cushion - old_cushion
confidence_adjustment = cushion_diff * 2.5

new_confidence = original_confidence + adjustment
```

**Decision: Make this FREE (not premium)**
- It's core functionality for Pick 6 users
- Pick 6 is a MASSIVE market
- Making it premium = "free tier can't use Pick 6"
- Better premium features exist (see pricing below)

---

## 💰 FREEMIUM PRICING MODEL

### **FREE TIER: "The Basic Bettor"**

**Included:**
- Top 10 props per week
- 2 pre-built parlays per week
- **2-3 saved custom parlays at a time** ✅ (once graded, they archive)
- **Manual line adjustment (unlimited)** ✅
- Basic prop search (10 searches/week)
- 1 sportsbook selection
- Last 7 days bet history
- Post-game auto-grading for saved parlays

**Limits:**
- Only top 10 props (not all 100+)
- Only 2 pre-built parlays (not all 6)
- **Max 2-3 active custom parlays** (must delete or wait for grading to create new)
- No saved filter presets
- No push notifications
- Basic filters only

---

### **PREMIUM TIER: "The Sharp" - $9.99/month**

**Everything in Free, PLUS:**

**Analysis:**
- ✅ All 100+ props analyzed
- ✅ All 6 pre-built parlays
- ✅ Advanced filters
- ✅ Undervalued line detection
- ✅ Alt line suggestions

**Parlay Builder + Tracker:**
- ✅ **Unlimited saved parlays** (no 2-3 limit)
- ✅ Auto-optimization suggestions
- ✅ Saved filter presets (unlimited)
- ✅ Parlay comparison tool
- ✅ Conflict detection
- ✅ Multiple sportsbook support
- ✅ Share parlays with friends
- ✅ Save parlays for future weeks

**Tracking & Alerts:**
- ✅ Unlimited parlay tracking
- ✅ **Push notifications** (line movements)
- ✅ **Post-game auto-grading** (Sunday night results)
- ✅ Full bet history
- ✅ Weekly performance reports

**Advanced:**
- ✅ Custom agent weights
- ✅ Historical agent accuracy
- ✅ Export parlays
- ✅ Saved parlays (unlimited)
- ✅ Early data access (Wed 6pm vs Thu 12pm)

---

### **PRO TIER: "The Syndicate" - $29.99/month**

**Everything in Premium, PLUS:**

**Advanced Analytics:**
- ✅ Prop edge calculator (EV vs line)
- ✅ Kelly Criterion bet sizing
- ✅ Bankroll management dashboard
- ✅ ROI tracking by agent/position/game
- ✅ Win rate by confidence tier

**AI Features:**
- ✅ Natural language queries
- ✅ Chat with bet history
- ✅ Automated learning (system adjusts weights)
- ✅ Personalized recommendations

**Community:**
- ✅ Trending parlays (what sharps bet)
- ✅ Leaderboard (top win rates)
- ✅ Share parlays with friends
- ✅ Copy plays from top performers

**Pro Tools:**
- ✅ API access
- ✅ CSV exports
- ✅ White-label reports
- ✅ Multi-week analysis

---

## 📊 REVENUE PROJECTIONS

**With line adjustment FREE:**
```
10,000 free users
    ↓ 5% convert to Premium
  500 premium @ $9.99 = $4,995/mo
    ↓ 10% upgrade to Pro
   50 pro @ $29.99 = $1,500/mo

Total MRR: $6,495/month ($78k/year)
```

**Target conversion:**
- Free → Premium: 5% (industry standard)
- Premium → Pro: 10%
- Break-even: 20 premium users ($194/mo costs)

---

## 🎯 BETTER FEATURES TO MONETIZE (Not Line Adjustment)

### **1. Push Notifications** 💰💰💰
```
🚨 LINE MOVEMENT ALERT
Justin Jefferson Rec Yds
79.5 → 82.5 (+3.0)
System confidence: Still 75 (STRONG)
```
- High value, high stickiness
- Premium-only feels justified

### **2. Post-Game Analysis** 💰💰💰
```
WHY IT HIT ✅
Travis Kelce Rec Yds 67/58.5

✅ Volume Agent was right
   Predicted: 25%+ targets
   Actual: 28% (9 of 32)

✅ Matchup Agent was right
   Predicted: Bills weak vs TE
   Actual: 67 yds, 6 catches

TAKEAWAY: Trust Volume + Matchup for Kelce
```
- DraftKings doesn't explain WHY
- Helps users learn edge
- Builds trust

### **3. Auto-Optimization** 💰💰
```
Your 3-leg: 72 confidence
💡 Swap Kelce for Hill → 78 (+6)
[Apply Fix]
```
- AI-powered value-add
- Premium-only

### **4. System Performance Dashboard** 💰💰
```
SYSTEM ACCURACY (Last 4 weeks)
80+ confidence: 78% hit rate
75-79: 71% hit rate
70-74: 62% hit rate

BY AGENT:
DVOA: 74% accurate
Matchup: 71% accurate
Trend: 58% accurate (avoid!)
```
- Transparency builds trust
- Data nerds love this

### **5. "Sharps are Betting" (Social)** 💰
```
🌟 TRENDING PARLAYS
847 top users built: "Chiefs Stack"
Avg confidence: 81
[Copy Parlay] (Premium)
```
- FOMO + social proof
- Community engagement

---

## 🚀 IMPLEMENTATION PHASES

### **Phase 1: Backend API (Weeks 1-3)**
- Convert Python analysis to FastAPI REST API
- PostgreSQL database setup
- Authentication (JWT)
- Core endpoints (props, parlays, analysis)

### **Phase 2: Mobile MVP (Weeks 4-8)**
- Home screen (top 10 props)
- Pre-built parlays
- Basic prop search
- Authentication/signup
- My Bets screen

### **Phase 3: Custom Builder (Weeks 9-10)**
- Filter UI
- Add/remove props
- Live confidence calculation
- Save parlays

### **Phase 4: Premium Features (Weeks 11-12)**
- Push notifications setup
- Post-game auto-grading (ESPN API)
- Payment integration (Stripe/RevenueCat)
- Agent customization

### **Phase 5: Polish & Launch (Weeks 13-14)**
- Testing
- App Store submission
- Marketing materials
- Beta testing

---

## 🛠️ TECH STACK RECOMMENDATIONS

### **Backend:**
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL (Heroku/Supabase)
- **Hosting:** Heroku, Railway, or DigitalOcean
- **Cache:** Redis (for performance)
- **Auth:** JWT tokens

### **Mobile:**
- **Framework:** React Native (recommended) or Flutter
- **Why React Native:** Larger community, easier hiring, JavaScript
- **State Management:** Redux Toolkit or Zustand
- **Navigation:** React Navigation
- **Push Notifications:** Firebase Cloud Messaging

### **Payments:**
- **iOS/Android IAP:** RevenueCat (handles both platforms)
- **Subscription Management:** RevenueCat + Stripe

### **Analytics:**
- **Mobile:** Mixpanel or Amplitude
- **Crash Reporting:** Sentry
- **Performance:** Firebase Performance

---

## 💡 KEY DESIGN PRINCIPLES

### **1. Speed First**
- Home screen loads in <2 seconds
- Optimistic UI updates
- Cache aggressively

### **2. Clarity Over Complexity**
- Color-coded confidence (no mental math)
- One-tap actions
- Progressive disclosure (advanced features hidden)

### **3. Trust Building**
- Always show WHY (top 3 reasons)
- System performance transparency
- Post-game "what we got right/wrong"

### **4. Mobile-First UX**
- Design for one-handed use
- Big tap targets (44x44 minimum)
- Bottom navigation (thumb-friendly)
- Pull-to-refresh
- Swipe gestures

---

## 📝 NEXT STEPS

1. **Choose mobile framework** (React Native vs Flutter)
2. **Set up backend API** (FastAPI + PostgreSQL)
3. **Design mockups** (Figma or similar)
4. **Build MVP** (Home + Parlays + My Bets)
5. **Test with beta users**
6. **Iterate based on feedback**
7. **Add premium features**
8. **Launch on App Store / Google Play**

---

## 🎯 SUCCESS METRICS

**MVP Success (First 3 months):**
- 1,000+ downloads
- 10% weekly active users
- 3% conversion to premium
- <5% churn rate

**Year 1 Goals:**
- 10,000+ users
- 500+ premium subscribers
- $5,000+ MRR
- 65%+ hit rate on 75+ confidence props

---

**Document Version:** 1.0
**Last Updated:** 2026-01-10
**Next Review:** After MVP launch
