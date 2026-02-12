/**
 * WaiverWireScreen — Available players ranked by projection, filtered by position.
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
import PlayerCard from '../../components/player/PlayerCard';

const POSITIONS = ['All', 'QB', 'RB', 'WR', 'TE'];

interface WaiverPlayer {
  player_id: number;
  player_name: string;
  team: string;
  position: string;
  headshot_url: string | null;
  fantasy_points: number;
  confidence: number;
  waiver_score: number;
}

export default function WaiverWireScreen({ route, navigation }: any) {
  const { leagueId, week, scoring } = route.params;
  const [position, setPosition] = useState('All');
  const [players, setPlayers] = useState<WaiverPlayer[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadWaivers();
  }, [position]);

  const loadWaivers = async () => {
    setLoading(true);
    try {
      const params: any = { week, scoring, limit: 30 };
      if (position !== 'All') params.position = position;

      const resp = await apiService['client'].get(`/api/fantasy/waiver-wire/${leagueId}`, { params });
      setPlayers(resp.data);
    } catch (err) {
      console.error('Error loading waiver wire:', err);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 15) return theme.colors.success;
    if (score >= 8) return theme.colors.primary;
    return theme.colors.textSecondary;
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="chevron-back" size={24} color={theme.colors.textPrimary} />
        </TouchableOpacity>
        <View>
          <Text style={styles.headerTitle}>Waiver Wire</Text>
          <Text style={styles.headerSub}>Week {week} · Best Available</Text>
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
          data={players}
          keyExtractor={(item) => `${item.player_id}`}
          contentContainerStyle={styles.listContent}
          renderItem={({ item, index }) => (
            <PlayerCard
              player={{
                name: item.player_name,
                team: item.team,
                position: item.position,
                headshot_url: item.headshot_url || undefined,
              }}
              subtitle={`${item.fantasy_points.toFixed(1)} proj pts · ${Math.round(item.confidence)} conf`}
              rightContent={
                <View style={styles.scoreCol}>
                  <Text style={styles.rank}>#{index + 1}</Text>
                  <Text style={[styles.waiverScore, { color: getScoreColor(item.waiver_score) }]}>
                    {item.waiver_score.toFixed(1)}
                  </Text>
                  <Text style={styles.scoreLabel}>score</Text>
                </View>
              }
            />
          )}
          ListEmptyComponent={
            <View style={styles.emptyState}>
              <Ionicons name="add-circle-outline" size={40} color={theme.colors.textTertiary} />
              <Text style={styles.emptyTitle}>No Players Available</Text>
              <Text style={styles.emptyText}>
                No projections available for unrostered players this week.
              </Text>
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
  scoreCol: {
    alignItems: 'center',
  },
  rank: {
    fontSize: 10,
    color: theme.colors.textTertiary,
    fontWeight: '600',
  },
  waiverScore: {
    fontSize: 18,
    fontWeight: '800',
  },
  scoreLabel: {
    fontSize: 9,
    color: theme.colors.textTertiary,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 60,
    paddingHorizontal: 32,
  },
  emptyTitle: {
    ...theme.typography.h3,
    marginTop: 12,
    marginBottom: 6,
  },
  emptyText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    lineHeight: 20,
  },
});
