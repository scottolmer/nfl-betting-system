/**
 * DFSPlayerDetailScreen — Reuses PlayerCard + shows platform line comparison.
 */

import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';
import PlayerCard from '../../components/player/PlayerCard';
import AgentBreakdownCard from '../../components/player/AgentBreakdownCard';
import PlatformLineBadge from '../../components/dfs/PlatformLineBadge';
import AgentReasoningCard from '../../components/dfs/AgentReasoningCard';
import { apiService } from '../../services/api';

export default function DFSPlayerDetailScreen({ route, navigation }: any) {
  const { player, statType, week, platform } = route.params;
  const [comparison, setComparison] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadComparison();
  }, []);

  const loadComparison = async () => {
    try {
      const resp = await apiService['client'].get(`/api/dfs/line-comparison/${player.player_id}`, {
        params: { stat_type: statType, week },
      });
      setComparison(resp.data);
    } catch (err) {
      console.error('Error loading line comparison:', err);
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
        <Text style={styles.headerTitle}>Player Detail</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={styles.scroll}>
        <PlayerCard
          player={{
            name: player.player_name,
            team: player.team,
            position: player.position,
            headshot_url: player.headshot_url,
          }}
          rightContent={
            player.confidence ? (
              <Text style={styles.bigConfidence}>{Math.round(player.confidence)}</Text>
            ) : null
          }
        />

        {loading ? (
          <ActivityIndicator color={theme.colors.primary} style={{ marginVertical: 20 }} />
        ) : (
          <>
            {/* Platform line comparison */}
            {comparison && (
              <>
                <PlatformLineBadge
                  platformLine={comparison.platform_line || 0}
                  consensusLine={comparison.sportsbook_consensus}
                  platform={platform}
                />

                {comparison.engine_projection && (
                  <View style={styles.projCard}>
                    <Text style={styles.projLabel}>Engine Projection</Text>
                    <Text style={styles.projValue}>{comparison.engine_projection}</Text>
                    {comparison.edge_note && (
                      <Text style={styles.edgeNote}>{comparison.edge_note}</Text>
                    )}
                  </View>
                )}

                {/* Book comparison */}
                {comparison.books && Object.keys(comparison.books).length > 0 && (
                  <View style={styles.booksCard}>
                    <Text style={styles.booksTitle}>Sportsbook Lines</Text>
                    {Object.entries(comparison.books).map(([book, data]: [string, any]) => (
                      <View key={book} style={styles.bookRow}>
                        <Text style={styles.bookName}>{book}</Text>
                        <Text style={styles.bookLine}>{data.line}</Text>
                      </View>
                    ))}
                  </View>
                )}
              </>
            )}

            {/* Agent breakdown */}
            {player.agent_breakdown && (
              <AgentBreakdownCard breakdown={player.agent_breakdown} />
            )}

            {/* Agent reasoning */}
            {player.agent_breakdown && (
              <AgentReasoningCard
                playerName={player.player_name}
                drivers={Object.entries(player.agent_breakdown).map(([name, data]: [string, any]) => ({
                  name,
                  score: data.score || 50,
                  weight: data.weight || 1,
                  direction: data.direction || 'OVER',
                }))}
              />
            )}
          </>
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
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
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
  headerTitle: {
    ...theme.typography.h3,
  },
  scroll: {
    paddingHorizontal: 16,
    paddingBottom: 40,
  },
  bigConfidence: {
    fontSize: 28,
    fontWeight: '800',
    color: theme.colors.success,
  },
  projCard: {
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 14,
    marginBottom: 12,
    alignItems: 'center',
  },
  projLabel: {
    ...theme.typography.caption,
    marginBottom: 4,
  },
  projValue: {
    fontSize: 28,
    fontWeight: '800',
    color: theme.colors.textPrimary,
  },
  edgeNote: {
    fontSize: 11,
    color: theme.colors.textSecondary,
    fontStyle: 'italic',
    marginTop: 4,
    textAlign: 'center',
  },
  booksCard: {
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 14,
    marginBottom: 12,
  },
  booksTitle: {
    ...theme.typography.caption,
    marginBottom: 8,
  },
  bookRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 4,
  },
  bookName: {
    fontSize: 13,
    color: theme.colors.textSecondary,
    fontWeight: '500',
  },
  bookLine: {
    fontSize: 13,
    color: theme.colors.textPrimary,
    fontWeight: '700',
  },
});
