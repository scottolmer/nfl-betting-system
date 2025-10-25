#!/bin/bash

# NFL Betting System - Quick Setup
# Run this to get started in 5 minutes

clear
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║        🏈  NFL BETTING ANALYSIS SYSTEM  🏈                 ║"
echo "║                                                            ║"
echo "║                    Quick Setup                             ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Change to project directory
cd /Users/scott/Desktop/nfl-betting-system

echo "📍 Current location: $(pwd)"
echo ""

# Step 1: Generate code files
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Generating Python code files..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 generate_code.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Environment Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  YOU MUST EDIT .env AND ADD YOUR API KEYS!"
    echo ""
    echo "   Required:"
    echo "   - CLAUDE_API_KEY (get from console.anthropic.com)"
    echo "   - GITHUB_TOKEN (get from github.com/settings/tokens)"
    echo "   - GITHUB_REPOSITORY=scottolmer/nfl-betting-system"
    echo ""
    echo "   Optional:"
    echo "   - SLACK_BOT_TOKEN (for Slack integration)"
    echo "   - BETTING_API_KEY (for line monitoring)"
    echo ""
    read -p "Press ENTER when you've filled in .env, or Ctrl+C to exit..."
else
    echo "✅ .env file already exists"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Testing Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 scripts/core/main.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ SETUP COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 WHAT'S READY:"
echo ""
echo "   ✅ Complete directory structure"
echo "   ✅ All Python modules"
echo "   ✅ Docker configuration"
echo "   ✅ Master analysis prompt"
echo "   ✅ Documentation"
echo ""
echo "🎯 CHOOSE YOUR PATH:"
echo ""
echo "   🟢 OPTION 1: Simple (Recommended)"
echo "      Use Claude Projects - no code needed"
echo "      Time: 15 min/week | Cost: $20/month"
echo ""
echo "      → Read: docs/QUICKSTART.md"
echo ""
echo "   🔵 OPTION 2: Full Automation"
echo "      Deploy complete system with Docker"
echo "      Time: 5 min/week | Cost: $50/month"
echo ""
echo "      → Read: docs/DEPLOYMENT.md"
echo "      → Then run: cd docker && docker-compose up -d"
echo ""
echo "📖 DOCUMENTATION:"
echo ""
echo "   • README.md         - System overview"
echo "   • STATUS.md         - Current setup status"
echo "   • docs/DEPLOYMENT.md - Full deployment guide"
echo "   • docs/QUICKSTART.md - Weekly workflow guide"
echo ""
echo "🚀 QUICK START:"
echo ""
echo "   For testing with Claude Projects:"
echo "   1. Go to claude.ai"
echo "   2. Create new Project: 'NFL Betting'"
echo "   3. Upload prompts/master_prompt_v2.0.md"
echo "   4. Upload your weekly CSV files"
echo "   5. Ask: 'Analyze Week 7'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
