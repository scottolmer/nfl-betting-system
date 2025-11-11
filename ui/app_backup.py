#!/usr/bin/env python
"""NFL Betting System - Streamlit UI Dashboard"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.api.claude_query_handler import ClaudeQueryHandler
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.parlay_builder import ParlayBuilder
from scripts.analysis.parlay_optimizer import ParlayOptimizer
from scripts.analysis.dependency_analyzer import DependencyAnalyzer

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="🏈 NFL Betting System",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SESSION STATE
# ============================================================================

if 'week' not in st.session_state:
    st.session_state.week = 9

if 'context' not in st.session_state:
    st.session_state.context = None

if 'all_analyses' not in st.session_state:
    st.session_state.all_analyses = None

if 'selected_prop' not in st.session_state:
    st.session_state.selected_prop = None

# ============================================================================
# SIDEBAR - SETTINGS & CONTROLS
# ============================================================================

st.sidebar.title("⚙️ Settings")

# Week selector
st.session_state.week = st.sidebar.slider(
    "NFL Week",
    1, 18,
    st.session_state.week,
    help="Select the NFL week to analyze"
)

# Load data button
if st.sidebar.button("🔄 Load Data", use_container_width=True):
    st.session_state.context = None
    st.session_state.all_analyses = None

st.sidebar.divider()

# Analysis controls
st.sidebar.subheader("📊 Analysis Controls")

min_confidence = st.sidebar.slider(
    "Minimum Confidence %",
    40, 100, 58,
    step=1,
    help="Filter props by minimum confidence threshold"
)

st.sidebar.divider()

# Parlay settings
st.sidebar.subheader("🎯 Parlay Settings")

parlay_min_conf = st.sidebar.slider(
    "Parlay Minimum Confidence %",
    50, 85, 65,
    step=1,
    help="Minimum confidence for props included in parlays"
)

optimization_enabled = st.sidebar.checkbox(
    "Enable Dependency Analysis",
    value=True,
    help="Use Claude API to analyze hidden correlations"
)

quality_threshold = None
if optimization_enabled:
    quality_threshold = st.sidebar.slider(
        "Quality Threshold %",
        60, 90, 75,
        step=1,
        help="Filter parlays by adjusted confidence after dependency analysis"
    )

st.sidebar.divider()
st.sidebar.markdown("---")
st.sidebar.caption("🧠 Powered by Multi-Agent Analysis + Claude API")

# ============================================================================
# MAIN HEADER
# ============================================================================

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.title("🏈 NFL Betting System")
with col2:
    st.metric("Week", st.session_state.week)
with col3:
    st.metric("Min Confidence", f"{min_confidence}%")

st.divider()

# ============================================================================
# NAVIGATION
# ============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard",
    "🔍 Prop Analysis",
    "🎯 Top Props",
    "🎰 Parlay Generator",
    "💡 Query Props"
])

# ============================================================================
# TAB 1: DASHBOARD
# ============================================================================

with tab1:
    st.header("📊 Week Dashboard")
    
    # Load data if not cached
    if st.session_state.context is None:
        with st.spinner(f"Loading data for Week {st.session_state.week}..."):
            loader = NFLDataLoader(data_dir=str(project_root / "data"))
            st.session_state.context = loader.load_all_data(week=st.session_state.week)
    
    context = st.session_state.context
    
    if context is None or not context.get('props'):
        st.warning("❌ No data available for this week")
    else:
        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        
        props_list = context.get('props', [])
        games_list = context.get('games', [])
        
        with col1:
            st.metric("Total Props", len(props_list))
        with col2:
            st.metric("Games", len(games_list) // 2 if games_list else 0)
        with col3:
            st.metric("Data Timestamp", datetime.now().strftime("%H:%M:%S"))
        with col4:
            st.metric("Status", "✅ Ready")
        
        st.divider()
        
        # Analyze all props if not done yet
        if st.session_state.all_analyses is None:
            with st.spinner("🧠 Analyzing all props with multi-agent framework..."):
                analyzer = PropAnalyzer()
                st.session_state.all_analyses = analyzer.analyze_all_props(
                    context,
                    min_confidence=40
                )
        
        all_analyses = st.session_state.all_analyses
        
        # Confidence distribution
        if all_analyses:
            confidences = [a.final_confidence for a in all_analyses]
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Histogram of confidence scores
                fig_hist = px.histogram(
                    x=confidences,
                    nbins=20,
                    title="Confidence Score Distribution",
                    labels={"x": "Confidence %", "count": "Number of Props"}
                )
                fig_hist.update_layout(height=400)
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col2:
                # Summary statistics
                conf_stats = {
                    "80%+": len([c for c in confidences if c >= 80]),
                    "75-80%": len([c for c in confidences if 75 <= c < 80]),
                    "70-75%": len([c for c in confidences if 70 <= c < 75]),
                    "65-70%": len([c for c in confidences if 65 <= c < 70]),
                    "60-65%": len([c for c in confidences if 60 <= c < 65]),
                    "50-60%": len([c for c in confidences if 50 <= c < 60]),
                    "<50%": len([c for c in confidences if c < 50]),
                }
                
                fig_pie = px.pie(
                    values=list(conf_stats.values()),
                    names=list(conf_stats.keys()),
                    title="Props by Confidence Bracket"
                )
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Key stats
            st.subheader("📈 Key Statistics")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                avg_conf = np.mean(confidences)
                st.metric("Average Confidence", f"{avg_conf:.1f}%")
            
            with col2:
                max_conf = np.max(confidences)
                st.metric("Max Confidence", f"{max_conf:.1f}%")
            
            with col3:
                median_conf = np.median(confidences)
                st.metric("Median Confidence", f"{median_conf:.1f}%")
            
            with col4:
                elite_props = len([c for c in confidences if c >= 80])
                st.metric("Elite Props (80%+)", elite_props)
            
            with col5:
                solid_props = len([c for c in confidences if c >= 75])
                st.metric("Solid Props (75%+)", solid_props)

# ============================================================================
# TAB 2: PROP ANALYSIS
# ============================================================================

with tab2:
    st.header("🔍 Individual Prop Analysis")
    
    # Load data if needed
    if st.session_state.context is None:
        with st.spinner(f"Loading data for Week {st.session_state.week}..."):
            loader = NFLDataLoader(data_dir=str(project_root / "data"))
            st.session_state.context = loader.load_all_data(week=st.session_state.week)
    
    context = st.session_state.context
    
    if context and context.get('props'):
        analyzer = PropAnalyzer()
        
        # Get list of all available props for quick selection
        props_list = context.get('props', [])
        prop_labels = [
            f"{p.get('player_name', 'Unknown')} - {p.get('stat_type', 'Unknown')} O{p.get('line', 0)}"
            for p in props_list[:100]  # Show first 100 for performance
        ]
        
        selected_label = st.selectbox(
            "Select a prop to analyze:",
            prop_labels,
            help="Choose from top 100 available props"
        )
        
        if selected_label:
            # Find the prop
            idx = prop_labels.index(selected_label)
            prop_data = props_list[idx]
            
            # Analyze it
            if st.button("🔍 Analyze This Prop", use_container_width=True):
                with st.spinner("Analyzing prop..."):
                    analysis = analyzer.analyze_prop(prop_data, context)
                    st.session_state.selected_prop = analysis
            
            if st.session_state.selected_prop:
                analysis = st.session_state.selected_prop
                prop = analysis.prop
                
                # Display prop details
                st.subheader(f"📋 {prop.player_name} - {prop.stat_type}")
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Team", prop.team)
                with col2:
                    st.metric("vs", prop.opponent)
                with col3:
                    st.metric("Line", f"{prop.line:.1f}")
                with col4:
                    st.metric("Confidence", f"{analysis.final_confidence:.1f}%")
                with col5:
                    recommendation = analysis.recommendation
                    st.metric("Recommendation", recommendation)
                
                st.divider()
                
                # Agent breakdown
                st.subheader("🧠 Agent Breakdown")
                
                if analysis.agent_breakdown:
                    agent_data = []
                    for agent_name, result in analysis.agent_breakdown.items():
                        agent_data.append({
                            "Agent": agent_name,
                            "Score": result['raw_score'],
                            "Direction": result['direction'],
                            "Weight": result['weight']
                        })
                    
                    agent_df = pd.DataFrame(agent_data)
                    
                    # Agent scores chart
                    fig_agents = px.bar(
                        agent_df,
                        x="Agent",
                        y="Score",
                        color="Score",
                        color_continuous_scale="RdYlGn",
                        title="Agent Confidence Scores",
                        range_color=[0, 100]
                    )
                    fig_agents.update_layout(height=400)
                    st.plotly_chart(fig_agents, use_container_width=True)
                    
                    # Agent details table
                    st.dataframe(agent_df, use_container_width=True)
                
                st.divider()
                
                # Rationale
                st.subheader("💭 Analysis Rationale")
                
                if analysis.rationale:
                    for point in analysis.rationale:
                        st.info(point)
                
                if analysis.edge_explanation:
                    st.success(f"**Edge:** {analysis.edge_explanation}")

# ============================================================================
# TAB 3: TOP PROPS
# ============================================================================

with tab3:
    st.header("🎯 Top Props by Confidence")
    
    # Load data if needed
    if st.session_state.context is None:
        with st.spinner(f"Loading data for Week {st.session_state.week}..."):
            loader = NFLDataLoader(data_dir=str(project_root / "data"))
            st.session_state.context = loader.load_all_data(week=st.session_state.week)
    
    context = st.session_state.context
    
    if context and context.get('props'):
        # Analyze all if needed
        if st.session_state.all_analyses is None:
            with st.spinner("🧠 Analyzing all props..."):
                analyzer = PropAnalyzer()
                st.session_state.all_analyses = analyzer.analyze_all_props(
                    context,
                    min_confidence=40
                )
        
        all_analyses = st.session_state.all_analyses
        
        # Filter by confidence
        filtered_analyses = [
            a for a in all_analyses
            if a.final_confidence >= min_confidence
        ]
        
        # Sort by confidence
        filtered_analyses.sort(
            key=lambda x: x.final_confidence,
            reverse=True
        )
        
        st.info(f"📊 Showing {len(filtered_analyses)} props with {min_confidence}%+ confidence")
        
        if filtered_analyses:
            # Create dataframe for display
            props_data = []
            for i, analysis in enumerate(filtered_analyses, 1):
                prop = analysis.prop
                props_data.append({
                    "Rank": i,
                    "Player": prop.player_name,
                    "Team": prop.team,
                    "vs": prop.opponent,
                    "Stat": prop.stat_type,
                    "Line": f"{prop.line:.1f}",
                    "Confidence": f"{analysis.final_confidence:.1f}%",
                    "Recommendation": analysis.recommendation,
                })
            
            df_props = pd.DataFrame(props_data)
            
            # Display table
            st.dataframe(
                df_props,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Rank": st.column_config.NumberColumn(width="small"),
                    "Confidence": st.column_config.ProgressColumn(
                        "Confidence",
                        min_value=0,
                        max_value=100,
                    ),
                }
            )
            
            # Export option
            csv_data = df_props.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv_data,
                file_name=f"top_props_week{st.session_state.week}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No props found with this confidence threshold")

# ============================================================================
# TAB 4: PARLAY GENERATOR
# ============================================================================

with tab4:
    st.header("🎰 Parlay Generator")
    
    # Load data if needed
    if st.session_state.context is None:
        with st.spinner(f"Loading data for Week {st.session_state.week}..."):
            loader = NFLDataLoader(data_dir=str(project_root / "data"))
            st.session_state.context = loader.load_all_data(week=st.session_state.week)
    
    context = st.session_state.context
    
    if context and context.get('props'):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            parlay_type = st.radio(
                "Parlay Type",
                ["Standard", "Optimized"],
                help="Standard uses simple math. Optimized uses Claude API to analyze correlations."
            )
        
        with col2:
            st.write("")  # Spacer
            generate_button = st.button(
                "🚀 Generate Parlays",
                use_container_width=True,
                type="primary"
            )
        
        with col3:
            st.write("")  # Spacer
        
        if generate_button:
            # Analyze all props first
            if st.session_state.all_analyses is None:
                with st.spinner("🧠 Analyzing all props..."):
                    analyzer = PropAnalyzer()
                    st.session_state.all_analyses = analyzer.analyze_all_props(
                        context,
                        min_confidence=40
                    )
            
            all_analyses = st.session_state.all_analyses
            
            if parlay_type == "Standard":
                with st.spinner("Building standard parlays..."):
                    parlay_builder = ParlayBuilder()
                    parlays = parlay_builder.build_parlays(
                        all_analyses,
                        min_confidence=parlay_min_conf
                    )
                    
                    # Display parlays
                    st.subheader("📋 Generated Parlays")
                    
                    for leg_type in ['2-leg', '3-leg', '4-leg', '5-leg']:
                        leg_parlays = parlays.get(leg_type, [])
                        if leg_parlays:
                            st.markdown(f"### {leg_type.upper()} PARLAYS ({len(leg_parlays)})")
                            
                            for i, parlay in enumerate(leg_parlays, 1):
                                with st.expander(f"Parlay {i}"):
                                    parlay_props = parlay.props
                                    parlay_df = pd.DataFrame([
                                        {
                                            "Player": p.prop.player_name,
                                            "Team": p.prop.team,
                                            "Stat": p.prop.stat_type,
                                            "Line": f"{p.prop.line:.1f}",
                                            "Confidence": f"{p.final_confidence:.1f}%"
                                        }
                                        for p in parlay_props
                                    ])
                                    st.dataframe(parlay_df, use_container_width=True, hide_index=True)
                                    
                                    parlay_confidence = parlay.parlay_confidence
                                    st.metric("Parlay Confidence", f"{parlay_confidence:.1f}%")
            
            else:  # Optimized
                with st.spinner("🧠 Building optimized parlays with dependency analysis..."):
                    api_key = os.environ.get('ANTHROPIC_API_KEY')
                    
                    if not api_key:
                        st.error("❌ ANTHROPIC_API_KEY not set in .env")
                    else:
                        optimizer = ParlayOptimizer(api_key=api_key)
                        optimized_parlays = optimizer.rebuild_parlays_low_correlation(
                            all_analyses,
                            target_parlays=10,
                            min_confidence=parlay_min_conf
                        )
                        
                        # Analyze dependencies
                        with st.spinner("🔍 Analyzing parlay dependencies..."):
                            dep_analyzer = DependencyAnalyzer(api_key=api_key)
                            
                            best = []
                            for ptype in ['2-leg', '3-leg', '4-leg', '5-leg']:
                                for parlay in optimized_parlays.get(ptype, []):
                                    analysis = dep_analyzer.analyze_parlay_dependencies(parlay)
                                    rec = analysis.get('recommendation')
                                    adj_conf = analysis.get('adjusted_confidence')
                                    
                                    if quality_threshold and adj_conf < quality_threshold:
                                        continue
                                    
                                    if rec != "AVOID":
                                        best.append({
                                            'parlay': parlay,
                                            'adjusted_confidence': adj_conf,
                                            'recommendation': rec,
                                            'adjustment': analysis.get('correlation_adjustment', {}).get('adjustment_value', 0),
                                            'analysis': analysis
                                        })
                        
                        best.sort(key=lambda x: x['adjusted_confidence'], reverse=True)
                        
                        # Display optimized parlays
                        st.subheader("📋 Optimized Parlays (Low-Correlation)")
                        
                        for i, item in enumerate(best, 1):
                            parlay = item['parlay']
                            adj_conf = item['adjusted_confidence']
                            recommendation = item['recommendation']
                            adjustment = item['adjustment']
                            
                            with st.expander(f"Parlay {i} - {adj_conf:.1f}% | {recommendation}"):
                                parlay_props = parlay.props
                                parlay_df = pd.DataFrame([
                                    {
                                        "Player": p.prop.player_name,
                                        "Team": p.prop.team,
                                        "Stat": p.prop.stat_type,
                                        "Line": f"{p.prop.line:.1f}",
                                        "Confidence": f"{p.final_confidence:.1f}%"
                                    }
                                    for p in parlay_props
                                ])
                                st.dataframe(parlay_df, use_container_width=True, hide_index=True)
                                
                                col1, col2, col3, col4 = st.columns(4)
                                
                                with col1:
                                    st.metric("Base Confidence", f"{parlay.parlay_confidence:.1f}%")
                                
                                with col2:
                                    st.metric("Adjusted Confidence", f"{adj_conf:.1f}%")
                                
                                with col3:
                                    st.metric("Adjustment", f"{adjustment:+.1f}%")
                                
                                with col4:
                                    st.metric("Recommendation", recommendation)

# ============================================================================
# TAB 5: QUERY PROPS
# ============================================================================

with tab5:
    st.header("💡 Natural Language Prop Query")
    
    st.write("Ask about specific player props in natural language")
    st.write("*Examples: 'Mahomes 250 pass yards', 'Justin Jefferson 75 receiving yards'*")
    
    query = st.text_input(
        "Enter your prop query:",
        placeholder="e.g., Mahomes 250 pass yards NYG"
    )
    
    weather_input = st.text_input(
        "Weather conditions (optional):",
        placeholder="e.g., 15mph wind, 32°F, clear"
    )
    
    if st.button("🔍 Analyze Query", use_container_width=True, type="primary"):
        if query:
            with st.spinner("Analyzing your query..."):
                handler = ClaudeQueryHandler()
                
                weather = None
                if weather_input:
                    weather = {'conditions': weather_input}
                
                response = handler.query(
                    query,
                    week=st.session_state.week,
                    weather=weather
                )
                
                st.markdown(response)
        else:
            st.warning("Please enter a prop query")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown(
    """
    <div style='text-align: center'>
    <small>🏈 NFL Betting System v2.0 | Multi-Agent Analysis + Claude API | Week {}</small>
    </div>
    """.format(st.session_state.week),
    unsafe_allow_html=True
)
