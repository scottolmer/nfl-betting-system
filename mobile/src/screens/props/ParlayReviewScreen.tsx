/**
 * ParlayReviewScreen — Review selected parlay legs, see correlation risk,
 * combined confidence, and save/place the parlay.
 */

import React from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';
import { useParlay } from '../../contexts/ParlayContext';
import { PropAnalysis } from '../../types';
import PlayerCard from '../../components/player/PlayerCard';
import GlassCard from '../../components/common/GlassCard';
import AnimatedCard from '../../components/animated/AnimatedCard';

export default function ParlayReviewScreen({ navigation }: any) {
  const { picks, combinedConfidence, removePick, clearPicks } = useParlay();

  // Detect correlation: same-team legs
  const teamCounts: Record<string, number> = {};
  picks.forEach((p) => {
    teamCounts[p.team] = (teamCounts[p.team] || 0) + 1;
  });
  const correlatedTeams = Object.entries(teamCounts).filter(([, count]) => count > 1);
  const hasCorrelation = correlatedTeams.length > 0;

  const riskLevel: 'low' | 'medium' | 'high' =
    correlatedTeams.some(([, c]) => c >= 3) ? 'high' : hasCorrelation ? 'medium' : 'low';

  const riskColor =
    riskLevel === 'high'
      ? theme.colors.danger
      : riskLevel === 'medium'
        ? theme.colors.gold
        : theme.colors.success;

  const avgConfidence =
    picks.length > 0
      ? Math.round(picks.reduce((sum, p) => sum + p.confidence, 0) / picks.length)
      : 0;

  const handleSave = () => {
    Alert.alert(
      'Parlay Saved',
      `${picks.length}-leg parlay saved to My Bets.`,
      [
        {
          text: 'OK',
          onPress: () => {
            clearPicks();
            navigation.goBack();
          },
        },
      ],
    );
  };

  const renderLeg = ({ item, index }: { item: PropAnalysis; index: number }) => (
    <AnimatedCard index={index}>
      <View style={styles.legRow}>
        <PlayerCard
          player={{
            name: item.player_name,
            team: item.team,
            position: item.position,
          }}
          subtitle={`${item.stat_type} ${item.bet_type} ${item.line}`}
          confidence={item.confidence}
          rightContent={
            <TouchableOpacity
              onPress={() => removePick(item)}
              style={styles.removeBtn}
              activeOpacity={0.7}
            >
              <Ionicons name="close-circle" size={22} color={theme.colors.danger} />
            </TouchableOpacity>
          }
        />
      </View>
    </AnimatedCard>
  );

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="chevron-back" size={24} color={theme.colors.textPrimary} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Review Parlay</Text>
        <View style={styles.backBtn} />
      </View>

      <FlatList
        data={picks}
        renderItem={renderLeg}
        keyExtractor={(item) => `${item.player_name}-${item.stat_type}-${item.bet_type}`}
        contentContainerStyle={styles.listContent}
        ListHeaderComponent={
          <>
            {/* Summary card */}
            <GlassCard>
              <View style={styles.summaryRow}>
                <View style={styles.summaryItem}>
                  <Text style={styles.summaryValue}>{picks.length}</Text>
                  <Text style={styles.summaryLabel}>Legs</Text>
                </View>
                <View style={styles.summaryDivider} />
                <View style={styles.summaryItem}>
                  <Text style={styles.summaryValue}>{avgConfidence}</Text>
                  <Text style={styles.summaryLabel}>Avg Conf</Text>
                </View>
                <View style={styles.summaryDivider} />
                <View style={styles.summaryItem}>
                  <Text style={[styles.summaryValue, { color: theme.colors.primary }]}>
                    {combinedConfidence}
                  </Text>
                  <Text style={styles.summaryLabel}>Combined</Text>
                </View>
              </View>
            </GlassCard>

            {/* Correlation warning */}
            <GlassCard>
              <View style={styles.corrHeader}>
                <Text style={styles.corrTitle}>Correlation Risk</Text>
                <Text style={[styles.corrBadge, { color: riskColor }]}>
                  {riskLevel.toUpperCase()}
                </Text>
              </View>

              {/* Gauge bar */}
              <View style={styles.gaugeTrack}>
                <View
                  style={[
                    styles.gaugeFill,
                    {
                      width: riskLevel === 'high' ? '80%' : riskLevel === 'medium' ? '50%' : '20%',
                      backgroundColor: riskColor,
                    },
                  ]}
                />
              </View>

              {hasCorrelation ? (
                <View style={styles.warnings}>
                  {correlatedTeams.map(([team, count]) => (
                    <View key={team} style={styles.warningRow}>
                      <Ionicons name="warning" size={14} color={theme.colors.gold} />
                      <Text style={styles.warningText}>
                        {count} legs from {team} — correlated outcomes
                      </Text>
                    </View>
                  ))}
                </View>
              ) : (
                <Text style={styles.corrGood}>
                  No same-team correlation detected
                </Text>
              )}
            </GlassCard>

            {/* Section label */}
            <Text style={styles.legsLabel}>PARLAY LEGS</Text>
          </>
        }
        ListFooterComponent={
          <View style={styles.footer}>
            <TouchableOpacity
              style={[styles.saveBtn, picks.length < 2 && styles.saveBtnDisabled]}
              onPress={handleSave}
              disabled={picks.length < 2}
              activeOpacity={0.7}
            >
              <Ionicons name="bookmark" size={18} color="#000" />
              <Text style={styles.saveBtnText}>Save Parlay</Text>
            </TouchableOpacity>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: 56,
    paddingHorizontal: 16,
    paddingBottom: 12,
  },
  backBtn: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerTitle: {
    ...theme.typography.h3,
  },
  listContent: {
    paddingHorizontal: 16,
    paddingBottom: 40,
  },
  // Summary
  summaryRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  summaryItem: {
    flex: 1,
    alignItems: 'center',
  },
  summaryValue: {
    fontSize: 22,
    fontWeight: '800',
    color: theme.colors.textPrimary,
  },
  summaryLabel: {
    fontSize: 10,
    fontWeight: '600',
    color: theme.colors.textTertiary,
    textTransform: 'uppercase',
    marginTop: 2,
  },
  summaryDivider: {
    width: 1,
    height: 28,
    backgroundColor: theme.colors.glassBorder,
  },
  // Correlation
  corrHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  corrTitle: {
    ...theme.typography.caption,
  },
  corrBadge: {
    fontSize: 12,
    fontWeight: '800',
  },
  gaugeTrack: {
    height: 6,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 3,
    overflow: 'hidden',
    marginBottom: 10,
  },
  gaugeFill: {
    height: 6,
    borderRadius: 3,
  },
  warnings: {
    gap: 6,
  },
  warningRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  warningText: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
  corrGood: {
    fontSize: 12,
    color: theme.colors.success,
  },
  // Legs
  legsLabel: {
    ...theme.typography.caption,
    marginTop: 16,
    marginBottom: 8,
  },
  legRow: {
    marginBottom: 4,
  },
  removeBtn: {
    padding: 4,
  },
  // Footer
  footer: {
    marginTop: 16,
    alignItems: 'center',
  },
  saveBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.m,
    paddingHorizontal: 32,
    paddingVertical: 14,
    gap: 8,
    width: '100%',
  },
  saveBtnDisabled: {
    opacity: 0.4,
  },
  saveBtnText: {
    fontSize: 16,
    fontWeight: '800',
    color: '#000',
  },
});
