/**
 * Review Step (Step 3)
 * Review complete parlay before saving
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { SavedParlayLeg, Sportsbook } from '../../types';
import InfoTooltip from '../common/InfoTooltip';

interface ReviewStepProps {
  parlayName: string;
  sportsbook: Sportsbook;
  legs: SavedParlayLeg[];
  combinedConfidence: number;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
  onAdjustLine?: (leg: SavedParlayLeg) => void;
}

export default function ReviewStep({
  parlayName,
  sportsbook,
  legs,
  combinedConfidence,
  riskLevel,
  onAdjustLine,
}: ReviewStepProps) {
  const getRiskColor = (risk: string): string => {
    switch (risk) {
      case 'LOW':
        return '#22C55E';
      case 'MEDIUM':
        return '#F59E0B';
      case 'HIGH':
        return '#EF4444';
      default:
        return '#6B7280';
    }
  };

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 70) return '#22C55E';
    if (confidence >= 60) return '#F59E0B';
    return '#EF4444';
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Parlay Summary Card */}
      <View style={styles.summaryCard}>
        <Text style={styles.summaryTitle}>{parlayName || 'Unnamed Parlay'}</Text>
        <Text style={styles.summarySportsbook}>{sportsbook}</Text>

        <View style={styles.statsRow}>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Legs</Text>
            <Text style={styles.statValue}>{legs.length}</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Combined Confidence</Text>
            <Text
              style={[
                styles.statValue,
                { color: getConfidenceColor(combinedConfidence) },
              ]}
            >
              {Math.round(combinedConfidence)}%
            </Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Risk Level</Text>
            <Text style={[styles.statValue, { color: getRiskColor(riskLevel) }]}>
              {riskLevel}
            </Text>
          </View>
        </View>
      </View>

      {/* Legs Section */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Parlay Legs</Text>
          <InfoTooltip tooltipKey="myParlays" iconSize={16} />
        </View>

        {legs.map((leg, index) => (
          <View key={index} style={styles.legCard}>
            <View style={styles.legHeader}>
              <View style={styles.legNumberContainer}>
                <Text style={styles.legNumber}>{index + 1}</Text>
              </View>
              <View style={styles.legContent}>
                <Text style={styles.legPlayer}>{leg.player_name}</Text>
                <Text style={styles.legTeam}>
                  {leg.team} {leg.position} vs {leg.opponent}
                </Text>
                <View style={styles.legPropRow}>
                  <Text style={styles.legStat}>{leg.stat_type}</Text>
                  <Text style={styles.legBetType}>{leg.bet_type}</Text>
                  <Text style={styles.legLine}>{leg.line}</Text>
                </View>
                {leg.adjusted_line &&
                  leg.adjusted_line !== leg.original_line && (
                    <Text style={styles.adjustedIndicator}>
                      (Adjusted from {leg.original_line})
                    </Text>
                  )}
                {leg.projection && (
                  <Text style={styles.legProjection}>
                    Projection: {leg.projection.toFixed(1)}
                    {leg.cushion && (
                      <Text
                        style={[
                          styles.legCushion,
                          {
                            color: leg.cushion > 0 ? '#22C55E' : '#EF4444',
                          },
                        ]}
                      >
                        {' '}
                        ({leg.cushion > 0 ? '+' : ''}
                        {leg.cushion.toFixed(1)})
                      </Text>
                    )}
                  </Text>
                )}
              </View>
              <View style={styles.legRight}>
                <Text
                  style={[
                    styles.legConfidence,
                    { color: getConfidenceColor(leg.confidence) },
                  ]}
                >
                  {Math.round(leg.confidence)}%
                </Text>
              </View>
            </View>
          </View>
        ))}
      </View>

      {/* Next Steps */}
      <View style={styles.infoBox}>
        <Text style={styles.infoIcon}>📋</Text>
        <View style={styles.infoContent}>
          <Text style={styles.infoTitle}>Next Steps</Text>
          <Text style={styles.infoText}>
            1. Review all legs above{'\n'}
            2. Tap "Save Parlay" to save to your library{'\n'}
            3. Copy props to your sportsbook{'\n'}
            4. Mark as "Placed" to track results
          </Text>
        </View>
      </View>

      {/* Disclaimer */}
      <View style={styles.disclaimerBox}>
        <Text style={styles.disclaimerText}>
          ⚠️ Remember: AI predictions are not guarantees. Bet responsibly and
          within your means.
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  content: {
    padding: 16,
  },
  summaryCard: {
    backgroundColor: '#1F2937',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
  },
  summaryTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  summarySportsbook: {
    fontSize: 14,
    color: '#9CA3AF',
    marginBottom: 16,
  },
  statsRow: {
    flexDirection: 'row',
    gap: 12,
  },
  statBox: {
    flex: 1,
    backgroundColor: '#374151',
    borderRadius: 8,
    padding: 12,
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 11,
    color: '#9CA3AF',
    marginBottom: 4,
    textAlign: 'center',
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  section: {
    marginBottom: 16,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  legCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  legHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  legNumberContainer: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#3B82F6',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  legNumber: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  legContent: {
    flex: 1,
  },
  legPlayer: {
    fontSize: 17,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 2,
  },
  legTeam: {
    fontSize: 13,
    color: '#6B7280',
    marginBottom: 6,
  },
  legPropRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 4,
  },
  legStat: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1F2937',
  },
  legBetType: {
    fontSize: 14,
    fontWeight: '600',
    color: '#3B82F6',
  },
  legLine: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  adjustedIndicator: {
    fontSize: 11,
    color: '#F59E0B',
    fontStyle: 'italic',
    marginBottom: 4,
  },
  legProjection: {
    fontSize: 12,
    color: '#6B7280',
  },
  legCushion: {
    fontWeight: '600',
  },
  legRight: {
    alignItems: 'center',
    marginLeft: 12,
  },
  legConfidence: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  infoBox: {
    flexDirection: 'row',
    backgroundColor: '#EFF6FF',
    borderLeftWidth: 4,
    borderLeftColor: '#3B82F6',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
  },
  infoIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  infoContent: {
    flex: 1,
  },
  infoTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 6,
  },
  infoText: {
    fontSize: 13,
    color: '#4B5563',
    lineHeight: 20,
  },
  disclaimerBox: {
    backgroundColor: '#FEF3C7',
    borderLeftWidth: 4,
    borderLeftColor: '#F59E0B',
    borderRadius: 8,
    padding: 16,
  },
  disclaimerText: {
    fontSize: 12,
    color: '#92400E',
    lineHeight: 18,
  },
});
