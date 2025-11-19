#!/usr/bin/env python
"""NFL Betting System - Streamlit Interface (CLI-Style)
Direct, efficient, results-focused - just like your CLI"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import os
from dotenv import load_dotenv

load_dotenv()

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.api.claude_query_handler import ClaudeQueryHandler
    from scripts.analysis.orchestrator import PropAnalyzer
    from scripts.analysis.data_loader import NFLDataLoader
    from scripts.analysis.parlay_builder import ParlayBuilder
    from scripts.analysis.parlay_optimizer import ParlayOptimizer
    from scripts.analysis.performance_tracker import PerformanceTracker
except ImportError as e:
    st.error(f"Import Error: {e}")
    st.stop()

st.set_page_config(page_title="🏈 NFL Betting CLI", layout="wide", initial_sidebar_state="collapsed")

if 'week' not in st.session_state:
    st.session_state.week = 9
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 1000

@st.cache_resource
def init_components():
    return {
        'handler': ClaudeQueryHandler(),
        'analyzer': PropAnalyzer(),
        'loader': NFLDataLoader(data_dir="data"),
        'builder': ParlayBuilder(),
        'tracker': PerformanceTracker(db_path="bets.db"),
    }

components = init_components()

st.title("🏈 NFL BETTING SYSTEM - CLI STYLE")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.session_state.week = st.number_input("📅 Week", 1, 18, st.session_state.week)
with col2:
    st.session_state.bankroll = st.number_input("💰 Bankroll", 0.0, 100000.0, float(st.session_state.bankroll))

st.markdown("---")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "⚙️ Analyze", "🔥 Top Props", "🎰 Parlays", "📊 Track", "💾 Results", "📈 Stats"
])

# TAB 1: ANALYZE
with tab1:
    st.subheader("⚙️ Analyze Single Prop")
    query = st.text_input("Enter prop query:", placeholder="e.g., Mahomes 250 pass yards", key="analyze_query")
    weather = st.text_input("Weather (optional):", placeholder="e.g., 15mph wind", key="analyze_weather")
    
    if st.button("🔍 Analyze", use_container_width=True, type="primary"):
        if query:
            with st.spinner("Analyzing..."):
                try:
                    weather_obj = {'conditions': weather} if weather else None
                    response = components['handler'].query(query, week=st.session_state.week, weather=weather_obj)
                    st.markdown(response)
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.error("Enter a query")

# TAB 2: TOP PROPS
with tab2:
    st.subheader("🔥 Top Props by Confidence")
    count = st.number_input("Show top N props:", 1, 100, 20, key="top_props_count")
    
    if st.button("📊 Load Top Props", use_container_width=True, type="primary"):
        with st.spinner(f"Analyzing Week {st.session_state.week}..."):
            try:
                context = components['loader'].load_all_data(week=st.session_state.week)
                all_analyses = components['analyzer'].analyze_all_props(context, min_confidence=40)
                all_analyses.sort(key=lambda x: x.final_confidence, reverse=True)
                top_props = all_analyses[:count]
                
                props_data = []
                for i, analysis in enumerate(top_props, 1):
                    prop = analysis.prop
                    conf = analysis.final_confidence
                    emoji = "🔥" if conf >= 80 else "⭐" if conf >= 75 else "✅" if conf >= 70 else "📈"
                    
                    props_data.append({
                        "": emoji,
                        "Rank": i,
                        "Player": prop.player_name,
                        "Team": prop.team,
                        "vs": prop.opponent,
                        "Stat": prop.stat_type,
                        "Line": f"{prop.line:.1f}",
                        "Confidence": f"{conf:.1f}%",
                    })
                
                st.dataframe(pd.DataFrame(props_data), use_container_width=True, hide_index=True)
                st.success(f"✅ Loaded {len(top_props)} props")
            except Exception as e:
                st.error(f"Error: {e}")

# TAB 3: PARLAYS
with tab3:
    st.subheader("🎰 Generate Parlays")
    
    col1, col2 = st.columns(2)
    with col1:
        parlay_type = st.radio("Type:", ["Standard", "Optimized"], horizontal=True, key="parlay_type")
    with col2:
        min_conf = st.number_input("Min Confidence %:", 40, 80, 62, key="parlay_conf")
    
    if st.button("🚀 Generate Parlays", use_container_width=True, type="primary"):
        with st.spinner(f"Generating {parlay_type} parlays..."):
            try:
                context = components['loader'].load_all_data(week=st.session_state.week)
                all_analyses = components['analyzer'].analyze_all_props(context, min_confidence=40)
                
                if parlay_type == "Standard":
                    parlays = components['builder'].build_parlays(all_analyses, min_confidence=min_conf)
                    for leg_type in ['2-leg', '3-leg', '4-leg']:
                        leg_parlays = parlays.get(leg_type, [])
                        if leg_parlays:
                            st.markdown(f"### {leg_type.upper()} ({len(leg_parlays)})")
                            for i, parlay in enumerate(leg_parlays[:5], 1):
                                conf = parlay.combined_confidence
                                emoji = "🔥" if conf >= 80 else "✅"
                                with st.container(border=True):
                                    st.write(f"**{emoji} Parlay {i}** - {conf:.1f}%")
                                    legs_list = [{"Player": leg.prop.player_name, "Stat": leg.prop.stat_type, "Line": f"{leg.prop.line:.1f}", "Conf": f"{leg.final_confidence:.1f}%"} for leg in parlay.legs]
                                    st.dataframe(pd.DataFrame(legs_list), use_container_width=True, hide_index=True)
                else:
                    api_key = os.environ.get('ANTHROPIC_API_KEY')
                    if not api_key:
                        st.error("ANTHROPIC_API_KEY not set")
                    else:
                        optimizer = ParlayOptimizer(api_key=api_key)
                        optimized = optimizer.rebuild_parlays_low_correlation(all_analyses, target_parlays=10, min_confidence=min_conf)
                        st.success("✅ Generated optimized parlays")
                        all_parlays = []
                        for ptype in ['2-leg', '3-leg', '4-leg']:
                            all_parlays.extend(optimized.get(ptype, []))
                        all_parlays.sort(key=lambda x: x.combined_confidence, reverse=True)
                        for i, parlay in enumerate(all_parlays[:10], 1):
                            conf = parlay.combined_confidence
                            emoji = "🔥" if conf >= 80 else "✅"
                            with st.container(border=True):
                                st.write(f"**{emoji} Parlay {i}** - {conf:.1f}%")
                                legs_list = [{"Player": leg.prop.player_name, "Stat": leg.prop.stat_type, "Conf": f"{leg.final_confidence:.1f}%"} for leg in parlay.legs]
                                st.dataframe(pd.DataFrame(legs_list), use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Error: {e}")

# TAB 4: TRACK
with tab4:
    st.subheader("📊 Parlay Tracking")
    col1, col2 = st.columns(2)
    with col1:
        track_week = st.number_input("Week to track:", 1, 18, st.session_state.week, key="track_week")
    with col2:
        track_filter = st.selectbox("Filter:", ["All", "Won", "Lost", "Pending"], key="track_filter")
    
    if st.button("📋 Load Tracked Parlays", use_container_width=True):
        try:
            tracker = components['tracker']
            parlays = tracker.get_parlays_by_week(track_week)
            if track_filter == "Won":
                parlays = [p for p in parlays if p.get('result') == 'won']
            elif track_filter == "Lost":
                parlays = [p for p in parlays if p.get('result') == 'lost']
            elif track_filter == "Pending":
                parlays = [p for p in parlays if p.get('result') == 'pending']
            
            if not parlays:
                st.info(f"No {track_filter.lower()} parlays for Week {track_week}")
            else:
                st.success(f"Found {len(parlays)} parlays")
                for parlay in parlays[:20]:
                    parlay_id = parlay.get('parlay_id', 'Unknown')
                    conf = parlay.get('effective_confidence', 0)
                    result = parlay.get('result', 'pending')
                    result_emoji = {"won": "✅", "lost": "❌", "pending": "⏳"}.get(result, "❓")
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.write(f"**{parlay_id}** - {conf:.1f}%")
                        with col2:
                            st.write(f"{result_emoji} {result.upper()}")
                        with col3:
                            with st.expander("Legs"):
                                for prop in parlay.get('props', []):
                                    st.write(f"• {prop['player']} {prop['direction']} {prop['line']}")
        except Exception as e:
            st.error(f"Error: {e}")

# TAB 5: RESULTS
with tab5:
    st.subheader("💾 Log Results")
    parlay_id = st.text_input("Parlay ID:", key="result_id")
    result_str = st.text_input("Result (e.g., 2/3):", key="result_input")
    if st.button("📝 Log Result", use_container_width=True):
        try:
            if '/' not in result_str:
                st.error("Format: X/Y (e.g., 2/3)")
            else:
                hits, total = map(int, result_str.split('/'))
                tracker = components['tracker']
                tracker.log_results(parlay_id, {f'leg_{i}': i < hits for i in range(total)})
                st.success(f"✅ Logged {hits}/{total} for {parlay_id}")
        except Exception as e:
            st.error(f"Error: {e}")

# TAB 6: STATS
with tab6:
    st.subheader("📈 Performance Stats")
    stats_view = st.radio("View:", ["Overall", "By Week", "By Type"], horizontal=True, key="stats_view")
    
    if st.button("📊 Load Statistics", use_container_width=True):
        try:
            tracker = components['tracker']
            if stats_view == "Overall":
                stats = tracker.get_statistics()
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Record", f"{stats['won']}-{stats['lost']}")
                with col2:
                    st.metric("Win Rate", f"{stats.get('win_rate', 0):.1f}%")
                with col3:
                    st.metric("Avg Confidence", f"{stats.get('avg_predicted_confidence', 0):.1f}%")
                with col4:
                    st.metric("Calibration", f"{stats.get('calibration_error', 0):+.1f}")
            elif stats_view == "By Week":
                stats_week = st.number_input("Week:", 1, 18, st.session_state.week, key="stats_week_input")
                stats = tracker.get_statistics(weeks=[stats_week])
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Record", f"{stats['won']}-{stats['lost']}")
                with col2:
                    st.metric("Win Rate", f"{stats.get('win_rate', 0):.1f}%")
                with col3:
                    st.metric("Calibration", f"{stats.get('calibration_error', 0):+.1f}")
            else:
                for leg in [2, 3, 4]:
                    stats = tracker.get_statistics(parlay_legs=leg)
                    if stats and (stats['won'] + stats['lost']) > 0:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**{leg}-Leg Parlays**")
                        with col2:
                            st.write(f"{stats['won']}-{stats['lost']} | {stats.get('win_rate', 0):.1f}%")
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.caption("🏈 NFL Betting System (CLI-Style) | Quick, Direct, Efficient")
