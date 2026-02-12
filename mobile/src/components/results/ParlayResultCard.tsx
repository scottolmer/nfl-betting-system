/**
 * Parlay Result Card
 * Displays individual parlay result with expandable leg details
 */

import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { SavedParlay } from '../../types';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';

interface ParlayResultCardProps {
  parlay: SavedParlay;
}

export default function ParlayResultCard({ parlay }: ParlayResultCardProps) {
  const [expanded, setExpanded] = useState(false);

  const isWon = parlay.status === 'won';
  const isLost = parlay.status === 'lost';
  const isPending = parlay.status === 'pending';

  const getStatusColor = () => {
    if (isWon) return theme.colors.success;
    if (isLost) return theme.colors.danger;
    return theme.colors.warning;
  };

  const getStatusBgColor = () => {
    if (isWon) return theme.colors.successMuted;
    if (isLost) return theme.colors.dangerMuted;
    return theme.colors.warningMuted;
  };

  const getStatusText = () => {
    if (isWon) return 'WON';
    if (isLost) return 'LOST';
    return 'PENDING';
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'LOW':
        return theme.colors.success;
      case 'MEDIUM':
        return theme.colors.warning;
      case 'HIGH':
        return theme.colors.danger;
      default:
        return theme.colors.textSecondary;
    }
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={styles.header}
        onPress={() => setExpanded(!expanded)}
        activeOpacity={0.7}
      >
        <View style={styles.headerLeft}>
          <Text style={styles.parlayName}>{parlay.name}</Text>
          <View style={styles.metadata}>
            <Text style={styles.metadataText}>Week {parlay.week}</Text>
            <Text style={styles.metadataDot}>•</Text>
            <Text style={styles.metadataText}>{parlay.legs.length} legs</Text>
            <Text style={styles.metadataDot}>•</Text>
            <Text style={styles.metadataText}>
              {parlay.combined_confidence.toFixed(0)}% confidence
            </Text>
          </View>
        </View>

        <Ionicons
          name={expanded ? 'chevron-up' : 'chevron-down'}
          size={20}
          color={theme.colors.textSecondary}
        />
      </TouchableOpacity>

      <View style={styles.statusRow}>
        <View style={[styles.statusBadge, { backgroundColor: getStatusBgColor() }]}>
          <Text style={[styles.statusText, { color: getStatusColor() }]}>
            {getStatusText()}
          </Text>
        </View>

        <View style={[styles.riskBadge, { borderColor: getRiskLevelColor(parlay.risk_level) }]}>
          <Text style={[styles.riskText, { color: getRiskLevelColor(parlay.risk_level) }]}>
            {parlay.risk_level} RISK
          </Text>
        </View>

        {parlay.result && (
          <View style={styles.legsHitBadge}>
            <Text style={styles.legsHitText}>
              {parlay.result.legs_hit}/{parlay.result.legs_total} legs hit
            </Text>
          </View>
        )}
      </View>

      {expanded && (
        <View style={styles.details}>
          <Text style={styles.detailsTitle}>Legs</Text>

          {parlay.legs.map((leg, index) => (
            <View key={index} style={styles.legRow}>
              <View style={styles.legInfo}>
                <Text style={styles.playerName}>{leg.player_name}</Text>
                <Text style={styles.legDetails}>
                  {leg.stat_type} {leg.bet_type} {leg.line}
                </Text>
                <Text style={styles.teamText}>
                  {leg.team} {leg.position ? `• ${leg.position}` : ''}
                </Text>
              </View>

              <View style={styles.legStats}>
                <Text style={styles.confidenceText}>
                  {leg.confidence.toFixed(0)}%
                </Text>
                {leg.cushion !== undefined && (
                  <Text style={styles.cushionText}>
                    {leg.cushion > 0 ? '+' : ''}{leg.cushion.toFixed(1)} cushion
                  </Text>
                )}
              </View>
            </View>
          ))}

          {parlay.sportsbook && (
            <View style={styles.sportsbookRow}>
              <Text style={styles.sportsbookLabel}>Sportsbook:</Text>
              <Text style={styles.sportsbookValue}>{parlay.sportsbook}</Text>
            </View>
          )}

          {parlay.placed_at && (
            <View style={styles.dateRow}>
              <Text style={styles.dateLabel}>Placed:</Text>
              <Text style={styles.dateValue}>
                {new Date(parlay.placed_at).toLocaleDateString()}
              </Text>
            </View>
          )}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: 12,
    marginHorizontal: 16,
    marginVertical: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 2,
    overflow: 'hidden',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    paddingBottom: 12,
  },
  headerLeft: {
    flex: 1,
    marginRight: 12,
  },
  parlayName: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.textPrimary,
    marginBottom: 4,
  },
  metadata: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
  },
  metadataText: {
    fontSize: 13,
    color: theme.colors.textSecondary,
  },
  metadataDot: {
    fontSize: 13,
    color: theme.colors.textTertiary,
    marginHorizontal: 6,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingBottom: 16,
    flexWrap: 'wrap',
    gap: 8,
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '700',
  },
  riskBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 10,
    borderWidth: 1.5,
  },
  riskText: {
    fontSize: 11,
    fontWeight: '600',
  },
  legsHitBadge: {
    backgroundColor: theme.colors.backgroundElevated,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 12,
  },
  legsHitText: {
    fontSize: 12,
    fontWeight: '600',
    color: theme.colors.textPrimary,
  },
  details: {
    borderTopWidth: 1,
    borderTopColor: theme.colors.glassBorder,
    padding: 16,
    paddingTop: 12,
  },
  detailsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.textPrimary,
    marginBottom: 12,
  },
  legRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.glassBorder,
  },
  legInfo: {
    flex: 1,
    marginRight: 12,
  },
  playerName: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.textPrimary,
    marginBottom: 2,
  },
  legDetails: {
    fontSize: 13,
    color: theme.colors.textSecondary,
    marginBottom: 2,
  },
  teamText: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
  legStats: {
    alignItems: 'flex-end',
  },
  confidenceText: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.textPrimary,
    marginBottom: 2,
  },
  cushionText: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
  sportsbookRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingTop: 12,
    marginTop: 8,
  },
  sportsbookLabel: {
    fontSize: 13,
    color: theme.colors.textSecondary,
  },
  sportsbookValue: {
    fontSize: 13,
    fontWeight: '600',
    color: theme.colors.textPrimary,
  },
  dateRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 4,
  },
  dateLabel: {
    fontSize: 13,
    color: theme.colors.textSecondary,
  },
  dateValue: {
    fontSize: 13,
    fontWeight: '600',
    color: theme.colors.textPrimary,
  },
});
