/**
 * Results Screen
 * Track betting performance with analytics
 */

import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl, TouchableOpacity, Alert } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { parlayStorage } from '../services/parlayStorage';
import { backendPreferences } from '../services/userPreferences';
import { SavedParlay } from '../types';
import ResultsSummaryCard from '../components/results/ResultsSummaryCard';
import ResultsAnalyticsCard from '../components/results/ResultsAnalyticsCard';
import ParlayResultCard from '../components/results/ParlayResultCard';
import ResultsFilterBar, { ResultsFilters } from '../components/results/ResultsFilterBar';
import ResultsEmptyState from '../components/results/ResultsEmptyState';
import InfoTooltip from '../components/common/InfoTooltip';

export default function ResultsScreen({ navigation }: any) {
  const [parlays, setParlays] = useState<SavedParlay[]>([]);
  const [filteredParlays, setFilteredParlays] = useState<SavedParlay[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filters, setFilters] = useState<ResultsFilters>({ status: 'all' });

  const loadData = async () => {
    try {
      const allParlays = await parlayStorage.getAllParlays();
      setParlays(allParlays);

      const analyticsData = await parlayStorage.getAnalytics();
      setAnalytics(analyticsData);
    } catch (error) {
      console.error('Error loading results:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);

    try {
      const backendUrl = await backendPreferences.getBackendUrl();

      // Get all unique weeks from placed parlays
      const allParlays = await parlayStorage.getAllParlays();
      const placedParlays = allParlays.filter(p => p.status === 'placed' || p.status === 'pending');
      const weeks = [...new Set(placedParlays.map(p => p.week))];

      if (weeks.length === 0) {
        Alert.alert('Info', 'No parlays to fetch results for. Mark parlays as "Placed" first.');
        setRefreshing(false);
        return;
      }

      // Fetch results for each week
      let totalUpdated = 0;
      for (const week of weeks) {
        const result = await parlayStorage.fetchResults(week, backendUrl);
        if (result.success) {
          totalUpdated += result.updated;
        }
      }

      if (totalUpdated > 0) {
        Alert.alert('Success', `Updated ${totalUpdated} parlay result${totalUpdated > 1 ? 's' : ''}`);
      } else {
        Alert.alert('Info', 'No new results available yet. Check back after games complete.');
      }

      await loadData();
    } catch (error) {
      console.error('Error refreshing results:', error);
      Alert.alert(
        'Error',
        'Failed to fetch results from backend. Make sure the backend is running.'
      );
    } finally {
      setRefreshing(false);
    }
  };

  const applyFilters = () => {
    let filtered = parlays.filter(p => p.status === 'won' || p.status === 'lost' || p.status === 'pending');

    // Filter by week
    if (filters.week !== undefined) {
      filtered = filtered.filter(p => p.week === filters.week);
    }

    // Filter by status
    if (filters.status && filters.status !== 'all') {
      filtered = filtered.filter(p => p.status === filters.status);
    }

    // Filter by confidence
    if (filters.minConfidence !== undefined) {
      filtered = filtered.filter(p => p.combined_confidence >= filters.minConfidence);
    }

    setFilteredParlays(filtered);
  };

  useEffect(() => {
    applyFilters();
  }, [parlays, filters]);

  useFocusEffect(
    useCallback(() => {
      loadData();
    }, [])
  );

  const handleNavigateToMyParlays = () => {
    navigation.navigate('My Parlays');
  };

  const getAvailableWeeks = () => {
    const gradedParlays = parlays.filter(p => p.status === 'won' || p.status === 'lost' || p.status === 'pending');
    const weeks = [...new Set(gradedParlays.map(p => p.week))];
    return weeks.sort((a, b) => b - a);
  };

  const gradedCount = parlays.filter(p => p.status === 'won' || p.status === 'lost').length;
  const pendingCount = parlays.filter(p => p.status === 'pending').length;

  if (loading) {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <View style={styles.headerTop}>
            <View>
              <Text style={styles.headerTitle}>Results</Text>
              <Text style={styles.headerSubtitle}>Track Your Performance</Text>
            </View>
            <InfoTooltip tooltipKey="hitRate" iconSize={20} iconColor="#9CA3AF" />
          </View>
        </View>
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Loading...</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.headerTop}>
          <View>
            <Text style={styles.headerTitle}>Results</Text>
            <Text style={styles.headerSubtitle}>Track Your Performance</Text>
          </View>
          <View style={styles.headerActions}>
            <InfoTooltip tooltipKey="hitRate" iconSize={20} iconColor="#9CA3AF" />
            <TouchableOpacity
              style={styles.refreshButton}
              onPress={handleRefresh}
              disabled={refreshing}
            >
              <Ionicons
                name="refresh"
                size={20}
                color="#9CA3AF"
                style={refreshing && styles.refreshing}
              />
            </TouchableOpacity>
          </View>
        </View>
      </View>

      {gradedCount === 0 && pendingCount === 0 ? (
        <ScrollView
          contentContainerStyle={styles.emptyContainer}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
          }
        >
          <ResultsEmptyState onNavigateToMyParlays={handleNavigateToMyParlays} />
        </ScrollView>
      ) : (
        <>
          <ResultsFilterBar
            filters={filters}
            onFilterChange={setFilters}
            availableWeeks={getAvailableWeeks()}
          />

          <ScrollView
            style={styles.scrollView}
            contentContainerStyle={styles.content}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
            }
          >
            {analytics && (
              <>
                <ResultsSummaryCard
                  totalGraded={analytics.total_graded}
                  wins={analytics.wins}
                  losses={analytics.losses}
                  winRate={analytics.win_rate}
                  avgConfidence={analytics.avg_confidence}
                  pending={pendingCount}
                />

                {analytics.total_graded > 0 && (
                  <ResultsAnalyticsCard confidenceTiers={analytics.by_confidence_tier} />
                )}
              </>
            )}

            {filteredParlays.length === 0 ? (
              <View style={styles.noResultsContainer}>
                <Text style={styles.noResultsText}>No parlays match your filters</Text>
                <TouchableOpacity
                  style={styles.clearFiltersButton}
                  onPress={() => setFilters({ status: 'all' })}
                >
                  <Text style={styles.clearFiltersText}>Clear Filters</Text>
                </TouchableOpacity>
              </View>
            ) : (
              <>
                <View style={styles.sectionHeader}>
                  <Text style={styles.sectionTitle}>Parlays</Text>
                  <Text style={styles.sectionCount}>
                    {filteredParlays.length} result{filteredParlays.length !== 1 ? 's' : ''}
                  </Text>
                </View>

                {filteredParlays.map(parlay => (
                  <ParlayResultCard key={parlay.id} parlay={parlay} />
                ))}
              </>
            )}

            <View style={styles.bottomPadding} />
          </ScrollView>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    backgroundColor: '#1F2937',
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
    color: '#FFFFFF',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#9CA3AF',
  },
  headerActions: {
    flexDirection: 'row',
    gap: 12,
    alignItems: 'center',
  },
  refreshButton: {
    padding: 4,
  },
  refreshing: {
    opacity: 0.5,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#6B7280',
  },
  emptyContainer: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  content: {
    paddingBottom: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingTop: 8,
    paddingBottom: 8,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
  },
  sectionCount: {
    fontSize: 14,
    color: '#6B7280',
  },
  noResultsContainer: {
    padding: 32,
    alignItems: 'center',
  },
  noResultsText: {
    fontSize: 16,
    color: '#6B7280',
    marginBottom: 16,
  },
  clearFiltersButton: {
    backgroundColor: '#3B82F6',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  clearFiltersText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  bottomPadding: {
    height: 20,
  },
});
