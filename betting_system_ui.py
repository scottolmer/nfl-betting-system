"""
NFL Betting System - Complete Streamlit UI
Multi-page dashboard for prop analysis, parlay generation, validation, and performance tracking
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.parlay_builder import ParlayBuilder
from scripts.analysis.prop_availability_validator import PropAvailabilityValidator
from scripts.analysis.parlay_rebuilder import ParlayRebuilder
from scripts.analysis.performance_tracker import PerformanceTracker
from scripts.analysis.agent_calibrator import AgentCalibrator

# Page config
st.set_page_config(
    page_title="NFL Betting System",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'week' not in st.session_state:
    st.session_state.week = 12
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'analyzed_props' not in st.session_state:
    st.session_state.analyzed_props = None
if 'parlays' not in st.session_state:
    st.session_state.parlays = None
if 'context' not in st.session_state:
    st.session_state.context = None

# Sidebar navigation
with st.sidebar:
    st.title("🏈 NFL Betting System")
    st.markdown("---")

    # Week selector
    st.session_state.week = st.number_input(
        "Week",
        min_value=1,
        max_value=18,
        value=st.session_state.week,
        key="week_selector"
    )

    # Load data button
    if st.button("📊 Load Data", type="primary", use_container_width=True):
        with st.spinner(f"Loading data for Week {st.session_state.week}..."):
            try:
                loader = NFLDataLoader(data_dir="data")
                st.session_state.context = loader.load_all_data(week=st.session_state.week)

                analyzer = PropAnalyzer()
                st.session_state.analyzed_props = analyzer.analyze_all_props(
                    st.session_state.context,
                    min_confidence=40
                )

                st.session_state.data_loaded = True
                st.success(f"✅ Loaded {len(st.session_state.analyzed_props)} props")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")

    # Navigation
    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "🎯 Prop Analysis",
            "🎲 Parlay Builder",
            "✅ Validation",
            "📊 Performance",
            "⚙️ Settings"
        ],
        key="nav_radio"
    )

    # Data status
    if st.session_state.data_loaded:
        st.success(f"📊 Week {st.session_state.week} loaded")
        st.caption(f"{len(st.session_state.analyzed_props)} props analyzed")
    else:
        st.info("👆 Load data to start")

# Main content based on page selection
if page == "🏠 Dashboard":
    st.title("🏈 NFL Betting System Dashboard")

    if not st.session_state.data_loaded:
        st.info("👈 Load data in the sidebar to view dashboard")

        # Show welcome and features
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 🎯 Prop Analysis")
            st.markdown("""
            - 8 AI agents analyze each prop
            - Confidence scores 0-100
            - OVER and UNDER support
            - Filter by position, team, stat
            """)

        with col2:
            st.markdown("### 🎲 Parlay Builder")
            st.markdown("""
            - Auto-generates 2-5 leg parlays
            - Player diversity optimization
            - Correlation bonuses
            - Risk-adjusted sizing
            """)

        with col3:
            st.markdown("### ✅ Validation")
            st.markdown("""
            - DK Pick6 availability check
            - Auto-learning system
            - Rule-based filtering
            - Parlay rebuilding
            """)

    else:
        # Show summary stats
        props = st.session_state.analyzed_props

        # Top metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Props", len(props))

        with col2:
            high_conf = len([p for p in props if p.final_confidence >= 70])
            st.metric("High Confidence (70+)", high_conf)

        with col3:
            over_count = len([p for p in props if getattr(p.prop, 'bet_type', 'OVER') == 'OVER'])
            st.metric("OVER Props", over_count)

        with col4:
            under_count = len([p for p in props if getattr(p.prop, 'bet_type', 'OVER') == 'UNDER'])
            st.metric("UNDER Props", under_count)

        st.markdown("---")

        # Top props preview
        st.subheader("🔥 Top 25 Props")

        sorted_props = sorted(props, key=lambda x: x.final_confidence, reverse=True)[:25]

        for i, analysis in enumerate(sorted_props, 1):
            prop = analysis.prop
            conf = analysis.final_confidence
            bet_type = getattr(prop, 'bet_type', 'OVER')

            # Confidence badge
            if conf >= 75:
                badge = "🔥"
            elif conf >= 70:
                badge = "⭐"
            else:
                badge = "✅"

            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                st.markdown(f"{badge} **{prop.player_name}** ({prop.team}) vs {prop.opponent}")
                st.caption(f"{prop.stat_type} {bet_type} {prop.line}")

            with col2:
                st.markdown(f"**Confidence: {conf}%**")

            with col3:
                if st.button("View Details", key=f"view_{i}"):
                    st.session_state.selected_prop = analysis
                    st.switch_page("pages/prop_details.py")

elif page == "🎯 Prop Analysis":
    st.title("🎯 Prop Analysis")

    if not st.session_state.data_loaded:
        st.info("👈 Load data first")
    else:
        props = st.session_state.analyzed_props

        # Filters
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            positions = ['All'] + sorted(list(set(p.prop.position for p in props)))
            position_filter = st.selectbox("Position", positions)

        with col2:
            # Team filter with multi-select
            all_teams = sorted(list(set(p.prop.team for p in props)))
            team_filter = st.multiselect("Teams (multi-select)", all_teams, default=[])

        with col3:
            bet_types = ['All', 'OVER', 'UNDER']
            bet_type_filter = st.selectbox("Bet Type", bet_types)

        with col4:
            min_conf = st.slider("Min Confidence", 0, 100, 60)

        with col5:
            sort_by = st.selectbox("Sort By", ["Confidence", "Player", "Team"])

        # Quick filter buttons for Thursday games
        st.markdown("**Quick Filters:**")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Thursday Games Only", use_container_width=True):
                team_filter = ['GB', 'DET', 'KC', 'DAL', 'CIN', 'BAL']
                st.rerun()

        with col2:
            if st.button("Clear Team Filter", use_container_width=True):
                team_filter = []
                st.rerun()

        # Apply filters
        filtered = props

        if position_filter != 'All':
            filtered = [p for p in filtered if p.prop.position == position_filter]

        if team_filter:
            filtered = [p for p in filtered if p.prop.team in team_filter]

        if bet_type_filter != 'All':
            filtered = [p for p in filtered if getattr(p.prop, 'bet_type', 'OVER') == bet_type_filter]

        filtered = [p for p in filtered if p.final_confidence >= min_conf]

        # Sort
        if sort_by == "Confidence":
            filtered = sorted(filtered, key=lambda x: x.final_confidence, reverse=True)
        elif sort_by == "Player":
            filtered = sorted(filtered, key=lambda x: x.prop.player_name)
        elif sort_by == "Team":
            filtered = sorted(filtered, key=lambda x: x.prop.team)

        st.markdown(f"**Showing {len(filtered)} props**")
        st.markdown("---")

        # Display props in a table
        if filtered:
            data = []
            for analysis in filtered:
                prop = analysis.prop
                data.append({
                    'Player': prop.player_name,
                    'Team': prop.team,
                    'Opp': prop.opponent,
                    'Pos': prop.position,
                    'Stat': prop.stat_type,
                    'Type': getattr(prop, 'bet_type', 'OVER'),
                    'Line': prop.line,
                    'Conf': f"{analysis.final_confidence}%"
                })

            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, height=600)

elif page == "🎲 Parlay Builder":
    st.title("🎲 Parlay Builder")

    if not st.session_state.data_loaded:
        st.info("👈 Load data first")
    else:
        st.markdown("### Settings")

        col1, col2 = st.columns(2)

        with col1:
            min_confidence = st.number_input("Min Confidence", 40, 100, 58)

        with col2:
            # Team filter for parlays
            all_teams = sorted(list(set(p.prop.team for p in st.session_state.analyzed_props)))
            filter_teams = st.multiselect("Filter to Teams (optional)", all_teams, default=[])

        # Quick filter for Thursday games
        col1, col2 = st.columns(2)

        with col1:
            thursday_filter = st.checkbox("Thursday Games Only (GB, DET, KC, DAL, CIN, BAL)")

        with col2:
            if thursday_filter:
                filter_teams = ['GB', 'DET', 'KC', 'DAL', 'CIN', 'BAL']
                st.info(f"Filtering to: {', '.join(filter_teams)}")

        if st.button("🎲 Generate Parlays", type="primary"):
            with st.spinner("Building parlays..."):
                # Filter props if teams selected
                props_to_use = st.session_state.analyzed_props
                if filter_teams:
                    props_to_use = [p for p in props_to_use if p.prop.team in filter_teams]
                    st.info(f"Building from {len(props_to_use)} props (filtered by teams)")

                builder = ParlayBuilder()
                parlays = builder.build_parlays(
                    props_to_use,
                    min_confidence=min_confidence
                )
                st.session_state.parlays = parlays
                st.success(f"✅ Built {sum(len(p) for p in parlays.values())} parlays")
                st.rerun()

        if st.session_state.parlays:
            st.markdown("---")

            # Display parlays by type
            for parlay_type in ['2-leg', '3-leg', '4-leg', '5-leg']:
                if parlay_type in st.session_state.parlays:
                    parlay_list = st.session_state.parlays[parlay_type]

                    if parlay_list:
                        st.subheader(f"📊 {parlay_type.upper()} Parlays ({len(parlay_list)})")

                        for i, parlay in enumerate(parlay_list, 1):
                            with st.expander(f"Parlay #{i} - Confidence: {parlay.combined_confidence}%"):
                                st.markdown(f"**{parlay.rationale}**")
                                st.caption(f"Risk: {parlay.risk_level}")

                                st.markdown("#### Legs:")
                                for j, leg in enumerate(parlay.legs, 1):
                                    bet_type = getattr(leg.prop, 'bet_type', 'OVER')
                                    st.markdown(f"""
                                    **{j}. {leg.prop.player_name}** ({leg.prop.team})
                                    - {leg.prop.stat_type} {bet_type} {leg.prop.line}
                                    - vs {leg.prop.opponent} | Confidence: {leg.final_confidence}%
                                    """)

elif page == "✅ Validation":
    st.title("✅ Parlay Validation")

    if st.session_state.parlays is None:
        st.info("👈 Generate parlays first in the Parlay Builder")
    else:
        st.markdown("Use the validation UI for the best experience:")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.code("streamlit run validation_ui.py")

        with col2:
            st.markdown("Or run: `run_validation_ui.bat`")

        st.markdown("---")

        # Quick stats
        validator = PropAvailabilityValidator('bets.db')
        stats = validator.get_validation_stats()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Validation Rules", stats['total_rules'])

        with col2:
            st.metric("Props Marked Available", stats['props_marked_available'])

        with col3:
            st.metric("Props Marked Unavailable", stats['props_marked_unavailable'])

elif page == "📊 Performance":
    st.title("📊 Performance Tracking")

    try:
        tracker = PerformanceTracker(db_path="bets.db")

        # Get all completed parlays
        results = tracker.get_all_results()

        if results:
            st.markdown("### Completed Parlays")

            # Summary metrics
            total_parlays = len(results)
            hits = len([r for r in results if r['result'] == 'HIT'])
            misses = len([r for r in results if r['result'] == 'MISS'])
            win_rate = (hits / total_parlays * 100) if total_parlays > 0 else 0

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Parlays", total_parlays)
            col2.metric("Hits", hits)
            col3.metric("Misses", misses)
            col4.metric("Win Rate", f"{win_rate:.1f}%")

            st.markdown("---")

            # Recent results table
            data = []
            for parlay in results[:20]:  # Show last 20
                data.append({
                    'ID': parlay.get('parlay_id', 'N/A'),
                    'Week': parlay.get('week', 'N/A'),
                    'Legs': parlay.get('leg_count', 'N/A'),
                    'Confidence': f"{parlay.get('confidence_score', 0)}%",
                    'Result': parlay.get('result', 'N/A')
                })

            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No completed parlays yet. Score some parlays to see performance data!")
            st.markdown("""
            **To track performance:**
            1. Generate parlays
            2. Place bets
            3. Use CLI to score results: `score-week <week>`
            4. Return here to see stats
            """)

        st.markdown("---")

        # Calibration
        st.markdown("### Agent Calibration")

        try:
            calibrator = AgentCalibrator(db_path="bets.db")
            st.info("📊 For detailed calibration analysis, use CLI: `calibrate-agents`")

            # Show if there's calibration data
            if results:
                st.caption(f"Calibration available for {total_parlays} completed parlays")
        except Exception as e:
            st.info("No calibration data yet")

    except Exception as e:
        st.error(f"Error loading performance data: {e}")
        import traceback
        st.code(traceback.format_exc())

elif page == "⚙️ Settings":
    st.title("⚙️ Settings")

    st.markdown("### System Configuration")

    # Data directory
    data_dir = st.text_input("Data Directory", value="data")

    # Database path
    db_path = st.text_input("Database Path", value="bets.db")

    # Default confidence
    default_conf = st.slider("Default Min Confidence", 0, 100, 58)

    st.markdown("---")

    st.markdown("### Validation System")

    validator = PropAvailabilityValidator('bets.db')
    stats = validator.get_validation_stats()

    st.info(f"""
    **Current Stats:**
    - Validation Rules: {stats['total_rules']}
    - Props Marked Available: {stats['props_marked_available']}
    - Props Marked Unavailable: {stats['props_marked_unavailable']}
    """)

    if st.button("Clear Prop Availability Data"):
        if st.checkbox("Confirm clear availability data"):
            import sqlite3
            conn = sqlite3.connect('bets.db')
            conn.execute('DELETE FROM prop_availability')
            conn.commit()
            conn.close()
            st.success("✅ Cleared prop availability data")
            st.rerun()

    st.markdown("---")

    st.markdown("### About")
    st.info("""
    **NFL Betting System**

    Features:
    - 8 AI agents for prop analysis
    - Automated parlay generation
    - DraftKings Pick6 validation
    - Performance tracking
    - Agent calibration

    Built with Streamlit & Claude Code
    """)

# Footer
st.markdown("---")
st.caption(f"NFL Betting System | Week {st.session_state.week} | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
