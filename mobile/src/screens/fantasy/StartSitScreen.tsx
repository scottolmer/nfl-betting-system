/**
 * StartSitScreen — Per-position start/sit rankings with agent reasoning.
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';
import { apiService } from '../../services/api';
import RosterSlot from '../../components/fantasy/RosterSlot';

const POSITIONS = ['All', 'QB', 'RB', 'WR', 'TE'];

interface RankedPlayer {
  player_id: number;
  player_name: string;
  team: string;
  position: string;
  fantasy_points: number;
  floor: number;
  ceiling: number;
  confidence: number;
  rank: number;
  verdict: 'START' | 'SIT' | 'FLEX';
  reason: string;
}

export default function StartSitScreen({ route, navigation }: any) {
  const { leagueId, sleeperUserId, week, scoring } = route.params;
  const [position, setPosition] = useState('All');
  const [rankings, setRankings] = useState<RankedPlayer[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  useEffect(() => {
    loadRankings();
  }, [position]);

  const loadRankings = async () => {
    setLoading(true);
    try {
      const params: any = { sleeper_user_id: sleeperUserId, week, scoring };
      if (position !== 'All') params.position = position;

      const resp = await apiService['client'].get(`/api/fantasy/start-sit/${leagueId}`, { params });
      setRankings(resp.data.rankings);
    } catch (err) {
      console.error('Error loading start/sit:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="chevron-back" size={24} color={theme.colors.textPrimary} />
        </TouchableOpacity>
        <View>
          <Text style={styles.headerTitle}>Start / Sit</Text>
          <Text style={styles.headerSub}>Week {week} · {scoring.toUpperCase()}</Text>
        </View>
      </View>

      {/* Position filter */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.filterBar}
        contentContainerStyle={styles.filterContent}
      >
        {POSITIONS.map((pos) => (
          <TouchableOpacity
            key={pos}
            style={[styles.filterChip, position === pos && styles.filterChipActive]}
            onPress={() => setPosition(pos)}
          >
            <Text style={[styles.filterText, position === pos && styles.filterTextActive]}>
              {pos}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {loading ? (
        <View style={styles.center}>
          <ActivityIndicator color={theme.colors.primary} size="large" />
        </View>
      ) : (
        <FlatList
          data={rankings}
          keyExtractor={(item) => `${item.player_id}`}
          contentContainerStyle={styles.listContent}
          renderItem={({ item }) => (
            <TouchableOpacity
              activeOpacity={0.8}
              onPress={() => setExpandedId(expandedId === item.player_id ? null : item.player_id)}
            >
              <RosterSlot
                slot={item.position}
                playerName={item.player_name}
                team={item.team}
                position={item.position}
                fantasyPoints={item.fantasy_points}
                floor={item.floor}
                ceiling={item.ceiling}
                verdict={item.verdict}
              />
              {expandedId === item.player_id && (
                <View style={styles.reasonCard}>
                  <Ionicons name="bulb" size={14} color={theme.colors.primary} />
                  <Text style={styles.reasonText}>{item.reason}</Text>
                </View>
              )}
            </TouchableOpacity>
          )}
          ListEmptyComponent={
            <View style={styles.emptyState}>
              <Text style={styles.emptyText}>No players to rank for this position.</Text>
            </View>
          }
        />
      )}
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
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingTop: 12,
    paddingHorizontal: 12,
    paddingBottom: 8,
    gap: 8,
  },
  backBtn: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerTitle: {
    ...theme.typography.h2,
  },
  headerSub: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
  filterBar: {
    maxHeight: 44,
    marginBottom: 8,
  },
  filterContent: {
    paddingHorizontal: 16,
    gap: 8,
  },
  filterChip: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: theme.colors.glassLow,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
  },
  filterChipActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  filterText: {
    fontSize: 13,
    fontWeight: '600',
    color: theme.colors.textSecondary,
  },
  filterTextActive: {
    color: '#fff',
  },
  listContent: {
    paddingHorizontal: 16,
    paddingBottom: 40,
  },
  reasonCard: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: theme.colors.primary + '10',
    borderRadius: theme.borderRadius.s,
    padding: 10,
    marginTop: -4,
    marginBottom: 6,
    gap: 8,
  },
  reasonText: {
    flex: 1,
    fontSize: 12,
    color: theme.colors.textSecondary,
    lineHeight: 17,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyText: {
    color: theme.colors.textTertiary,
    fontSize: 14,
  },
});
