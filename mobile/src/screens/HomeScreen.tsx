import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
  TouchableOpacity,
} from 'react-native';
import { apiService } from '../services/api';
import { PropAnalysis } from '../types';

export default function HomeScreen() {
  const [props, setProps] = useState<PropAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentWeek] = useState(17); // TODO: Make this dynamic

  useEffect(() => {
    loadTopProps();
  }, []);

  const loadTopProps = async () => {
    try {
      setError(null);
      const data = await apiService.getTopProps({
        week: currentWeek,
        limit: 10,
      });
      setProps(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load props');
      console.error('Error loading props:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadTopProps();
  };

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 80) return '#22C55E'; // Green (🔥)
    if (confidence >= 75) return '#F59E0B'; // Orange (⭐)
    if (confidence >= 70) return '#3B82F6'; // Blue (✅)
    return '#6B7280'; // Gray
  };

  const getConfidenceEmoji = (confidence: number): string => {
    if (confidence >= 80) return '🔥';
    if (confidence >= 75) return '⭐';
    if (confidence >= 70) return '✅';
    return '📊';
  };

  const renderPropItem = ({ item }: { item: PropAnalysis }) => (
    <TouchableOpacity style={styles.propCard}>
      <View style={styles.propHeader}>
        <View style={styles.confidenceContainer}>
          <Text style={styles.confidenceEmoji}>
            {getConfidenceEmoji(item.confidence)}
          </Text>
          <Text
            style={[
              styles.confidenceScore,
              { color: getConfidenceColor(item.confidence) },
            ]}
          >
            {Math.round(item.confidence)}
          </Text>
        </View>
        <View style={styles.playerInfo}>
          <Text style={styles.playerName}>{item.player_name}</Text>
          <Text style={styles.teamPosition}>
            {item.team} {item.position} vs {item.opponent}
          </Text>
        </View>
      </View>

      <View style={styles.propDetails}>
        <View style={styles.statRow}>
          <Text style={styles.statType}>{item.stat_type}</Text>
          <Text style={styles.betType}>{item.bet_type}</Text>
          <Text style={styles.line}>{item.line}</Text>
        </View>
        {item.projection && (
          <Text style={styles.projection}>
            Proj: {item.projection.toFixed(1)}
            {item.cushion && ` (${item.cushion > 0 ? '+' : ''}${item.cushion.toFixed(1)})`}
          </Text>
        )}
      </View>

      <View style={styles.reasonsContainer}>
        {(item.top_reasons || []).slice(0, 2).map((reason, index) => (
          <Text key={index} style={styles.reason}>
            • {reason}
          </Text>
        ))}
      </View>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator color="#3B82F6" />
        <Text style={styles.loadingText}>Loading top props...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>⚠️ {error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={loadTopProps}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Top Props</Text>
        <Text style={styles.headerSubtitle}>Week {currentWeek} • Top 10 by Confidence</Text>
      </View>

      <FlatList
        data={props}
        renderItem={renderPropItem}
        keyExtractor={(item, index) => `${item.player_name}-${item.stat_type}-${index}`}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No props available</Text>
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
  propCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  propHeader: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  confidenceContainer: {
    alignItems: 'center',
    marginRight: 12,
    minWidth: 60,
  },
  confidenceEmoji: {
    fontSize: 24,
    marginBottom: 4,
  },
  confidenceScore: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  playerInfo: {
    flex: 1,
  },
  playerName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 2,
  },
  teamPosition: {
    fontSize: 14,
    color: '#6B7280',
  },
  propDetails: {
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    paddingTop: 12,
    marginBottom: 8,
  },
  statRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  statType: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginRight: 8,
  },
  betType: {
    fontSize: 14,
    fontWeight: '600',
    color: '#3B82F6',
    marginRight: 8,
  },
  line: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  projection: {
    fontSize: 13,
    color: '#6B7280',
    marginTop: 2,
  },
  reasonsContainer: {
    marginTop: 8,
  },
  reason: {
    fontSize: 13,
    color: '#4B5563',
    marginBottom: 2,
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
