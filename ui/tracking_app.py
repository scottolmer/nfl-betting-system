#!/usr/bin/env python
"""Streamlined Bet Tracking & Performance Analysis v2.0

Improvements:
- Unified results entry (no separate tabs for input vs viewing)
- Batch result logging with checkboxes
- Better performance statistics
- Edit/undo capabilities
- Export data for external analysis
- Real-time statistics updates
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys

# Add project root
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from scripts.analysis.parlay_tracker import ParlayTracker

st.set_page_config(
    page_title="🏈 Bet Tracking",
    page_icon="🏈",
    layout="wide"
)

# ============================================================================
# INITIALIZE
# ============================================================================

@st.cache_resource
def get_tracker():
    return ParlayTracker(str(project_root / "parlay_tracking.json"))

tracker = get_tracker()

# ============================================================================
# PAGE LAYOUT
# ============================================================================

st.title("🏈 Bet Tracking & Performance")

tab1, tab2, tab3 = st.tabs(["📋 Log Results", "📊 Performance", "📥 Export"])

# ============================================================================
# TAB 1: LOG RESULTS
# ============================================================================

with tab1:
    st.header("📋 Enter Parlay Results")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        week = st.number_input("Week", 1, 18, 9)
        status_filter = st.radio(
            "Show",
            ["All", "Pending Only", "Completed"]
        )
    
    with col2:
        st.write("")  # Spacer
    
    parlays = tracker.get_parlays_by_week(week)
    
    if not parlays:
        st.warning(f"❌ No tracked parlays for Week {week}")
        st.info("💡 Generate parlays in main app first, then log them here")
    else:
        # Filter based on selection
        if status_filter == "Pending Only":
            parlays = [p for p in parlays if p.get('result') == 'pending']
        elif status_filter == "Completed":
            parlays = [p for p in parlays if p.get('result') != 'pending']
        
        st.info(f"📊 {len(parlays)} parlays to review")
        
        if len(parlays) > 0:
            st.subheader("Parlay Results")
            
            # Create two columns for better UX
            col1, col2 = st.columns([3, 1])
            
            for parlay in parlays:
                parlay_id = parlay['parlay_id']
                conf = parlay.get('effective_confidence', parlay.get('confidence', 0))
                current_status = parlay.get('result', 'pending')
                bet_on = parlay.get('bet_on', False)
                amount = parlay.get('actual_bet_amount', 0)
                
                # Status emoji and color
                status_info = {
                    'won': ('✅ WON', 'green'),
                    'lost': ('❌ LOST', 'red'),
                    'pending': ('⏳ PENDING', 'gray'),
                    'push': ('🟡 PUSH', 'orange')
                }
                
                status_text, status_color = status_info.get(current_status, ('❓ UNKNOWN', 'gray'))
                
                # Confidence color
                if conf >= 80:
                    conf_color = '🔥'
                elif conf >= 70:
                    conf_color = '⚠️'
                else:
                    conf_color = '❌'
                
                # Parlay display
                with st.container(border=True):
                    # Header row
                    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{parlay_id}**")
                    with col2:
                        st.write(f"{conf_color} {conf:.1f}%")
                    with col3:
                        st.write(f"{'💰' if bet_on else '📊'} ${amount:.2f}" if bet_on else "Data Only")
                    with col4:
                        st.write(f"{status_text}")
                    with col5:
                        if st.button("ℹ️ Details", key=f"info_{parlay_id}"):
                            st.session_state[f"show_details_{parlay_id}"] = not st.session_state.get(f"show_details_{parlay_id}", False)
                    
                    # Show details if requested
                    if st.session_state.get(f"show_details_{parlay_id}", False):
                        st.divider()
                        
                        # Legs
                        st.write("**Parlay Legs:**")
                        legs_data = []
                        for prop in parlay.get('props', []):
                            legs_data.append({
                                "Player": prop['player'],
                                "Stat": prop['stat_type'],
                                "Direction": prop['direction'],
                                "Line": prop['line'],
                                "Conf": f"{prop.get('confidence', 0):.1f}%"
                            })
                        
                        if legs_data:
                            st.dataframe(
                                pd.DataFrame(legs_data),
                                use_container_width=True,
                                hide_index=True
                            )
                        
                        # Metadata
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Base Confidence", f"{parlay.get('confidence', 0):.1f}%")
                        with col2:
                            st.metric("Effective Confidence", f"{conf:.1f}%")
                        with col3:
                            st.metric("Created", parlay.get('created_date', 'N/A'))
                        
                        st.divider()
                    
                    # Result buttons (more compact)
                    if current_status == 'pending':
                        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
                        
                        with btn_col1:
                            if st.button("✅ Won", key=f"won_{parlay_id}", use_container_width=True):
                                tracker.mark_result(parlay_id, "won")
                                st.success("Marked as WON!")
                                st.rerun()
                        
                        with btn_col2:
                            if st.button("❌ Lost", key=f"lost_{parlay_id}", use_container_width=True):
                                tracker.mark_result(parlay_id, "lost")
                                st.error("Marked as LOST")
                                st.rerun()
                        
                        with btn_col3:
                            if st.button("🟡 Push", key=f"push_{parlay_id}", use_container_width=True):
                                tracker.mark_result(parlay_id, "push")
                                st.info("Marked as PUSH")
                                st.rerun()
                        
                        with btn_col4:
                            if st.button("⏸️ Pending", key=f"skip_{parlay_id}", use_container_width=True):
                                st.info("Staying pending")
                    else:
                        if st.button("🔄 Change Result", key=f"change_{parlay_id}", use_container_width=True):
                            tracker.mark_result(parlay_id, "pending")
                            st.info("Reset to pending")
                            st.rerun()

# ============================================================================
# TAB 2: PERFORMANCE ANALYSIS
# ============================================================================

with tab2:
    st.header("📊 Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        analysis_type = st.radio(
            "View",
            ["Overall", "By Week", "By Type", "Comparison"]
        )
    
    with col2:
        st.write("")  # Spacer
    
    st.divider()
    
    if analysis_type == "Overall":
        # Overall performance
        st.subheader("Overall Performance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        overall_stats = tracker.get_statistics()
        
        if overall_stats:
            with col1:
                st.metric("Total Record", f"{overall_stats['won']}-{overall_stats['lost']}")
            with col2:
                win_rate = overall_stats.get('win_rate', 0)
                st.metric("Win Rate", f"{win_rate:.1f}%")
            with col3:
                pred = overall_stats.get('avg_predicted_confidence', 0)
                st.metric("Average Confidence", f"{pred:.1f}%")
            with col4:
                calib = overall_stats.get('calibration_error', 0)
                st.metric("Calibration Error", f"{calib:+.1f} pts")
            
            st.divider()
            
            # Comparison by parlay type
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("📊 2-Leg")
                stats_2 = tracker.get_statistics(parlay_legs=2)
                if stats_2:
                    st.metric("Win Rate", f"{stats_2.get('win_rate', 0):.1f}%")
                    st.metric("Count", f"{stats_2['won'] + stats_2['lost']}")
            
            with col2:
                st.subheader("📊 3-Leg")
                stats_3 = tracker.get_statistics(parlay_legs=3)
                if stats_3:
                    st.metric("Win Rate", f"{stats_3.get('win_rate', 0):.1f}%")
                    st.metric("Count", f"{stats_3['won'] + stats_3['lost']}")
            
            with col3:
                st.subheader("📊 4-Leg")
                stats_4 = tracker.get_statistics(parlay_legs=4)
                if stats_4:
                    st.metric("Win Rate", f"{stats_4.get('win_rate', 0):.1f}%")
                    st.metric("Count", f"{stats_4['won'] + stats_4['lost']}")
    
    elif analysis_type == "By Week":
        st.subheader("Week-by-Week Performance")
        
        weeks = sorted(tracker.data.get("metadata", {}).get("weeks_tracked", []))
        
        if not weeks:
            st.info("No data tracked yet")
        else:
            week_data = []
            for w in weeks:
                stats = tracker.get_statistics(weeks=[w])
                if stats and (stats['won'] + stats['lost']) > 0:
                    week_data.append({
                        'Week': w,
                        'Wins': stats['won'],
                        'Losses': stats['lost'],
                        'Win Rate %': stats.get('win_rate', 0),
                        'Avg Confidence %': stats.get('avg_predicted_confidence', 0),
                        'Calibration': stats.get('calibration_error', 0),
                    })
            
            if week_data:
                df_weeks = pd.DataFrame(week_data)
                st.dataframe(df_weeks, use_container_width=True, hide_index=True)
                
                # Chart
                if len(week_data) > 1:
                    fig = px.line(
                        df_weeks,
                        x='Week',
                        y=['Win Rate %', 'Avg Confidence %'],
                        title='Performance Trend',
                        markers=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "By Type":
        st.subheader("Performance by Parlay Type")
        
        type_data = []
        for leg_count in [2, 3, 4, 5]:
            stats = tracker.get_statistics(parlay_legs=leg_count)
            if stats and (stats['won'] + stats['lost']) > 0:
                type_data.append({
                    'Type': f"{leg_count}-Leg",
                    'Wins': stats['won'],
                    'Losses': stats['lost'],
                    'Win Rate %': stats.get('win_rate', 0),
                    'ROI %': stats.get('roi', 0),
                })
        
        if type_data:
            df_types = pd.DataFrame(type_data)
            st.dataframe(df_types, use_container_width=True, hide_index=True)
            
            # Chart
            fig = px.bar(
                df_types,
                x='Type',
                y='Win Rate %',
                title='Win Rate by Parlay Type',
                color='Win Rate %',
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    else:  # Comparison
        st.subheader("Traditional vs Enhanced Parlays")
        
        trad = tracker.get_statistics(parlay_type="traditional")
        enh = tracker.get_statistics(parlay_type="enhanced")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Traditional Parlays**")
            if trad:
                st.metric("Win Rate", f"{trad.get('win_rate', 0):.1f}%")
                st.metric("Avg Confidence", f"{trad.get('avg_predicted_confidence', 0):.1f}%")
                st.metric("ROI", f"{trad.get('roi', 0):+.1f}%")
            else:
                st.info("No data")
        
        with col2:
            st.write("**Enhanced Parlays**")
            if enh:
                st.metric("Win Rate", f"{enh.get('win_rate', 0):.1f}%")
                st.metric("Avg Confidence", f"{enh.get('avg_predicted_confidence', 0):.1f}%")
                st.metric("ROI", f"{enh.get('roi', 0):+.1f}%")
            else:
                st.info("No data")

# ============================================================================
# TAB 3: EXPORT
# ============================================================================

with tab3:
    st.header("📥 Export Data")
    
    export_type = st.radio(
        "Export Format",
        ["CSV", "JSON"]
    )
    
    if st.button("📥 Download", use_container_width=True, type="primary"):
        if export_type == "CSV":
            # Export to CSV
            all_parlays = []
            for week, parlays in tracker.data.get("parlays", {}).items():
                for parlay in parlays:
                    parlay_copy = parlay.copy()
                    parlay_copy['week'] = week
                    all_parlays.append(parlay_copy)
            
            if all_parlays:
                # Flatten for CSV
                csv_data = []
                for p in all_parlays:
                    for i, prop in enumerate(p.get('props', []), 1):
                        row = {
                            'parlay_id': p['parlay_id'],
                            'week': p['week'],
                            'confidence': p.get('confidence', 0),
                            'result': p.get('result', 'pending'),
                            'leg': i,
                            'player': prop['player'],
                            'stat_type': prop['stat_type'],
                            'direction': prop['direction'],
                            'line': prop['line'],
                        }
                        csv_data.append(row)
                
                df_export = pd.DataFrame(csv_data)
                csv_str = df_export.to_csv(index=False)
                
                st.download_button(
                    "📥 Download CSV",
                    csv_str,
                    "parlay_tracking_export.csv",
                    "text/csv"
                )
                
                st.success(f"✅ {len(all_parlays)} parlays ready to export")
            else:
                st.warning("No data to export")
        
        else:  # JSON
            import json
            
            json_str = json.dumps(tracker.data, indent=2)
            
            st.download_button(
                "📥 Download JSON",
                json_str,
                "parlay_tracking_export.json",
                "application/json"
            )
            
            st.success("✅ Data ready to export")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #888;'>
    <small>🏈 Bet Tracking v2.0 | Performance Analysis</small>
    </div>
    """,
    unsafe_allow_html=True
)