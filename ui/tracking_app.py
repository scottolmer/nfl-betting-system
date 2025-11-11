#!/usr/bin/env python
"""Simple Bet Tracking Interface - Run alongside your main app"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add project root
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from scripts.analysis.parlay_tracker import ParlayTracker

st.set_page_config(page_title="🏈 Bet Tracking", layout="wide")

# Initialize tracker
@st.cache_resource
def get_tracker():
    return ParlayTracker(str(project_root / "parlay_tracking.json"))

tracker = get_tracker()

st.title("🏈 Bet Tracking & Performance")

tab1, tab2 = st.tabs(["✅ Select Bets & Enter Results", "📈 Performance"])

# TAB 1: Bet Selection and Results
with tab1:
    week = st.number_input("Week", 1, 18, 9)
    
    parlays = tracker.get_parlays_by_week(week)
    
    if not parlays:
        st.warning(f"No tracked parlays for Week {week}")
        st.info("💡 Generate parlays in main app first, then manually add them here or use the tracking integration")
    else:
        subtab1, subtab2 = st.tabs(["📋 Select Bets", "✅ Enter Results"])
        
        with subtab1:
            st.subheader("Mark What You're Betting")
            for p in parlays:
                with st.expander(f"{p['parlay_id']} - {p['effective_confidence']:.1f}% {'💰' if p['bet_on'] else ''}"):
                    for prop in p['props']:
                        st.write(f"• {prop['player']} {prop['direction']} {prop['line']} {prop['stat_type']}")
                    
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        bet = st.checkbox("Bet", p['bet_on'], key=f"bet_{p['parlay_id']}")
                    with col2:
                        if bet:
                            amt = st.number_input("Amount", value=float(p.get('actual_bet_amount') or p['kelly_bet_size']), key=f"amt_{p['parlay_id']}")
                            if st.button("💾 Save", key=f"save_{p['parlay_id']}"):
                                tracker.mark_bet(p['parlay_id'], amt)
                                st.success("Saved!")
                                st.rerun()
        
        with subtab2:
            st.subheader("Enter Results")
            for p in parlays:
                status = "✅ WON" if p['result'] == 'won' else "❌ LOST" if p['result'] == 'lost' else "⏳ PENDING" if p['result'] == 'pending' else ""
                with st.expander(f"{p['parlay_id']} - {p['effective_confidence']:.1f}% {status}"):
                    for prop in p['props']:
                        st.write(f"• {prop['player']} {prop['direction']} {prop['line']}")
                    
                    col1, col2, col3 = st.columns(3)
                    if col1.button("✅ Won", key=f"won_{p['parlay_id']}"):
                        tracker.mark_result(p['parlay_id'], "won")
                        st.rerun()
                    if col2.button("❌ Lost", key=f"lost_{p['parlay_id']}"):
                        tracker.mark_result(p['parlay_id'], "lost")
                        st.rerun()
                    if col3.button("⏳ Pending", key=f"pend_{p['parlay_id']}"):
                        tracker.mark_result(p['parlay_id'], "pending")
                        st.rerun()
            
            # Week summary
            stats = tracker.get_statistics(weeks=[week])
            if stats:
                st.divider()
                st.subheader("Week Summary")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Record", f"{stats['won']}-{stats['lost']}")
                col2.metric("Win Rate", f"{stats['win_rate']:.1f}%")
                col3.metric("Predicted", f"{stats['avg_predicted_confidence']:.1f}%")
                col4.metric("Calibration", f"{stats['calibration_error']:+.1f} pts")

# TAB 2: Performance
with tab2:
    st.subheader("Overall Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📊 Traditional**")
        trad = tracker.get_statistics(parlay_type="traditional")
        if trad:
            st.metric("Win Rate", f"{trad['win_rate']:.1f}%")
            st.metric("Predicted", f"{trad['avg_predicted_confidence']:.1f}%")
            st.metric("Calibration", f"{trad['calibration_error']:+.1f} pts")
            if trad['bet_parlays'] > 0:
                st.metric("ROI", f"{trad['roi']:+.1f}%")
        else:
            st.info("No data yet")
    
    with col2:
        st.write("**🧠 Enhanced**")
        enh = tracker.get_statistics(parlay_type="enhanced")
        if enh:
            st.metric("Win Rate", f"{enh['win_rate']:.1f}%")
            st.metric("Predicted", f"{enh['avg_predicted_confidence']:.1f}%")
            st.metric("Calibration", f"{enh['calibration_error']:+.1f} pts")
            if enh['bet_parlays'] > 0:
                st.metric("ROI", f"{enh['roi']:+.1f}%")
        else:
            st.info("No data yet")
    
    st.divider()
    st.subheader("Week-by-Week")
    
    weeks = sorted(tracker.data.get("metadata", {}).get("weeks_tracked", []))
    for w in weeks:
        with st.expander(f"Week {w}"):
            stats = tracker.get_statistics(weeks=[w])
            if stats:
                col1, col2, col3 = st.columns(3)
                col1.metric("Record", f"{stats['won']}-{stats['lost']}")
                col2.metric("Win Rate", f"{stats['win_rate']:.1f}%")
                col3.metric("Calibration", f"{stats['calibration_error']:+.1f} pts")
