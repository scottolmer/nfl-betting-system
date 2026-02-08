"""
NFL Betting System - Chat Interface
A premium, chat-first experience for NFL prop analysis and parlay building.
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import time
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.parlay_builder import ParlayBuilder
from scripts.analysis.correlation_detector import EnhancedParlayBuilder

# --- Agent System (Chat Logic) ---

class BettingAgent:
    def __init__(self):
        self.context = st.session_state.get('context')
        self.analyzed_props = st.session_state.get('analyzed_props')
    
    def process_query(self, query):
        """
        Simple intent router. In the future, this can be replaced by an LLM call.
        """
        query = query.lower()
        
        # 1. Check Data Loaded
        if not self.context or not self.analyzed_props:
            return self._response_load_data()
            
        # 2. Intent: Parlay
        if "parlay" in query:
            return self._response_build_parlay(query)

        # 3. Intent: Best Props / Top Plays
        if "best" in query or "prop" in query or "top" in query:
            return self._response_top_props(query)

        # 4. Intent: Specific Player
        # (Simple check against player names in props)
        for prop in self.analyzed_props:
            if prop.prop.player_name.lower() in query:
                return self._response_player_analysis(prop)

        # Default
        return {
            "type": "text",
            "content": "I can help you analyze props or build parlays. Try asking:\n- 'Give me the top 5 props'\n- 'Build a safe parlay'\n- 'Stats for Patrick Mahomes'"
        }

    def _response_load_data(self):
        return {
            "type": "action_needed",
            "content": "I need to load the latest data before I can help.",
            "action": "load_data"
        }

    def _response_top_props(self, query):
        # Sort by confidence
        props = sorted(self.analyzed_props, key=lambda x: x.final_confidence, reverse=True)[:10]
        return {
            "type": "props_table",
            "content": "Here are the highest confidence plays on the board:",
            "data": props
        }

    def _response_build_parlay(self, query):
        builder = EnhancedParlayBuilder()
        parlays = builder.build_parlays_with_correlation(self.analyzed_props, min_confidence=55)
        
        # Flatten results
        all_parlays = []
        for p_list in parlays.values():
            all_parlays.extend(p_list)
        
        # Pick top 3 by confidence
        top_parlays = sorted(all_parlays, key=lambda x: x.combined_confidence, reverse=True)[:3]
        
        return {
            "type": "parlay_cards",
            "content": f"I found {len(top_parlays)} solid parlay options with low correlation risk.",
            "data": top_parlays
        }

    def _response_player_analysis(self, analysis):
        return {
            "type": "player_card",
            "content": f"Deep dive on **{analysis.prop.player_name}**:",
            "data": analysis
        }

# --- Streamlit UI ---

st.set_page_config(
    page_title="NFL Betting AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed" 
)

# Custom CSS for "Midnight Glass"
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .user-message {
        background: rgba(30, 41, 59, 0.5);
    }
    .agent-message {
        background: rgba(15, 23, 42, 0.5);
        border-left: 3px solid #00c0ff;
    }
    /* Hide generic elements for clean look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Session State Init
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello. I am your betting assistant. How can I help you win today?"}]
if "context" not in st.session_state:
    st.session_state.context = None
if 'week' not in st.session_state:
    st.session_state.week = 17 # Default to late season for demo

# --- Sidebar (Hidden Admin Params) ---
with st.sidebar:
    st.title("System Controls")
    st.session_state.week = st.number_input("Analysis Week", 1, 18, st.session_state.week)
    if st.button("♻️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.page_link("pages/admin.py", label="Go to Admin Panel", icon="🛡️")


# --- Main Chat ---

st.title("🏈 NFL Betting AI")

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # If message has complex data attached (tables, parlays), render it
        if "data" in msg:
            data_type = msg.get("data_type")
            data = msg.get("data")
            
            if data_type == "props":
                # Render props table
                df_data = []
                for p in data:
                     df_data.append({
                         "Player": p.prop.player_name,
                         "Prop": f"{p.prop.stat_type} {p.prop.line}",
                         "Type": p.prop.bet_type,
                         "Confidence": f"{p.final_confidence}%"
                     })
                st.dataframe(pd.DataFrame(df_data), use_container_width=True)
            
            elif data_type == "parlays":
                for i, parlay in enumerate(data, 1):
                    with st.expander(f"Parlay Option {i} ({parlay.combined_confidence}% Conf)"):
                        st.markdown(f"*{parlay.rationale}*")
                        for leg in parlay.legs:
                            st.markdown(f"- **{leg.prop.player_name}**: {leg.prop.stat_type} {leg.prop.bet_type} {leg.prop.line}")

# Input
if prompt := st.chat_input("Ask about props, parlays, or stats..."):
    # User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Agent Processing
    with st.chat_message("assistant"):
        agent = BettingAgent()
        
        with st.spinner("Analyzing..."):
            response = agent.process_query(prompt)
            
            if response["type"] == "action_needed" and response["action"] == "load_data":
                st.markdown("Loading data for Week " + str(st.session_state.week) + "...")
                # Load Data
                loader = NFLDataLoader(data_dir="data")
                st.session_state.context = loader.load_all_data(week=st.session_state.week)
                analyzer = PropAnalyzer()
                st.session_state.analyzed_props = analyzer.analyze_all_props(st.session_state.context)
                
                final_text = f"Data loaded! Analyzed {len(st.session_state.analyzed_props)} props. What would you like to see?"
                st.markdown(final_text)
                st.session_state.messages.append({"role": "assistant", "content": final_text})
                
            elif response["type"] == "text":
                st.markdown(response["content"])
                st.session_state.messages.append({"role": "assistant", "content": response["content"]})
                
            elif response["type"] == "props_table":
                st.markdown(response["content"])
                
                df_data = []
                for p in response["data"]:
                     df_data.append({
                         "Player": p.prop.player_name,
                         "Prop": f"{p.prop.stat_type} {p.prop.line}",
                         "Type": p.prop.bet_type,
                         "Confidence": f"{p.final_confidence}%"
                     })
                st.dataframe(pd.DataFrame(df_data), use_container_width=True)
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response["content"], 
                    "data": response["data"], 
                    "data_type": "props"
                })

            elif response["type"] == "parlay_cards":
                st.markdown(response["content"])
                for i, parlay in enumerate(response["data"], 1):
                    with st.expander(f"Parlay Option {i} ({parlay.combined_confidence}% Conf)"):
                        st.markdown(f"*{parlay.rationale}*")
                        for leg in parlay.legs:
                            st.markdown(f"- **{leg.prop.player_name}**: {leg.prop.stat_type} {leg.prop.bet_type} {leg.prop.line}")
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response["content"], 
                    "data": response["data"], 
                    "data_type": "parlays"
                })

            elif response["type"] == "player_card":
                an = response["data"]
                st.markdown(response["content"])
                st.json(an.agent_signals) # Simple debug view for now
                st.session_state.messages.append({"role": "assistant", "content": response["content"]})

