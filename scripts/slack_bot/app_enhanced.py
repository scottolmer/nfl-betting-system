"""
Enhanced Slack Bot - Integrated with Multi-Agent Analysis System

Combines:
- Original Slack bot commands
- New 8-agent prop analysis
- Confidence scoring
- Parlay building
- Line movement monitoring
"""

import os
import sys
from pathlib import Path
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.parlay_builder import ParlayBuilder
from scripts.api.odds_api import OddsAPI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Slack app
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Initialize analysis system
data_loader = NFLDataLoader(data_dir=str(project_root / "data"))
prop_analyzer = PropAnalyzer()
parlay_builder = ParlayBuilder()

# ============================================================================
# COMMAND: /analyze_props - Multi-Agent Analysis
# ============================================================================

@app.command("/analyze_props")
def analyze_props_command(ack, say, command):
    """Analyze props using 8-agent system with confidence scoring"""
    ack()
    
    try:
        # Get week from command text or use default
        week = int(command.get('text', os.environ.get('NFL_WEEK', 7)))
        
        say(f"🧠 Analyzing Week {week} props using 8-agent system...")
        
        # Load all data
        context = data_loader.load_all_data(week=week)
        
        # Analyze all props
        all_analyses = prop_analyzer.analyze_all_props(context, min_confidence=60)
        
        # Get top 10 highest confidence
        top_props = sorted(all_analyses, key=lambda x: x.final_confidence, reverse=True)[:10]
        
        # Format response
        response = f"*🎯 TOP 10 PROPS - WEEK {week}*\n\n"
        
        for i, analysis in enumerate(top_props, 1):
            prop = analysis.prop
            conf = analysis.final_confidence
            
            # Confidence emoji
            if conf >= 75:
                emoji = "🔥"
            elif conf >= 70:
                emoji = "⭐"
            elif conf >= 65:
                emoji = "✅"
            else:
                emoji = "📊"
            
            response += f"{emoji} *{i}. {prop.player_name}* ({prop.team})\n"
            response += f"   {prop.stat_type} OVER {prop.line}\n"
            response += f"   Confidence: *{conf}* | vs {prop.opponent}\n"
            
            # Top 2 reasons
            if analysis.rationale:
                response += f"   • {analysis.rationale[0]}\n"
                if len(analysis.rationale) > 1:
                    response += f"   • {analysis.rationale[1]}\n"
            response += "\n"
        
        response += f"\n💡 _Analyzed {len(all_analyses)} total props_"
        
        say(response)
        
    except Exception as e:
        logger.error(f"Error in analyze_props: {e}")
        say(f"❌ Error analyzing props: {str(e)}")


# ============================================================================
# COMMAND: /build_parlays - Parlay Generation
# ============================================================================

@app.command("/build_parlays")
def build_parlays_command(ack, say, command):
    """Build optimal parlays using correlation strategies"""
    ack()
    
    try:
        week = int(command.get('text', os.environ.get('NFL_WEEK', 7)))
        
        say(f"🎯 Building optimal parlays for Week {week}...")
        
        # Load and analyze
        context = data_loader.load_all_data(week=week)
        all_analyses = prop_analyzer.analyze_all_props(context, min_confidence=60)
        
        # Diversify props
        diversified = diversify_props(all_analyses)
        
        # Build parlays
        parlays = parlay_builder.build_parlays(diversified, min_confidence=65)
        
        # Format response
        response = f"*🎰 WEEK {week} PARLAYS*\n\n"
        
        for parlay_type in ['2-leg', '3-leg', '4-leg']:
            parlay_list = parlays.get(parlay_type, [])
            
            if parlay_list:
                response += f"*{parlay_type.upper()} PARLAYS:*\n"
                
                for i, parlay in enumerate(parlay_list, 1):
                    response += f"\n*Parlay {i}* - {parlay.risk_level} RISK (Conf: {parlay.combined_confidence})\n"
                    response += f"💰 Bet: {parlay.recommended_units} units\n"
                    
                    for j, leg in enumerate(parlay.legs, 1):
                        response += f"  {j}. {leg['player']} - {leg['stat']} {leg['pick']} {leg['line']}\n"
                
                response += "\n"
        
        # Calculate total units
        total_units = sum(
            parlay.recommended_units 
            for parlay_list in parlays.values() 
            for parlay in parlay_list
        )
        
        response += f"💸 *Total Investment:* {total_units:.1f} units (${total_units * 10:.0f} @ $10/unit)\n"
        
        say(response)
        
    except Exception as e:
        logger.error(f"Error in build_parlays: {e}")
        say(f"❌ Error building parlays: {str(e)}")


