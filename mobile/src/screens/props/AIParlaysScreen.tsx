/**
 * AIParlaysScreen — Displays AI-generated parlays from the 6-agent engine.
 * Fetches from /api/parlays/prebuilt which runs full correlation analysis,
 * player diversity constraints, and risk assessment.
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';
import { apiService } from '../../services/api';
import { Parlay } from '../../types';
import GlassCard from '../../components/common/GlassCard';
import AnimatedCard from '../../components/animated/AnimatedCard';

function getRiskColor(risk: string): string {
  switch (risk) {
    case 'LOW': return theme.colors.success;
    case 'MEDIUM': return theme.colors.gold;
    case 'HIGH': return theme.colors.danger;
    default: return theme.colors.textSecondary;
  }
}

function getConfidenceColor(conf: number): string {
  if (conf >= 70) return theme.colors.success;
  if (conf >= 60) return theme.colors.primary;
  if (conf >= 50) return theme.colors.gold;
  return theme.colors.danger;
}

export default function AIParlaysScreen({ route, navigation }: any) {
  const week = route?.params?.week ?? 13;
  const [parlays, setParlays] = useState<Parlay[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const loadParlays = async () => {
    try {
      setError(null);
      const data = await apiService.getPrebuiltParlays({
        week,
        min_confidence: 58,
      });
      setParlays(data);
    } catch (err: any) {
      setError(err.message || 'Failed to generate parlays');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadParlays();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    loadParlays();
  };

  const renderParlay = ({ item, index }: { item: Parlay; index: number }) => {
    const riskColor = getRiskColor(item.risk_level);
    const confColor = getConfidenceColor(item.combined_confidence);

    return (
      <AnimatedCard index={index}>
        <TouchableOpacity activeOpacity={0.8} onPress={() => navigation.navigate('ParlayDetail', { parlay: item, week })}>
          <GlassCard glow={item.combined_confidence >= 70}>
            {/* Header row */}
            <View style={styles.parlayHeader}>
              <View style={styles.parlayMeta}>
                <View style={[styles.legCountBadge, { backgroundColor: confColor }]}>
                  <Text style={styles.legCountText}>{item.leg_count}L</Text>
                </View>
                <View>
                  <Text style={styles.parlayName}>
                    {item.parlay_type || item.name}
                  </Text>
                  <View style={styles.riskRow}>
                    <View style={[styles.riskDot, { backgroundColor: riskColor }]} />
                    <Text style={[styles.riskText, { color: riskColor }]}>
                      {item.risk_level} RISK
                    </Text>
                  </View>
                </View>
              </View>

              <View style={styles.confBox}>
                <Text style={[styles.confScore, { color: confColor }]}>
                  {Math.round(item.combined_confidence)}
                </Text>
                <Text style={styles.confLabel}>CONF</Text>
              </View>
            </View>

            {/* Leg previews (always show compact) */}
            <View style={styles.legPreviews}>
              {item.legs.map((leg, i) => (
                <View key={i} style={styles.legPreviewRow}>
                  <Text style={styles.legPlayerName} numberOfLines={1}>
                    {leg.player_name}
                  </Text>
                  <Text style={styles.legStat}>
                    {leg.stat_type} {leg.bet_type} {leg.line}
                  </Text>
                  <Text style={[styles.legConf, {
                    color: getConfidenceColor(leg.confidence),
                  }]}>
                    {Math.round(leg.confidence)}
                  </Text>
                </View>
              ))}
            </View>

            {/* Tap hint */}
            <View style={styles.expandHint}>
              <Ionicons name="chevron-forward" size={14} color={theme.colors.textTertiary} />
            </View>
          </GlassCard>
        </TouchableOpacity>
      </AnimatedCard>
    );
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color={theme.colors.primary} size="large" />
        <Text style={styles.loadingText}>Generating AI parlays...</Text>
        <Text style={styles.loadingSub}>Running 6-agent analysis with correlation scoring</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="chevron-back" size={24} color={theme.colors.textPrimary} />
        </TouchableOpacity>
        <View>
          <Text style={styles.headerTitle}>AI Parlays</Text>
          <Text style={styles.headerSub}>Week {week} — 6-Agent Engine</Text>
        </View>
        <View style={styles.backBtn} />
      </View>

      {/* Info banner */}
      <View style={styles.infoBanner}>
        <Ionicons name="sparkles" size={16} color={theme.colors.primary} />
        <Text style={styles.infoText}>
          Generated with player diversity, correlation scoring, and risk assessment
        </Text>
      </View>

      {/* Error */}
      {error && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity onPress={loadParlays}>
            <Text style={styles.retryText}>Retry</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Parlays list */}
      <FlatList
        data={parlays}
        renderItem={renderParlay}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={theme.colors.primary} />
        }
        ListEmptyComponent={
          !error ? (
            <View style={styles.emptyState}>
              <Ionicons name="alert-circle-outline" size={48} color={theme.colors.textTertiary} />
              <Text style={styles.emptyTitle}>No Parlays Generated</Text>
              <Text style={styles.emptyText}>
                Not enough high-confidence props to build parlays this week.
              </Text>
            </View>
          ) : null
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
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
    paddingHorizontal: 32,
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
    ...theme.typography.h2,
    textAlign: 'center',
  },
  headerSub: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    textAlign: 'center',
  },
  infoBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: theme.colors.primaryMuted,
    marginHorizontal: 16,
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: theme.borderRadius.s,
    marginBottom: 12,
  },
  infoText: {
    flex: 1,
    fontSize: 12,
    color: theme.colors.primary,
    lineHeight: 16,
  },
  loadingText: {
    marginTop: 16,
    color: theme.colors.textPrimary,
    fontSize: 16,
    fontWeight: '600',
  },
  loadingSub: {
    marginTop: 4,
    color: theme.colors.textTertiary,
    fontSize: 12,
  },
  errorBanner: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: theme.colors.dangerMuted,
    paddingHorizontal: 16,
    paddingVertical: 8,
    marginHorizontal: 16,
    borderRadius: theme.borderRadius.s,
    marginBottom: 8,
  },
  errorText: {
    color: theme.colors.danger,
    fontSize: 12,
    flex: 1,
  },
  retryText: {
    color: theme.colors.primary,
    fontSize: 12,
    fontWeight: '700',
    marginLeft: 12,
  },
  listContent: {
    paddingHorizontal: 16,
    paddingBottom: 40,
  },
  // Parlay card
  parlayHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  parlayMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  legCountBadge: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },
  legCountText: {
    fontSize: 13,
    fontWeight: '800',
    color: '#000',
  },
  parlayName: {
    fontSize: 14,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
  riskRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 2,
  },
  riskDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
  },
  riskText: {
    fontSize: 10,
    fontWeight: '700',
  },
  confBox: {
    alignItems: 'center',
  },
  confScore: {
    fontSize: 24,
    fontWeight: '800',
  },
  confLabel: {
    fontSize: 9,
    fontWeight: '600',
    color: theme.colors.textTertiary,
    letterSpacing: 0.5,
  },
  // Leg previews
  legPreviews: {
    gap: 6,
    borderTopWidth: 1,
    borderTopColor: theme.colors.glassBorder,
    paddingTop: 10,
  },
  legPreviewRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  legPlayerName: {
    flex: 1,
    fontSize: 13,
    fontWeight: '600',
    color: theme.colors.textPrimary,
    textTransform: 'capitalize',
  },
  legStat: {
    fontSize: 11,
    color: theme.colors.textSecondary,
  },
  legConf: {
    fontSize: 13,
    fontWeight: '800',
    width: 28,
    textAlign: 'right',
  },
  expandHint: {
    alignItems: 'center',
    marginTop: 6,
  },
  // Empty
  emptyState: {
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyTitle: {
    ...theme.typography.h3,
    marginTop: 16,
    marginBottom: 8,
  },
  emptyText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    lineHeight: 20,
  },
});
