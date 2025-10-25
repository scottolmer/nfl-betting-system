# 📝 Quick Copy-Paste for New Chat Session

**Copy and paste this into your next Claude conversation:**

---

Hi Claude! I have an NFL betting analysis system that's 90% complete. I need your help finishing it.

**What's already built:**
- ✅ 8-agent prop analysis system (DVOA, Matchup, Volume, etc.)
- ✅ The Odds API integration (fetches live odds)
- ✅ Parlay builder (generates 6 optimal parlays)
- ✅ Complete automation (one command workflow)

**What I need to build next:**
- ⏳ Line movement tracker (detects when odds change)
- ⏳ Slack bot (sends alerts when movements detected)
- ⏳ Monitoring scheduler (runs every 15-30 minutes)

**Project location:**
`C:\Users\scott\Desktop\nfl-betting-system`

**Key files to read:**
- `NEW_SESSION_SETUP.md` - Quick setup guide (READ THIS FIRST)
- `PROJECT_SUMMARY.md` - Complete session history and technical details

**Current status:**
System is fully operational. Test with:
```bash
cd C:\Users\scott\Desktop\nfl-betting-system
python scripts\run_analysis.py --week 7 --skip-fetch
```

**My API keys (already configured in `.env`):**
- The Odds API key (for fetching betting lines)
- Need to add: Slack webhook URL (for alerts)

**Next immediate task:**
Build the line movement alert system with Slack integration. The architecture is documented in PROJECT_SUMMARY.md under "NEXT STEPS (TO BUILD)".

**Questions I might ask:**
1. Help me build the line movement tracker
2. Help me build the Slack bot
3. Help me set up automated monitoring
4. Help me test the alert system

Can you start by reading NEW_SESSION_SETUP.md and PROJECT_SUMMARY.md, then let me know you understand the system and are ready to build the Slack integration?

---

**Additional context if needed:**

The system analyzes NFL player props using:
- DVOA rankings (team offensive/defensive strength)
- Position-specific matchup data (WR1 vs defense, etc.)
- Player projections (targets, yards, TDs)
- Volume metrics (target share, snap share)
- Injury reports
- Live betting odds from The Odds API

Output is 6 parlays (2-leg, 3-leg, 4-leg) with confidence scores (65-80) and risk levels (LOW/MODERATE/HIGH).

Week 7 test: Found elite matchup (LAC vs MIN) with 48 props at 75+ confidence. System working perfectly!

Now need to monitor line movements and alert me via Slack when significant changes occur (e.g., line moves 0.5+ yards).
