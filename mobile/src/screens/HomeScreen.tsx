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
import QuickStartSection from '../components/home/QuickStartSection';
import CollapsiblePropCard from '../components/home/CollapsiblePropCard';
import InfoTooltip from '../components/common/InfoTooltip';

export default function HomeScreen({ navigation }: any) {
  const [props, setProps] = useState<PropAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentWeek] = useState(17); // TODO: Make this dynamic
  const [showTutorial, setShowTutorial] = useState(false);

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

  const renderPropItem = ({ item }: { item: PropAnalysis }) => (
    <CollapsiblePropCard prop={item} />
  );

  const handleViewPreBuilt = () => {
    navigation.navigate('Pre-Built');
  };

  const handleBuildCustom = () => {
    navigation.navigate('My Parlays');
  };

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
        <View style={styles.headerTop}>
          <View>
            <Text style={styles.headerTitle}>🏈 NFL Betting Analysis</Text>
            <Text style={styles.headerSubtitle}>Week {currentWeek}</Text>
          </View>
          <View style={styles.headerActions}>
            <InfoTooltip tooltipKey="preBuildParlays" iconSize={20} iconColor="#9CA3AF" />
          </View>
        </View>
      </View>

      <FlatList
        data={props}
        renderItem={renderPropItem}
        keyExtractor={(item, index) => `${item.player_name}-${item.stat_type}-${index}`}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListHeaderComponent={
          <>
            <QuickStartSection
              featuredProp={props[0]}
              onViewPreBuilt={handleViewPreBuilt}
              onBuildCustom={handleBuildCustom}
            />
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>Top 10 Props</Text>
              <InfoTooltip tooltipKey="confidence" iconSize={16} iconColor="#6B7280" />
            </View>
          </>
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No props available</Text>
          </View>
        }
        ListFooterComponent={
          <View style={styles.helpFooter}>
            <Text style={styles.helpFooterText}>💡 New to betting props?</Text>
            <TouchableOpacity onPress={() => setShowTutorial(true)}>
              <Text style={styles.helpFooterLink}>Watch Tutorial</Text>
            </TouchableOpacity>
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
    fontSize: 22,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 2,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#9CA3AF',
  },
  headerActions: {
    flexDirection: 'row',
    gap: 12,
  },
  listContainer: {
    paddingBottom: 16,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingTop: 8,
    paddingBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  helpFooter: {
    padding: 20,
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    marginTop: 8,
  },
  helpFooterText: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 8,
  },
  helpFooterLink: {
    fontSize: 15,
    fontWeight: '600',
    color: '#3B82F6',
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
