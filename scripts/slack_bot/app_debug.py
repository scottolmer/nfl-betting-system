"""
Slack Bot - Debug Version
Logs everything for troubleshooting
"""
import os
from flask import Flask, request, jsonify
from slack_sdk import WebClient
import logging

# Enable detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
slack_client = WebClient(token=SLACK_BOT_TOKEN) if SLACK_BOT_TOKEN else None

@app.route('/health', methods=['GET'])
def health():
    logger.info("Health check requested")
    return jsonify({'status': 'healthy'})

@app.route('/slack/events', methods=['POST'])
def slack_events():
    logger.info("=== EVENT RECEIVED ===")
    
    # Log the raw request
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Body: {request.get_data(as_text=True)}")
    
    data = request.json
    logger.info(f"Parsed JSON: {data}")
    
    # Handle URL verification
    if data.get('type') == 'url_verification':
        challenge = data.get('challenge')
        logger.info(f"URL verification challenge: {challenge}")
        response = {'challenge': challenge}
        logger.info(f"Sending response: {response}")
        return jsonify(response)
    
    logger.info("Regular event received")
    return jsonify({'ok': True})

@app.route('/slack/commands', methods=['POST'])
def slack_commands():
    logger.info("=== COMMAND RECEIVED ===")
    command = request.form.get('command')
    logger.info(f"Command: {command}")
    
    return jsonify({
        'response_type': 'ephemeral',
        'text': f'Command {command} received! System ready.'
    })

@app.route('/slack/interactions', methods=['POST'])
def slack_interactions():
    logger.info("=== INTERACTION RECEIVED ===")
    return jsonify({'ok': True})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    logger.info(f"Starting Slack bot (DEBUG MODE) on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
