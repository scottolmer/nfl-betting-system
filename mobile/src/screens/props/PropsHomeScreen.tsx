/**
 * PropsHomeScreen — Day-based prop browsing.
 * Shows one game day at a time with < > navigation.
 * Auto-selects the current/next game day on load.
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
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
import { sportsbookPreferences } from '../../services/userPreferences';
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

/** Parse "MM/DD/YYYY" or ISO 8601 into a Date (Hermes-safe) */
function parseCommenceTime(commenceTime?: string): Date | null {
  if (!commenceTime) return null;
  const slashParts = commenceTime.split('/');
  if (slashParts.length === 3) {
    const [month, day, year] = slashParts.map(Number);
    if (month && day && year) return new Date(year, month - 1, day);
  }
  const d = new Date(commenceTime);
  return isNaN(d.getTime()) ? null : d;
}

/** Returns a date key like "11/27/2025" for grouping */
function getDateKey(commenceTime?: string): string {
  const d = parseCommenceTime(commenceTime);
  if (!d) return '';
  return `${d.getMonth() + 1}/${d.getDate()}/${d.getFullYear()}`;
}

interface GameDay {
  dateKey: string;
  label: string;       // "Thu Nov 27"
  date: Date;
  count: number;
}

export default function PropsHomeScreen({ navigation }: any) {
  const { togglePick, isPicked, picks, isDayLocked } = useParlay();
  const [allProps, setAllProps] = useState<PropAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchFocused, setSearchFocused] = useState(false);
  const [activeDayIndex, setActiveDayIndex] = useState(0);
  const [currentWeek] = useState(() => {
    const seasonStart = new Date(2025, 8, 4);
    const now = new Date();
    const diffMs = now.getTime() - seasonStart.getTime();
    const diffWeeks = Math.floor(diffMs / (7 * 24 * 60 * 60 * 1000)) + 1;
    return Math.max(1, Math.min(18, diffWeeks));
  });

  const loadProps = useCallback(async () => {
    try {
      setError(null);
      const preferredBook = await sportsbookPreferences.getPreferredSportsbook();
      const data = await apiService.getProps({
        week: currentWeek,
        min_confidence: 55,
        preferred_book: preferredBook && preferredBook !== 'auto' ? preferredBook : undefined,
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
    setActiveFilter('All');
    setSearchQuery('');
    loadProps();
  }, [loadProps]);

  const onRefresh = () => {
    setRefreshing(true);
    loadProps();
  };

  // Derive unique game days sorted chronologically
  const gameDays: GameDay[] = useMemo(() => {
    const dayMap = new Map<string, GameDay>();
    allProps.forEach((p) => {
      if (p.commence_time) {
        const d = parseCommenceTime(p.commence_time);
        if (!d) return;
        const dateKey = getDateKey(p.commence_time);
        if (!dayMap.has(dateKey)) {
          const dayName = d.toLocaleDateString('en-US', { weekday: 'short' });
          const monthDay = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
          dayMap.set(dateKey, { dateKey, label: `${dayName} ${monthDay}`, date: d, count: 0 });
        }
        dayMap.get(dateKey)!.count++;
      }
    });
    return Array.from(dayMap.values()).sort((a, b) => a.date.getTime() - b.date.getTime());
  }, [allProps]);

  // Auto-select current/next game day when data loads
  useEffect(() => {
    if (gameDays.length === 0) return;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    // Find first day that is today or in the future
    let bestIndex = gameDays.findIndex((d) => {
      const gameDate = new Date(d.date);
      gameDate.setHours(0, 0, 0, 0);
      return gameDate >= today;
    });
    // All days in the past — show the last one
    if (bestIndex === -1) bestIndex = gameDays.length - 1;
    setActiveDayIndex(bestIndex);
  }, [gameDays]);

  const activeDay = gameDays[activeDayIndex] || null;
  const canGoBack = activeDayIndex > 0;
  const canGoForward = activeDayIndex < gameDays.length - 1;

  // Filter to active day + stat type + search
  const filteredProps = allProps.filter((p) => {
    // Day filter
    if (activeDay) {
      const propKey = getDateKey(p.commence_time);
      if (propKey !== activeDay.dateKey) return false;
    }
    // Stat type filter
    if (activeFilter !== 'All') {
      if (activeFilter === 'TDs') {
        if (!p.stat_type.includes('TD')) return false;
      } else if (p.stat_type !== activeFilter) {
        return false;
      }
    }
    // Search filter
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
    const dayMismatch = isDayLocked(item);
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
                onPress={() => { if (!dayMismatch) togglePick(item); }}
                style={[
                  styles.addBtn,
                  selected && styles.addBtnActive,
                  dayMismatch && styles.addBtnDimmed,
                ]}
                activeOpacity={dayMismatch ? 1 : 0.7}
              >
                <Ionicons
                  name={selected ? 'checkmark' : 'add'}
                  size={16}
                  color={
                    dayMismatch
                      ? theme.colors.textTertiary
                      : selected
                        ? '#000'
                        : theme.colors.primary
                  }
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
      </View>

      {/* Day Navigator */}
      {gameDays.length > 0 ? (
        <View style={styles.dayNav}>
          <TouchableOpacity
            onPress={() => setActiveDayIndex((i) => Math.max(0, i - 1))}
            style={styles.dayArrow}
            disabled={!canGoBack}
          >
            <Ionicons
              name="chevron-back"
              size={22}
              color={canGoBack ? theme.colors.primary : theme.colors.textTertiary}
            />
          </TouchableOpacity>
          <View style={styles.dayCenter}>
            <Text style={styles.dayLabel}>{activeDay?.label}</Text>
            <Text style={styles.dayCount}>{activeDay?.count} props</Text>
          </View>
          <TouchableOpacity
            onPress={() => setActiveDayIndex((i) => Math.min(gameDays.length - 1, i + 1))}
            style={styles.dayArrow}
            disabled={!canGoForward}
          >
            <Ionicons
              name="chevron-forward"
              size={22}
              color={canGoForward ? theme.colors.primary : theme.colors.textTertiary}
            />
          </TouchableOpacity>
        </View>
      ) : (
        <View style={styles.dayNav}>
          <Text style={styles.dayLabel}>No games this week</Text>
        </View>
      )}

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
      {!loading && filteredProps.length > 0 && (
        <Text style={styles.resultCount}>
          {filteredProps.length} props
          {activeFilter !== 'All' || searchQuery ? ` (filtered)` : ''}
        </Text>
      )}

      {/* Props List */}
      <FlatList
        data={filteredProps}
        renderItem={renderPropItem}
        keyExtractor={(item, i) => `${item.player_name}-${item.stat_type}-${item.bet_type}`}
        contentContainerStyle={[
          styles.listContent,
          picks.length > 0 && styles.listContentWithBar,
        ]}
        removeClippedSubviews={true}
        initialNumToRender={8}
        windowSize={5}
        maxToRenderPerBatch={8}
        updateCellsBatchingPeriod={50}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={theme.colors.primary}
          />
        }
        ListEmptyComponent={
          <View style={styles.emptyCenter}>
            <Text style={styles.emptyText}>
              {searchQuery ? 'No matching props found' : 'No props available for this day'}
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
    paddingBottom: 4,
  },
  headerTitle: {
    ...theme.typography.h1,
    color: theme.colors.primary,
  },
  // Day navigator
  dayNav: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 16,
    paddingVertical: 10,
  },
  dayArrow: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },
  dayCenter: {
    flex: 1,
    alignItems: 'center',
  },
  dayLabel: {
    fontSize: 18,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
  dayCount: {
    fontSize: 12,
    fontWeight: '500',
    color: theme.colors.textTertiary,
    marginTop: 2,
  },
  // Search
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
  // Stat filters
  filterList: {
    height: 54,
    flexGrow: 0,
    marginBottom: 4,
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
  // Right actions
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
  addBtnDimmed: {
    borderColor: theme.colors.textTertiary,
    opacity: 0.35,
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
