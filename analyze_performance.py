"""
Performance Analytics Tool
Analyzes historical prop performance to calculate accuracy and ROI
"""

import sqlite3
import pandas as pd
import json
from collections import defaultdict

def analyze_performance():
    """Analyze all scored props and generate performance report"""

    conn = sqlite3.connect('bets.db')

    # Get all scored props with agent data
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

    if len(df) == 0:
        print("No scored props found!")
        return

    print(f"\n{'='*80}")
    print(f"PERFORMANCE ANALYSIS REPORT")
    print(f"{'='*80}\n")

    # Overall accuracy
    total = len(df)
    wins = df['result'].sum()
    accuracy = (wins / total) * 100

    print(f"OVERALL PERFORMANCE")
    print(f"{'-'*80}")
    print(f"Total Props Analyzed: {total}")
    print(f"Wins: {wins}")
    print(f"Losses: {total - wins}")
    print(f"Accuracy: {accuracy:.2f}%\n")

    # Accuracy by confidence level
    print(f"ACCURACY BY CONFIDENCE LEVEL")
    print(f"{'-'*80}")

    # Create confidence buckets
    df['conf_bucket'] = pd.cut(df['confidence'],
                                bins=[0, 50, 60, 70, 80, 90, 100],
                                labels=['<50', '50-60', '60-70', '70-80', '80-90', '90+'])

    conf_analysis = df.groupby('conf_bucket').agg({
        'result': ['count', 'sum', 'mean']
    }).round(4)

    for bucket in conf_analysis.index:
        count = int(conf_analysis.loc[bucket, ('result', 'count')])
        wins = int(conf_analysis.loc[bucket, ('result', 'sum')])
        rate = conf_analysis.loc[bucket, ('result', 'mean')] * 100

        if count > 0:
            print(f"{bucket:>8}: {wins:>3}/{count:<3} = {rate:>5.1f}%")

    # Accuracy by bet type
    print(f"\nACCURACY BY BET TYPE")
    print(f"{'-'*80}")

    bet_analysis = df.groupby('bet_type').agg({
        'result': ['count', 'sum', 'mean']
    }).round(4)

    for bet_type in bet_analysis.index:
        count = int(bet_analysis.loc[bet_type, ('result', 'count')])
        wins = int(bet_analysis.loc[bet_type, ('result', 'sum')])
        rate = bet_analysis.loc[bet_type, ('result', 'mean')] * 100

        print(f"{bet_type:>8}: {wins:>3}/{count:<3} = {rate:>5.1f}%")

    # Accuracy by prop type
    print(f"\nACCURACY BY PROP TYPE")
    print(f"{'-'*80}")

    prop_analysis = df.groupby('prop_type').agg({
        'result': ['count', 'sum', 'mean']
    }).sort_values(('result', 'count'), ascending=False).round(4)

    for prop_type in prop_analysis.index[:10]:  # Top 10
        count = int(prop_analysis.loc[prop_type, ('result', 'count')])
        wins = int(prop_analysis.loc[prop_type, ('result', 'sum')])
        rate = prop_analysis.loc[prop_type, ('result', 'mean')] * 100

        if count >= 5:  # Only show types with 5+ samples
            print(f"{prop_type[:30]:30}: {wins:>3}/{count:<3} = {rate:>5.1f}%")

    # Agent performance
    print(f"\nAGENT PERFORMANCE ANALYSIS")
    print(f"{'-'*80}")

    agent_stats = defaultdict(lambda: {'correct': 0, 'total': 0, 'positive_correct': 0, 'positive_total': 0})

    for _, row in df.iterrows():
        if pd.notna(row['agent_scores']):
            try:
                agents = json.loads(row['agent_scores'])
                result = row['result']

                for agent, score in agents.items():
                    if score != 50:  # Only count non-neutral scores
                        agent_stats[agent]['total'] += 1

                        # If agent was positive (>50) and we won, or negative (<50) and we lost
                        if (score > 50 and result == 1) or (score < 50 and result == 0):
                            agent_stats[agent]['correct'] += 1

                        # Track positive predictions separately
                        if score > 50:
                            agent_stats[agent]['positive_total'] += 1
                            if result == 1:
                                agent_stats[agent]['positive_correct'] += 1
            except:
                pass

    # Sort by total predictions
    sorted_agents = sorted(agent_stats.items(), key=lambda x: x[1]['total'], reverse=True)

    print(f"{'Agent':<25} {'Accuracy':>10} {'Positive Acc':>15} {'Count':>8}")
    print(f"{'-'*80}")

    for agent, stats in sorted_agents:
        if stats['total'] >= 10:  # Only show agents with 10+ predictions
            accuracy = (stats['correct'] / stats['total']) * 100

            if stats['positive_total'] > 0:
                pos_acc = (stats['positive_correct'] / stats['positive_total']) * 100
                pos_str = f"{pos_acc:>5.1f}% ({stats['positive_correct']}/{stats['positive_total']})"
            else:
                pos_str = "N/A"

            print(f"{agent[:25]:<25} {accuracy:>5.1f}% {pos_str:>20} {stats['total']:>8}")

    # Weekly performance
    print(f"\nWEEKLY PERFORMANCE")
    print(f"{'-'*80}")

    weekly = df.groupby('week').agg({
        'result': ['count', 'sum', 'mean']
    }).sort_index().round(4)

    for week in weekly.index:
        count = int(weekly.loc[week, ('result', 'count')])
        wins = int(weekly.loc[week, ('result', 'sum')])
        rate = weekly.loc[week, ('result', 'mean')] * 100

        print(f"Week {week:>2}: {wins:>3}/{count:<3} = {rate:>5.1f}%")

    # ROI Analysis (simplified - assumes -110 odds)
    print(f"\nROI ANALYSIS (assuming -110 odds)")
    print(f"{'-'*80}")

    # At -110 odds, you risk $110 to win $100
    # So ROI = (Wins * 100 - Losses * 110) / (Total * 110)

    losses = total - wins
    profit = (wins * 100) - (losses * 110)
    total_risked = total * 110
    roi = (profit / total_risked) * 100

    print(f"Total Props Bet: {total}")
    print(f"Total Risked: ${total_risked:,.2f} (at $110/bet)")
    print(f"Total Returned: ${wins * 210:,.2f}")
    print(f"Net Profit/Loss: ${profit:,.2f}")
    print(f"ROI: {roi:.2f}%")

    # ROI by confidence bucket
    print(f"\nROI BY CONFIDENCE LEVEL")
    print(f"{'-'*80}")

    for bucket in conf_analysis.index:
        count = int(conf_analysis.loc[bucket, ('result', 'count')])
        wins = int(conf_analysis.loc[bucket, ('result', 'sum')])

        if count > 0:
            losses = count - wins
            profit = (wins * 100) - (losses * 110)
            risked = count * 110
            roi = (profit / risked) * 100

            print(f"{bucket:>8}: ROI = {roi:>6.2f}% (${profit:>7.2f} profit on ${risked:>7.2f} risked)")

    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    analyze_performance()
