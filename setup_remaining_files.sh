#!/bin/bash

# NFL Betting System - Complete Setup Script
# This script creates all remaining code files

echo "🏈 Setting up NFL Betting System..."
echo ""

BASE_DIR="/Users/scott/Desktop/nfl-betting-system"
cd "$BASE_DIR"

# ============================================================================
# MASTER PROMPT
# ============================================================================

echo "📝 Creating master prompt..."

cat > prompts/master_prompt_v2.0.md << 'EOF'
# NFL PLAYER PROP BETTING ANALYSIS SYSTEM
Version: 2.0 | Updated: October 2025

You are an elite NFL betting analyst specializing in player prop analysis for DraftKings Pick-6 parlays. Your role is to evaluate weekly NFL data and construct high-confidence, +EV parlay recommendations using a rigorous 5-factor analytical framework.

## PRIMARY OBJECTIVE

Analyze uploaded weekly NFL data (player stats, defensive rankings, betting lines, injuries, weather) and output **6 parlays** (2-leg through 6-leg configurations) with detailed confidence scoring and rationale.

---

## ANALYTICAL FRAMEWORK: 5-FACTOR MODEL

Every player prop evaluation MUST incorporate these 5 factors:

### FACTOR 1: DEFENSIVE MATCHUP (Weight: 25%)
- Opponent's defensive ranking vs position (DVOA data)
- Yards/points allowed to position (last 4 weeks)
- Top-10 matchup: +15 confidence
- Bottom-10 defense: -5 to -10 confidence

### FACTOR 2: RECENT PERFORMANCE TREND (Weight: 20%)
- Last 3-4 game performance vs prop line
- Hit line in 3 of last 4: +12 confidence
- Trending up: +5 bonus

### FACTOR 3: USAGE TRENDS (Weight: 20%)
- Snap percentage, target/touch share
- Snap% ≥ 80%: +10 confidence
- Recent role expansion: +5 bonus

### FACTOR 4: GAME ENVIRONMENT (Weight: 15%)
- Game total ≥ 48 points: +8 confidence
- Weather/venue adjustments: -5 to +2

### FACTOR 5: INJURY CONTEXT & LINE VALUE (Weight: 20%)
- Key teammate injuries: +8 confidence
- EV ≥ 10%: +10 confidence

## CONFIDENCE SCORING

Base = 50, add factors, cap at 85
- 75-85: Elite
- 65-74: High  
- 55-64: Moderate
- 50-54: Low
- <50: Avoid

## PARLAY SPECIFICATIONS

Output 6 parlays:
1. 2-LEG (High Confidence) - 70+ combined confidence
2. 3-LEG (Balanced) - 60+ combined confidence
3. 3-LEG (Game Stack) - 60+ combined confidence
4. 4-LEG (Volume) - 50+ combined confidence
5. 5-LEG (Game Total) - 45+ combined confidence
6. 6-LEG (Max Upside) - 40+ combined confidence

## OUTPUT FORMAT

For each parlay provide:
- Configuration & confidence
- Each leg with: Player, Prop, Line, Projection, Confidence, Rationale
- Exposure analysis
- Top 5 standalone plays
- Line movement notes

## CRITICAL RULES
- Never quote exact text from sources
- Be conservative (70+ rare)
- Show EV calculations
- No guarantees or "locks"
- Max 2 parlays per player
EOF

echo "✅ Master prompt created"

# ============================================================================
# DEPLOYMENT GUIDE
# ============================================================================

echo "📖 Creating deployment guide..."

cat > docs/DEPLOYMENT.md << 'EOF'
# NFL Betting System - Deployment Guide

## Prerequisites
- Docker and Docker Compose installed
- Slack workspace (admin access)
- Claude API key
- GitHub personal access token

## Step 1: Configure Environment

```bash
cd /Users/scott/Desktop/nfl-betting-system
cp .env.example .env
nano .env
```

Fill in:
- CLAUDE_API_KEY
- GITHUB_TOKEN (from github.com/settings/tokens)
- GITHUB_REPOSITORY=scottolmer/nfl-betting-system
- SLACK_BOT_TOKEN (from api.slack.com/apps)
- SLACK_SIGNING_SECRET

## Step 2: Build Docker Containers

```bash
cd docker
docker-compose build
```

## Step 3: Start Services

```bash
docker-compose up -d
```

Check status:
```bash
docker-compose ps
docker-compose logs -f
```

## Step 4: Configure Slack App

1. Go to api.slack.com/apps
2. Create new app: "NFL Betting Bot"
3. Add OAuth scopes: chat:write, commands, app_mentions:read
4. Install to workspace
5. Copy Bot Token → SLACK_BOT_TOKEN in .env

## Step 5: Expose to Internet

For testing:
```bash
brew install ngrok
ngrok http 3000
```

Copy https URL and set in Slack app:
- Event URL: https://YOUR-URL.ngrok.io/slack/events
- Interactive URL: https://YOUR-URL.ngrok.io/slack/interactions
- Command URL: https://YOUR-URL.ngrok.io/slack/commands

## Step 6: Test

In Slack:
```
/betting_help
```

Should receive help message!

## Updating

```bash
git pull
docker-compose down
docker-compose up -d --build
```
EOF

echo "✅ Deployment guide created"

# ============================================================================
# QUICK START GUIDE
# ============================================================================

cat > docs/QUICKSTART.md << 'EOF'
# Quick Start Guide

## 1. First Time Setup (30 minutes)

```bash
# Fill in .env file
cp .env.example .env
nano .env

# Build and start
cd docker
docker-compose up -d

# Check logs
docker-compose logs -f
```

## 2. Weekly Workflow

### Monday: Upload Data
```bash
# Add your CSV files to data/weekly_data/
cp ~/Downloads/wk7_*.csv data/weekly_data/
```

### Tuesday: Generate Parlays

Option A - Manual (use Claude Projects):
1. Go to claude.ai
2. Upload CSVs + master prompt
3. Get 6 parlays

Option B - Automated (if GitHub Actions configured):
- Runs automatically Tuesday 10 AM
- Check results/ folder for output

### Wednesday: Enter Results

In Slack:
```
/enter_results 7
```

Click "Auto-Fetch" to pull stats from ESPN.

### Thursday: Review Calibration

GitHub Actions runs calibration automatically.
Check results/calibration/ for accuracy report.

## 3. Manual Commands

```bash
# Run weekly analysis manually
python scripts/core/main.py

# Fetch results manually  
python scripts/stats_scraping/auto_populate_results.py

# Run calibration
python scripts/calibration/calibration_main.py
```

## 4. Monitoring

```bash
# View Slack bot logs
docker-compose logs -f slack-bot

# View line monitor logs
docker-compose logs -f line-monitor

# Check health
curl http://localhost:3000/health
```
EOF

echo "✅ Quick start guide created"

# ============================================================================
# FINALIZE
# ============================================================================

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 NEXT STEPS:"
echo ""
echo "1. Fill in your .env file:"
echo "   nano .env"
echo ""
echo "2. Get your API keys:"
echo "   - Claude: console.anthropic.com"
echo "   - GitHub: github.com/settings/tokens"
echo "   - Slack: api.slack.com/apps"
echo ""
echo "3. Read the deployment guide:"
echo "   open docs/DEPLOYMENT.md"
echo ""
echo "4. Start the system:"
echo "   cd docker && docker-compose up -d"
echo ""
echo "🎉 You're ready to go!"
