"""
NFL Betting System - Terminal-Style UI
Natural language interface with CLI-style interaction
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scripts.analysis.chat_interface import NLQueryInterface

# Page config - dark theme
st.set_page_config(
    page_title="NFL Betting Terminal",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for terminal look
st.markdown("""
<style>
    /* Dark terminal background */
    .stApp {
        background-color: #0e1117;
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Terminal-style text */
    .terminal-output {
        font-family: 'Courier New', monospace;
        background-color: #1a1d24;
        color: #00ff00;
        padding: 20px;
        border-radius: 5px;
        border: 1px solid #333;
        white-space: pre-wrap;
        font-size: 14px;
        line-height: 1.6;
        overflow-x: auto;
    }

    /* Command prompt style */
    .prompt {
        color: #00ff00;
        font-family: 'Courier New', monospace;
        font-weight: bold;
    }

    /* Input styling */
    .stTextInput input {
        font-family: 'Courier New', monospace;
        background-color: #1a1d24;
        color: #00ff00;
        border: 1px solid #00ff00;
        font-size: 14px;
    }

    /* Button styling */
    .stButton button {
        font-family: 'Courier New', monospace;
        background-color: #1a1d24;
        color: #00ff00;
        border: 1px solid #00ff00;
        font-size: 12px;
    }

    .stButton button:hover {
        background-color: #00ff00;
        color: #000;
    }

    /* Command suggestions */
    .command-chip {
        display: inline-block;
        background-color: #1a1d24;
        color: #00ff00;
        padding: 5px 10px;
        margin: 3px;
        border-radius: 3px;
        border: 1px solid #333;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        cursor: pointer;
    }

    /* History item */
    .history-item {
        font-family: 'Courier New', monospace;
        color: #666;
        font-size: 12px;
        padding: 3px 0;
        cursor: pointer;
    }

    .history-item:hover {
        color: #00ff00;
    }

    /* Metric boxes */
    .metric-box {
        background-color: #1a1d24;
        border: 1px solid #333;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
    }

    .metric-value {
        font-family: 'Courier New', monospace;
        color: #00ff00;
        font-size: 24px;
        font-weight: bold;
    }

    .metric-label {
        font-family: 'Courier New', monospace;
        color: #666;
        font-size: 12px;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'output_buffer' not in st.session_state:
    st.session_state.output_buffer = []
if 'interface' not in st.session_state:
    try:
        st.session_state.interface = NLQueryInterface(data_dir="data")
    except Exception as e:
        st.error(f"Failed to initialize interface: {e}")
        st.stop()
if 'current_week' not in st.session_state:
    st.session_state.current_week = 12

# Header
st.markdown("<h1 style='color: #00ff00; font-family: Courier New, monospace;'>🏈 NFL BETTING TERMINAL</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color: #666; font-family: Courier New, monospace;'>Week {st.session_state.current_week} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)

# Quick command chips
st.markdown("<p style='color: #666; font-family: Courier New, monospace; margin-top: 20px;'>QUICK COMMANDS:</p>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📋 help", use_container_width=True):
        st.session_state.input_buffer = "help"
        st.rerun()

with col2:
    if st.button(f"📅 week {st.session_state.current_week} props", use_container_width=True):
        st.session_state.input_buffer = f"show all props for week {st.session_state.current_week}"
        st.rerun()

with col3:
    if st.button("🔥 top 20 props", use_container_width=True):
        st.session_state.input_buffer = f"show top 20 props for week {st.session_state.current_week}"
        st.rerun()

col4, col5, col6 = st.columns(3)

with col4:
    if st.button("🎲 standard parlays", use_container_width=True):
        st.session_state.input_buffer = f"build 2-leg, 3-leg, and 4-leg parlays for week {st.session_state.current_week}"
        st.rerun()

with col5:
    if st.button("⚡ optimized parlays", use_container_width=True):
        st.session_state.input_buffer = f"build optimized 2-leg, 3-leg, and 4-leg parlays for week {st.session_state.current_week}"
        st.rerun()

with col6:
    if st.button("🧹 clear", use_container_width=True):
        st.session_state.output_buffer = []
        st.session_state.history = []
        st.rerun()

st.markdown("---")

# Command input area
st.markdown("<p class='prompt'>nfl-betting@terminal:~$ </p>", unsafe_allow_html=True)

# Use session state to handle input
if 'input_buffer' not in st.session_state:
    st.session_state.input_buffer = ""

# Create form for command input
with st.form(key="command_form", clear_on_submit=True):
    col1, col2 = st.columns([8, 1])

    with col1:
        user_input = st.text_input(
            "Command",
            value=st.session_state.input_buffer,
            placeholder="Type a command or question in plain English... (e.g., 'show QB props for week 12', 'build a 3-leg parlay')",
            label_visibility="collapsed",
            key="command_input"
        )

    with col2:
        submit = st.form_submit_button("▶ RUN", use_container_width=True)

# Process command
if submit and user_input:
    # Clear input buffer
    st.session_state.input_buffer = ""

    # Add to history
    timestamp = datetime.now().strftime('%H:%M:%S')
    st.session_state.history.append({"time": timestamp, "command": user_input})

    # Add command to output buffer
    st.session_state.output_buffer.append({
        "type": "command",
        "time": timestamp,
        "content": user_input
    })

    # Process with NL interface
    with st.spinner("Processing..."):
        try:
            interface = st.session_state.interface

            # Translate and execute
            command = interface.translate_query(user_input)
            result = interface.execute_command(command)

            # Add result to output buffer
            st.session_state.output_buffer.append({
                "type": "output",
                "time": timestamp,
                "content": result
            })

        except Exception as e:
            st.session_state.output_buffer.append({
                "type": "error",
                "time": timestamp,
                "content": f"[ERROR] {str(e)}"
            })

    st.rerun()

# Clear input buffer if it was set by a button
if st.session_state.input_buffer:
    st.session_state.input_buffer = ""

# Display output buffer (terminal style)
if st.session_state.output_buffer:
    st.markdown("<div style='margin-top: 30px;'>", unsafe_allow_html=True)

    # Show most recent entries first (reverse chronological)
    for entry in reversed(st.session_state.output_buffer[-20:]):  # Show last 20 entries
        timestamp = entry["time"]

        if entry["type"] == "command":
            st.markdown(f"<p style='color: #00ff00; font-family: Courier New, monospace; margin: 10px 0 5px 0;'>[{timestamp}] $ {entry['content']}</p>", unsafe_allow_html=True)

        elif entry["type"] == "output":
            # Style the output with terminal colors
            content = entry['content']

            # Convert markdown-style formatting to terminal colors
            content = content.replace('[SUCCESS]', '<span style="color: #00ff00;">[SUCCESS]</span>')
            content = content.replace('[ERROR]', '<span style="color: #ff0000;">[ERROR]</span>')
            content = content.replace('[BET]', '<span style="color: #ffff00;">[BET]</span>')
            content = content.replace('🔥', '<span style="color: #ff6600;">🔥</span>')
            content = content.replace('✅', '<span style="color: #00ff00;">✅</span>')
            content = content.replace('⭐', '<span style="color: #ffff00;">⭐</span>')

            st.markdown(f"<div class='terminal-output'>{content}</div>", unsafe_allow_html=True)

        elif entry["type"] == "error":
            st.markdown(f"<div class='terminal-output' style='color: #ff0000; border-color: #ff0000;'>{entry['content']}</div>", unsafe_allow_html=True)

        st.markdown("<div style='margin: 15px 0;'></div>", unsafe_allow_html=True)
else:
    # Welcome message
    st.markdown("""
    <div class='terminal-output'>
    Welcome to NFL Betting Terminal
    ================================

    Type commands in plain English to interact with the betting system.

    Examples:
      • "show me parlays for week 12"
      • "top QB props with confidence over 70"
      • "build a 3-leg parlay"
      • "show under bets for week 12"
      • "explain parlay TRAD_W12_abc123"

    Type 'help' for more examples, or use the quick command buttons above.
    </div>
    """, unsafe_allow_html=True)

# Sidebar - compact history and stats
with st.sidebar:
    st.markdown("<h3 style='color: #00ff00; font-family: Courier New, monospace;'>HISTORY</h3>", unsafe_allow_html=True)

    if st.session_state.history:
        for item in reversed(st.session_state.history[-10:]):  # Last 10 commands
            if st.button(f"[{item['time']}] {item['command'][:40]}...", key=f"hist_{item['time']}", use_container_width=True):
                st.session_state.input_buffer = item['command']
                st.rerun()
    else:
        st.markdown("<p style='color: #666; font-family: Courier New, monospace; font-size: 12px;'>No commands yet</p>", unsafe_allow_html=True)

    st.markdown("---")

    # Week selector
    st.markdown("<h3 style='color: #00ff00; font-family: Courier New, monospace;'>SETTINGS</h3>", unsafe_allow_html=True)

    new_week = st.number_input(
        "Week",
        min_value=1,
        max_value=18,
        value=st.session_state.current_week,
        key="week_selector"
    )

    if new_week != st.session_state.current_week:
        st.session_state.current_week = new_week
        st.rerun()

    st.markdown("---")

    # Quick reference
    st.markdown("<h3 style='color: #00ff00; font-family: Courier New, monospace;'>QUICK REF</h3>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-family: Courier New, monospace; font-size: 11px; color: #666;'>
    <b>View Data:</b><br/>
    • show props<br/>
    • list parlays<br/>
    • top props<br/>
    <br/>
    <b>Build:</b><br/>
    • build parlay<br/>
    • optimized parlay<br/>
    • create 2-leg<br/>
    <br/>
    <b>Filter:</b><br/>
    • filter to QB<br/>
    • over bets only<br/>
    • under bets<br/>
    • confidence > 70<br/>
    <br/>
    <b>Analyze:</b><br/>
    • explain parlay<br/>
    • agent breakdown<br/>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #666; font-family: Courier New, monospace; font-size: 11px;'>NFL Betting Terminal v1.0 | Type 'help' for commands</p>", unsafe_allow_html=True)
