"""
NFL Betting System - Bloomberg/Trading Terminal Style UI
Multi-panel real-time data display
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scripts.analysis.chat_interface import NLQueryInterface
from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.correlation_detector import EnhancedParlayBuilder

# Page config - wide layout for multi-panel
st.set_page_config(
    page_title="NFL Betting Terminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Bloomberg Terminal style
st.markdown("""
<style>
    /* Dark terminal background */
    .stApp {
        background-color: #0a0e27;
    }

    /* Hide default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Panel styling */
    .terminal-panel {
        background: linear-gradient(135deg, #1a1f3a 0%, #0f1123 100%);
        border: 1px solid #2d3548;
        border-radius: 4px;
        padding: 15px;
        margin: 5px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    }

    .panel-header {
        color: #00d4ff;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 10px;
        padding-bottom: 8px;
        border-bottom: 1px solid #2d3548;
    }

    .panel-subheader {
        color: #7a8ba0;
        font-family: 'Consolas', monospace;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Data display */
    .data-row {
        font-family: 'Consolas', monospace;
        padding: 8px 0;
        border-bottom: 1px solid #1a1f3a;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .data-label {
        color: #7a8ba0;
        font-size: 13px;
    }

    .data-value {
        color: #ffffff;
        font-size: 15px;
        font-weight: 600;
    }

    .data-value.positive {
        color: #00ff88;
    }

    .data-value.negative {
        color: #ff4444;
    }

    .data-value.warning {
        color: #ffaa00;
    }

    /* Metric boxes */
    .metric-box {
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid #00d4ff;
        border-radius: 3px;
        padding: 12px;
        text-align: center;
    }

    .metric-value {
        font-family: 'Consolas', monospace;
        color: #00d4ff;
        font-size: 28px;
        font-weight: 700;
    }

    .metric-label {
        font-family: 'Consolas', monospace;
        color: #7a8ba0;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 5px;
    }

    /* Table styling */
    .dataframe {
        font-family: 'Consolas', monospace !important;
        font-size: 11px !important;
        background-color: #0f1123 !important;
    }

    .dataframe th {
        background-color: #1a1f3a !important;
        color: #00d4ff !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        font-size: 10px !important;
        letter-spacing: 1px !important;
        padding: 8px !important;
    }

    .dataframe td {
        color: #ffffff !important;
        padding: 8px !important;
        border-bottom: 1px solid #1a1f3a !important;
    }

    /* Buttons */
    .stButton button {
        font-family: 'Consolas', monospace;
        background: linear-gradient(135deg, #1a1f3a 0%, #0f1123 100%);
        color: #00d4ff;
        border: 1px solid #00d4ff;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        padding: 8px 16px;
        transition: all 0.3s ease;
    }

    .stButton button:hover {
        background: #00d4ff;
        color: #0a0e27;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.5);
    }

    /* Input styling */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        font-family: 'Consolas', monospace;
        background-color: #1a1f3a;
        color: #ffffff;
        border: 1px solid #2d3548;
        font-size: 12px;
    }

    /* Status indicators */
    .status-live {
        display: inline-block;
        width: 8px;
        height: 8px;
        background-color: #00ff88;
        border-radius: 50%;
        animation: pulse 2s infinite;
        margin-right: 8px;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* Title bar */
    .title-bar {
        background: linear-gradient(90deg, #00d4ff 0%, #0080ff 100%);
        padding: 15px 20px;
        margin: -20px -20px 20px -20px;
        border-radius: 4px 4px 0 0;
    }

    .title-text {
        color: #0a0e27;
        font-family: 'Consolas', monospace;
        font-size: 18px;
        font-weight: 900;
        letter-spacing: 2px;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #0f1123;
    }

    ::-webkit-scrollbar-thumb {
        background: #2d3548;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #00d4ff;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'week' not in st.session_state:
    st.session_state.week = 12
if 'analyzed_props' not in st.session_state:
    st.session_state.analyzed_props = None
if 'optimized_parlays' not in st.session_state:
    st.session_state.optimized_parlays = None
if 'top_props' not in st.session_state:
    st.session_state.top_props = []
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

# Initialize components
@st.cache_resource
def init_components():
    return {
        'loader': NFLDataLoader(data_dir="data"),
        'analyzer': PropAnalyzer(),
        'builder': EnhancedParlayBuilder()
    }

components = init_components()

# Title bar
st.markdown(f"""
<div class='title-bar'>
    <span class='status-live'></span>
    <span class='title-text'>NFL BETTING TERMINAL</span>
    <span style='float: right; color: #0a0e27; font-family: Consolas; font-size: 12px; font-weight: 600;'>
        WEEK {st.session_state.week} | {datetime.now().strftime('%H:%M:%S')}
    </span>
</div>
""", unsafe_allow_html=True)

# Status indicator
if st.session_state.data_loaded:
    st.success(f"✅ Week {st.session_state.week} loaded: {len(st.session_state.analyzed_props) if st.session_state.analyzed_props else 0} props | {len(st.session_state.top_props)} unique")
else:
    st.info(f"💡 Click 'LOAD DATA' to analyze Week {st.session_state.week}")

# Control panel at top
col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])

with col1:
    st.session_state.week = st.number_input("WEEK", 1, 18, st.session_state.week, key="week_input")

with col2:
    if st.button("⚡ LOAD DATA", use_container_width=True, type="primary"):
        try:
            # Load data
            context = components['loader'].load_all_data(week=st.session_state.week)
            all_props = components['analyzer'].analyze_all_props(context, min_confidence=40)

            # Store in session state
            st.session_state.analyzed_props = all_props
            st.session_state.data_loaded = True
            st.session_state.last_update = datetime.now()

            # Auto-calculate top props - deduplicate by player + stat type
            if all_props:
                sorted_props = sorted(all_props, key=lambda x: x.final_confidence, reverse=True)

                # Deduplicate: keep only best prop per player-stat-direction combo
                seen = set()
                unique_props = []
                for prop_analysis in sorted_props:
                    prop = prop_analysis.prop
                    key = (prop.player_name, prop.stat_type, prop.direction)
                    if key not in seen:
                        seen.add(key)
                        unique_props.append(prop_analysis)
                    if len(unique_props) >= 20:
                        break

                st.session_state.top_props = unique_props
            else:
                st.session_state.top_props = []

            st.rerun()

        except Exception as e:
            st.error(f"❌ Error: {e}")
            import traceback
            st.code(traceback.format_exc())

with col3:
    if st.button("🎲 BUILD PARLAYS", use_container_width=True):
        if st.session_state.analyzed_props:
            with st.spinner("Building optimized parlays..."):
                try:
                    parlays = components['builder'].build_parlays_with_correlation(
                        st.session_state.analyzed_props,
                        min_confidence=58
                    )
                    st.session_state.optimized_parlays = parlays
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Load data first")

with col4:
    min_conf_filter = st.number_input("MIN CONF", 0, 100, 60, key="min_conf")

with col5:
    position_filter = st.selectbox("POSITION", ["ALL", "QB", "RB", "WR", "TE"], key="pos_filter")

with col6:
    if st.button("🔄 REFRESH", use_container_width=True):
        st.rerun()

st.markdown("<div style='margin: 15px 0;'></div>", unsafe_allow_html=True)

# Main layout - 3 columns
left_col, middle_col, right_col = st.columns([1, 1.5, 1])

# LEFT PANEL - Market Overview & Top Props
with left_col:
    # Market stats panel
    st.markdown("""
    <div class='terminal-panel'>
        <div class='panel-header'>📊 MARKET OVERVIEW</div>
    """, unsafe_allow_html=True)

    if st.session_state.data_loaded and st.session_state.analyzed_props:
        props = st.session_state.analyzed_props

        # Filter by confidence
        filtered_props = [p for p in props if p.final_confidence >= min_conf_filter]
        if position_filter != "ALL":
            filtered_props = [p for p in filtered_props if p.prop.position == position_filter]

        # Deduplicate for stats
        seen_stats = set()
        unique_for_stats = []
        for prop_analysis in filtered_props:
            prop = prop_analysis.prop
            stats_key = (prop.player_name, prop.stat_type, prop.direction)
            if stats_key not in seen_stats:
                seen_stats.add(stats_key)
                unique_for_stats.append(prop_analysis)

        total_before_dedup = len(filtered_props)
        total_after_dedup = len(unique_for_stats)

        high_conf = len([p for p in unique_for_stats if p.final_confidence >= 70])
        over_count = len([p for p in unique_for_stats if p.prop.direction == 'OVER'])
        under_count = len([p for p in unique_for_stats if p.prop.direction == 'UNDER'])
        avg_conf = sum(p.final_confidence for p in unique_for_stats) / len(unique_for_stats) if unique_for_stats else 0

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class='metric-box'>
                <div class='metric-value'>{total_after_dedup}</div>
                <div class='metric-label'>Unique Props</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class='metric-box'>
                <div class='metric-value'>{high_conf}</div>
                <div class='metric-label'>High Conf (70+)</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)

        col3, col4 = st.columns(2)
        with col3:
            st.markdown(f"""
            <div class='data-row'>
                <span class='data-label'>OVER PROPS</span>
                <span class='data-value positive'>{over_count}</span>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class='data-row'>
                <span class='data-label'>UNDER PROPS</span>
                <span class='data-value negative'>{under_count}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='data-row'>
            <span class='data-label'>AVG CONFIDENCE</span>
            <span class='data-value'>{avg_conf:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)

        # Show deduplication info
        duplicates_removed = total_before_dedup - total_after_dedup
        if duplicates_removed > 0:
            st.markdown(f"""
            <div class='data-row'>
                <span class='data-label'>DUPLICATES REMOVED</span>
                <span class='data-value warning'>{duplicates_removed}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<div style='color: #7a8ba0; font-family: Consolas; font-size: 11px; text-align: center; padding: 20px;'>NO DATA LOADED<br/>Click 'LOAD DATA' to begin</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)

    # Top props panel
    st.markdown("""
    <div class='terminal-panel'>
        <div class='panel-header'>🔥 TOP PROPS</div>
        <div class='panel-subheader'>Highest Confidence Plays</div>
    """, unsafe_allow_html=True)

    if st.session_state.top_props:
        for i, analysis in enumerate(st.session_state.top_props[:10], 1):
            prop = analysis.prop
            conf = analysis.final_confidence

            direction_color = "positive" if prop.direction == "OVER" else "negative"

            st.markdown(f"""
            <div class='data-row' style='flex-direction: column; align-items: flex-start; padding: 12px 0;'>
                <div style='display: flex; justify-content: space-between; width: 100%;'>
                    <span class='data-value' style='font-size: 13px;'>{prop.player_name}</span>
                    <span class='data-value {direction_color}' style='font-size: 13px;'>{conf:.1f}%</span>
                </div>
                <div style='color: #7a8ba0; font-size: 11px; margin-top: 4px; line-height: 1.4;'>
                    {prop.stat_type} {prop.direction} {prop.line}
                </div>
                <div style='color: #666; font-size: 10px; margin-top: 2px;'>
                    {prop.team} vs {prop.opponent}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<div style='color: #7a8ba0; font-family: Consolas; font-size: 11px; text-align: center; padding: 20px;'>Load data to see top props</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# MIDDLE PANEL - Optimized Parlays (Main Display)
with middle_col:
    st.markdown("""
    <div class='terminal-panel'>
        <div class='panel-header'>⚡ OPTIMIZED PARLAYS</div>
        <div class='panel-subheader'>Correlation-Aware Selections</div>
    """, unsafe_allow_html=True)

    if st.session_state.optimized_parlays:
        parlays = st.session_state.optimized_parlays

        # Display each parlay type
        for ptype in ['2-leg', '3-leg', '4-leg']:
            if ptype in parlays and parlays[ptype]:
                st.markdown(f"""
                <div style='margin: 15px 0 10px 0;'>
                    <span style='color: #00d4ff; font-family: Consolas; font-size: 11px; font-weight: 700; letter-spacing: 1px;'>
                        {ptype.upper()} PARLAYS
                    </span>
                </div>
                """, unsafe_allow_html=True)

                for idx, parlay in enumerate(parlays[ptype][:2], 1):  # Show top 2 per type
                    conf = parlay.combined_confidence

                    # Determine confidence color
                    if conf >= 70:
                        conf_class = "positive"
                    elif conf >= 60:
                        conf_class = "warning"
                    else:
                        conf_class = "negative"

                    # Check for penalty
                    penalty_text = ""
                    if hasattr(parlay, 'correlation_penalty') and parlay.correlation_penalty < 0:
                        original = int(conf - parlay.correlation_penalty)

                        # Extract penalty reason from warnings
                        penalty_reason = ""
                        if hasattr(parlay, 'correlation_warnings') and parlay.correlation_warnings:
                            # Get shared agents from first warning
                            first_warning = parlay.correlation_warnings[0]
                            if "driven by" in first_warning:
                                agents_part = first_warning.split("driven by")[-1].strip()
                                penalty_reason = f" - {agents_part}"

                        penalty_text = f"<span style='color: #ff4444; font-size: 10px;'>(was {original}%, {int(parlay.correlation_penalty)}% penalty{penalty_reason})</span>"

                    st.markdown(f"""
                    <div style='background: rgba(0, 212, 255, 0.05); border: 1px solid #2d3548; border-radius: 3px; padding: 12px; margin: 8px 0;'>
                        <div style='display: flex; justify-content: space-between; margin-bottom: 8px;'>
                            <span style='color: #7a8ba0; font-family: Consolas; font-size: 10px;'>PARLAY #{idx}</span>
                            <span class='data-value {conf_class}' style='font-size: 14px;'>{conf:.1f}%</span>
                        </div>
                        {penalty_text}
                    """, unsafe_allow_html=True)

                    # Show correlation warnings if any
                    if hasattr(parlay, 'correlation_warnings') and parlay.correlation_warnings:
                        st.markdown("""
                        <div style='background: rgba(255, 170, 0, 0.15); border-left: 3px solid #ffaa00; padding: 10px 12px; margin: 10px 0; border-radius: 3px;'>
                            <div style='color: #ffaa00; font-family: Consolas; font-size: 11px; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 6px;'>
                                ⚠️ CORRELATION RISKS
                            </div>
                        """, unsafe_allow_html=True)
                        for warning in parlay.correlation_warnings:
                            st.markdown(f"<div style='color: #ffaa00; font-family: Consolas; font-size: 11px; line-height: 1.6; margin: 4px 0;'>• {warning}</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)

                    # Show legs
                    for leg_idx, leg in enumerate(parlay.legs, 1):
                        prop = leg.prop
                        leg_conf = leg.final_confidence

                        # Get top agents
                        agents = ""
                        if hasattr(leg, 'top_contributing_agents') and leg.top_contributing_agents:
                            top_2 = [a[0] for a in leg.top_contributing_agents[:2]]
                            agents = f"<span style='color: #7a8ba0; font-size: 9px;'>[{', '.join(top_2)}]</span>"

                        direction_color = "positive" if prop.direction == "OVER" else "negative"

                        st.markdown(f"""
                        <div style='margin: 8px 0; padding-left: 12px; border-left: 2px solid #2d3548;'>
                            <div style='display: flex; justify-content: space-between;'>
                                <span style='color: #ffffff; font-family: Consolas; font-size: 13px; font-weight: 600;'>
                                    {leg_idx}. {prop.player_name} ({prop.position})
                                </span>
                                <span class='data-value {direction_color}' style='font-size: 13px;'>{leg_conf:.1f}%</span>
                            </div>
                            <div style='color: #7a8ba0; font-family: Consolas; font-size: 11px; margin-top: 3px; line-height: 1.5;'>
                                {prop.stat_type} {prop.direction} {prop.line} | {prop.team} vs {prop.opponent}
                            </div>
                            <div style='color: #7a8ba0; font-family: Consolas; font-size: 10px; margin-top: 2px;'>
                                {agents}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='color: #7a8ba0; font-family: Consolas; font-size: 11px; text-align: center; padding: 40px;'>NO PARLAYS GENERATED<br/><br/>Click 'BUILD PARLAYS' to generate optimized parlays</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# RIGHT PANEL - Props Table & Filters
with right_col:
    st.markdown("""
    <div class='terminal-panel'>
        <div class='panel-header'>📋 PROPS TABLE</div>
        <div class='panel-subheader'>Filtered View</div>
    """, unsafe_allow_html=True)

    if st.session_state.data_loaded and st.session_state.analyzed_props:
        # Filter props
        filtered = st.session_state.analyzed_props
        filtered = [p for p in filtered if p.final_confidence >= min_conf_filter]
        if position_filter != "ALL":
            filtered = [p for p in filtered if p.prop.position == position_filter]

        # Sort by confidence
        filtered = sorted(filtered, key=lambda x: x.final_confidence, reverse=True)

        # Deduplicate: keep only best prop per player-stat-direction combo
        seen_combos = set()
        unique_filtered = []
        for prop_analysis in filtered:
            prop = prop_analysis.prop
            combo_key = (prop.player_name, prop.stat_type, prop.direction)
            if combo_key not in seen_combos:
                seen_combos.add(combo_key)
                unique_filtered.append(prop_analysis)

        filtered = unique_filtered

        # Create table data
        if filtered:
            data = []
            for analysis in filtered[:30]:  # Show top 30
                prop = analysis.prop
                data.append({
                    'Player': prop.player_name[:15],
                    'Pos': prop.position,
                    'Stat': prop.stat_type[:12],
                    'Dir': prop.direction,
                    'Line': f"{prop.line:.1f}",
                    'Conf': f"{analysis.final_confidence:.0f}%",
                    'Team': prop.team
                })

            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, height=600, hide_index=True)

            st.markdown(f"""
            <div style='margin-top: 10px; text-align: center;'>
                <span style='color: #7a8ba0; font-family: Consolas; font-size: 9px;'>
                    SHOWING {len(data)} OF {len(filtered)} PROPS
                </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='color: #7a8ba0; font-family: Consolas; font-size: 11px; text-align: center; padding: 20px;'>No props match filters</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='color: #7a8ba0; font-family: Consolas; font-size: 11px; text-align: center; padding: 20px;'>Load data to view props</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)

    # System status panel
    st.markdown("""
    <div class='terminal-panel'>
        <div class='panel-header'>📡 SYSTEM STATUS</div>
    """, unsafe_allow_html=True)

    status = "🟢 READY" if st.session_state.data_loaded else "🔴 IDLE"
    status_color = "positive" if st.session_state.data_loaded else "negative"

    st.markdown(f"""
    <div class='data-row'>
        <span class='data-label'>STATUS</span>
        <span class='data-value {status_color}'>{status}</span>
    </div>
    <div class='data-row'>
        <span class='data-label'>WEEK</span>
        <span class='data-value'>{st.session_state.week}</span>
    </div>
    <div class='data-row'>
        <span class='data-label'>LAST UPDATE</span>
        <span class='data-value' style='font-size: 11px;'>{st.session_state.last_update.strftime('%H:%M:%S')}</span>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.analyzed_props:
        st.markdown(f"""
        <div class='data-row'>
            <span class='data-label'>PROPS LOADED</span>
            <span class='data-value'>{len(st.session_state.analyzed_props)}</span>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.optimized_parlays:
        total_parlays = sum(len(v) for v in st.session_state.optimized_parlays.values())
        st.markdown(f"""
        <div class='data-row'>
            <span class='data-label'>PARLAYS BUILT</span>
            <span class='data-value'>{total_parlays}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #2d3548; font-family: Consolas; font-size: 9px; letter-spacing: 1px;'>
    NFL BETTING TERMINAL v2.0 | REAL-TIME DATA ANALYSIS | OPTIMIZED PARLAYS
</div>
""", unsafe_allow_html=True)
