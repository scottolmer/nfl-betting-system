"""
Slack Bot - Minimal working version
"""
import os
from flask import Flask, request, jsonify
from slack_sdk import WebClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
slack_client = WebClient(token=SLACK_BOT_TOKEN) if SLACK_BOT_TOKEN else None

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.json
    if data.get('type') == 'url_verification':
        return jsonify({'challenge': data['challenge']})
    return jsonify({'ok': True})

@app.route('/slack/commands', methods=['POST'])
def slack_commands():
    command = request.form.get('command')
    return jsonify({
        'response_type': 'ephemeral',
        'text': f'Command {command} received! System ready.'
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    logger.info(f"Starting Slack bot on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