# ============================================================================
# COMMAND: /check_confidence - Player Confidence Check
# ============================================================================

@app.command("/check_confidence")
def check_confidence_command(ack, say, command):
    """Check confidence for specific player props"""
    ack()
    
    try:
        player_name = command.get('text', '').strip()
        
        if not player_name:
            say("❌ Please provide a player name: `/check_confidence Justin Jefferson`")
            return
        
        week = int(os.environ.get('NFL_WEEK', 7))
        
        say(f"🔍 Checking confidence for *{player_name}* (Week {week})...")
        
        # Load and analyze
        context = data_loader.load_all_data(week=week)
        all_analyses = prop_analyzer.analyze_all_props(context, min_confidence=50)
        
        # Filter by player
        player_props = [
            a for a in all_analyses 
            if player_name.lower() in a.prop.player_name.lower()
        ]
        
        if not player_props:
            say(f"❌ No props found for '{player_name}'")
            return
        
        # Format response
        response = f"*📊 {player_props[0].prop.player_name}* ({player_props[0].prop.team})\n\n"
        
        for analysis in sorted(player_props, key=lambda x: x.final_confidence, reverse=True):
            prop = analysis.prop
            conf = analysis.final_confidence
            
            # Confidence level
            if conf >= 75:
                level = "🔥 ELITE"
            elif conf >= 70:
                level = "⭐ HIGH"
            elif conf >= 65:
                level = "✅ GOOD"
            elif conf >= 60:
                level = "📊 MODERATE"
            else:
                level = "⚠️ LOW"
            
            response += f"{level} | *{prop.stat_type} OVER {prop.line}*\n"
            response += f"Confidence: *{conf}* | vs {prop.opponent}\n"
            
            # Show all reasons
            for reason in analysis.rationale[:3]:
                response += f"  • {reason}\n"
            
            response += "\n"
        
        say(response)
        
    except Exception as e:
        logger.error(f"Error in check_confidence: {e}")
        say(f"❌ Error checking confidence: {str(e)}")


# ============================================================================
# COMMAND: /line_movement - Show Recent Movements
# ============================================================================

@app.command("/line_movement")
def line_movement_command(ack, say, command):
    """Show recent line movements (integrates with line monitor)"""
    ack()
    
    try:
        import pandas as pd
        
        movement_file = project_root / "data" / "lines" / "line_movements_log.csv"
        
        if not movement_file.exists():
            say("❌ No line movement data found. Is the monitor running?")
            return
        
        # Load recent movements
        df = pd.read_csv(movement_file)
        
        # Get last 10 movements
        recent = df.tail(10)
        
        response = "*📈 RECENT LINE MOVEMENTS*\n\n"
        
        for _, row in recent.iterrows():
            movement_type = row.get('movement_type', 'Unknown')
            description = row.get('description', 'N/A')
            timestamp = row.get('timestamp', '')
            
            response += f"• {description}\n"
            response += f"  _{timestamp}_\n\n"
        
        say(response)
        
    except Exception as e:
        logger.error(f"Error in line_movement: {e}")
        say(f"❌ Error retrieving line movements: {str(e)}")


# ============================================================================
# COMMAND: /betting_help - Show All Commands
# ============================================================================

@app.command("/betting_help")
def help_command(ack, say):
    """Show all available commands"""
    ack()
    
    help_text = """
*🏈 NFL BETTING SYSTEM COMMANDS*

*📊 Analysis Commands:*
• `/analyze_props [week]` - Analyze props with 8-agent system
• `/check_confidence [player]` - Check confidence for player
• `/build_parlays [week]` - Generate optimal parlays

*📈 Monitoring Commands:*
• `/line_movement` - Show recent line movements
• `/fetch_odds [week]` - Fetch latest odds from API

*ℹ️ Info Commands:*
• `/betting_help` - Show this help message
• `/system_status` - Check system status

*💡 Examples:*
```
/analyze_props 7
/check_confidence Justin Jefferson
/build_parlays 8
/line_movement
```

*🎯 Confidence Levels:*
• 🔥 75+ = ELITE (max bet)
• ⭐ 70-74 = HIGH (strong bet)
• ✅ 65-69 = GOOD (standard bet)
• 📊 60-64 = MODERATE (small bet)
• ⚠️ <60 = LOW (pass)
"""
    
    say(help_text)


