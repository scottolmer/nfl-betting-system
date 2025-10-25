"""
Slack Bot - Claude API Integration
Generates NFL parlays using Claude API
"""
import os
import sys
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from anthropic import Anthropic
import logging
from pathlib import Path
from dotenv import load_dotenv  # ← ADDED THIS

# Load .env file FIRST!
load_dotenv()  # ← ADDED THIS

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize clients (NOW these will read from .env)
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')

slack_client = WebClient(token=SLACK_BOT_TOKEN) if SLACK_BOT_TOKEN else None
claude_client = Anthropic(api_key=CLAUDE_API_KEY) if CLAUDE_API_KEY else None

# Load master prompt
PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "master_prompt_v2.0.md"

def load_master_prompt():
    """Load the master analysis prompt"""
    try:
        with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading prompt: {e}")
        return None

MASTER_PROMPT = load_master_prompt()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'claude_configured': CLAUDE_API_KEY is not None,
        'slack_configured': SLACK_BOT_TOKEN is not None
    })

@app.route('/slack/events', methods=['POST'])
def slack_events():
    """Handle Slack events"""
    data = request.json
    
    # URL verification
    if data.get('type') == 'url_verification':
        return jsonify({'challenge': data['challenge']})
    
    # Handle events
    if data.get('type') == 'event_callback':
        event = data.get('event', {})
        
        if event.get('type') == 'app_mention':
            handle_mention(event)
        elif event.get('type') == 'message' and event.get('channel_type') == 'im':
            handle_dm(event)
    
    return jsonify({'ok': True})

def handle_mention(event):
    """Handle @mentions"""
    channel = event.get('channel')
    text = event.get('text', '').lower()
    
    if 'analyze' in text or 'parlay' in text:
        slack_client.chat_postMessage(
            channel=channel,
            text="To analyze and generate parlays, use the `/analyze_week` command with your week number. Example: `/analyze_week 7`"
        )
    else:
        slack_client.chat_postMessage(
            channel=channel,
            text="👋 Hi! I can help you analyze NFL data and generate parlays. Use `/betting_help` to see all commands!"
        )

def handle_dm(event):
    """Handle direct messages"""
    channel = event.get('channel')
    text = event.get('text', '')
    
    slack_client.chat_postMessage(
        channel=channel,
        text=f"Got your message: {text}\n\nUse `/betting_help` to see available commands!"
    )

@app.route('/slack/commands', methods=['POST'])
def slack_commands():
    """Handle slash commands"""
    command = request.form.get('command')
    text = request.form.get('text', '')
    channel_id = request.form.get('channel_id')
    user_id = request.form.get('user_id')
    response_url = request.form.get('response_url')
    
    logger.info(f"Command received: {command} with text: {text}")
    
    if command == '/betting_help':
        return handle_help_command()
    
    elif command == '/analyze_week':
        return handle_analyze_command(text, channel_id, response_url)
    
    elif command == '/week_summary':
        return handle_summary_command(text)
    
    elif command == '/enter_results':
        return handle_results_command(text)
    
    else:
        return jsonify({
            'response_type': 'ephemeral',
            'text': f'Unknown command: {command}'
        })

def handle_help_command():
    """Show help message"""
    help_text = """*🏈 NFL Betting Bot - Commands*

*Available Commands:*
• `/betting_help` - Show this help message
• `/analyze_week [number]` - Generate parlays for a week (requires CSV data)
• `/week_summary [number]` - View results summary
• `/enter_results [number]` - Enter game results

*How to Use:*
1. Upload your weekly CSV files to the data folder
2. Run `/analyze_week 7` to generate 6 parlays
3. Review the parlays with confidence scores
4. After games, use `/enter_results 7` to track accuracy

*Claude API Status:* """ + ("✅ Connected" if CLAUDE_API_KEY else "❌ Not configured") + """

*Need Help?*
- Make sure your .env file has CLAUDE_API_KEY
- Upload CSV files to: data/weekly_data/
- Check logs if analysis fails

_Tip: You can also use Claude Projects at claude.ai for a simpler workflow!_
"""
    
    return jsonify({
        'response_type': 'ephemeral',
        'text': help_text
    })

