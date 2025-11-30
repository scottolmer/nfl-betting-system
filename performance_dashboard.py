"""
Performance Analytics Dashboard
Real-time visualization of betting system performance
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
from collections import defaultdict
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Performance Analytics",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .big-metric {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
    }
    .metric-label {
        font-size: 16px;
        text-align: center;
        color: gray;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_performance_data():
    """Load all scored props from database"""
    conn = sqlite3.connect('bets.db')

    query = """
    SELECT
        prop_id, week, player, team, opponent,
        prop_type, bet_type, line, confidence,
        agent_scores, result, actual_value, scored_date
    FROM analyzed_props
    WHERE result IS NOT NULL
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df

def calculate_agent_stats(df):
    """Calculate per-agent performance statistics"""
    agent_stats = defaultdict(lambda: {
        'correct': 0, 'total': 0,
        'positive_correct': 0, 'positive_total': 0,
        'negative_correct': 0, 'negative_total': 0
    })

    for _, row in df.iterrows():
        if pd.notna(row['agent_scores']):
            try:
                agents = json.loads(row['agent_scores'])
                result = row['result']

                for agent, score in agents.items():
                    if score != 50:
                        agent_stats[agent]['total'] += 1

                        # If agent was correct in direction
                        if (score > 50 and result == 1) or (score < 50 and result == 0):
                            agent_stats[agent]['correct'] += 1

                        # Track positive predictions
                        if score > 50:
                            agent_stats[agent]['positive_total'] += 1
                            if result == 1:
                                agent_stats[agent]['positive_correct'] += 1

                        # Track negative predictions
                        if score < 50:
                            agent_stats[agent]['negative_total'] += 1
                            if result == 0:
                                agent_stats[agent]['negative_correct'] += 1
            except:
                pass

    return agent_stats

# Load data
df = load_performance_data()

if len(df) == 0:
    st.error("No performance data found. Make sure props have been scored in the database.")
    st.stop()

# Title
st.title("📊 Performance Analytics Dashboard")
st.markdown(f"*Analyzing {len(df)} scored props*")

# Top-level metrics
col1, col2, col3, col4 = st.columns(4)

total = len(df)
wins = int(df['result'].sum())
accuracy = (wins / total) * 100

with col1:
    st.markdown(f"<div class='metric-label'>Overall Accuracy</div>", unsafe_allow_html=True)
    color = "green" if accuracy >= 60 else "orange" if accuracy >= 52.4 else "red"
    st.markdown(f"<div class='big-metric' style='color: {color};'>{accuracy:.1f}%</div>", unsafe_allow_html=True)
    st.caption(f"{wins} wins / {total} total")

with col2:
    high_conf = df[df['confidence'] >= 70]
    if len(high_conf) > 0:
        hc_accuracy = (high_conf['result'].sum() / len(high_conf)) * 100
    else:
        hc_accuracy = 0
    st.markdown(f"<div class='metric-label'>70+ Confidence</div>", unsafe_allow_html=True)
    color = "green" if hc_accuracy >= 65 else "orange" if hc_accuracy >= 55 else "red"
    st.markdown(f"<div class='big-metric' style='color: {color};'>{hc_accuracy:.1f}%</div>", unsafe_allow_html=True)
    st.caption(f"{len(high_conf)} props")

with col3:
    over_df = df[df['bet_type'] == 'OVER']
    over_acc = (over_df['result'].sum() / len(over_df)) * 100 if len(over_df) > 0 else 0
    st.markdown(f"<div class='metric-label'>OVER Accuracy</div>", unsafe_allow_html=True)
    color = "green" if over_acc >= 60 else "orange" if over_acc >= 52.4 else "red"
    st.markdown(f"<div class='big-metric' style='color: {color};'>{over_acc:.1f}%</div>", unsafe_allow_html=True)
    st.caption(f"{len(over_df)} props")

