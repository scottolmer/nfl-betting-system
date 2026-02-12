/**
 * FantasyHomeScreen V2 — Cyan accent migration, GlassCard usage, gradient CTA.
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
import MatchupCard from '../../components/fantasy/MatchupCard';
import GlassCard from '../../components/common/GlassCard';
import AnimatedCard from '../../components/animated/AnimatedCard';
import AsyncStorage from '@react-native-async-storage/async-storage';

const SLEEPER_STORAGE_KEY = 'sleeper_connection';

interface SleeperConnection {
  userId: string;
  username: string;
  displayName: string;
  leagueId: string;
  leagueName: string;
  scoring: string;
}

export default function FantasyHomeScreen({ navigation }: any) {
  const [connection, setConnection] = useState<SleeperConnection | null>(null);
  const [matchup, setMatchup] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [currentWeek] = useState(17);

  useEffect(() => {
    loadConnection();
  }, []);

  const loadConnection = async () => {
    try {
      const stored = await AsyncStorage.getItem(SLEEPER_STORAGE_KEY);
      if (stored) {
        const conn = JSON.parse(stored) as SleeperConnection;
        setConnection(conn);
        await loadMatchup(conn);
      }
    } catch (err) {
      console.error('Error loading Sleeper connection:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadMatchup = async (conn: SleeperConnection) => {
    try {
      const resp = await apiService['client'].get(`/api/fantasy/matchup/${conn.leagueId}`, {
        params: { sleeper_user_id: conn.userId, week: currentWeek, scoring: conn.scoring },
      });
      setMatchup(resp.data);
    } catch (err) {
      console.error('Error loading matchup:', err);
    }
  };

  const handleDisconnect = async () => {
    await AsyncStorage.removeItem(SLEEPER_STORAGE_KEY);
    setConnection(null);
    setMatchup(null);
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color={theme.colors.primary} size="large" />
      </View>
    );
  }

  // Not connected
  if (!connection) {
    return (
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Fantasy</Text>
          <Text style={styles.headerSubtitle}>Week {currentWeek}</Text>
        </View>

        <AnimatedCard index={0}>
          <GlassCard style={styles.onboardCard}>
            <View style={styles.onboardIconCircle}>
              <Ionicons name="trophy" size={28} color={theme.colors.primary} />
            </View>
            <Text style={styles.onboardTitle}>Connect Your League</Text>
            <Text style={styles.onboardDesc}>
              Import your Sleeper roster to get start/sit advice, waiver wire rankings,
              matchup heatmaps, and trade analysis — all powered by our 6-agent engine.
            </Text>
            <TouchableOpacity
              style={styles.connectBtn}
              onPress={() => navigation.navigate('SleeperConnect')}
              activeOpacity={0.8}
            >
              <Ionicons name="link" size={18} color="#000" />
              <Text style={styles.connectBtnText}>Connect Sleeper</Text>
            </TouchableOpacity>
          </GlassCard>
        </AnimatedCard>

        <View style={styles.featureList}>
          {[
            { icon: 'swap-vertical', title: 'Start/Sit', desc: 'Agent-powered lineup decisions' },
            { icon: 'add-circle', title: 'Waiver Wire', desc: 'Best available pickups ranked' },
            { icon: 'grid', title: 'Matchup Heatmap', desc: 'DVOA-colored matchup grid' },
            { icon: 'git-compare', title: 'Trade Analyzer', desc: 'ROS projection comparison' },
          ].map((f, i) => (
            <AnimatedCard key={i} index={i + 1}>
              <View style={styles.featureRow}>
                <View style={styles.featureIcon}>
                  <Ionicons name={f.icon as any} size={18} color={theme.colors.primary} />
                </View>
                <View style={styles.featureInfo}>
                  <Text style={styles.featureTitle}>{f.title}</Text>
                  <Text style={styles.featureDesc}>{f.desc}</Text>
                </View>
              </View>
            </AnimatedCard>
          ))}
        </View>
      </ScrollView>
    );
  }

  // Connected — dashboard
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.headerConnected}>
        <View>
          <Text style={styles.headerTitle}>Fantasy</Text>
          <Text style={styles.headerSubtitle}>{connection.leagueName} {'\u00B7'} Week {currentWeek}</Text>
        </View>
        <TouchableOpacity onPress={handleDisconnect} style={styles.disconnectBtn}>
          <Ionicons name="log-out-outline" size={18} color={theme.colors.textTertiary} />
        </TouchableOpacity>
      </View>

      {/* Matchup card */}
      {matchup && (
        <AnimatedCard index={0}>
          <View style={styles.section}>
            <MatchupCard
              userTotal={matchup.user.projected_total}
              opponentTotal={matchup.opponent.projected_total}
              winProbability={matchup.win_probability}
              week={currentWeek}
            />
          </View>
        </AnimatedCard>
      )}

      {/* Quick actions grid */}
      <View style={styles.actionGrid}>
        {[
          {
            icon: 'people',
            title: 'My Roster',
            screen: 'Roster',
            params: { leagueId: connection.leagueId, sleeperUserId: connection.userId, week: currentWeek, scoring: connection.scoring },
          },
          {
            icon: 'swap-vertical',
            title: 'Start/Sit',
            screen: 'StartSit',
            params: { leagueId: connection.leagueId, sleeperUserId: connection.userId, week: currentWeek, scoring: connection.scoring },
          },
          {
            icon: 'add-circle',
            title: 'Waivers',
            screen: 'WaiverWire',
            params: { leagueId: connection.leagueId, week: currentWeek, scoring: connection.scoring },
          },
          {
            icon: 'grid',
            title: 'Heatmap',
            screen: 'MatchupHeatmap',
            params: { leagueId: connection.leagueId, sleeperUserId: connection.userId, week: currentWeek },
          },
          {
            icon: 'git-compare',
            title: 'Trade',
            screen: 'TradeAnalyzer',
            params: { week: currentWeek, scoring: connection.scoring },
          },
          {
            icon: 'flash',
            title: 'Optimize',
            screen: 'Roster',
            params: { leagueId: connection.leagueId, sleeperUserId: connection.userId, week: currentWeek, scoring: connection.scoring, autoOptimize: true },
          },
        ].map((action, i) => (
          <AnimatedCard key={i} index={i}>
            <TouchableOpacity
              style={styles.actionCard}
              onPress={() => navigation.navigate(action.screen, action.params)}
              activeOpacity={0.7}
            >
              <View style={styles.actionIconCircle}>
                <Ionicons name={action.icon as any} size={20} color={theme.colors.primary} />
              </View>
              <Text style={styles.actionTitle}>{action.title}</Text>
            </TouchableOpacity>
          </AnimatedCard>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  content: {
    paddingBottom: 40,
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
  },
  header: {
    paddingTop: 16,
    paddingHorizontal: 20,
    paddingBottom: 12,
  },
  headerConnected: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 16,
    paddingHorizontal: 20,
    paddingBottom: 12,
  },
  headerTitle: {
    ...theme.typography.h1,
    color: theme.colors.primary,
  },
  headerSubtitle: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginTop: 2,
  },
  disconnectBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: theme.colors.backgroundCard,
    justifyContent: 'center',
    alignItems: 'center',
  },
  section: {
    paddingHorizontal: 16,
  },
  // Onboarding
  onboardCard: {
    marginHorizontal: 16,
    alignItems: 'center',
    padding: 28,
  },
  onboardIconCircle: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: theme.colors.primaryMuted,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  onboardTitle: {
    ...theme.typography.h2,
    marginBottom: 8,
  },
  onboardDesc: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    lineHeight: 20,
    marginBottom: 20,
  },
  connectBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.m,
    paddingVertical: 14,
    paddingHorizontal: 28,
    gap: 8,
    ...theme.shadows.glow,
  },
  connectBtnText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#000',
  },
  featureList: {
    paddingHorizontal: 16,
    gap: 2,
  },
  featureRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: theme.borderRadius.s,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 14,
    gap: 12,
  },
  featureIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: theme.colors.primaryMuted,
    justifyContent: 'center',
    alignItems: 'center',
  },
  featureInfo: {
    flex: 1,
  },
  featureTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
  featureDesc: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    marginTop: 1,
  },
  // Dashboard
  actionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 16,
    gap: 10,
  },
  actionCard: {
    width: '100%',
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 16,
    alignItems: 'center',
    gap: 8,
  },
  actionIconCircle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: theme.colors.primaryMuted,
    justifyContent: 'center',
    alignItems: 'center',
  },
  actionTitle: {
    fontSize: 12,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
});
