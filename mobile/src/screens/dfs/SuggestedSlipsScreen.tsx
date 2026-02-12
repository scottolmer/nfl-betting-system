/**
 * SuggestedSlipsScreen — Engine-generated optimal DFS slips.
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';
import { apiService } from '../../services/api';
import CorrelationIndicator from '../../components/dfs/CorrelationIndicator';
import FlexPlayOptimizer from '../../components/dfs/FlexPlayOptimizer';

interface SuggestedSlip {
  picks: Array<{
    player_name: string;
    team: string;
    position: string;
    stat_type: string;
    platform_stat: string;
    platform_line: number | null;
    confidence: number | null;
    direction: string | null;
  }>;
  correlation: {
    total_penalty: number;
    warnings: string[];
    risk_level: 'low' | 'medium' | 'high';
    adjusted_confidence: number;
  };
  flex_recommendation: {
    flex_pick: any;
    reason: string;
    all_candidates?: any[];
  };
  combined_confidence: number;
}

export default function SuggestedSlipsScreen({ route, navigation }: any) {
  const { platform, week } = route.params;
  const [slips, setSlips] = useState<SuggestedSlip[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSuggestions();
  }, []);

  const loadSuggestions = async () => {
    try {
      const resp = await apiService['client'].get('/api/dfs/suggestions', {
        params: { week, platform, slip_size: 5, count: 3 },
      });
      setSlips(resp.data);
    } catch (err) {
      console.error('Error loading suggestions:', err);
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (c: number) => {
    if (c >= 65) return theme.colors.success;
    if (c >= 55) return theme.colors.primary;
    return theme.colors.textSecondary;
  };

  const renderSlip = ({ item, index }: { item: SuggestedSlip; index: number }) => (
    <View style={styles.slipCard}>
      <View style={styles.slipHeader}>
        <View style={styles.slipRank}>
          <Text style={styles.rankText}>#{index + 1}</Text>
        </View>
        <View style={styles.slipMeta}>
          <Text style={styles.slipTitle}>Suggested Slip</Text>
          <Text style={styles.slipPicks}>{item.picks.length} picks · {platform}</Text>
        </View>
        <View style={styles.slipConfBox}>
          <Text style={[styles.slipConf, { color: getConfidenceColor(item.combined_confidence) }]}>
            {Math.round(item.combined_confidence)}
          </Text>
          <Text style={styles.slipConfLabel}>CONF</Text>
        </View>
      </View>

      {/* Picks */}
      {item.picks.map((pick, i) => {
        const isFlexPick =
          item.flex_recommendation?.flex_pick?.player_name === pick.player_name;
        return (
          <View key={i} style={styles.pickRow}>
            <View style={styles.pickLeft}>
              {isFlexPick && (
                <View style={styles.flexTag}>
                  <Text style={styles.flexTagText}>FLEX</Text>
                </View>
              )}
              <Text style={styles.pickName} numberOfLines={1}>{pick.player_name}</Text>
              <Text style={styles.pickTeam}>{pick.team} · {pick.position}</Text>
            </View>
            <View style={styles.pickRight}>
              <Text style={styles.pickStat}>{pick.platform_stat}</Text>
              <Text style={styles.pickLine}>
                {pick.direction || 'OVER'} {pick.platform_line ?? '—'}
              </Text>
            </View>
            <Text style={[styles.pickConf, { color: getConfidenceColor(pick.confidence || 0) }]}>
              {pick.confidence ? Math.round(pick.confidence) : '—'}
            </Text>
          </View>
        );
      })}

      {/* Correlation */}
      <CorrelationIndicator
        penalty={item.correlation.total_penalty}
        riskLevel={item.correlation.risk_level}
        warnings={item.correlation.warnings}
      />
    </View>
  );

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color={theme.colors.primary} size="large" />
        <Text style={styles.loadingText}>Generating optimal slips...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="chevron-back" size={24} color={theme.colors.textPrimary} />
        </TouchableOpacity>
        <View>
          <Text style={styles.headerTitle}>Suggested Slips</Text>
          <Text style={styles.headerSub}>{platform} · Week {week}</Text>
        </View>
      </View>

      <FlatList
        data={slips}
        renderItem={renderSlip}
        keyExtractor={(_, i) => `slip-${i}`}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Ionicons name="flash-outline" size={48} color={theme.colors.textTertiary} />
            <Text style={styles.emptyTitle}>No Suggestions Available</Text>
            <Text style={styles.emptyText}>
              Suggestions require projection data. Check back when odds data is loaded for this week.
            </Text>
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
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingTop: 12,
    paddingHorizontal: 12,
    paddingBottom: 8,
    gap: 8,
  },
  backBtn: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerTitle: {
    ...theme.typography.h2,
  },
  headerSub: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
  listContent: {
    paddingHorizontal: 16,
    paddingBottom: 40,
  },
  slipCard: {
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 16,
    marginBottom: 16,
  },
  slipHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 14,
    gap: 10,
  },
  slipRank: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: theme.colors.glassHigh,
    justifyContent: 'center',
    alignItems: 'center',
  },
  rankText: {
    fontSize: 13,
    fontWeight: '800',
    color: theme.colors.primary,
  },
  slipMeta: {
    flex: 1,
  },
  slipTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
  slipPicks: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
  slipConfBox: {
    alignItems: 'center',
  },
  slipConf: {
    fontSize: 22,
    fontWeight: '800',
  },
  slipConfLabel: {
    fontSize: 9,
    fontWeight: '700',
    color: theme.colors.textTertiary,
  },
  pickRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.03)',
  },
  pickLeft: {
    flex: 1,
  },
  flexTag: {
    backgroundColor: theme.colors.primary,
    borderRadius: 3,
    paddingHorizontal: 5,
    paddingVertical: 1,
    alignSelf: 'flex-start',
    marginBottom: 2,
  },
  flexTagText: {
    fontSize: 8,
    fontWeight: '800',
    color: '#fff',
    letterSpacing: 0.5,
  },
  pickName: {
    fontSize: 13,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
  pickTeam: {
    fontSize: 10,
    color: theme.colors.textTertiary,
  },
  pickRight: {
    alignItems: 'flex-end',
    marginRight: 10,
  },
  pickStat: {
    fontSize: 11,
    color: theme.colors.textSecondary,
    fontWeight: '500',
  },
  pickLine: {
    fontSize: 12,
    color: theme.colors.textPrimary,
    fontWeight: '700',
  },
  pickConf: {
    fontSize: 14,
    fontWeight: '800',
    width: 30,
    textAlign: 'right',
  },
  loadingText: {
    marginTop: 12,
    color: theme.colors.textSecondary,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 60,
    paddingHorizontal: 32,
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
