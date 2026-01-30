/**
 * Collapsible Prop Card
 * Prop card that starts collapsed, tap to expand for full details
 */

import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { PropAnalysis } from '../../types';

interface CollapsiblePropCardProps {
  prop: PropAnalysis;
  onPress?: () => void;
}

export default function CollapsiblePropCard({ prop, onPress }: CollapsiblePropCardProps) {
  const [expanded, setExpanded] = useState(false);

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 80) return '#22C55E';
    if (confidence >= 75) return '#F59E0B';
    if (confidence >= 70) return '#3B82F6';
    return '#6B7280';
  };

  const getConfidenceEmoji = (confidence: number): string => {
    if (confidence >= 80) return '🔥';
    if (confidence >= 75) return '⭐';
    if (confidence >= 70) return '✅';
    return '📊';
  };

  const handlePress = () => {
    if (onPress) {
      onPress();
    } else {
      setExpanded(!expanded);
    }
  };

  return (
    <TouchableOpacity
      style={styles.card}
      onPress={handlePress}
      activeOpacity={0.7}
    >
      {/* Always Visible: Header */}
      <View style={styles.header}>
        <View style={styles.confidenceContainer}>
          <Text style={styles.confidenceEmoji}>
            {getConfidenceEmoji(prop.confidence)}
          </Text>
          <Text
            style={[
              styles.confidenceScore,
              { color: getConfidenceColor(prop.confidence) },
            ]}
          >
            {Math.round(prop.confidence)}
          </Text>
        </View>

        <View style={styles.playerInfo}>
          <Text style={styles.playerName}>{prop.player_name}</Text>
          <Text style={styles.teamPosition}>
            {prop.team} {prop.position} vs {prop.opponent}
          </Text>
        </View>

        <Text style={styles.expandIcon}>{expanded ? '▲' : '▼'}</Text>
      </View>

      {/* Always Visible: Prop Line */}
      <View style={styles.propLine}>
        <Text style={styles.statType}>{prop.stat_type}</Text>
        <Text style={styles.betType}>{prop.bet_type}</Text>
        <Text style={styles.line}>{prop.line}</Text>
      </View>

      {/* Collapsible: Additional Details */}
      {expanded && (
        <View style={styles.expandedContent}>
          {prop.projection && (
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Projection:</Text>
              <Text style={styles.detailValue}>
                {prop.projection.toFixed(1)}
                {prop.cushion && (
                  <Text style={styles.cushion}>
                    {' '}({prop.cushion > 0 ? '+' : ''}{prop.cushion.toFixed(1)})
                  </Text>
                )}
              </Text>
            </View>
          )}

          {prop.top_reasons && prop.top_reasons.length > 0 && (
            <View style={styles.reasonsSection}>
              <Text style={styles.reasonsLabel}>Top Reasons:</Text>
              {prop.top_reasons.slice(0, 3).map((reason, index) => (
                <Text key={index} style={styles.reason}>
                  • {reason}
                </Text>
              ))}
            </View>
          )}

          {prop.agent_analyses && prop.agent_analyses.length > 0 && (
            <Text style={styles.agentCount}>
              {prop.agent_analyses.length} AI agents analyzed
            </Text>
          )}
        </View>
      )}

      {!expanded && (
        <Text style={styles.tapHint}>Tap to expand</Text>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  header: {
    flexDirection: 'row',
    marginBottom: 12,
    alignItems: 'center',
  },
  confidenceContainer: {
    alignItems: 'center',
    marginRight: 12,
    minWidth: 50,
  },
  confidenceEmoji: {
    fontSize: 20,
    marginBottom: 2,
  },
  confidenceScore: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  playerInfo: {
    flex: 1,
  },
  playerName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 2,
  },
  teamPosition: {
    fontSize: 13,
    color: '#6B7280',
  },
  expandIcon: {
    fontSize: 12,
    color: '#9CA3AF',
    marginLeft: 8,
  },
  propLine: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingBottom: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  statType: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
  },
  betType: {
    fontSize: 13,
    fontWeight: '600',
    color: '#3B82F6',
  },
  line: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  tapHint: {
    fontSize: 11,
    color: '#9CA3AF',
    textAlign: 'center',
    marginTop: 8,
    fontStyle: 'italic',
  },
  expandedContent: {
    marginTop: 12,
    paddingTop: 12,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  detailLabel: {
    fontSize: 13,
    color: '#6B7280',
    fontWeight: '600',
  },
  detailValue: {
    fontSize: 13,
    color: '#1F2937',
    fontWeight: '600',
  },
  cushion: {
    color: '#22C55E',
  },
  reasonsSection: {
    marginTop: 8,
  },
  reasonsLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 6,
  },
  reason: {
    fontSize: 12,
    color: '#4B5563',
    lineHeight: 18,
    marginBottom: 3,
  },
  agentCount: {
    fontSize: 11,
    color: '#9CA3AF',
    marginTop: 8,
    textAlign: 'center',
    fontStyle: 'italic',
  },
});
