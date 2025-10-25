# 🎯 DATA FILES SETUP - CORRECT VERSION

**IMPORTANT:** We use betting lines as "projections" - no separate projection file needed!

---

## 📊 REQUIRED FILES FOR WEEK 7

Place these in `C:\Users\scott\Desktop\nfl-betting-system\data\`:

### 1. DVOA Rankings (Team Strength)
```
DVOA_Off_wk_7.csv   ← Offensive DVOA by team
DVOA_Def_wk_7.csv   ← Defensive DVOA by team
```

### 2. Defensive Matchups
```
Def_vs_WR_wk_7.csv  ← How defenses perform vs WR1/WR2/WR3
```

### 3. Betting Lines (THE PROJECTIONS!)
```
betting_lines_wk_7.csv  ← Player props from DraftKings/FanDuel
```

**This file contains:**
- Player names
- Prop types (pass_yds, rush_yds, reception_yds, etc.)
- Over/Under lines
- Odds

**The lines ARE the market projections!**

### 4. Optional: Injury Report
```
week7_injury_report.txt  ← Player injury status
```

---

## ⚡ QUICK SETUP (One Command)

```bash
# Double-click this file:
SETUP_DATA_FILES.bat
```

**This will:**
1. Copy all project files to `/data` folder
2. Rename betting lines correctly
3. Create Week 7 DVOA files (using Week 6 as most recent)
4. Set everything up perfectly!

---

## 📁 YOUR CURRENT FILES

You have:
- ✅ `DVOA_Off_wk_6.csv`
- ✅ `DVOA_Def_wk_6.csv`
- ✅ `Def_vs_WR_wk_6.csv`
- ✅ `Betting_Lines_wk_7_Saturday__Sheet1.csv`
- ✅ `week7_injury_report.txt`

**Perfect! Just need to copy them to `/data` folder.**

---

## 🎯 WHY NO PROJECTIONS FILE?

**Old way (wrong):**
- Get projections from FantasyPros
- Get betting lines separately
- Compare projections vs lines

**Our way (correct):**
- Betting lines ARE the projections
- Lines = market consensus projection
- We analyze vs DVOA/matchups to find value

**The betting lines file contains all the "projections" we need!**

---

## 📊 BETTING LINES FILE FORMAT

Your file should look like this:

```csv
game_id,commence_time,bookmaker,home_team,away_team,market,label,description,price,point
...,10/19/2025,DraftKings,JAX,LAR,player_pass_yds,Over,Matthew Stafford,-112,247.5
...,10/19/2025,DraftKings,JAX,LAR,player_rush_yds,Over,Kyren Williams,-118,67.5
...,10/19/2025,DraftKings,JAX,LAR,player_reception_yds,Over,Puka Nacua,-105,58.5
```

**The `point` column = the line = the "projection"**

---

## 🧠 HOW THE SYSTEM WORKS

1. **Load betting lines** (player props with Over/Under lines)
2. **Load DVOA data** (team offensive/defensive strength)
3. **Load matchup data** (how defenses perform vs WR1/WR2/etc)
4. **Analyze each prop:**
   - Is the line too low given the matchup?
   - Does DVOA suggest more production?
   - Is there positive expected value?
5. **Output confidence score** (0-100)

**The betting line is what we're betting on - not a separate projection!**

---

## ✅ AFTER RUNNING SETUP_DATA_FILES.BAT

You'll have:
```
data/
  ├── DVOA_Off_wk_7.csv
  ├── DVOA_Def_wk_7.csv
  ├── Def_vs_WR_wk_7.csv
  ├── betting_lines_wk_7.csv      ← THE PROJECTIONS!
  └── week7_injury_report.txt
```

Then test:
```bash
TEST_SYSTEM.bat
```

Should see:
```
✅ DVOA_Off_wk_7.csv
✅ DVOA_Def_wk_7.csv
✅ Def_vs_WR_wk_7.csv
✅ betting_lines_wk_7.csv
✅ All data files present!
```

---

## 🎯 SUMMARY

**You DON'T need:**
- ❌ NFL_Projections_Wk_7.csv
- ❌ FantasyPros projections
- ❌ Any separate projection file

**You DO need:**
- ✅ DVOA rankings (context)
- ✅ Defensive matchups (context)
- ✅ Betting lines (the lines we analyze!)
- ✅ Injury report (context)

**The betting lines file IS your projection source!**

---

## 🚀 READY TO GO

```bash
# 1. Setup files
SETUP_DATA_FILES.bat

# 2. Test
TEST_SYSTEM.bat

# 3. Start
START_SYSTEM.bat

# 4. Use in Slack
/analyze_props 7
/build_parlays 7
```

**That's it! 🔥**
