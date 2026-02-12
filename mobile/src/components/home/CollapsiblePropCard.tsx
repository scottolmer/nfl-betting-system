/**
 * Collapsible Prop Card
 * Prop card that starts collapsed, tap to expand — dark theme with glow
 */

import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { theme } from '../../constants/theme';
import { PropAnalysis } from '../../types';

interface CollapsiblePropCardProps {
  prop: PropAnalysis;
  onPress?: () => void;
}

export default function CollapsiblePropCard({ prop, onPress }: CollapsiblePropCardProps) {
  const [expanded, setExpanded] = useState(false);

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 70) return theme.colors.primary;
    if (confidence >= 60) return theme.colors.success;
    return theme.colors.textSecondary;
  };

  const handlePress = () => {
    if (onPress) {
      onPress();
    } else {
      setExpanded(!expanded);
    }
  };

  const isHighConf = prop.confidence >= 70;

  return (
    <TouchableOpacity
      style={[styles.card, isHighConf && styles.cardGlow]}
      onPress={handlePress}
      activeOpacity={0.7}
    >
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.confidenceContainer}>
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

        <Text style={styles.expandIcon}>{expanded ? '\u25B2' : '\u25BC'}</Text>
      </View>

      {/* Prop Line */}
      <View style={styles.propLine}>
        <Text style={styles.statType}>{prop.stat_type}</Text>
        <Text style={[styles.betType, { color: prop.bet_type === 'OVER' ? theme.colors.success : theme.colors.danger }]}>
          {prop.bet_type}
        </Text>
        <Text style={styles.line}>{prop.line}</Text>
      </View>

      {/* Expanded Details */}
      {expanded && (
        <View style={styles.expandedContent}>
          {prop.projection && (
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Projection:</Text>
              <Text style={styles.detailValue}>
                {prop.projection.toFixed(1)}
                {prop.cushion && (
                  <Text style={[styles.cushion, { color: prop.cushion > 0 ? theme.colors.success : theme.colors.danger }]}>
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
                  {'\u2022'} {reason}
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
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 16,
    marginBottom: 12,
    ...theme.shadows.card,
  },
  cardGlow: {
    borderColor: theme.colors.glassBorderActive,
    ...theme.shadows.glow,
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
  confidenceScore: {
    fontSize: 22,
    fontWeight: '800',
  },
  playerInfo: {
    flex: 1,
  },
  playerName: {
    fontSize: 16,
    fontWeight: '700',
    color: theme.colors.textPrimary,
    marginBottom: 2,
  },
  teamPosition: {
    fontSize: 13,
    color: theme.colors.textSecondary,
  },
  expandIcon: {
    fontSize: 12,
    color: theme.colors.textTertiary,
    marginLeft: 8,
  },
  propLine: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingBottom: 8,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.glassBorder,
  },
  statType: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.textPrimary,
  },
  betType: {
    fontSize: 13,
    fontWeight: '700',
  },
  line: {
    fontSize: 15,
    fontWeight: '800',
    color: theme.colors.textPrimary,
  },
  tapHint: {
    fontSize: 11,
    color: theme.colors.textTertiary,
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
    color: theme.colors.textSecondary,
    fontWeight: '600',
  },
  detailValue: {
    fontSize: 13,
    color: theme.colors.textPrimary,
    fontWeight: '600',
  },
  cushion: {
    fontWeight: '700',
  },
  reasonsSection: {
    marginTop: 8,
  },
  reasonsLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: theme.colors.textPrimary,
    marginBottom: 6,
  },
  reason: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    lineHeight: 18,
    marginBottom: 3,
  },
  agentCount: {
    fontSize: 11,
    color: theme.colors.textTertiary,
    marginTop: 8,
    textAlign: 'center',
    fontStyle: 'italic',
  },
});
