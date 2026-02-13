/**
 * BetSlipScreen — Active/placed/graded bets, server-synced.
 */

import React, { useState, useEffect, useCallback } from 'react';
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
import { useAuth } from '../../contexts/AuthContext';

interface Bet {
  id: string;
  mode: string;
  platform: string | null;
  week: number;
  legs: Array<{
    player_name: string;
    team: string;
    stat_type: string;
    line: number;
    direction: string;
    confidence?: number;
  }>;
  status: string;
  confidence: number | null;
  created_at: string | null;
}

type FilterTab = 'all' | 'pending' | 'placed' | 'graded';

export default function BetSlipScreen({ navigation }: any) {
  const { isAuthenticated } = useAuth();
  const [bets, setBets] = useState<Bet[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<FilterTab>('all');


  const loadBets = useCallback(async () => {
    setLoading(true);
    try {
      // Load guest bets from storage
      const { storageService } = require('../../services/storage');
      const guestBets = await storageService.getGuestBets();

      const mappedGuestBets: Bet[] = guestBets.map((gb: any) => ({
        id: gb.id,
        mode: 'guest',
        platform: null,
        week: gb.week || 18,
        legs: gb.legs.map((l: any) => ({
          player_name: l.player_name,
          team: l.team,
          stat_type: l.stat_type,
          line: l.line,
          direction: l.bet_type || 'OVER',
          confidence: l.confidence
        })),
        status: gb.status || 'pending',
        confidence: gb.combined_confidence,
        created_at: gb.created_at
      }));

      // If authenticated, we would also fetch server bets here
      // const serverBets = isAuthenticated ? await api.getBets() : [];

      // Merge and sort
      const allBets = [...mappedGuestBets];
      allBets.sort((a, b) => {
        const dA = a.created_at ? new Date(a.created_at).getTime() : 0;
        const dB = b.created_at ? new Date(b.created_at).getTime() : 0;
        return dB - dA;
      });

      setBets(allBets);
    } catch (err) {
      console.error('Error loading bets:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    loadBets();
  }, [loadBets]);

  // Removed filteredBets logic block if it was here, but it's below.
  // We need to keep filteredBets.

  const filteredBets = bets.filter((b) => {
    if (activeTab === 'all') return true;
    if (activeTab === 'pending') return b.status === 'pending';
    if (activeTab === 'placed') return b.status === 'placed';
    if (activeTab === 'graded') return b.status === 'won' || b.status === 'lost' || b.status === 'push';
    return true;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'won': return theme.colors.success;
      case 'lost': return theme.colors.danger;
      case 'placed': return theme.colors.primary;
      case 'push': return theme.colors.gold;
      default: return theme.colors.textSecondary;
    }
  };

  const renderBet = ({ item }: { item: Bet }) => (
    <View style={styles.betCard}>
      <View style={styles.betHeader}>
        <View style={styles.betMeta}>
          <Text style={[styles.statusBadge, { color: getStatusColor(item.status) }]}>
            {item.status.toUpperCase()}
          </Text>
          <Text style={styles.weekLabel}>Week {item.week}</Text>
          {item.platform && <Text style={styles.platformLabel}>{item.platform}</Text>}
        </View>
        {item.confidence != null && (
          <Text style={styles.betConfidence}>{Math.round(item.confidence)}</Text>
        )}
      </View>
      {item.legs.map((leg, i) => (
        <View key={i} style={styles.legRow}>
          <Text style={styles.legPlayer} numberOfLines={1}>{leg.player_name}</Text>
          <Text style={styles.legDetail}>
            {leg.stat_type} {leg.direction} {leg.line}
          </Text>
        </View>
      ))}
      {item.created_at && (
        <Text style={styles.timestamp}>
          {new Date(item.created_at).toLocaleDateString()} {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </Text>
      )}
    </View>
  );

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color={theme.colors.primary} size="large" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>My Bets</Text>
      </View>

      {/* Filter tabs */}
      <View style={styles.tabs}>
        {(['all', 'pending', 'placed', 'graded'] as FilterTab[]).map((tab) => (
          <TouchableOpacity
            key={tab}
            style={[styles.tab, activeTab === tab && styles.tabActive]}
            onPress={() => setActiveTab(tab)}
          >
            <Text style={[styles.tabText, activeTab === tab && styles.tabTextActive]}>
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <FlatList
        data={filteredBets}
        renderItem={renderBet}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContent}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); loadBets(); }} tintColor={theme.colors.primary} />}
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Ionicons name="receipt-outline" size={48} color={theme.colors.textTertiary} />
            <Text style={styles.emptyTitle}>No Bets Yet</Text>
            <Text style={styles.emptyText}>
              Parlays you build from Props will appear here.
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
    paddingHorizontal: 32,
  },
  header: {
    paddingTop: 60,
    paddingHorizontal: 20,
    paddingBottom: 12,
  },
  headerTitle: {
    ...theme.typography.h1,
  },
  tabs: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    marginBottom: 12,
    gap: 6,
  },
  tab: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: theme.borderRadius.s,
    backgroundColor: theme.colors.glassLow,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    alignItems: 'center',
  },
  tabActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  tabText: {
    fontSize: 12,
    fontWeight: '600',
    color: theme.colors.textSecondary,
  },
  tabTextActive: {
    color: '#fff',
  },
  listContent: {
    paddingHorizontal: 16,
    paddingBottom: 80,
  },
  betCard: {
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 14,
    marginBottom: 10,
  },
  betHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  betMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  statusBadge: {
    fontSize: 11,
    fontWeight: '800',
  },
  weekLabel: {
    fontSize: 11,
    color: theme.colors.textTertiary,
  },
  platformLabel: {
    fontSize: 10,
    color: theme.colors.textTertiary,
    backgroundColor: theme.colors.glassHigh,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  betConfidence: {
    fontSize: 18,
    fontWeight: '800',
    color: theme.colors.primary,
  },
  legRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 3,
  },
  legPlayer: {
    fontSize: 13,
    fontWeight: '600',
    color: theme.colors.textPrimary,
    flex: 1,
  },
  legDetail: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    fontWeight: '500',
  },
  timestamp: {
    fontSize: 10,
    color: theme.colors.textTertiary,
    marginTop: 6,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 60,
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
  authTitle: {
    ...theme.typography.h3,
    marginTop: 16,
    marginBottom: 8,
  },
  authText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    textAlign: 'center',
  },
});