def handle_analyze_command(week_text, channel_id, response_url):
    """Generate parlays using Claude API"""
    
    # Check if Claude is configured
    if not claude_client:
        return jsonify({
            'response_type': 'ephemeral',
            'text': '❌ Claude API not configured. Add CLAUDE_API_KEY to your .env file.'
        })
    
    if not MASTER_PROMPT:
        return jsonify({
            'response_type': 'ephemeral',
            'text': '❌ Master prompt not found. Check that prompts/master_prompt_v2.0.md exists.'
        })
    
    # Parse week number
    try:
        week = int(week_text) if week_text else 7
    except:
        return jsonify({
            'response_type': 'ephemeral',
            'text': '❌ Invalid week number. Usage: `/analyze_week 7`'
        })
    
    # Send immediate response
    slack_client.chat_postMessage(
        channel=channel_id,
        text=f"🔄 Analyzing Week {week}... This may take 30-60 seconds."
    )
    
    # Check for data files
    data_dir = Path(__file__).parent.parent.parent / "data" / "weekly_data"
    csv_files = list(data_dir.glob(f"wk{week}_*.csv"))
    
    if not csv_files:
        slack_client.chat_postMessage(
            channel=channel_id,
            text=f"❌ No data files found for Week {week}.\n\nPlease upload CSV files to: `data/weekly_data/wk{week}_*.csv`"
        )
        return jsonify({'ok': True})
    
    # Load CSV data
    try:
        data_summary = f"Found {len(csv_files)} data files for Week {week}:\n"
        for f in csv_files:
            data_summary += f"- {f.name}\n"
        
        # For now, send a simplified request to Claude
        message = f"""{MASTER_PROMPT}

---

# WEEK {week} ANALYSIS REQUEST

I have {len(csv_files)} CSV data files for Week {week}.

Since I cannot directly pass CSV file contents in this Slack integration, please provide:

1. A sample 6-parlay output format
2. Instructions for how to properly analyze the data
3. Key factors to consider for Week {week}

Note: For full analysis, the user should upload CSV files directly to Claude Projects.
"""
        
        # Call Claude API
        logger.info(f"Calling Claude API for Week {week}")
        
        response = claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            temperature=0.3,
            messages=[{"role": "user", "content": message}]
        )
        
        result = response.content[0].text
        
        # Send result to Slack (truncate if too long)
        if len(result) > 3000:
            result = result[:3000] + "\n\n... (truncated - full analysis too long for Slack)"
        
        slack_client.chat_postMessage(
            channel=channel_id,
            text=f"*Week {week} Analysis:*\n\n{result}\n\n_For full analysis with your CSV data, use Claude Projects at claude.ai_"
        )
        
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        slack_client.chat_postMessage(
            channel=channel_id,
            text=f"❌ Analysis failed: {str(e)}"
        )
    
    return jsonify({'ok': True})

def handle_summary_command(week_text):
    """Show week summary"""
    try:
        week = int(week_text) if week_text else 7
    except:
        week = 7
    
    # Check for results file
    results_path = Path(__file__).parent.parent.parent / "data" / "results_tracking" / f"wk{week}_actual_results.csv"
    
    if not results_path.exists():
        return jsonify({
            'response_type': 'ephemeral',
            'text': f'❌ No results found for Week {week}.\n\nUse `/enter_results {week}` to enter results first.'
        })
    
    try:
        import pandas as pd
        df = pd.read_csv(results_path)
        
        total = len(df)
        hits = df['hit'].sum() if 'hit' in df.columns else 0
        accuracy = (hits / total * 100) if total > 0 else 0
        
        summary = f"""*📊 Week {week} Results Summary*

Total Legs: {total}
Hits: {int(hits)} ({accuracy:.1f}%)
Misses: {int(total - hits)}

View detailed results in: `results/wk{week}_parlays.json`
"""
        
        return jsonify({
            'response_type': 'in_channel',
            'text': summary
        })
    except Exception as e:
        return jsonify({
            'response_type': 'ephemeral',
            'text': f'❌ Error loading results: {str(e)}'
        })

def handle_results_command(week_text):
    """Handle enter results command"""
    try:
        week = int(week_text) if week_text else 7
    except:
        week = 7
    
    return jsonify({
        'response_type': 'ephemeral',
        'text': f"""*📝 Enter Results for Week {week}*

To enter results:
1. Go to: `data/results_tracking/wk{week}_actual_results.csv`
2. Fill in the 'actual_value' and 'hit' columns
3. Run calibration: `python scripts/calibration/calibration_main.py`

Or use the auto-fetch feature (coming soon) to pull stats from ESPN automatically!
"""
    })

@app.route('/slack/interactions', methods=['POST'])
def slack_interactions():
    """Handle interactive components"""
    return jsonify({'ok': True})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    
    logger.info("=" * 60)
    logger.info("NFL BETTING BOT - CLAUDE API EDITION")
    logger.info("=" * 60)
    logger.info(f"Claude API: {'✅ Configured' if CLAUDE_API_KEY else '❌ Not configured'}")
    logger.info(f"Slack API: {'✅ Configured' if SLACK_BOT_TOKEN else '❌ Not configured'}")
    logger.info(f"Master Prompt: {'✅ Loaded' if MASTER_PROMPT else '❌ Not found'}")
    logger.info(f"Starting on port {port}")
    logger.info("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=False)
