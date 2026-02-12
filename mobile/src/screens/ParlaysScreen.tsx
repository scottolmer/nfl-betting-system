import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
  TouchableOpacity,
  ScrollView,
} from 'react-native';
import { apiService } from '../services/api';
import { Parlay, ParlayLeg } from '../types';
import HelpBanner from '../components/common/HelpBanner';
import InfoTooltip from '../components/common/InfoTooltip';
import ParlayFilters, { FilterOption } from '../components/parlays/ParlayFilters';
import Badge from '../components/common/Badge';
import { theme } from '../constants/theme';

export default function ParlaysScreen() {
  const [parlays, setParlays] = useState<Parlay[]>([]);
  const [filteredParlays, setFilteredParlays] = useState<Parlay[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedParlay, setExpandedParlay] = useState<string | null>(null);
  const [currentWeek] = useState(17); // TODO: Make this dynamic
  const [selectedFilter, setSelectedFilter] = useState<FilterOption>('all');

  useEffect(() => {
    loadParlays();
  }, []);

  const loadParlays = async () => {
    try {
      setError(null);
      const data = await apiService.getPrebuiltParlays({
        week: currentWeek,
        min_confidence: 58,
      });
      setParlays(data);
      setFilteredParlays(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load parlays');
      console.error('Error loading parlays:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleFilterChange = (filter: FilterOption) => {
    setSelectedFilter(filter);

    if (filter === 'all') {
      setFilteredParlays(parlays);
    } else if (filter === '2-leg') {
      setFilteredParlays(parlays.filter(p => p.leg_count === 2));
    } else if (filter === '3-leg') {
      setFilteredParlays(parlays.filter(p => p.leg_count === 3));
    } else if (filter === '4+') {
      setFilteredParlays(parlays.filter(p => p.leg_count >= 4));
    }
  };

  const getFilterCounts = () => ({
    all: parlays.length,
    '2-leg': parlays.filter(p => p.leg_count === 2).length,
    '3-leg': parlays.filter(p => p.leg_count === 3).length,
    '4+': parlays.filter(p => p.leg_count >= 4).length,
  });

  const onRefresh = () => {
    setRefreshing(true);
    loadParlays();
  };

  const toggleExpand = (parlayId: string) => {
    setExpandedParlay(expandedParlay === parlayId ? null : parlayId);
  };

  const getRiskColor = (risk: string): string => {
    switch (risk) {
      case 'LOW':
        return theme.colors.success;
      case 'MEDIUM':
        return theme.colors.warning;
      case 'HIGH':
        return theme.colors.danger;
      default:
        return theme.colors.textSecondary;
    }
  };

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 80) return theme.colors.success;
    if (confidence >= 70) return theme.colors.warning;
    return theme.colors.textSecondary;
  };

  const renderLeg = (leg: ParlayLeg, index: number) => (
    <View key={index} style={styles.legContainer}>
      <View style={styles.legHeader}>
        <Text style={styles.legNumber}>{index + 1}</Text>
        <View style={styles.legInfo}>
          <Text style={styles.legPlayer}>
            {leg.player_name} ({leg.team})
          </Text>
          <Text style={styles.legDetails}>
            {leg.stat_type} {leg.bet_type} {leg.line} vs {leg.opponent}
          </Text>
          <Text style={[styles.legConfidence, { color: getConfidenceColor(leg.confidence) }]}>
            {Math.round(leg.confidence)} confidence
          </Text>
        </View>
      </View>
    </View>
  );

  const renderParlayCard = ({ item, index }: { item: Parlay; index: number }) => {
    const isExpanded = expandedParlay === item.id;
    const isFeatured = index === 0 && item.combined_confidence >= 75;

    return (
      <View style={styles.parlayCard}>
        {isFeatured && (
          <View style={styles.featuredBadgeContainer}>
            <Badge text="FEATURED" variant="featured" size="small" />
          </View>
        )}
        <TouchableOpacity onPress={() => toggleExpand(item.id)}>
          <View style={styles.parlayHeader}>
            <View style={styles.parlayTitleContainer}>
              <Text style={styles.parlayTitle}>{item.name}</Text>
              <View style={styles.parlayMetaRow}>
                <Text style={styles.parlaySubtitle}>
                  {item.leg_count} legs • {Math.round(item.combined_confidence)} confidence
                </Text>
                <InfoTooltip tooltipKey="combinedConfidence" iconSize={14} iconColor={theme.colors.textTertiary} />
              </View>
            </View>
            <View style={styles.parlayBadges}>
              <View style={styles.riskBadgeContainer}>
                <View style={[styles.riskBadge, { backgroundColor: getRiskColor(item.risk_level) }]}>
                  <Text style={styles.riskBadgeText}>{item.risk_level}</Text>
                </View>
                <InfoTooltip tooltipKey="riskLevel" iconSize={12} iconColor={theme.colors.textTertiary} />
              </View>
            </View>
          </View>
        </TouchableOpacity>

        {isExpanded && (
          <View style={styles.parlayLegs}>
            <View style={styles.legsHeader}>
              <Text style={styles.legsHeaderText}>Parlay Legs</Text>
            </View>
            {item.legs.map((leg, index) => renderLeg(leg, index))}

            <View style={styles.actionsContainer}>
              <TouchableOpacity style={styles.primaryButton}>
                <Text style={styles.primaryButtonText}>📋 Copy Props</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.secondaryButton}>
                <Text style={styles.secondaryButtonText}>💾 Save</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator color={theme.colors.primary} />
        <Text style={styles.loadingText}>Generating parlays...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>⚠️ {error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={loadParlays}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.headerTop}>
          <View>
            <Text style={styles.headerTitle}>Pre-Built Parlays</Text>
            <Text style={styles.headerSubtitle}>
              Week {currentWeek} • {parlays.length} Parlays
            </Text>
          </View>
          <InfoTooltip tooltipKey="preBuildParlays" iconSize={20} iconColor={theme.colors.textTertiary} />
        </View>
      </View>

      <FlatList
        data={filteredParlays}
        renderItem={renderParlayCard}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListHeaderComponent={
          <>
            <HelpBanner
              bannerId="prebuilt-parlays-help"
              title="How to Use"
              items={[
                'Browse combinations below',
                'Tap to see details',
                'Copy to your sportsbook',
                'Save to My Parlays',
              ]}
            />
            <ParlayFilters
              selectedFilter={selectedFilter}
              onFilterChange={handleFilterChange}
              counts={getFilterCounts()}
            />
          </>
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No parlays match the selected filter</Text>
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
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
    padding: 20,
  },
  header: {
    backgroundColor: theme.colors.backgroundCard,
    paddingTop: 60,
    paddingBottom: 16,
    paddingHorizontal: 20,
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.textPrimary,
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 14,
    color: theme.colors.textTertiary,
  },
  listContainer: {
    paddingBottom: 16,
  },
  parlayCard: {
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: 12,
    marginBottom: 12,
    marginHorizontal: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    overflow: 'hidden',
  },
  featuredBadgeContainer: {
    position: 'absolute',
    top: 12,
    right: 12,
    zIndex: 10,
  },
  parlayHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
  },
  parlayTitleContainer: {
    flex: 1,
  },
  parlayTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.textPrimary,
    marginBottom: 4,
  },
  parlayMetaRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  parlaySubtitle: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  parlayBadges: {
    alignItems: 'flex-end',
  },
  riskBadgeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  riskBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  riskBadgeText: {
    color: theme.colors.textPrimary,
    fontSize: 12,
    fontWeight: 'bold',
  },
  parlayLegs: {
    borderTopWidth: 1,
    borderTopColor: theme.colors.glassBorder,
    backgroundColor: theme.colors.backgroundElevated,
  },
  legsHeader: {
    padding: 12,
    backgroundColor: theme.colors.backgroundElevated,
  },
  legsHeaderText: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.textSecondary,
    textTransform: 'uppercase',
  },
  legContainer: {
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.glassBorder,
  },
  legHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  legNumber: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: theme.colors.primary,
    color: theme.colors.backgroundCard,
    textAlign: 'center',
    lineHeight: 24,
    fontSize: 14,
    fontWeight: 'bold',
    marginRight: 12,
  },
  legInfo: {
    flex: 1,
  },
  legPlayer: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.textPrimary,
    marginBottom: 2,
  },
  legDetails: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginBottom: 4,
  },
  legConfidence: {
    fontSize: 13,
    fontWeight: '600',
  },
  actionsContainer: {
    flexDirection: 'row',
    padding: 12,
    gap: 8,
  },
  primaryButton: {
    flex: 1,
    backgroundColor: theme.colors.primary,
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  primaryButtonText: {
    color: theme.colors.backgroundCard,
    fontSize: 16,
    fontWeight: '600',
  },
  secondaryButton: {
    flex: 1,
    backgroundColor: theme.colors.backgroundCard,
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
  },
  secondaryButtonText: {
    color: theme.colors.textPrimary,
    fontSize: 16,
    fontWeight: '600',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: theme.colors.textSecondary,
  },
  errorText: {
    fontSize: 16,
    color: theme.colors.danger,
    textAlign: 'center',
    marginBottom: 16,
  },
  retryButton: {
    backgroundColor: theme.colors.primary,
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: theme.colors.backgroundCard,
    fontSize: 16,
    fontWeight: '600',
  },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: theme.colors.textSecondary,
  },
});
