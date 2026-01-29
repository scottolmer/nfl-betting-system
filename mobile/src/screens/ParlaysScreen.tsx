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

export default function ParlaysScreen() {
  const [parlays, setParlays] = useState<Parlay[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedParlay, setExpandedParlay] = useState<string | null>(null);
  const [currentWeek] = useState(17); // TODO: Make this dynamic

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
    } catch (err: any) {
      setError(err.message || 'Failed to load parlays');
      console.error('Error loading parlays:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

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
        return '#22C55E';
      case 'MEDIUM':
        return '#F59E0B';
      case 'HIGH':
        return '#EF4444';
      default:
        return '#6B7280';
    }
  };

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 80) return '#22C55E';
    if (confidence >= 70) return '#F59E0B';
    return '#6B7280';
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

  const renderParlayCard = ({ item }: { item: Parlay }) => {
    const isExpanded = expandedParlay === item.id;

    return (
      <View style={styles.parlayCard}>
        <TouchableOpacity onPress={() => toggleExpand(item.id)}>
          <View style={styles.parlayHeader}>
            <View style={styles.parlayTitleContainer}>
              <Text style={styles.parlayTitle}>{item.name}</Text>
              <Text style={styles.parlaySubtitle}>
                {item.leg_count} legs • {Math.round(item.combined_confidence)} confidence
              </Text>
            </View>
            <View style={styles.parlayBadges}>
              <View style={[styles.riskBadge, { backgroundColor: getRiskColor(item.risk_level) }]}>
                <Text style={styles.riskBadgeText}>{item.risk_level}</Text>
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
        <ActivityIndicator color="#3B82F6" />
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
        <Text style={styles.headerTitle}>Pre-Built Parlays</Text>
        <Text style={styles.headerSubtitle}>
          Week {currentWeek} • {parlays.length} Parlays
        </Text>
      </View>

      <FlatList
        data={parlays}
        renderItem={renderParlayCard}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No parlays available</Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    padding: 20,
  },
  header: {
    backgroundColor: '#1F2937',
    padding: 20,
    paddingTop: 60,
    paddingBottom: 20,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#9CA3AF',
  },
  listContainer: {
    padding: 16,
  },
  parlayCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    overflow: 'hidden',
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
    color: '#1F2937',
    marginBottom: 4,
  },
  parlaySubtitle: {
    fontSize: 14,
    color: '#6B7280',
  },
  parlayBadges: {
    alignItems: 'flex-end',
  },
  riskBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  riskBadgeText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: 'bold',
  },
  parlayLegs: {
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    backgroundColor: '#F9FAFB',
  },
  legsHeader: {
    padding: 12,
    backgroundColor: '#F3F4F6',
  },
  legsHeaderText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6B7280',
    textTransform: 'uppercase',
  },
  legContainer: {
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  legHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  legNumber: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#3B82F6',
    color: '#FFFFFF',
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
    color: '#1F2937',
    marginBottom: 2,
  },
  legDetails: {
    fontSize: 14,
    color: '#6B7280',
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
    backgroundColor: '#3B82F6',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  primaryButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  secondaryButton: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#D1D5DB',
  },
  secondaryButtonText: {
    color: '#1F2937',
    fontSize: 16,
    fontWeight: '600',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#6B7280',
  },
  errorText: {
    fontSize: 16,
    color: '#EF4444',
    textAlign: 'center',
    marginBottom: 16,
  },
  retryButton: {
    backgroundColor: '#3B82F6',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: '#6B7280',
  },
});