with col4:
    under_df = df[df['bet_type'] == 'UNDER']
    under_acc = (under_df['result'].sum() / len(under_df)) * 100 if len(under_df) > 0 else 0
    st.markdown(f"<div class='metric-label'>UNDER Accuracy</div>", unsafe_allow_html=True)
    color = "green" if under_acc >= 60 else "orange" if under_acc >= 52.4 else "red"
    st.markdown(f"<div class='big-metric' style='color: {color};'>{under_acc:.1f}%</div>", unsafe_allow_html=True)
    st.caption(f"{len(under_df)} props")

st.markdown("---")

# Two columns for charts
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Accuracy by Confidence Level")

    # Create confidence buckets
    df['conf_bucket'] = pd.cut(df['confidence'],
                                bins=[0, 50, 55, 60, 65, 70, 75, 80, 85, 90, 100],
                                labels=['<50', '50-55', '55-60', '60-65', '65-70',
                                       '70-75', '75-80', '80-85', '85-90', '90+'])

    conf_stats = df.groupby('conf_bucket', observed=True).agg({
        'result': ['count', 'sum', 'mean']
    }).reset_index()

    conf_stats.columns = ['bucket', 'count', 'wins', 'accuracy']
    conf_stats['accuracy'] = conf_stats['accuracy'] * 100

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=conf_stats['bucket'],
        y=conf_stats['accuracy'],
        text=conf_stats['accuracy'].round(1),
        texttemplate='%{text}%',
        textposition='outside',
        marker_color=['red' if x < 52.4 else 'orange' if x < 60 else 'green'
                     for x in conf_stats['accuracy']]
    ))

    fig.add_hline(y=52.4, line_dash="dash", line_color="gray",
                  annotation_text="Break-even (52.4%)", annotation_position="right")

    fig.update_layout(
        xaxis_title="Confidence Level",
        yaxis_title="Win Rate %",
        yaxis_range=[0, 100],
        height=400,
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # Show sample sizes
    st.caption("Sample sizes: " + ", ".join([f"{row['bucket']}: {int(row['count'])}"
                                              for _, row in conf_stats.iterrows()]))

with chart_col2:
    st.subheader("Weekly Performance Trend")

    weekly = df.groupby('week').agg({
        'result': ['count', 'sum', 'mean']
    }).reset_index()

    weekly.columns = ['week', 'count', 'wins', 'accuracy']
    weekly['accuracy'] = weekly['accuracy'] * 100

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=weekly['week'],
        y=weekly['accuracy'],
        mode='lines+markers+text',
        text=weekly['accuracy'].round(1),
        texttemplate='%{text}%',
        textposition='top center',
        line=dict(color='blue', width=3),
        marker=dict(size=12, color=weekly['accuracy'],
                   colorscale=[[0, 'red'], [0.524, 'orange'], [1, 'green']],
                   cmin=0, cmax=100)
    ))

    fig.add_hline(y=52.4, line_dash="dash", line_color="gray",
                  annotation_text="Break-even", annotation_position="left")

    fig.update_layout(
        xaxis_title="Week",
        yaxis_title="Win Rate %",
        yaxis_range=[0, 100],
        height=400,
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption("Sample sizes: " + ", ".join([f"Wk{int(row['week'])}: {int(row['count'])}"
                                              for _, row in weekly.iterrows()]))

st.markdown("---")

# Agent Performance
st.subheader("🤖 Agent Performance Analysis")

agent_stats = calculate_agent_stats(df)

agent_df = []
for agent, stats in agent_stats.items():
    if stats['total'] >= 10:
        overall_acc = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0

        pos_acc = (stats['positive_correct'] / stats['positive_total']) * 100 if stats['positive_total'] > 0 else None
        neg_acc = (stats['negative_correct'] / stats['negative_total']) * 100 if stats['negative_total'] > 0 else None

        agent_df.append({
            'Agent': agent,
            'Total': stats['total'],
            'Overall Accuracy': overall_acc,
            'Positive Acc': pos_acc,
            'Positive Count': stats['positive_total'],
            'Negative Acc': neg_acc,
            'Negative Count': stats['negative_total']
        })

agent_df = pd.DataFrame(agent_df).sort_values('Total', ascending=False)

# Display agent table with color coding
st.dataframe(
    agent_df.style.format({
        'Overall Accuracy': '{:.1f}%',
        'Positive Acc': '{:.1f}%',
        'Negative Acc': '{:.1f}%',
        'Total': '{:.0f}',
        'Positive Count': '{:.0f}',
        'Negative Count': '{:.0f}'
    }).background_gradient(subset=['Overall Accuracy'], cmap='RdYlGn', vmin=0, vmax=100),
    use_container_width=True
)

st.caption("⚠️ **Low accuracy agents may need recalibration or removal**")

st.markdown("---")

# Prop Type Performance
col1, col2 = st.columns(2)

with col1:
    st.subheader("Performance by Prop Type")

    prop_stats = df.groupby('prop_type').agg({
        'result': ['count', 'sum', 'mean']
    }).reset_index()

    prop_stats.columns = ['prop_type', 'count', 'wins', 'accuracy']
    prop_stats['accuracy'] = prop_stats['accuracy'] * 100
    prop_stats = prop_stats[prop_stats['count'] >= 5].sort_values('count', ascending=False)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=prop_stats['prop_type'][:10],
        x=prop_stats['accuracy'][:10],
        orientation='h',
        text=prop_stats['accuracy'][:10].round(1),
        texttemplate='%{text}%',
        textposition='outside',
        marker_color=['red' if x < 52.4 else 'orange' if x < 60 else 'green'
                     for x in prop_stats['accuracy'][:10]]
    ))

    fig.add_vline(x=52.4, line_dash="dash", line_color="gray")

    fig.update_layout(
        xaxis_title="Win Rate %",
        yaxis_title="Prop Type",
        xaxis_range=[0, 100],
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("ROI by Confidence Level")

    # Calculate ROI for each confidence bucket
    roi_data = []

    for bucket in conf_stats['bucket']:
        bucket_df = df[df['conf_bucket'] == bucket]
        count = len(bucket_df)
        wins = int(bucket_df['result'].sum())
        losses = count - wins

        profit = (wins * 100) - (losses * 110)
        risked = count * 110
        roi = (profit / risked) * 100 if risked > 0 else 0

        roi_data.append({
            'bucket': bucket,
            'roi': roi,
            'profit': profit,
            'count': count
        })

    roi_df = pd.DataFrame(roi_data)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=roi_df['bucket'],
        y=roi_df['roi'],
        text=roi_df['roi'].round(1),
        texttemplate='%{text}%',
        textposition='outside',
        marker_color=['red' if x < 0 else 'green' for x in roi_df['roi']]
    ))

    fig.add_hline(y=0, line_dash="solid", line_color="black")

    fig.update_layout(
        xaxis_title="Confidence Level",
        yaxis_title="ROI %",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # Show recommendation
    profitable_buckets = roi_df[roi_df['roi'] > 0]['bucket'].tolist()
    if profitable_buckets:
        st.success(f"✅ **Profitable confidence ranges:** {', '.join(profitable_buckets)}")
    else:
        st.warning("⚠️ No confidence ranges are currently profitable")

st.markdown("---")

# Recent Performance
st.subheader("📋 Recent Scored Props")

recent = df.sort_values('scored_date', ascending=False).head(50)

display_df = recent[['week', 'player', 'prop_type', 'bet_type', 'line',
                     'confidence', 'actual_value', 'result']].copy()

display_df['result_str'] = display_df['result'].map({1: '✅ WIN', 0: '❌ LOSS'})
display_df = display_df.drop('result', axis=1)
display_df.columns = ['Week', 'Player', 'Prop Type', 'Direction', 'Line',
                      'Confidence', 'Actual', 'Result']

st.dataframe(
    display_df.style.format({
        'Confidence': '{:.1f}',
        'Line': '{:.1f}',
        'Actual': '{:.1f}'
    }).apply(lambda x: ['background-color: #d4f4dd' if v == '✅ WIN'
                        else 'background-color: #ffd4d4' if v == '❌ LOSS'
                        else '' for v in x], subset=['Result']),
    use_container_width=True,
    height=600
)

# Footer
st.markdown("---")
st.caption("📊 Performance Dashboard | Refresh to update data")
