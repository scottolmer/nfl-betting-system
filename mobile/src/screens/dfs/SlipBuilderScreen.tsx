/**
 * SlipBuilderScreen — Browse/search players, tap to add, real-time correlation,
 * flex optimizer, review with agent reasoning.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';
import { apiService } from '../../services/api';
import PlayerCard from '../../components/player/PlayerCard';
import SlipSummaryBar from '../../components/dfs/SlipSummaryBar';
import CorrelationIndicator from '../../components/dfs/CorrelationIndicator';
import AgentReasoningCard from '../../components/dfs/AgentReasoningCard';
import FlexPlayOptimizer from '../../components/dfs/FlexPlayOptimizer';

interface DFSLine {
  player_id: number;
  player_name: string;
  team: string;
  position: string;
  headshot_url?: string;
  stat_type: string;
  platform_stat: string;
  platform_line: number | null;
  sportsbook_consensus: number | null;
  engine_projection: number | null;
  confidence: number | null;
  direction: string | null;
  agent_breakdown: Record<string, any> | null;
}

interface CorrelationResult {
  total_penalty: number;
  warnings: string[];
  risk_level: 'low' | 'medium' | 'high';
  adjusted_confidence: number;
}

interface FlexResult {
  flex_pick: any;
  reason: string;
  all_candidates?: any[];
}

const MAX_PICKS = 5;

export default function SlipBuilderScreen({ route, navigation }: any) {
  const { platform, week } = route.params;
  const [lines, setLines] = useState<DFSLine[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [picks, setPicks] = useState<DFSLine[]>([]);
  const [correlation, setCorrelation] = useState<CorrelationResult | null>(null);
  const [flex, setFlex] = useState<FlexResult | null>(null);
  const [showReview, setShowReview] = useState(false);

  useEffect(() => {
    loadLines();
  }, []);

  // Recalculate correlation when picks change
  useEffect(() => {
    if (picks.length >= 2) {
      scoreCorrelation();
      optimizeFlex();
    } else {
      setCorrelation(null);
      setFlex(null);
    }
  }, [picks]);

  const loadLines = async () => {
    try {
      const resp = await apiService['client'].get('/api/dfs/lines', {
        params: { week, platform },
      });
      setLines(resp.data);
    } catch (err) {
      console.error('Error loading DFS lines:', err);
    } finally {
      setLoading(false);
    }
  };

  const scoreCorrelation = async () => {
    try {
      const resp = await apiService['client'].post('/api/dfs/correlation-score', {
        picks: picks.map((p) => ({
          player_name: p.player_name,
          team: p.team,
          position: p.position,
          stat_type: p.stat_type,
          line: p.platform_line || 0,
          confidence: p.confidence || 50,
          agent_breakdown: p.agent_breakdown,
        })),
      });
      setCorrelation(resp.data);
    } catch {
      // Fail silently — correlation is supplementary
    }
  };

  const optimizeFlex = async () => {
    try {
      const resp = await apiService['client'].post('/api/dfs/optimize-flex', {
        picks: picks.map((p) => ({
          player_name: p.player_name,
          team: p.team,
          position: p.position,
          stat_type: p.stat_type,
          line: p.platform_line || 0,
          confidence: p.confidence || 50,
          agent_breakdown: p.agent_breakdown,
        })),
      });
      setFlex(resp.data);
    } catch {
      // Fail silently
    }
  };

  const togglePick = (line: DFSLine) => {
    const exists = picks.find((p) => p.player_id === line.player_id && p.stat_type === line.stat_type);
    if (exists) {
      setPicks(picks.filter((p) => !(p.player_id === line.player_id && p.stat_type === line.stat_type)));
    } else if (picks.length < MAX_PICKS) {
      setPicks([...picks, line]);
    }
  };

  const isPicked = (line: DFSLine) =>
    picks.some((p) => p.player_id === line.player_id && p.stat_type === line.stat_type);

  const filteredLines = searchQuery
    ? lines.filter(
        (l) =>
          l.player_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          l.team.toLowerCase().includes(searchQuery.toLowerCase()),
      )
    : lines;

  const renderLine = ({ item }: { item: DFSLine }) => {
    const selected = isPicked(item);
    return (
      <TouchableOpacity onPress={() => togglePick(item)} activeOpacity={0.7}>
        <PlayerCard
          player={{
            name: item.player_name,
            team: item.team,
            position: item.position,
            headshot_url: item.headshot_url,
          }}
          subtitle={`${item.platform_stat} · ${item.platform_line ?? '—'}`}
          rightContent={
            <View style={styles.pickRight}>
              <Text style={[styles.confidence, { color: (item.confidence || 0) >= 60 ? theme.colors.success : theme.colors.textSecondary }]}>
                {item.confidence ? Math.round(item.confidence) : '—'}
              </Text>
              <View style={[styles.checkCircle, selected && styles.checkCircleActive]}>
                {selected && <Ionicons name="checkmark" size={14} color="#fff" />}
              </View>
            </View>
          }
        />
      </TouchableOpacity>
    );
  };

  if (showReview) {
    return (
      <View style={styles.container}>
        <View style={styles.reviewHeader}>
          <TouchableOpacity onPress={() => setShowReview(false)} style={styles.backBtn}>
            <Ionicons name="chevron-back" size={24} color={theme.colors.textPrimary} />
          </TouchableOpacity>
          <Text style={styles.reviewTitle}>Review Parlay</Text>
          <View style={{ width: 40 }} />
        </View>

        <FlatList
          data={picks}
          keyExtractor={(item) => `${item.player_id}-${item.stat_type}`}
          contentContainerStyle={styles.reviewContent}
          renderItem={({ item }) => (
            <PlayerCard
              player={{
                name: item.player_name,
                team: item.team,
                position: item.position,
                headshot_url: item.headshot_url,
              }}
              subtitle={`${item.platform_stat} · ${item.platform_line ?? '—'} · ${item.direction || 'OVER'}`}
              rightContent={
                <Text style={styles.reviewConfidence}>{item.confidence ? Math.round(item.confidence) : '—'}</Text>
              }
            />
          )}
          ListFooterComponent={
            <>
              {correlation && (
                <CorrelationIndicator
                  penalty={correlation.total_penalty}
                  riskLevel={correlation.risk_level}
                  warnings={correlation.warnings}
                />
              )}
              {flex && (
                <FlexPlayOptimizer
                  flexPick={flex.flex_pick}
                  reason={flex.reason}
                  allCandidates={flex.all_candidates}
                />
              )}
              {picks.length > 0 && picks[0].agent_breakdown && (
                <AgentReasoningCard
                  playerName={picks[0].player_name}
                  drivers={Object.entries(picks[0].agent_breakdown).map(([name, data]: [string, any]) => ({
                    name,
                    score: data.score || 50,
                    weight: data.weight || 1,
                    direction: data.direction || 'OVER',
                  }))}
                />
              )}
            </>
          }
        />
      </View>
    );
  }

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color={theme.colors.primary} size="large" />
        <Text style={styles.loadingText}>Loading {platform} lines...</Text>
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
          <Text style={styles.headerTitle}>Build Parlay</Text>
          <Text style={styles.headerSub}>{platform} · Week {week}</Text>
        </View>
      </View>

      {/* Search */}
      <View style={styles.searchBar}>
        <Ionicons name="search" size={16} color={theme.colors.textTertiary} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search player or team..."
          placeholderTextColor={theme.colors.textTertiary}
          value={searchQuery}
          onChangeText={setSearchQuery}
        />
      </View>

      {/* Compact correlation indicator */}
      {correlation && picks.length >= 2 && (
        <View style={styles.correlationRow}>
          <CorrelationIndicator
            penalty={correlation.total_penalty}
            riskLevel={correlation.risk_level}
            compact
          />
        </View>
      )}

      {/* Player list */}
      <FlatList
        data={filteredLines}
        renderItem={renderLine}
        keyExtractor={(item) => `${item.player_id}-${item.stat_type}`}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={
          <View style={styles.center}>
            <Text style={styles.emptyText}>
              {searchQuery ? 'No matching players' : 'No lines available for this week'}
            </Text>
          </View>
        }
      />

      {/* Summary bar */}
      {picks.length > 0 && (
        <SlipSummaryBar
          pickCount={picks.length}
          maxPicks={MAX_PICKS}
          correlationRisk={correlation?.risk_level || 'low'}
          adjustedConfidence={correlation?.adjusted_confidence || 0}
          onReview={() => setShowReview(true)}
        />
      )}
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
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.glassInput,
    borderRadius: theme.borderRadius.s,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    paddingHorizontal: 10,
    height: 40,
    marginHorizontal: 16,
    marginBottom: 8,
    gap: 6,
  },
  searchInput: {
    flex: 1,
    color: theme.colors.textPrimary,
    fontSize: 14,
  },
  correlationRow: {
    paddingHorizontal: 16,
    marginBottom: 6,
  },
  listContent: {
    paddingHorizontal: 16,
    paddingBottom: 100,
  },
  pickRight: {
    alignItems: 'center',
    gap: 4,
  },
  confidence: {
    fontSize: 16,
    fontWeight: '800',
  },
  checkCircle: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: theme.colors.glassBorder,
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkCircleActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  loadingText: {
    marginTop: 12,
    color: theme.colors.textSecondary,
  },
  emptyText: {
    color: theme.colors.textTertiary,
    fontSize: 14,
    marginTop: 40,
  },
  // Review mode
  reviewHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: 12,
    paddingHorizontal: 12,
    paddingBottom: 8,
  },
  reviewTitle: {
    ...theme.typography.h2,
  },
  reviewContent: {
    paddingHorizontal: 16,
    paddingBottom: 40,
  },
  reviewConfidence: {
    fontSize: 20,
    fontWeight: '800',
    color: theme.colors.success,
  },
});
