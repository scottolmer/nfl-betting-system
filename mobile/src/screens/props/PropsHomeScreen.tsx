/**
 * PropsHomeScreen — Top picks feed, category filters, search, pull-to-refresh.
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
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';
import { apiService } from '../../services/api';
import { PropAnalysis } from '../../types';
import PlayerCard from '../../components/player/PlayerCard';

const STAT_FILTERS = ['All', 'Pass Yds', 'Rush Yds', 'Rec Yds', 'Receptions', 'TDs'];

export default function PropsHomeScreen({ navigation }: any) {
  const [props, setProps] = useState<PropAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [currentWeek] = useState(17);

  const loadProps = useCallback(async () => {
    try {
      setError(null);
      const statType = activeFilter === 'All' ? undefined : activeFilter;
      const data = await apiService.getProps({
        week: currentWeek,
        min_confidence: 55,
        stat_type: statType,
        limit: 50,
      });
      setProps(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load props');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [activeFilter, currentWeek]);

  useEffect(() => {
    loadProps();
  }, [loadProps]);

  const onRefresh = () => {
    setRefreshing(true);
    loadProps();
  };

  const filteredProps = searchQuery
    ? props.filter((p) =>
        p.player_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.team.toLowerCase().includes(searchQuery.toLowerCase()),
      )
    : props;

  const getConfidenceColor = (c: number) => {
    if (c >= 70) return theme.colors.success;
    if (c >= 60) return theme.colors.primary;
    return theme.colors.textSecondary;
  };

  const renderPropItem = ({ item }: { item: PropAnalysis }) => (
    <PlayerCard
      player={{
        name: item.player_name,
        team: item.team,
        position: item.position,
      }}
      subtitle={`${item.stat_type} ${item.bet_type} ${item.line}`}
      onPress={() =>
        navigation.navigate('PropDetail', {
          prop: item,
          week: currentWeek,
        })
      }
      rightContent={
        <View style={styles.confidenceBadge}>
          <Text style={[styles.confidenceText, { color: getConfidenceColor(item.confidence) }]}>
            {Math.round(item.confidence)}
          </Text>
          <Text style={styles.confidenceLabel}>{item.bet_type}</Text>
        </View>
      }
    />
  );

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
        <View style={styles.searchBar}>
          <Ionicons name="search" size={16} color={theme.colors.textTertiary} />
          <TextInput
            style={styles.searchInput}
            placeholder="Search player or team..."
            placeholderTextColor={theme.colors.textTertiary}
            value={searchQuery}
            onChangeText={setSearchQuery}
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
      <FlatList
        horizontal
        showsHorizontalScrollIndicator={false}
        data={STAT_FILTERS}
        keyExtractor={(item) => item}
        style={styles.filterList}
        contentContainerStyle={styles.filterContent}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={[styles.filterChip, activeFilter === item && styles.filterChipActive]}
            onPress={() => setActiveFilter(item)}
          >
            <Text style={[styles.filterText, activeFilter === item && styles.filterTextActive]}>
              {item}
            </Text>
          </TouchableOpacity>
        )}
      />

      {/* Error State */}
      {error && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity onPress={loadProps}>
            <Text style={styles.retryText}>Retry</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Props List */}
      <FlatList
        data={filteredProps}
        renderItem={renderPropItem}
        keyExtractor={(item, i) => `${item.player_name}-${item.stat_type}-${i}`}
        contentContainerStyle={styles.listContent}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={theme.colors.primary} />}
        ListEmptyComponent={
          <View style={styles.center}>
            <Text style={styles.emptyText}>
              {searchQuery ? 'No matching props found' : 'No props available'}
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
    paddingTop: 60,
    paddingHorizontal: 20,
    paddingBottom: 12,
  },
  headerTitle: {
    ...theme.typography.h1,
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
    backgroundColor: theme.colors.glassInput,
    borderRadius: theme.borderRadius.s,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    paddingHorizontal: 10,
    height: 40,
    gap: 6,
  },
  searchInput: {
    flex: 1,
    color: theme.colors.textPrimary,
    fontSize: 14,
  },
  edgeButton: {
    width: 40,
    height: 40,
    borderRadius: theme.borderRadius.s,
    backgroundColor: theme.colors.glassLow,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    justifyContent: 'center',
    alignItems: 'center',
  },
  filterList: {
    maxHeight: 40,
    marginBottom: 8,
  },
  filterContent: {
    paddingHorizontal: 16,
    gap: 6,
  },
  filterChip: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: theme.borderRadius.pill,
    backgroundColor: theme.colors.glassLow,
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
    color: '#fff',
  },
  listContent: {
    paddingHorizontal: 16,
    paddingBottom: 80,
  },
  confidenceBadge: {
    alignItems: 'center',
  },
  confidenceText: {
    fontSize: 20,
    fontWeight: '800',
  },
  confidenceLabel: {
    fontSize: 10,
    fontWeight: '700',
    color: theme.colors.textTertiary,
  },
  loadingText: {
    marginTop: 12,
    color: theme.colors.textSecondary,
  },
  errorBanner: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: 'rgba(244,63,94,0.15)',
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
  emptyText: {
    color: theme.colors.textTertiary,
    fontSize: 14,
    marginTop: 40,
  },
});
