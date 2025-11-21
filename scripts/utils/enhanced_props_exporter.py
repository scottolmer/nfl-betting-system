"""
Enhanced Props Exporter - Advanced Claude integration with correlation clustering
and contradiction detection

Features:
1. Correlation Clusters - Groups related props (same player, same game, etc.)
2. Agent Breakdown Analysis - Detailed breakdown of each agent's reasoning
3. Contradiction Detection - Identifies props that disagree with each other
"""

import json
from typing import List, Dict, Tuple, Optional, Set
from datetime import datetime
from collections import defaultdict
from scripts.analysis.models import PropAnalysis


class EnhancedPropsExporter:
    """Advanced props exporter with clustering and contradiction detection"""

    def __init__(self):
        self.exported_props = []
        self.clusters = {}
        self.contradictions = []

    @staticmethod
    def analyze_correlations(props: List[PropAnalysis]) -> Dict:
        """
        Identify correlation clusters across props
        
        Cluster types:
        1. SAME_PLAYER - Multiple stats for same player
        2. SAME_GAME - Multiple players from same game
        3. OPPOSITE_BETS - Contradictory props
        4. GAME_STACK - QB + WR from same game
        """
        clusters = defaultdict(list)
        
        player_props = defaultdict(list)
        game_props = defaultdict(list)
        
        for prop in props:
            player = prop.prop.player_name.lower()
            game = f"{prop.prop.team}_{prop.prop.opponent}".lower()
            
            player_props[player].append(prop)
            game_props[game].append(prop)
        
        # Cluster 1: Same player multiple stats
        for player, player_prop_list in player_props.items():
            if len(player_prop_list) > 1:
                clusters['SAME_PLAYER'].append({
                    'player': player_prop_list[0].prop.player_name,
                    'props': player_prop_list,
                    'count': len(player_prop_list),
                    'strength': 'VERY_HIGH'
                })
        
        # Cluster 2: Same game
        for game, game_prop_list in game_props.items():
            if len(game_prop_list) > 1:
                unique_players = set(p.prop.player_name.lower() for p in game_prop_list)
                if len(unique_players) > 1:
                    clusters['SAME_GAME'].append({
                        'game': game_prop_list[0].prop.team + ' vs ' + game_prop_list[0].prop.opponent,
                        'props': game_prop_list,
                        'count': len(game_prop_list),
                        'unique_players': len(unique_players),
                        'strength': 'HIGH'
                    })
        
        # Cluster 3: Opposite bets
        opposite_stat_types = defaultdict(lambda: {'OVER': [], 'UNDER': []})
        for prop in props:
            stat_key = prop.prop.stat_type.lower()
            bet_type = prop.prop.bet_type
            opposite_stat_types[stat_key][bet_type].append(prop)
        
        for stat_type, bets in opposite_stat_types.items():
            if bets['OVER'] and bets['UNDER']:
                clusters['OPPOSITE_BETS'].append({
                    'stat_type': bets['OVER'][0].prop.stat_type,
                    'overs': bets['OVER'],
                    'unders': bets['UNDER'],
                    'strength': 'HIGH'
                })
        
        # Cluster 4: Game stacks
        for game, game_prop_list in game_props.items():
            positions = set(p.prop.position.upper() for p in game_prop_list)
            if 'QB' in positions and ('WR' in positions or 'TE' in positions):
                clusters['GAME_STACK'].append({
                    'game': game_prop_list[0].prop.team + ' vs ' + game_prop_list[0].prop.opponent,
                    'qbs': [p for p in game_prop_list if p.prop.position.upper() == 'QB'],
                    'receivers': [p for p in game_prop_list if p.prop.position.upper() in ['WR', 'TE']],
                    'strength': 'VERY_HIGH'
                })
        
        return dict(clusters)

    @staticmethod
    def detect_contradictions(props: List[PropAnalysis]) -> List[Dict]:
        """Detect contradictory props in the set"""
        contradictions = []
        
        stat_bets = defaultdict(lambda: {'OVER': [], 'UNDER': []})
        for prop in props:
            stat_key = f"{prop.prop.stat_type}_{prop.prop.player_name}".lower()
            stat_bets[stat_key][prop.prop.bet_type].append(prop)
        
        for stat_key, bets in stat_bets.items():
            if bets['OVER'] and bets['UNDER']:
                over_prop = bets['OVER'][0]
                under_prop = bets['UNDER'][0]
                
                over_conf = over_prop.final_confidence
                under_conf = under_prop.final_confidence
                
                if over_conf >= 65 and under_conf >= 65:
                    contradictions.append({
                        'type': 'HIGH_CONF_OPPOSITE',
                        'player': over_prop.prop.player_name,
                        'stat': over_prop.prop.stat_type,
                        'severity': 'CRITICAL' if abs(over_conf - under_conf) < 10 else 'WARNING',
                        'explanation': f"Both {over_conf}% (OVER) and {under_conf}% (UNDER) have high confidence"
                    })
        
        for prop in props:
            agent_scores = prop.agent_breakdown
            scores = [v for v in agent_scores.values() if v and v != 50]
            
            if scores:
                high_scores = sum(1 for s in scores if s > 65)
                low_scores = sum(1 for s in scores if s < 35)
                
                if high_scores > 0 and low_scores > 0:
                    contradictions.append({
                        'type': 'AGENT_DISAGREEMENT',
                        'player': prop.prop.player_name,
                        'stat': prop.prop.stat_type,
                        'bet_type': prop.prop.bet_type,
                        'confidence': prop.final_confidence,
                        'bullish_agents': high_scores,
                        'bearish_agents': low_scores,
                        'severity': 'WARNING',
                        'explanation': f"Agents disagree: {high_scores} bullish, {low_scores} bearish"
                    })
        
        return contradictions

    @staticmethod
    def create_agent_profiles(props: List[PropAnalysis]) -> Dict:
        """Create detailed agent analysis profiles"""
        agent_profiles = defaultdict(lambda: {
            'bullish_props': [],
            'bearish_props': [],
            'neutral_props': [],
            'scores': [],
            'agreement_rate': 0
        })
        
        agents = ['DVOA', 'Matchup', 'Volume', 'Injury', 'Trend', 'GameScript', 'Variance', 'Weather']
        
        for agent in agents:
            for prop in props:
                score = prop.agent_breakdown.get(agent, 50)
                agent_profiles[agent]['scores'].append(score)
                
                if score > 65:
                    agent_profiles[agent]['bullish_props'].append({
                        'player': prop.prop.player_name,
                        'stat': prop.prop.stat_type,
                        'bet': prop.prop.bet_type,
                        'agent_score': score,
                        'final_confidence': prop.final_confidence
                    })
                elif score < 35:
                    agent_profiles[agent]['bearish_props'].append({
                        'player': prop.prop.player_name,
                        'stat': prop.prop.stat_type,
                        'bet': prop.prop.bet_type,
                        'agent_score': score,
                        'final_confidence': prop.final_confidence
                    })
                else:
                    agent_profiles[agent]['neutral_props'].append(prop.prop.player_name)
            
            scores = agent_profiles[agent]['scores']
            if scores:
                avg_score = sum(scores) / len(scores)
                agreements = 0
                for prop in props:
                    agent_score = prop.agent_breakdown.get(agent, 50)
                    final_conf = prop.final_confidence
                    if (agent_score > 60 and final_conf > 60) or (agent_score < 40 and final_conf < 40):
                        agreements += 1
                
                agreement_rate = (agreements / len(props) * 100) if props else 0
                
                agent_profiles[agent]['average_score'] = avg_score
                agent_profiles[agent]['agreement_rate'] = agreement_rate
                agent_profiles[agent]['active'] = len(scores) > 0
        
        return dict(agent_profiles)

    @staticmethod
    def export_with_clusters(props: List[PropAnalysis], num_props: Optional[int] = None) -> str:
        """Export props WITH correlation clusters and contradiction detection"""
        if num_props:
            props = props[:num_props]
        
        clusters = EnhancedPropsExporter.analyze_correlations(props)
        contradictions = EnhancedPropsExporter.detect_contradictions(props)
        agent_profiles = EnhancedPropsExporter.create_agent_profiles(props)
        
        props_data = []
        for prop in props:
            prop_dict = {
                "player": prop.prop.player_name,
                "position": prop.prop.position,
                "team": prop.prop.team,
                "opponent": prop.prop.opponent,
                "stat_type": prop.prop.stat_type,
                "line": prop.prop.line,
                "bet_type": prop.prop.bet_type,
                "confidence": round(prop.final_confidence, 1),
                "recommendation": prop.recommendation,
                "agent_breakdown": {
                    agent: round(score, 1) if score else 50
                    for agent, score in prop.agent_breakdown.items()
                },
                "rationale": prop.rationale[:3] if prop.rationale else [],
            }
            props_data.append(prop_dict)
        
        clusters_data = {}
        for cluster_type, cluster_list in clusters.items():
            clusters_data[cluster_type] = {
                'count': len(cluster_list),
                'clusters': []
            }
            for cluster in cluster_list:
                cluster_summary = {
                    'strength': cluster.get('strength', 'MEDIUM'),
                    'prop_count': cluster.get('count', len(cluster.get('props', []))),
                }
                if cluster_type == 'SAME_PLAYER':
                    cluster_summary['player'] = cluster['player']
                    cluster_summary['stats'] = [p.prop.stat_type for p in cluster['props']]
                clusters_data[cluster_type]['clusters'].append(cluster_summary)
        
        contradictions_data = []
        for contra in contradictions:
            contradictions_data.append({
                'type': contra['type'],
                'player': contra.get('player', 'N/A'),
                'severity': contra['severity'],
                'explanation': contra['explanation'],
            })
        
        agent_profiles_data = {}
        for agent, profile in agent_profiles.items():
            agent_profiles_data[agent] = {
                'active': profile['active'],
                'average_score': round(profile['average_score'], 1) if profile['active'] else 50,
                'agreement_rate': round(profile['agreement_rate'], 1),
                'bullish_count': len(profile['bullish_props']),
                'bearish_count': len(profile['bearish_props']),
            }
        
        export_data = {
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "total_props": len(props_data),
                "clusters_detected": sum(len(v['clusters']) for v in clusters_data.values()),
                "contradictions_detected": len(contradictions_data),
            },
            "props": props_data,
            "correlation_clusters": clusters_data,
            "contradictions": contradictions_data,
            "agent_analysis": agent_profiles_data,
        }
        
        return json.dumps(export_data, indent=2)

    @staticmethod
    def export_with_clusters_formatted(props: List[PropAnalysis], num_props: Optional[int] = None) -> Tuple[str, str]:
        """Export with clusters AND return formatted summary for display"""
        if num_props:
            props = props[:num_props]
        
        clusters = EnhancedPropsExporter.analyze_correlations(props)
        contradictions = EnhancedPropsExporter.detect_contradictions(props)
        agent_profiles = EnhancedPropsExporter.create_agent_profiles(props)
        
        summary_lines = [
            "\n" + "="*80,
            "📊 ENHANCED PROPS EXPORT WITH CLUSTERING & CONTRADICTION DETECTION",
            "="*80,
            f"\n📈 Total Props: {len(props)}",
            f"🔗 Clusters Detected: {sum(len(v) for v in clusters.values())}",
            f"⚠️  Contradictions Found: {len(contradictions)}",
            "\n" + "-"*80,
            "CORRELATION CLUSTERS",
            "-"*80
        ]
        
        if clusters.get('SAME_PLAYER'):
            summary_lines.append(f"\n🔴 SAME PLAYER ({len(clusters['SAME_PLAYER'])} clusters)")
            for cluster in clusters['SAME_PLAYER'][:3]:
                summary_lines.append(f"   • {cluster['player']}: {', '.join([p.prop.stat_type for p in cluster['props']])}")
        
        summary_lines.append("\n" + "-"*80)
        summary_lines.append("CONTRADICTIONS")
        summary_lines.append("-"*80)
        
        if contradictions:
            for contra in contradictions[:5]:
                summary_lines.append(f"\n⚠️  {contra['type']} (Severity: {contra['severity']})")
                summary_lines.append(f"   {contra['explanation']}")
        else:
            summary_lines.append("\n✅ No major contradictions detected!")
        
        summary_lines.append("\n" + "="*80)
        
        json_export = EnhancedPropsExporter.export_with_clusters(props, num_props)
        summary_text = "\n".join(summary_lines)
        
        return json_export, summary_text
