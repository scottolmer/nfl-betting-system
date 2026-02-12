/**
 * EdgeFinderScreen — Sorted list of biggest edges (confidence vs line divergence).
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
import PlayerCard from '../../components/player/PlayerCard';
import { apiService } from '../../services/api';

interface EdgeResult {
  player_name: string;
  team: string;
  position: string;
  headshot_url?: string;
  stat_type: string;
  line: number;
  direction: string;
  confidence: number;
  best_book: string;
  best_price: number;
  edge_pct: number;
  suggested_units: number;
  has_edge: boolean;
}

export default function EdgeFinderScreen({ route, navigation }: any) {
  const week = route.params?.week || 17;
  const [edges, setEdges] = useState<EdgeResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadEdges = async () => {
    try {
      // Call the edge-finder endpoint
      const resp = await apiService['client'].get('/api/props/edge-finder', {
        params: { week, min_edge: 2, min_confidence: 55, limit: 30 },
      });
      setEdges(resp.data);
    } catch (err) {
      console.error('Edge finder error:', err);
      // Fallback: show empty state gracefully
      setEdges([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadEdges();
  }, []);

  const formatOdds = (price: number) => (price > 0 ? `+${price}` : `${price}`);

  const renderEdge = ({ item }: { item: EdgeResult }) => (
    <PlayerCard
      player={{
        name: item.player_name,
        team: item.team,
        position: item.position,
        headshot_url: item.headshot_url,
      }}
      subtitle={`${item.stat_type} ${item.direction} ${item.line} · ${item.best_book}`}
      onPress={() => navigation.navigate('PropDetail', {
        prop: {
          player_name: item.player_name,
          team: item.team,
          position: item.position,
          stat_type: item.stat_type,
          line: item.line,
          bet_type: item.direction,
          opponent: '',
          confidence: item.confidence,
          top_reasons: [],
          agent_analyses: [],
        },
        week,
      })}
      rightContent={
        <View style={styles.edgeBadge}>
          <Text style={styles.edgePct}>+{item.edge_pct.toFixed(1)}%</Text>
          <Text style={styles.edgeUnits}>{item.suggested_units.toFixed(1)}u</Text>
          <Text style={styles.edgePrice}>{formatOdds(item.best_price)}</Text>
        </View>
      }
    />
  );

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color={theme.colors.primary} size="large" />
        <Text style={styles.loadingText}>Finding edges...</Text>
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
          <Text style={styles.headerTitle}>Edge Finder</Text>
          <Text style={styles.headerSubtitle}>{edges.length} edges found · Week {week}</Text>
        </View>
      </View>

      <FlatList
        data={edges}
        renderItem={renderEdge}
        keyExtractor={(item, i) => `${item.player_name}-${item.stat_type}-${i}`}
        contentContainerStyle={styles.listContent}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); loadEdges(); }} tintColor={theme.colors.primary} />}
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Ionicons name="flash-outline" size={48} color={theme.colors.textTertiary} />
            <Text style={styles.emptyTitle}>No Edges Found</Text>
            <Text style={styles.emptyText}>
              Edges appear when our engine's confidence significantly exceeds the market's implied probability.
              Check back closer to game time when odds data is available.
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
    paddingTop: 56,
    paddingHorizontal: 16,
    paddingBottom: 12,
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
  headerSubtitle: {
    fontSize: 13,
    color: theme.colors.textSecondary,
  },
  listContent: {
    paddingHorizontal: 16,
    paddingBottom: 40,
  },
  edgeBadge: {
    alignItems: 'flex-end',
  },
  edgePct: {
    fontSize: 16,
    fontWeight: '800',
    color: theme.colors.success,
  },
  edgeUnits: {
    fontSize: 12,
    fontWeight: '700',
    color: theme.colors.gold,
  },
  edgePrice: {
    fontSize: 10,
    color: theme.colors.textTertiary,
    fontWeight: '600',
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