# ============================================================================
# COMMAND: /fetch_odds - Fetch Latest Odds
# ============================================================================

@app.command("/fetch_odds")
def fetch_odds_command(ack, say, command):
    """Fetch latest odds from The Odds API"""
    ack()
    
    try:
        week = int(command.get('text', os.environ.get('NFL_WEEK', 7)))
        
        say(f"📡 Fetching latest odds for Week {week}...")
        
        api = OddsAPI()
        
        # Check quota
        quota = api.check_api_quota()
        say(f"📊 API Quota - Remaining: {quota['remaining']}, Used: {quota['used']}")
        
        # Fetch props
        props = api.get_player_props(
            markets='player_pass_yds,player_reception_yds,player_rush_yds,'
                   'player_receptions,player_pass_tds'
        )
        
        if props:
            # Save to CSV
            import pandas as pd
            df = pd.DataFrame(props)
            output_file = project_root / "data" / f"betting_lines_wk_{week}_live.csv"
            df.to_csv(output_file, index=False)
            
            say(f"✅ Fetched {len(props)} props and saved to database")
            
            # Show sample
            sample = df.sample(min(5, len(df)))
            response = "\n*Sample Props:*\n"
            for _, row in sample.iterrows():
                response += f"• {row['player_name']}: {row['stat_type']} {row['direction']} {row['line']}\n"
            
            say(response)
        else:
            say("⚠️ No props fetched from API")
        
    except Exception as e:
        logger.error(f"Error fetching odds: {e}")
        say(f"❌ Error fetching odds: {str(e)}")


# ============================================================================
# COMMAND: /system_status - System Health Check
# ============================================================================

@app.command("/system_status")
def system_status_command(ack, say):
    """Check system status"""
    ack()
    
    status = "*🔧 SYSTEM STATUS*\n\n"
    
    # Check data files
    data_dir = project_root / "data"
    week = int(os.environ.get('NFL_WEEK', 7))
    
    required_files = [
        f"DVOA_Off_wk_{week}.csv",
        f"DVOA_Def_wk_{week}.csv",
        f"Def_vs_WR_wk_{week}.csv",
        f"NFL_Projections_Wk_{week}_updated.csv"
    ]
    
    status += "*📁 Data Files:*\n"
    for file in required_files:
        file_path = data_dir / file
        if file_path.exists():
            status += f"✅ {file}\n"
        else:
            status += f"❌ {file}\n"
    
    # Check API
    status += "\n*🔑 API Status:*\n"
    try:
        api = OddsAPI()
        quota = api.check_api_quota()
        status += f"✅ The Odds API - {quota['remaining']} requests remaining\n"
    except:
        status += "❌ The Odds API - Not configured\n"
    
    # Check line monitor
    movement_file = project_root / "data" / "lines" / "line_movements_log.csv"
    if movement_file.exists():
        status += "✅ Line Monitor - Active\n"
    else:
        status += "⚠️ Line Monitor - No data\n"
    
    status += f"\n*📅 Current Week:* {week}\n"
    
    say(status)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def diversify_props(all_analyses):
    """Diversify props across games for parlay variety"""
    games = {}
    for analysis in all_analyses:
        game = f"{analysis.prop.team} vs {analysis.prop.opponent}"
        if game not in games:
            games[game] = []
        games[game].append(analysis)
    
    # Sort each game's props
    for game in games:
        games[game].sort(key=lambda x: x.final_confidence, reverse=True)
    
    # Round-robin selection
    diversified = []
    max_rounds = max(len(props) for props in games.values())
    
    for round_num in range(max_rounds):
        for game, props in sorted(games.items(), key=lambda x: len(x[1]), reverse=True):
            if round_num < len(props):
                diversified.append(props[round_num])
    
    return diversified


# ============================================================================
# START APPLICATION
# ============================================================================

if __name__ == "__main__":
    logger.info("🏈 Starting Enhanced NFL Betting Slack Bot...")
    logger.info(f"📅 Current Week: {os.environ.get('NFL_WEEK', 7)}")
    logger.info("✅ Multi-agent analysis integrated")
    logger.info("✅ Parlay builder integrated")
    logger.info("✅ The Odds API integrated")
    
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()
