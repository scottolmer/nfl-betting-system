/**
 * PropsHomeScreen V2 — Chart-rich cards, gradient text header, Hot Picks scroll,
 * pill search bar with cyan focus, filter chips with cyan active state.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
  TouchableOpacity,
  TextInput,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';
import { apiService } from '../../services/api';
import { PropAnalysis } from '../../types';
import PlayerCard from '../../components/player/PlayerCard';
import ConfidenceGauge from '../../components/charts/ConfidenceGauge';
import AnimatedCard from '../../components/animated/AnimatedCard';
import FloatingParlayBar from '../../components/parlay/FloatingParlayBar';
import { useParlay } from '../../contexts/ParlayContext';

const STAT_FILTERS = ['All', 'Pass Yds', 'Rush Yds', 'Rec Yds', 'Receptions', 'TDs'];

const TEAM_SEARCH: Record<string, string[]> = {
  ARI: ['cardinals', 'arizona'],
  ATL: ['falcons', 'atlanta'],
  BAL: ['ravens', 'baltimore'],
  BUF: ['bills', 'buffalo'],
  CAR: ['panthers', 'carolina'],
  CHI: ['bears', 'chicago'],
  CIN: ['bengals', 'cincinnati'],
  CLE: ['browns', 'cleveland'],
  DAL: ['cowboys', 'dallas'],
  DEN: ['broncos', 'denver'],
  DET: ['lions', 'detroit'],
  GB: ['packers', 'green bay'],
  HOU: ['texans', 'houston'],
  IND: ['colts', 'indianapolis'],
  JAX: ['jaguars', 'jacksonville'],
  KC: ['chiefs', 'kansas city'],
  LAC: ['chargers', 'los angeles chargers'],
  LAR: ['rams', 'los angeles rams'],
  LV: ['raiders', 'las vegas'],
  MIA: ['dolphins', 'miami'],
  MIN: ['vikings', 'minnesota'],
  NE: ['patriots', 'new england'],
  NO: ['saints', 'new orleans'],
  NYG: ['giants', 'new york giants'],
  NYJ: ['jets', 'new york jets'],
  PHI: ['eagles', 'philadelphia'],
  PIT: ['steelers', 'pittsburgh'],
  SEA: ['seahawks', 'seattle'],
  SF: ['49ers', 'niners', 'san francisco'],
  TB: ['buccaneers', 'bucs', 'tampa bay'],
  TEN: ['titans', 'tennessee'],
  WAS: ['commanders', 'washington'],
};

function matchesTeamSearch(teamAbbr: string, query: string): boolean {
  if (teamAbbr.toLowerCase().includes(query)) return true;
  const aliases = TEAM_SEARCH[teamAbbr.toUpperCase()];
  return aliases ? aliases.some((a) => a.includes(query)) : false;
}

export default function PropsHomeScreen({ navigation }: any) {
  const { togglePick, isPicked, picks } = useParlay();
  const [allProps, setAllProps] = useState<PropAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchFocused, setSearchFocused] = useState(false);
  const [currentWeek] = useState(13);

  const loadProps = useCallback(async () => {
    try {
      setError(null);
      const data = await apiService.getProps({
        week: currentWeek,
        min_confidence: 55,
        limit: 200,
      });
      setAllProps(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load props');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [currentWeek]);

  useEffect(() => {
    loadProps();
  }, [loadProps]);

  const onRefresh = () => {
    setRefreshing(true);
    loadProps();
  };

  // Client-side filtering (instant)
  const filteredProps = allProps.filter((p) => {
    // Stat type filter
    if (activeFilter !== 'All') {
      if (activeFilter === 'TDs') {
        if (!p.stat_type.includes('TD')) return false;
      } else if (p.stat_type !== activeFilter) {
        return false;
      }
    }
    // Search filter (player name, team abbr, team name, city)
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      if (!p.player_name.toLowerCase().includes(q) && !matchesTeamSearch(p.team, q)) {
        return false;
      }
    }
    return true;
  });

  const renderPropItem = ({ item, index }: { item: PropAnalysis; index: number }) => {
    const selected = isPicked(item);
    return (
      <AnimatedCard index={index}>
        <PlayerCard
          player={{
            name: item.player_name,
            team: item.team,
            position: item.position,
          }}
          subtitle={`${item.stat_type} ${item.bet_type} ${item.line}`}
          confidence={item.confidence}
          onPress={() =>
            navigation.navigate('PropDetail', {
              prop: item,
              week: currentWeek,
            })
          }
          rightContent={
            <View style={styles.rightActions}>
              <ConfidenceGauge score={item.confidence} size="sm" showLabel={false} />
              <TouchableOpacity
                onPress={() => togglePick(item)}
                style={[styles.addBtn, selected && styles.addBtnActive]}
                activeOpacity={0.7}
              >
                <Ionicons
                  name={selected ? 'checkmark' : 'add'}
                  size={16}
                  color={selected ? '#000' : theme.colors.primary}
                />
              </TouchableOpacity>
            </View>
          }
        />
      </AnimatedCard>
    );
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color={theme.colors.primary} size="large" />
        <Text style={styles.loadingText}>Loading props...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Props</Text>
        <Text style={styles.headerSubtitle}>Week {currentWeek}</Text>
      </View>

      {/* Search */}
      <View style={styles.searchRow}>
        <View style={[styles.searchBar, searchFocused && styles.searchBarFocused]}>
          <Ionicons name="search" size={16} color={searchFocused ? theme.colors.primary : theme.colors.textTertiary} />
          <TextInput
            style={styles.searchInput}
            placeholder="Search player or team..."
            placeholderTextColor={theme.colors.textTertiary}
            value={searchQuery}
            onChangeText={setSearchQuery}
            onFocus={() => setSearchFocused(true)}
            onBlur={() => setSearchFocused(false)}
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity onPress={() => setSearchQuery('')}>
              <Ionicons name="close-circle" size={16} color={theme.colors.textTertiary} />
            </TouchableOpacity>
          )}
        </View>
        <TouchableOpacity
          style={styles.edgeButton}
          onPress={() => navigation.navigate('EdgeFinder', { week: currentWeek })}
        >
          <Ionicons name="flash" size={18} color={theme.colors.gold} />
        </TouchableOpacity>
      </View>

      {/* AI Parlays CTA */}
      <TouchableOpacity
        style={styles.aiParlaysCTA}
        onPress={() => navigation.navigate('AIParlays', { week: currentWeek })}
        activeOpacity={0.8}
      >
        <Ionicons name="sparkles" size={16} color={theme.colors.primary} />
        <Text style={styles.aiParlaysText}>AI Parlays</Text>
        <Text style={styles.aiParlaysSub}>6-agent optimized</Text>
        <Ionicons name="chevron-forward" size={14} color={theme.colors.textTertiary} />
      </TouchableOpacity>

      {/* Stat Filters */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.filterList}
        contentContainerStyle={styles.filterContent}
      >
        {STAT_FILTERS.map((item) => (
          <TouchableOpacity
            key={item}
            style={[styles.filterChip, activeFilter === item && styles.filterChipActive]}
            onPress={() => setActiveFilter(item)}
          >
            <Text style={[styles.filterText, activeFilter === item && styles.filterTextActive]}>
              {item}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Error State */}
      {error && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity onPress={loadProps}>
            <Text style={styles.retryText}>Retry</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Result count */}
      {!loading && allProps.length > 0 && (
        <Text style={styles.resultCount}>
          {filteredProps.length} of {allProps.length} props
        </Text>
      )}

      {/* Props List */}
      <FlatList
        data={filteredProps}
        renderItem={renderPropItem}
        keyExtractor={(item, i) => `${item.player_name}-${item.stat_type}-${i}`}
        contentContainerStyle={[styles.listContent, picks.length > 0 && styles.listContentWithBar]}
        removeClippedSubviews={true}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={theme.colors.primary} />}
        ListEmptyComponent={
          <View style={styles.emptyCenter}>
            <Text style={styles.emptyText}>
              {searchQuery ? 'No matching props found' : 'No props available'}
            </Text>
          </View>
        }
      />

      {/* Floating parlay bar */}
      <FloatingParlayBar onReview={() => navigation.navigate('ParlayReview')} />
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
    paddingTop: 60,
    paddingHorizontal: 20,
    paddingBottom: 12,
  },
  headerTitle: {
    ...theme.typography.h1,
    color: theme.colors.primary,
  },
  headerSubtitle: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginTop: 2,
  },
  searchRow: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    marginBottom: 8,
    gap: 8,
  },
  searchBar: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: theme.borderRadius.pill,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    paddingHorizontal: 14,
    height: 40,
    gap: 8,
  },
  searchBarFocused: {
    borderColor: theme.colors.glassBorderActive,
  },
  searchInput: {
    flex: 1,
    color: theme.colors.textPrimary,
    fontSize: 14,
  },
  edgeButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: theme.colors.backgroundCard,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    justifyContent: 'center',
    alignItems: 'center',
  },
  aiParlaysCTA: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.backgroundCard,
    borderWidth: 1,
    borderColor: theme.colors.glassBorderActive,
    borderRadius: theme.borderRadius.m,
    marginHorizontal: 16,
    marginBottom: 10,
    paddingHorizontal: 14,
    paddingVertical: 10,
    gap: 8,
  },
  aiParlaysText: {
    fontSize: 14,
    fontWeight: '700',
    color: theme.colors.primary,
  },
  aiParlaysSub: {
    flex: 1,
    fontSize: 11,
    color: theme.colors.textTertiary,
  },
  filterList: {
    height: 50,
    flexGrow: 0,
    marginBottom: 12,
  },
  filterContent: {
    paddingHorizontal: 16,
    gap: 8,
    alignItems: 'center',
  },
  filterChip: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: theme.borderRadius.pill,
    backgroundColor: theme.colors.backgroundCard,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
  },
  filterChipActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  filterText: {
    fontSize: 12,
    fontWeight: '600',
    color: theme.colors.textSecondary,
  },
  filterTextActive: {
    color: '#000',
  },

  resultCount: {
    fontSize: 12,
    color: theme.colors.textTertiary,
    paddingHorizontal: 16,
    marginBottom: 8,
  },
  // Right actions (confidence + add button)
  rightActions: {
    alignItems: 'center',
    gap: 6,
  },
  addBtn: {
    width: 28,
    height: 28,
    borderRadius: 14,
    borderWidth: 1.5,
    borderColor: theme.colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  addBtnActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  // List
  listContent: {
    paddingHorizontal: 16,
    paddingBottom: 80,
  },
  listContentWithBar: {
    paddingBottom: 140,
  },
  loadingText: {
    marginTop: 12,
    color: theme.colors.textSecondary,
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
  },
  retryText: {
    color: theme.colors.primary,
    fontSize: 12,
    fontWeight: '700',
  },
  emptyCenter: {
    alignItems: 'center',
    marginTop: 40,
  },
  emptyText: {
    color: theme.colors.textTertiary,
    fontSize: 14,
  },
});
