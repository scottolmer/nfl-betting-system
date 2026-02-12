/**
 * MatchupHeatmapScreen — Your players vs opponent defense, color-coded grid.
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';
import { apiService } from '../../services/api';
import HeatmapCell from '../../components/fantasy/HeatmapCell';

interface HeatmapPlayer {
  player_id: number;
  player_name: string;
  team: string;
  position: string;
  opponent: string;
  overall_grade: 'favorable' | 'neutral' | 'unfavorable';
  overall_color_value: number;
  stat_matchups: Array<{
    stat_type: string;
    projection: number | null;
    confidence: number | null;
    matchup_grade: 'favorable' | 'neutral' | 'unfavorable';
    color_value: number;
  }>;
}

function getGradeColor(grade: string): string {
  if (grade === 'favorable') return theme.colors.success;
  if (grade === 'unfavorable') return theme.colors.danger;
  return theme.colors.warning;
}

export default function MatchupHeatmapScreen({ route, navigation }: any) {
  const { leagueId, sleeperUserId, week } = route.params;
  const [heatmap, setHeatmap] = useState<HeatmapPlayer[]>([]);
  const [loading, setLoading] = useState(true);
  const [opponentTeam, setOpponentTeam] = useState('');

  useEffect(() => {
    loadMatchupData();
  }, []);

  const loadMatchupData = async () => {
    try {
      // First get matchup to find opponent team
      const matchupResp = await apiService['client'].get(`/api/fantasy/matchup/${leagueId}`, {
        params: { sleeper_user_id: sleeperUserId, week },
      });

      // Get opponent team from their top player
      const oppPlayers = matchupResp.data.opponent?.players || [];
      const oppTeam = oppPlayers.length > 0 ? oppPlayers[0].team : 'UNK';
      setOpponentTeam(oppTeam);

      // Get heatmap
      const resp = await apiService['client'].get(`/api/fantasy/matchup-heatmap/${leagueId}`, {
        params: { sleeper_user_id: sleeperUserId, week, opponent_team: oppTeam },
      });
      setHeatmap(resp.data);
    } catch (err) {
      console.error('Error loading heatmap:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color={theme.colors.primary} size="large" />
        <Text style={styles.loadingText}>Building matchup heatmap...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="chevron-back" size={24} color={theme.colors.textPrimary} />
        </TouchableOpacity>
        <View>
          <Text style={styles.headerTitle}>Matchup Heatmap</Text>
          <Text style={styles.headerSub}>Week {week} vs {opponentTeam}</Text>
        </View>
      </View>

      {/* Legend */}
      <View style={styles.legend}>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: theme.colors.success }]} />
          <Text style={styles.legendLabel}>Favorable</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: theme.colors.warning }]} />
          <Text style={styles.legendLabel}>Neutral</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: theme.colors.danger }]} />
          <Text style={styles.legendLabel}>Unfavorable</Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        {heatmap.map((player) => (
          <View key={player.player_id} style={styles.playerRow}>
            {/* Player info */}
            <View style={styles.playerInfo}>
              <View style={styles.positionBadge}>
                <Text style={styles.positionText}>{player.position}</Text>
              </View>
              <View>
                <Text style={styles.playerName} numberOfLines={1}>{player.player_name}</Text>
                <Text style={styles.playerTeam}>{player.team}</Text>
              </View>
              <View
                style={[
                  styles.overallBadge,
                  { backgroundColor: getGradeColor(player.overall_grade) + '20' },
                ]}
              >
                <Text style={[styles.overallText, { color: getGradeColor(player.overall_grade) }]}>
                  {player.overall_grade === 'favorable' ? 'Good' : player.overall_grade === 'unfavorable' ? 'Bad' : 'Avg'}
                </Text>
              </View>
            </View>

            {/* Stat cells */}
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.cellRow}
            >
              {player.stat_matchups.map((sm, i) => (
                <HeatmapCell
                  key={i}
                  statType={sm.stat_type}
                  projection={sm.projection}
                  confidence={sm.confidence}
                  matchupGrade={sm.matchup_grade}
                  colorValue={sm.color_value}
                />
              ))}
            </ScrollView>
          </View>
        ))}

        {heatmap.length === 0 && (
          <View style={styles.emptyState}>
            <Ionicons name="grid-outline" size={40} color={theme.colors.textTertiary} />
            <Text style={styles.emptyText}>No matchup data available for this week.</Text>
          </View>
        )}
      </ScrollView>
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
  legend: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 16,
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.glassBorder,
    marginBottom: 8,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
  },
  legendDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  legendLabel: {
    fontSize: 11,
    color: theme.colors.textSecondary,
  },
  scrollContent: {
    paddingHorizontal: 16,
    paddingBottom: 40,
  },
  playerRow: {
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 12,
    marginBottom: 10,
  },
  playerInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 10,
  },
  positionBadge: {
    backgroundColor: theme.colors.glassHigh,
    borderRadius: 4,
    paddingHorizontal: 6,
    paddingVertical: 2,
  },
  positionText: {
    fontSize: 10,
    fontWeight: '800',
    color: theme.colors.primary,
  },
  playerName: {
    fontSize: 14,
    fontWeight: '700',
    color: theme.colors.textPrimary,
    maxWidth: 160,
  },
  playerTeam: {
    fontSize: 11,
    color: theme.colors.textTertiary,
  },
  overallBadge: {
    marginLeft: 'auto',
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 3,
  },
  overallText: {
    fontSize: 11,
    fontWeight: '700',
  },
  cellRow: {
    gap: 8,
  },
  loadingText: {
    marginTop: 12,
    color: theme.colors.textSecondary,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyText: {
    color: theme.colors.textTertiary,
    fontSize: 14,
    marginTop: 12,
  },
});
