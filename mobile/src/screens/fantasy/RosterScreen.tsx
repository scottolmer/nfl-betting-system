/**
 * RosterScreen — Full roster by position with projected fantasy points.
 * "Optimize Lineup" button triggers server-side lineup optimizer.
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';
import { apiService } from '../../services/api';
import RosterSlot from '../../components/fantasy/RosterSlot';
import ProjectionBar from '../../components/fantasy/ProjectionBar';

interface RosterPlayer {
  player_id: number;
  player_name: string;
  team: string;
  position: string;
  fantasy_points: number;
  floor: number;
  ceiling: number;
  confidence: number;
}

export default function RosterScreen({ route, navigation }: any) {
  const { leagueId, sleeperUserId, week, scoring, autoOptimize } = route.params;
  const [roster, setRoster] = useState<RosterPlayer[]>([]);
  const [optimizedLineup, setOptimizedLineup] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [optimizing, setOptimizing] = useState(false);
  const [totalProjected, setTotalProjected] = useState(0);

  useEffect(() => {
    loadRoster();
  }, []);

  const loadRoster = async () => {
    try {
      const resp = await apiService['client'].get(`/api/fantasy/roster/${leagueId}`, {
        params: { sleeper_user_id: sleeperUserId, week, scoring },
      });
      setRoster(resp.data.players);
      setTotalProjected(resp.data.total_projected);

      if (autoOptimize) {
        optimizeLineup(resp.data.players.map((p: any) => p.player_id));
      }
    } catch (err) {
      console.error('Error loading roster:', err);
    } finally {
      setLoading(false);
    }
  };

  const optimizeLineup = async (playerIds?: number[]) => {
    setOptimizing(true);
    try {
      const ids = playerIds || roster.map((p) => p.player_id);
      const resp = await apiService['client'].post('/api/fantasy/optimize-lineup', {
        player_ids: ids,
        week,
        scoring,
      });
      setOptimizedLineup(resp.data);
    } catch (err) {
      console.error('Error optimizing lineup:', err);
    } finally {
      setOptimizing(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color={theme.colors.primary} size="large" />
        <Text style={styles.loadingText}>Loading roster...</Text>
      </View>
    );
  }

  const displayPlayers = optimizedLineup
    ? [...optimizedLineup.lineup, ...optimizedLineup.bench]
    : roster;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="chevron-back" size={24} color={theme.colors.textPrimary} />
        </TouchableOpacity>
        <View style={styles.headerCenter}>
          <Text style={styles.headerTitle}>
            {optimizedLineup ? 'Optimized Lineup' : 'My Roster'}
          </Text>
          <Text style={styles.headerSub}>
            Week {week} · {scoring.toUpperCase()} · {(optimizedLineup?.projected_total || totalProjected).toFixed(1)} pts
          </Text>
        </View>
        <TouchableOpacity
          onPress={() => optimizeLineup()}
          disabled={optimizing}
          style={styles.optimizeBtn}
        >
          {optimizing ? (
            <ActivityIndicator color={theme.colors.primary} size="small" />
          ) : (
            <Ionicons name="flash" size={20} color={theme.colors.primary} />
          )}
        </TouchableOpacity>
      </View>

      {/* Total projection bar */}
      <View style={styles.totalBar}>
        <ProjectionBar
          floor={totalProjected * 0.75}
          ceiling={totalProjected * 1.25}
          projected={optimizedLineup?.projected_total || totalProjected}
          confidence={65}
          label="Team Projection"
        />
      </View>

      <FlatList
        data={displayPlayers}
        keyExtractor={(item) => `${item.player_id}`}
        contentContainerStyle={styles.listContent}
        renderItem={({ item }) => (
          <RosterSlot
            slot={item.slot || item.position}
            playerName={item.player_name}
            team={item.team}
            position={item.position}
            fantasyPoints={item.fantasy_points}
            floor={item.floor}
            ceiling={item.ceiling}
          />
        )}
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Text style={styles.emptyText}>No players found. Is your roster synced?</Text>
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
    flexDirection: 'row',
    alignItems: 'center',
    paddingTop: 12,
    paddingHorizontal: 12,
    paddingBottom: 8,
  },
  backBtn: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerCenter: {
    flex: 1,
    marginLeft: 4,
  },
  headerTitle: {
    ...theme.typography.h3,
  },
  headerSub: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
  optimizeBtn: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  totalBar: {
    paddingHorizontal: 16,
    marginBottom: 8,
  },
  listContent: {
    paddingHorizontal: 16,
    paddingBottom: 40,
  },
  loadingText: {
    marginTop: 12,
    color: theme.colors.textSecondary,
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
