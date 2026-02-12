/**
 * SleeperConnectScreen — Enter Sleeper username, select a league.
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  FlatList,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';
import { apiService } from '../../services/api';
import AsyncStorage from '@react-native-async-storage/async-storage';

const SLEEPER_STORAGE_KEY = 'sleeper_connection';

interface LeagueInfo {
  league_id: string;
  name: string;
  total_rosters: number;
  scoring_settings: string;
  status: string;
}

export default function SleeperConnectScreen({ navigation }: any) {
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [sleeperUser, setSleeperUser] = useState<any>(null);
  const [leagues, setLeagues] = useState<LeagueInfo[]>([]);

  const handleLookup = async () => {
    if (!username.trim()) return;
    setLoading(true);
    setSleeperUser(null);
    setLeagues([]);

    try {
      const resp = await apiService['client'].post('/api/fantasy/connect-sleeper', {
        username: username.trim(),
      });
      setSleeperUser(resp.data.user);
      setLeagues(resp.data.leagues);
      if (resp.data.leagues.length === 0) {
        Alert.alert('No Leagues', 'No NFL leagues found for this user in the current season.');
      }
    } catch (err: any) {
      if (err.response?.status === 404) {
        Alert.alert('Not Found', `Sleeper user "${username}" not found. Check the spelling.`);
      } else {
        Alert.alert('Error', 'Failed to connect. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSelectLeague = async (league: LeagueInfo) => {
    const connection = {
      userId: sleeperUser.user_id,
      username: sleeperUser.username,
      displayName: sleeperUser.display_name || sleeperUser.username,
      leagueId: league.league_id,
      leagueName: league.name,
      scoring: league.scoring_settings,
    };

    await AsyncStorage.setItem(SLEEPER_STORAGE_KEY, JSON.stringify(connection));
    navigation.goBack();
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="chevron-back" size={24} color={theme.colors.textPrimary} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Connect Sleeper</Text>
        <View style={{ width: 40 }} />
      </View>

      {/* Username input */}
      <View style={styles.inputSection}>
        <Text style={styles.inputLabel}>Sleeper Username</Text>
        <View style={styles.inputRow}>
          <TextInput
            style={styles.input}
            placeholder="Enter your Sleeper username"
            placeholderTextColor={theme.colors.textTertiary}
            value={username}
            onChangeText={setUsername}
            autoCapitalize="none"
            autoCorrect={false}
            returnKeyType="search"
            onSubmitEditing={handleLookup}
          />
          <TouchableOpacity
            style={[styles.searchBtn, !username.trim() && styles.searchBtnDisabled]}
            onPress={handleLookup}
            disabled={!username.trim() || loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" size="small" />
            ) : (
              <Ionicons name="search" size={18} color="#fff" />
            )}
          </TouchableOpacity>
        </View>
        <Text style={styles.inputHint}>
          This is your Sleeper app username, not your display name.
        </Text>
      </View>

      {/* User found */}
      {sleeperUser && (
        <View style={styles.userCard}>
          <Ionicons name="person-circle" size={36} color={theme.colors.primary} />
          <View style={styles.userInfo}>
            <Text style={styles.userName}>{sleeperUser.display_name || sleeperUser.username}</Text>
            <Text style={styles.userHandle}>@{sleeperUser.username}</Text>
          </View>
          <Ionicons name="checkmark-circle" size={20} color={theme.colors.success} />
        </View>
      )}

      {/* League list */}
      {leagues.length > 0 && (
        <>
          <Text style={styles.sectionTitle}>Select a League</Text>
          <FlatList
            data={leagues}
            keyExtractor={(item) => item.league_id}
            contentContainerStyle={styles.leagueList}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={styles.leagueCard}
                onPress={() => handleSelectLeague(item)}
                activeOpacity={0.7}
              >
                <View style={styles.leagueIcon}>
                  <Ionicons name="trophy" size={18} color={theme.colors.primary} />
                </View>
                <View style={styles.leagueInfo}>
                  <Text style={styles.leagueName}>{item.name}</Text>
                  <Text style={styles.leagueMeta}>
                    {item.total_rosters} teams · {item.scoring_settings.toUpperCase()}
                  </Text>
                </View>
                <Ionicons name="chevron-forward" size={16} color={theme.colors.textTertiary} />
              </TouchableOpacity>
            )}
          />
        </>
      )}
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
  inputSection: {
    paddingHorizontal: 16,
    paddingTop: 8,
    marginBottom: 16,
  },
  inputLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: theme.colors.textSecondary,
    marginBottom: 8,
  },
  inputRow: {
    flexDirection: 'row',
    gap: 8,
  },
  input: {
    flex: 1,
    backgroundColor: theme.colors.glassInput,
    borderRadius: theme.borderRadius.s,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    paddingHorizontal: 14,
    height: 44,
    color: theme.colors.textPrimary,
    fontSize: 15,
  },
  searchBtn: {
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.s,
    width: 44,
    height: 44,
    justifyContent: 'center',
    alignItems: 'center',
  },
  searchBtnDisabled: {
    opacity: 0.5,
  },
  inputHint: {
    fontSize: 11,
    color: theme.colors.textTertiary,
    marginTop: 6,
  },
  userCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.success + '40',
    padding: 14,
    marginHorizontal: 16,
    marginBottom: 20,
    gap: 12,
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    fontSize: 15,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
  userHandle: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
  sectionTitle: {
    ...theme.typography.h3,
    paddingHorizontal: 20,
    marginBottom: 10,
  },
  leagueList: {
    paddingHorizontal: 16,
    paddingBottom: 40,
  },
  leagueCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 14,
    marginBottom: 8,
    gap: 12,
  },
  leagueIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: theme.colors.primary + '15',
    justifyContent: 'center',
    alignItems: 'center',
  },
  leagueInfo: {
    flex: 1,
  },
  leagueName: {
    fontSize: 15,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
  leagueMeta: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    marginTop: 2,
  },
});
