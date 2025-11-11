================================================================================
GITHUB SETUP GUIDE - NFL BETTING SYSTEM
================================================================================

STEP 1: CREATE GITHUB ACCOUNT (if needed)
==========================================

1. Go to https://github.com/signup
2. Create account with email, password, username
3. Verify email
4. Done!


STEP 2: CREATE NEW REPOSITORY ON GITHUB
========================================

1. Log in to GitHub (https://github.com)
2. Click + icon (top right) → "New repository"
3. Fill in:
   - Repository name: nfl-betting-system
   - Description: "Sophisticated NFL betting system with DraftKings Pick 6 
                   optimization, multi-agent analysis framework (DVOA, Matchup, 
                   Injury, Volume, GameScript, Trend, Variance, Weather), and 
                   parlay optimization with dependency analysis"
   - Public or Private: Choose based on preference
   - Check "Add a README file" ✓
   - Check "Add .gitignore" ✓ (choose Python)
   - License: MIT (optional but recommended)
4. Click "Create repository"
5. You'll see the repository page


STEP 3: CLONE REPOSITORY TO YOUR COMPUTER
==========================================

On your Windows machine, open PowerShell and run:

```powershell
cd Desktop
git clone https://github.com/YOUR_USERNAME/nfl-betting-system.git
cd nfl-betting-system
```

Replace YOUR_USERNAME with your actual GitHub username!


STEP 4: COPY YOUR PROJECT INTO THE CLONED REPO
===============================================

Option A: Copy files manually (easiest)
1. Open File Explorer
2. Navigate to: C:\Users\scott\Desktop\nfl-betting-system (the new cloned folder)
3. Open another File Explorer window at: C:\Users\scott\Desktop\nfl-betting-systemv2
4. Copy ALL files from v2 folder EXCEPT:
   - .git folder (keep it in the clone, don't copy from v2)
   - __pycache__ folders
   - *.pyc files
   - venv or virtual environment folders
5. Paste into the cloned folder (overwrite if needed)

Option B: Command line (more powerful)
```powershell
# From inside the cloned nfl-betting-system folder:
cp -r C:\Users\scott\Desktop\nfl-betting-systemv2\* . -Force -Exclude .git,__pycache__,venv
```


STEP 5: CONFIGURE GIT USER (ONE TIME)
=====================================

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Or per-project only (recommended):
```powershell
git config user.name "Your Name"
git config user.email "your.email@example.com"
```


STEP 6: CREATE .gitignore FILE
==============================

Create a file named .gitignore in your project root:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
*.egg-info/
.eggs/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Sensitive files
.env
.env.local
secrets.json
credentials.json

# Data files (optional - remove if you want to commit data)
data/wk*.csv
data/betting_history/
*.db

# Logs
logs/
*.log

# Cache
.cache/
.pytest_cache/

# OS
.DS_Store
Thumbs.db

# Virtual environments
venv/
ENV/
env/

# IDE
.vscode/
.idea/
```


STEP 7: CHECK WHAT WILL BE COMMITTED
====================================

```powershell
git status
```

This shows:
- Green (added): Files that will be committed
- Red (untracked): Files NOT being committed
- Make sure sensitive files (.env, *.db with secrets) are NOT in green

If you see .env or bets.db in red, that's GOOD (they're ignored)


STEP 8: ADD FILES TO STAGING
=============================

```powershell
# Add all files (respecting .gitignore)
git add .

# Or see what you're adding first:
git status
```


STEP 9: CREATE FIRST COMMIT
============================

```powershell
git commit -m "Initial commit: NFL betting system with multi-agent analysis framework"
```

Or more detailed:

```powershell
git commit -m "Initial commit: NFL betting system

- Multi-agent analysis framework (8 agents: DVOA, Matchup, Injury, Volume, GameScript, Trend, Variance, Weather)
- DraftKings Pick 6 parlay optimization
- Dependency analysis for correlation detection
- Kelly Criterion position sizing
- Performance tracking and calibration
- Live betting lines integration
- RotoWire injury data scraping
- Comprehensive CLI and GUI interfaces
"
```


STEP 10: PUSH TO GITHUB
=======================

```powershell
git branch -M main
git push -u origin main
```

This pushes everything to GitHub!

Your repository is now on GitHub! 🎉


STEP 11: CREATE README.md
=========================

Create/update README.md in your project root:

```markdown
# NFL Betting System 🏈

Sophisticated betting system for DraftKings Pick 6 contests with multi-agent 
analysis framework and automated parlay optimization.

## Features

### 8-Agent Analysis Framework
- **DVOA**: Offensive/defensive efficiency ratings
- **Matchup**: Head-to-head situational analysis
- **Injury**: Real-time injury report integration
- **Volume**: Usage statistics and snap counts
- **GameScript**: Game flow and pace analysis
- **Trend**: Historical performance patterns
- **Variance**: Volatility and consistency metrics
- **Weather**: Environmental impact analysis

### Advanced Optimization
- Dependency analysis for correlation detection
- Kelly Criterion position sizing
- Low-correlation parlay building
- Player exposure management
- Automated performance tracking

### Data Integration
- Live DraftKings betting lines
- Real-time RotoWire injury data
- DVOA ratings and team statistics
- Historical performance data

### Interfaces
- Command-line CLI (betting_cli.py)
- Interactive GUI (Streamlit dashboard)
- Slack bot integration
- Web dashboard

## Quick Start

### Setup
```bash
pip install -r requirements.txt
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
```

### Run Analysis
```bash
python betting_cli.py
```

### Generate Parlays
```
📊 Enter command: parlays
📊 Enter command: opt-parlays
```

### Check Injury System
```
📊 Enter command: injury-diagnostic
📊 Enter command: injury-diagnostic swift
```

## Project Structure
- `scripts/analysis/` - Core analysis engines
- `scripts/analysis/agents/` - 8 individual agents
- `data/` - CSV data files and betting lines
- `betting_cli.py` - Main command-line interface
- `run.py` - Alternative CLI runner

## Configuration
Update `.env` with:
- `ANTHROPIC_API_KEY` - For Claude API integration
- `NFL_WEEK` - Current NFL week

## Performance Tracking
All parlays are automatically logged to `bets.db` for:
- Win/loss tracking
- Agent calibration analysis
- Historical performance trends

## Latest Updates
- Injury Agent now with granular penalties (QUESTIONABLE=50pt, PROBABLE=30pt)
- Injury diagnostic command for system validation
- 8-agent orchestration fully integrated
- Live odds integration with DraftKings API fallback

## Author
Scott Olmer

## License
MIT
```


UPDATING AND PUSHING CHANGES
=============================

After making changes locally:

```powershell
# See what changed
git status

# Stage changes
git add .

# Commit with message
git commit -m "Update: Added injury diagnostic command to betting CLI"

# Push to GitHub
git push
```

Quick commands:
```powershell
git add .
git commit -m "Your message here"
git push
```


TROUBLESHOOTING
===============

Problem: "fatal: Not a git repository"
Solution: Make sure you're in the right directory
```powershell
cd C:\Users\scott\Desktop\nfl-betting-system
```

Problem: "Authentication failed" when pushing
Solution: GitHub requires token, not password
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token (select: repo, read:user, gist)
3. Copy token
4. When Git asks for password, paste the token

Problem: ".env file is showing in git"
Solution: Make sure .gitignore has .env and run:
```powershell
git rm --cached .env
git commit -m "Remove .env from tracking"
git push
```

Problem: "bets.db showing in git"
Solution: Same as above
```powershell
git rm --cached bets.db
git commit -m "Remove database from tracking"
git push
```


BEST PRACTICES
==============

1. Commit frequently (not just once)
   - Logical chunks of work
   - Clear commit messages
   - Easy to revert if needed

2. Use descriptive commit messages
   - Bad: "update stuff"
   - Good: "Fix injury agent weight calculation and add diagnostic command"

3. Never commit secrets
   - .env files
   - API keys
   - Database backups with sensitive data
   - Use .gitignore!

4. Push regularly
   - Backup your work
   - Easy to collaborate
   - GitHub is the source of truth

5. Create branches for features
   ```powershell
   git checkout -b feature/injury-diagnostics
   # Make changes
   git add .
   git commit -m "Add injury diagnostic system"
   git push -u origin feature/injury-diagnostics
   # Then create Pull Request on GitHub to merge to main
   ```


NEXT STEPS
==========

After pushing:
1. Go to your GitHub repo: https://github.com/YOUR_USERNAME/nfl-betting-system
2. Verify all files are there
3. Update README.md if needed
4. Add topics: betting, nfl, sports-analytics, machine-learning
5. Consider making it a "template repository" if others want to fork it
6. Star it if you like it! ⭐


SHARING WITH OTHERS
====================

To share your repo:
1. GitHub URL: https://github.com/YOUR_USERNAME/nfl-betting-system
2. If Private: Add collaborators in Settings → Collaborators
3. If Public: Anyone can clone and use it

```bash
git clone https://github.com/YOUR_USERNAME/nfl-betting-system.git
cd nfl-betting-system
pip install -r requirements.txt
```

================================================================================
