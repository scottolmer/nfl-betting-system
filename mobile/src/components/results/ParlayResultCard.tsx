/**
 * Parlay Result Card
 * Displays individual parlay result with expandable leg details
 */

import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { SavedParlay } from '../../types';
import { Ionicons } from '@expo/vector-icons';

interface ParlayResultCardProps {
  parlay: SavedParlay;
}

export default function ParlayResultCard({ parlay }: ParlayResultCardProps) {
  const [expanded, setExpanded] = useState(false);

  const isWon = parlay.status === 'won';
  const isLost = parlay.status === 'lost';
  const isPending = parlay.status === 'pending';

  const getStatusColor = () => {
    if (isWon) return '#10B981';
    if (isLost) return '#EF4444';
    return '#F59E0B';
  };

  const getStatusBgColor = () => {
    if (isWon) return '#D1FAE5';
    if (isLost) return '#FEE2E2';
    return '#FEF3C7';
  };

  const getStatusText = () => {
    if (isWon) return 'WON';
    if (isLost) return 'LOST';
    return 'PENDING';
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'LOW':
        return '#10B981';
      case 'MEDIUM':
        return '#F59E0B';
      case 'HIGH':
        return '#EF4444';
      default:
        return '#6B7280';
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
          color="#6B7280"
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
    backgroundColor: '#FFFFFF',
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
    color: '#1F2937',
    marginBottom: 4,
  },
  metadata: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
  },
  metadataText: {
    fontSize: 13,
    color: '#6B7280',
  },
  metadataDot: {
    fontSize: 13,
    color: '#9CA3AF',
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
    backgroundColor: '#F3F4F6',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 12,
  },
  legsHitText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#1F2937',
  },
  details: {
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    padding: 16,
    paddingTop: 12,
  },
  detailsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 12,
  },
  legRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  legInfo: {
    flex: 1,
    marginRight: 12,
  },
  playerName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 2,
  },
  legDetails: {
    fontSize: 13,
    color: '#4B5563',
    marginBottom: 2,
  },
  teamText: {
    fontSize: 12,
    color: '#6B7280',
  },
  legStats: {
    alignItems: 'flex-end',
  },
  confidenceText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 2,
  },
  cushionText: {
    fontSize: 12,
    color: '#6B7280',
  },
  sportsbookRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingTop: 12,
    marginTop: 8,
  },
  sportsbookLabel: {
    fontSize: 13,
    color: '#6B7280',
  },
  sportsbookValue: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1F2937',
  },
  dateRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 4,
  },
  dateLabel: {
    fontSize: 13,
    color: '#6B7280',
  },
  dateValue: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1F2937',
  },
});
