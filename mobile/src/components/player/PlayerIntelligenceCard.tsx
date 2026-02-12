/**
 * PlayerIntelligenceCard — Complete player view: headshot, agents,
 * projection, matchup overlay, game environment.
 */

import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';
import { apiService } from '../../services/api';
import PlayerCard from './PlayerCard';
import AgentBreakdownCard from './AgentBreakdownCard';
import GameEnvironmentCard from '../game/GameEnvironmentCard';

interface PlayerIntelligenceCardProps {
  playerId: number;
  week: number;
  onClose?: () => void;
  compact?: boolean;
}

export default function PlayerIntelligenceCard({
  playerId,
  week,
  onClose,
  compact,
}: PlayerIntelligenceCardProps) {
  const [intel, setIntel] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(!compact);

  useEffect(() => {
    loadIntel();
  }, [playerId, week]);

  const loadIntel = async () => {
    try {
      const resp = await apiService['client'].get(`/api/feed/player-intel/${playerId}`, {
        params: { week },
      });
      setIntel(resp.data);
    } catch (err) {
      console.error('Error loading player intel:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingCard}>
        <ActivityIndicator color={theme.colors.primary} />
      </View>
    );
  }

  if (!intel || intel.error) {
    return null;
  }

  const { player, stat_projections, top_drivers, game_environment } = intel;

  const confColor =
    (intel.primary_confidence || 0) >= 65
      ? theme.colors.success
      : (intel.primary_confidence || 0) >= 55
      ? theme.colors.primary
      : theme.colors.textSecondary;

  return (
    <View style={styles.card}>
      {/* Header with close button */}
      {onClose && (
        <TouchableOpacity style={styles.closeBtn} onPress={onClose}>
          <Ionicons name="close" size={18} color={theme.colors.textTertiary} />
        </TouchableOpacity>
      )}

      {/* Player card */}
      <PlayerCard
        player={{
          name: player.name,
          team: player.team,
          position: player.position,
          headshot_url: player.headshot_url,
        }}
        rightContent={
          intel.primary_confidence ? (
            <View style={styles.confCol}>
              <Text style={[styles.bigConf, { color: confColor }]}>
                {Math.round(intel.primary_confidence)}
              </Text>
              <Text style={styles.confLabel}>
                {intel.primary_direction || 'NEUTRAL'}
              </Text>
            </View>
          ) : null
        }
      />

      {/* Stat projections */}
      {stat_projections.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Projections</Text>
          {stat_projections.slice(0, expanded ? undefined : 2).map((sp: any, i: number) => (
            <View key={i} style={styles.projRow}>
              <View style={styles.projLeft}>
                <Text style={styles.projStat}>{sp.stat_label}</Text>
                <Text style={styles.projLine}>
                  Line: {sp.consensus_line ?? sp.implied_line ?? '—'}
                </Text>
              </View>
              <View style={styles.projRight}>
                <Text style={styles.projValue}>
                  {sp.engine_projection?.toFixed(1) ?? '—'}
                </Text>
                <View
                  style={[
                    styles.dirBadge,
                    {
                      backgroundColor:
                        sp.direction === 'OVER'
                          ? theme.colors.success + '20'
                          : sp.direction === 'UNDER'
                          ? theme.colors.danger + '20'
                          : theme.colors.glassHigh,
                    },
                  ]}
                >
                  <Text
                    style={[
                      styles.dirText,
                      {
                        color:
                          sp.direction === 'OVER'
                            ? theme.colors.success
                            : sp.direction === 'UNDER'
                            ? theme.colors.danger
                            : theme.colors.textTertiary,
                      },
                    ]}
                  >
                    {sp.direction || '—'}
                  </Text>
                </View>
                <Text style={styles.projConf}>
                  {sp.confidence ? `${Math.round(sp.confidence)} conf` : ''}
                </Text>
              </View>
            </View>
          ))}
        </View>
      )}

      {/* Top Drivers */}
      {top_drivers.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Key Drivers</Text>
          {top_drivers.map((d: any, i: number) => (
            <View key={i} style={styles.driverRow}>
              <View style={styles.driverRank}>
                <Text style={styles.driverRankText}>#{i + 1}</Text>
              </View>
              <View style={styles.driverInfo}>
                <Text style={styles.driverName}>{d.agent}</Text>
                <Text style={styles.driverDir}>{d.direction}</Text>
              </View>
              <View style={styles.driverScoreBar}>
                <View
                  style={[
                    styles.driverFill,
                    {
                      width: `${Math.min(d.score, 100)}%`,
                      backgroundColor:
                        d.score >= 60
                          ? theme.colors.success
                          : d.score <= 40
                          ? theme.colors.danger
                          : theme.colors.warning,
                    },
                  ]}
                />
              </View>
              <Text style={styles.driverScore}>{Math.round(d.score)}</Text>
            </View>
          ))}
        </View>
      )}

      {/* Game Environment */}
      {game_environment && game_environment.implied_total && (
        <View style={styles.section}>
          <GameEnvironmentCard
            homeTeam={game_environment.home_team}
            awayTeam={game_environment.away_team}
            impliedTotal={game_environment.implied_total}
            spread={game_environment.spread}
            spreadFavor={game_environment.spread_favor}
            dome={game_environment.dome}
          />
        </View>
      )}

      {/* Expand/collapse for compact mode */}
      {compact && stat_projections.length > 2 && (
        <TouchableOpacity style={styles.expandBtn} onPress={() => setExpanded(!expanded)}>
          <Text style={styles.expandText}>
            {expanded ? 'Show Less' : `Show ${stat_projections.length - 2} More Stats`}
          </Text>
          <Ionicons
            name={expanded ? 'chevron-up' : 'chevron-down'}
            size={14}
            color={theme.colors.primary}
          />
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 14,
    marginBottom: 12,
  },
  loadingCard: {
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 30,
    marginBottom: 12,
    alignItems: 'center',
  },
  closeBtn: {
    position: 'absolute',
    top: 8,
    right: 8,
    zIndex: 10,
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: theme.colors.glassHigh,
    justifyContent: 'center',
    alignItems: 'center',
  },
  confCol: {
    alignItems: 'center',
  },
  bigConf: {
    fontSize: 26,
    fontWeight: '800',
  },
  confLabel: {
    fontSize: 9,
    fontWeight: '700',
    color: theme.colors.textTertiary,
    letterSpacing: 0.5,
  },
  section: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: theme.colors.glassBorder,
  },
  sectionTitle: {
    fontSize: 11,
    fontWeight: '700',
    color: theme.colors.textTertiary,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 8,
  },
  // Projections
  projRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 6,
  },
  projLeft: {
    flex: 1,
  },
  projStat: {
    fontSize: 13,
    fontWeight: '600',
    color: theme.colors.textPrimary,
  },
  projLine: {
    fontSize: 11,
    color: theme.colors.textTertiary,
    marginTop: 1,
  },
  projRight: {
    alignItems: 'flex-end',
    gap: 2,
  },
  projValue: {
    fontSize: 16,
    fontWeight: '800',
    color: theme.colors.textPrimary,
  },
  dirBadge: {
    borderRadius: 4,
    paddingHorizontal: 6,
    paddingVertical: 1,
  },
  dirText: {
    fontSize: 9,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  projConf: {
    fontSize: 10,
    color: theme.colors.textTertiary,
  },
  // Drivers
  driverRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 6,
  },
  driverRank: {
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: theme.colors.glassHigh,
    justifyContent: 'center',
    alignItems: 'center',
  },
  driverRankText: {
    fontSize: 9,
    fontWeight: '800',
    color: theme.colors.primary,
  },
  driverInfo: {
    width: 70,
  },
  driverName: {
    fontSize: 11,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
  driverDir: {
    fontSize: 9,
    color: theme.colors.textTertiary,
  },
  driverScoreBar: {
    flex: 1,
    height: 6,
    backgroundColor: theme.colors.glassHigh,
    borderRadius: 3,
    overflow: 'hidden',
  },
  driverFill: {
    height: '100%',
    borderRadius: 3,
  },
  driverScore: {
    fontSize: 12,
    fontWeight: '700',
    color: theme.colors.textPrimary,
    width: 24,
    textAlign: 'right',
  },
  expandBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: 10,
    gap: 4,
  },
  expandText: {
    fontSize: 12,
    fontWeight: '600',
    color: theme.colors.primary,
  },
});
