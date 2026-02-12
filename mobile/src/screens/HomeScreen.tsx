/**
 * HomeScreen V2 — Unified feed with gradient text header, enhanced cards,
 * sparklines in Prop Edges, ConfidenceGauge in DFS, green/red fantasy alerts.
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../constants/theme';
import { apiService } from '../services/api';
import { useMode } from '../contexts/ModeContext';
import PlayerCard from '../components/player/PlayerCard';
import PlayerIntelligenceCard from '../components/player/PlayerIntelligenceCard';
import GameSlateCard from '../components/game/GameSlateCard';
import PlayerSearchBar from '../components/search/PlayerSearchBar';
import ConfidenceGauge from '../components/charts/ConfidenceGauge';
import GlassCard from '../components/common/GlassCard';
import AnimatedCard from '../components/animated/AnimatedCard';

interface FeedSection {
  title: string;
  subtitle: string;
  items: any[];
}

export default function HomeScreen({ navigation }: any) {
  const { setMode } = useMode();
  const [feed, setFeed] = useState<Record<string, FeedSection> | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedPlayerId, setSelectedPlayerId] = useState<number | null>(null);
  const [currentWeek] = useState(17);

  useEffect(() => {
    loadFeed();
  }, []);

  const loadFeed = async () => {
    try {
      const resp = await apiService['client'].get('/api/feed/home', {
        params: { week: currentWeek, limit: 5 },
      });
      setFeed(resp.data.sections);
    } catch (err) {
      console.error('Error loading feed:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadFeed();
  };

  const handlePlayerSelect = (player: any) => {
    setSelectedPlayerId(player.id);
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color={theme.colors.primary} size="large" />
        <Text style={styles.loadingText}>Loading your feed...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={theme.colors.primary} />}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Discover</Text>
          <Text style={styles.headerSub}>Week {currentWeek} {'\u00B7'} All Modes</Text>
        </View>

        {/* Universal Search */}
        <View style={styles.searchSection}>
          <PlayerSearchBar
            onSelectPlayer={handlePlayerSelect}
            placeholder="Search any player..."
          />
        </View>

        {/* Player Intel Card */}
        {selectedPlayerId && (
          <View style={styles.section}>
            <PlayerIntelligenceCard
              playerId={selectedPlayerId}
              week={currentWeek}
              onClose={() => setSelectedPlayerId(null)}
              compact
            />
          </View>
        )}

        {/* Top Prop Edges */}
        {feed?.prop_edges && feed.prop_edges.items.length > 0 && (
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <View>
                <Text style={styles.sectionTitle}>{feed.prop_edges.title}</Text>
                <Text style={styles.sectionSub}>{feed.prop_edges.subtitle}</Text>
              </View>
              <TouchableOpacity onPress={() => setMode('props')}>
                <Text style={styles.seeAll}>See All</Text>
              </TouchableOpacity>
            </View>
            {feed.prop_edges.items.map((item: any, i: number) => (
              <AnimatedCard key={i} index={i}>
                <TouchableOpacity
                  activeOpacity={0.7}
                  onPress={() => setSelectedPlayerId(item.player_id)}
                >
                  <PlayerCard
                    player={{
                      name: item.player_name,
                      team: item.team,
                      position: item.position,
                      headshot_url: item.headshot_url,
                    }}
                    subtitle={`${item.stat_type} ${'\u00B7'} ${item.direction} ${item.implied_line ?? ''}`}
                    confidence={item.confidence}
                    rightContent={
                      <View style={styles.edgeRight}>
                        <ConfidenceGauge score={item.confidence} size="sm" showLabel={false} />
                        <View style={styles.edgeBadge}>
                          <Text style={styles.edgeText}>+{item.edge?.toFixed(0)} edge</Text>
                        </View>
                      </View>
                    }
                  />
                </TouchableOpacity>
              </AnimatedCard>
            ))}
          </View>
        )}

        {/* DFS Highlights */}
        {feed?.dfs_picks && feed.dfs_picks.items.length > 0 && (
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <View>
                <Text style={styles.sectionTitle}>{feed.dfs_picks.title}</Text>
                <Text style={styles.sectionSub}>{feed.dfs_picks.subtitle}</Text>
              </View>
              <TouchableOpacity onPress={() => setMode('dfs')}>
                <Text style={styles.seeAll}>Go to DFS</Text>
              </TouchableOpacity>
            </View>
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.horizontalList}
            >
              {feed.dfs_picks.items.map((item: any, i: number) => (
                <TouchableOpacity
                  key={i}
                  style={styles.dfsChip}
                  activeOpacity={0.7}
                  onPress={() => setSelectedPlayerId(item.player_id)}
                >
                  <Text style={styles.dfsName} numberOfLines={1}>{item.player_name}</Text>
                  <Text style={styles.dfsMeta}>{item.team} {'\u00B7'} {item.position}</Text>
                  <View style={styles.dfsGauge}>
                    <ConfidenceGauge score={item.confidence} size="sm" showLabel={false} />
                  </View>
                  <Text style={styles.dfsDir}>{item.direction}</Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        )}

        {/* Fantasy Alerts */}
        {feed?.fantasy_alerts && feed.fantasy_alerts.items.length > 0 && (
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <View>
                <Text style={styles.sectionTitle}>{feed.fantasy_alerts.title}</Text>
                <Text style={styles.sectionSub}>{feed.fantasy_alerts.subtitle}</Text>
              </View>
              <TouchableOpacity onPress={() => setMode('fantasy')}>
                <Text style={styles.seeAll}>Fantasy</Text>
              </TouchableOpacity>
            </View>
            {feed.fantasy_alerts.items.map((item: any, i: number) => {
              const isStart = item.alert_type === 'start';
              return (
                <View
                  key={i}
                  style={[styles.alertRow, { borderLeftColor: isStart ? theme.colors.success : theme.colors.danger }]}
                >
                  <View style={[styles.alertIcon, { backgroundColor: isStart ? theme.colors.successMuted : theme.colors.dangerMuted }]}>
                    <Ionicons
                      name={isStart ? 'arrow-up' : 'arrow-down'}
                      size={14}
                      color={isStart ? theme.colors.success : theme.colors.danger}
                    />
                  </View>
                  <View style={styles.alertInfo}>
                    <Text style={styles.alertPlayer}>{item.player_name}</Text>
                    <Text style={styles.alertMsg}>{item.message}</Text>
                  </View>
                </View>
              );
            })}
          </View>
        )}

        {/* Game Slate */}
        {feed?.game_slate && feed.game_slate.items.length > 0 && (
          <View style={styles.section}>
            <GameSlateCard games={feed.game_slate.items} week={currentWeek} />
          </View>
        )}

        {/* Empty state */}
        {!feed && (
          <View style={styles.emptyState}>
            <Ionicons name="analytics-outline" size={48} color={theme.colors.textTertiary} />
            <Text style={styles.emptyTitle}>No Data Yet</Text>
            <Text style={styles.emptyText}>
              Once odds data is loaded for this week, your personalized feed will appear here.
            </Text>
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  content: {
    paddingBottom: 40,
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
  },
  header: {
    paddingTop: 16,
    paddingHorizontal: 20,
    paddingBottom: 12,
  },
  headerTitle: {
    ...theme.typography.h1,
    color: theme.colors.primary,
  },
  headerSub: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginTop: 2,
  },
  searchSection: {
    paddingHorizontal: 16,
    marginBottom: 12,
    zIndex: 100,
  },
  section: {
    paddingHorizontal: 16,
    marginBottom: 16,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 10,
  },
  sectionTitle: {
    ...theme.typography.h3,
  },
  sectionSub: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    marginTop: 1,
  },
  seeAll: {
    fontSize: 13,
    fontWeight: '600',
    color: theme.colors.primary,
  },
  // Prop edges
  edgeRight: {
    alignItems: 'center',
    gap: 4,
  },
  edgeBadge: {
    backgroundColor: theme.colors.successMuted,
    borderRadius: 4,
    paddingHorizontal: 6,
    paddingVertical: 1,
  },
  edgeText: {
    fontSize: 9,
    fontWeight: '700',
    color: theme.colors.success,
  },
  // DFS horizontal
  horizontalList: {
    gap: 10,
    paddingVertical: 2,
  },
  dfsChip: {
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 12,
    alignItems: 'center',
    width: 110,
  },
  dfsName: {
    fontSize: 12,
    fontWeight: '700',
    color: theme.colors.textPrimary,
    textAlign: 'center',
  },
  dfsMeta: {
    fontSize: 10,
    color: theme.colors.textTertiary,
    marginTop: 2,
  },
  dfsGauge: {
    marginVertical: 6,
  },
  dfsDir: {
    fontSize: 9,
    fontWeight: '700',
    color: theme.colors.textTertiary,
  },
  // Fantasy alerts
  alertRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: theme.borderRadius.s,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    borderLeftWidth: 3,
    padding: 10,
    marginBottom: 6,
    gap: 10,
  },
  alertIcon: {
    width: 30,
    height: 30,
    borderRadius: 15,
    justifyContent: 'center',
    alignItems: 'center',
  },
  alertInfo: {
    flex: 1,
  },
  alertPlayer: {
    fontSize: 13,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
  alertMsg: {
    fontSize: 11,
    color: theme.colors.textSecondary,
    marginTop: 1,
  },
  // Empty
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
  loadingText: {
    marginTop: 12,
    color: theme.colors.textSecondary,
  },
});
