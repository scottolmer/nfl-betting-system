# 🚀 Quick Start - NFL Betting System UI

## Get Started in 60 Seconds

### 1. Install (30 seconds)
```bash
cd C:\Users\scott\Desktop\nfl-betting-systemv2\ui
pip install -r requirements.txt
```

### 2. Run (5 seconds)
From project root:
```bash
streamlit run ui/app.py
```

Or simply double-click:
```
C:\Users\scott\Desktop\nfl-betting-systemv2\run_ui.bat
```

### 3. Use (25 seconds)
- Dashboard opens automatically at `http://localhost:8501`
- Start with **Dashboard** tab to see overview
- Move to **Top Props** to see high-confidence bets
- Try **Parlay Generator** for parlays
- Use **Query Props** for natural language analysis

## What You Get

| Tab | Purpose |
|-----|---------|
| 📊 Dashboard | Week overview & statistics |
| 🔍 Prop Analysis | Deep-dive single props |
| 🎯 Top Props | Best props by confidence |
| 🎰 Parlay Generator | Create 2/3/4/5-leg parlays |
| 💡 Query Props | Ask Claude about specific props |

## Key Features

✨ **5 Analysis Views** - Multiple perspectives on your data
🧠 **Claude Integration** - Natural language queries & dependency analysis
📊 **Real-time Charts** - Interactive Plotly visualizations
💾 **Export to CSV** - Download prop lists for Excel
⚡ **Fast Caching** - First load 2-3 min, then instant switching

## Sidebar Controls

All settings are in the left sidebar:
- **Week** (1-18) - Switch which week to analyze
- **Min Confidence** (40-100%) - Filter by threshold
- **Parlay Settings** - Control parlay generation
- **Dependency Analysis** - Enable Claude API correlation check

## Files Location

```
nfl-betting-systemv2/
├── ui/                          ← Your UI folder
│   ├── app.py                  ← Main dashboard (1200+ lines)
│   ├── requirements.txt         ← Dependencies to install
│   ├── README.md               ← Full documentation
│   └── SETUP.md                ← Configuration guide
├── run_ui.bat                   ← One-click launcher
├── UI_IMPLEMENTATION_SUMMARY.md ← Implementation details
└── ... (rest of your system)
```

## Common Commands

```bash
# Install dependencies
pip install -r ui/requirements.txt

# Run dashboard
streamlit run ui/app.py

# Use different port (if 8501 is busy)
streamlit run ui/app.py --server.port 8502

# Stop server
Ctrl + C (in terminal)

# Fresh install
pip install -r ui/requirements.txt --force-reinstall
```

## First-Time Setup

1. ✅ Verify `.env` has `ANTHROPIC_API_KEY`
2. ✅ Verify data files exist in `data/` directory
3. ✅ Install Streamlit: `pip install -r ui/requirements.txt`
4. ✅ Run dashboard: `streamlit run ui/app.py`
5. ✅ Open browser to `http://localhost:8501`

## Troubleshooting

**"Module not found"**
→ Run: `pip install -r ui/requirements.txt --force-reinstall`

**"No data for week"**
→ Check `data/` directory has files for that week

**"API key error"**
→ Verify `.env` has `ANTHROPIC_API_KEY=sk-ant-...`

**"Port 8501 in use"**
→ Run: `streamlit run ui/app.py --server.port 8502`

## Next Steps

1. **Explore**: Open each tab and see what you can do
2. **Analyze**: Use Top Props to find high-confidence bets
3. **Generate**: Create parlays and see confidence scores
4. **Export**: Download props to Excel for further analysis
5. **Query**: Ask Claude specific prop questions

## Documentation

- **Full User Guide**: `ui/README.md`
- **Configuration Guide**: `ui/SETUP.md`
- **Implementation Details**: `UI_IMPLEMENTATION_SUMMARY.md`

## Support

For issues:
1. Check `ui/README.md` troubleshooting section
2. Review `ui/SETUP.md` for configuration help
3. Check your `.env` file for API key
4. Verify data files exist in `data/` directory

---

**That's it!** You now have a professional betting analysis dashboard. 

Enjoy! 🏈📊🎯
