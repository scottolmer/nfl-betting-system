import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Modal,
} from 'react-native';
import { parlayStorage, FREE_TIER_PARLAY_LIMIT } from '../services/parlayStorage';
import { SavedParlay } from '../types';
import CreateParlayScreen from './CreateParlayScreen';

export default function BuildScreen() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [parlays, setParlays] = useState<SavedParlay[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [remainingSlots, setRemainingSlots] = useState(FREE_TIER_PARLAY_LIMIT);
  const [expandedParlay, setExpandedParlay] = useState<string | null>(null);

  useEffect(() => {
    loadParlays();
  }, []);

  const loadParlays = async () => {
    try {
      const data = await parlayStorage.getAllParlays();
      const slots = await parlayStorage.getRemainingSlots();
      setParlays(data);
      setRemainingSlots(slots);
    } catch (error) {
      console.error('Error loading parlays:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    loadParlays();
  }, []);

  const handleCreateParlay = () => {
    if (remainingSlots <= 0) {
      Alert.alert(
        'Free Tier Limit Reached',
        `You've reached the maximum of ${FREE_TIER_PARLAY_LIMIT} saved parlays.\n\nDelete old parlays or upgrade to Premium for unlimited parlays.`,
        [{ text: 'OK' }]
      );
      return;
    }

    setShowCreateModal(true);
  };

  const handleDeleteParlay = (id: string, name: string) => {
    Alert.alert(
      'Delete Parlay',
      `Are you sure you want to delete "${name}"?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            const success = await parlayStorage.deleteParlay(id);
            if (success) {
              loadParlays();
            } else {
              Alert.alert('Error', 'Failed to delete parlay');
            }
          },
        },
      ]
    );
  };

  const handleMarkAsPlaced = (id: string, name: string) => {
    Alert.prompt(
      'Mark as Placed',
      `Enter bet amount for "${name}" (optional)`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Mark Placed',
          onPress: async (betAmount) => {
            const amount = betAmount ? parseFloat(betAmount) : undefined;
            const success = await parlayStorage.markAsPlaced(id, amount);
            if (success) {
              loadParlays();
              Alert.alert('Success', 'Parlay marked as placed!');
            } else {
              Alert.alert('Error', 'Failed to update parlay');
            }
          },
        },
      ],
      'plain-text',
      '',
      'numeric'
    );
  };

  const handleCopyParlay = (parlay: SavedParlay) => {
    // TODO: Implement clipboard copy
    Alert.alert(
      'Copy Parlay',
      'Parlay details will be copied to clipboard',
      [{ text: 'OK' }]
    );
  };

  const toggleExpand = (id: string) => {
    setExpandedParlay(expandedParlay === id ? null : id);
  };

  const getStatusColor = (status: SavedParlay['status']): string => {
    switch (status) {
      case 'draft': return '#6B7280';
      case 'placed': return '#3B82F6';
      case 'won': return '#22C55E';
      case 'lost': return '#EF4444';
      case 'pending': return '#F59E0B';
      default: return '#6B7280';
    }
  };

  const getStatusLabel = (status: SavedParlay['status']): string => {
    switch (status) {
      case 'draft': return 'Draft';
      case 'placed': return 'Placed';
      case 'won': return 'Won';
      case 'lost': return 'Lost';
      case 'pending': return 'Pending';
      default: return 'Unknown';
    }
  };

  const getRiskColor = (risk: string): string => {
    switch (risk) {
      case 'LOW': return '#22C55E';
      case 'MEDIUM': return '#F59E0B';
      case 'HIGH': return '#EF4444';
      default: return '#6B7280';
    }
  };

  const renderParlayCard = (parlay: SavedParlay) => {
    const isExpanded = expandedParlay === parlay.id;

    return (
      <View key={parlay.id} style={styles.parlayCard}>
        <TouchableOpacity onPress={() => toggleExpand(parlay.id)}>
          <View style={styles.parlayHeader}>
            <View style={styles.parlayTitleContainer}>
              <Text style={styles.parlayTitle}>{parlay.name}</Text>
              <Text style={styles.parlaySubtitle}>
                {parlay.legs.length} legs • {Math.round(parlay.combined_confidence)} confidence
                {parlay.sportsbook && ` • ${parlay.sportsbook}`}
              </Text>
            </View>
            <View style={styles.parlayBadges}>
              <View style={[styles.statusBadge, { backgroundColor: getStatusColor(parlay.status) }]}>
                <Text style={styles.badgeText}>{getStatusLabel(parlay.status)}</Text>
              </View>
              <View style={[styles.riskBadge, { backgroundColor: getRiskColor(parlay.risk_level) }]}>
                <Text style={styles.badgeText}>{parlay.risk_level}</Text>
              </View>
            </View>
          </View>
        </TouchableOpacity>

        {isExpanded && (
          <View style={styles.parlayDetails}>
            <View style={styles.legsHeader}>
              <Text style={styles.legsHeaderText}>Parlay Legs</Text>
            </View>

            {parlay.legs.map((leg, index) => (
              <View key={index} style={styles.legContainer}>
                <View style={styles.legHeader}>
                  <Text style={styles.legNumber}>{index + 1}</Text>
                  <View style={styles.legInfo}>
                    <Text style={styles.legPlayer}>
                      {leg.player_name} ({leg.team} {leg.position})
                    </Text>
                    <Text style={styles.legDetails}>
                      {leg.stat_type} {leg.bet_type} {leg.line}
                      {leg.adjusted_line && ` (adj: ${leg.adjusted_line})`}
                      {' vs '}{leg.opponent}
                    </Text>
                    <Text style={styles.legConfidence}>
                      {Math.round(leg.confidence)} confidence
                      {leg.projection && ` • Proj: ${leg.projection.toFixed(1)}`}
                    </Text>
                  </View>
                </View>
              </View>
            ))}

            <View style={styles.actionsContainer}>
              <TouchableOpacity
                style={styles.actionButton}
                onPress={() => handleCopyParlay(parlay)}
              >
                <Text style={styles.actionButtonText}>📋 Copy</Text>
              </TouchableOpacity>

              {parlay.status === 'draft' && (
                <TouchableOpacity
                  style={[styles.actionButton, styles.primaryButton]}
                  onPress={() => handleMarkAsPlaced(parlay.id, parlay.name)}
                >
                  <Text style={styles.primaryButtonText}>✅ Mark Placed</Text>
                </TouchableOpacity>
              )}

              <TouchableOpacity
                style={[styles.actionButton, styles.dangerButton]}
                onPress={() => handleDeleteParlay(parlay.id, parlay.name)}
              >
                <Text style={styles.dangerButtonText}>🗑️ Delete</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {/* Create Parlay Modal */}
      <Modal
        visible={showCreateModal}
        animationType="slide"
        presentationStyle="fullScreen"
      >
        <CreateParlayScreen
          onClose={() => setShowCreateModal(false)}
          onSaved={() => {
            loadParlays();
          }}
        />
      </Modal>

      <View style={styles.header}>
        <Text style={styles.headerTitle}>My Parlays</Text>
        <Text style={styles.headerSubtitle}>
          {parlays.length} of {FREE_TIER_PARLAY_LIMIT} parlays
          {remainingSlots > 0 && ` • ${remainingSlots} slots remaining`}
        </Text>
      </View>

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        <TouchableOpacity
          style={[
            styles.createButton,
            remainingSlots <= 0 && styles.createButtonDisabled
          ]}
          onPress={handleCreateParlay}
        >
          <Text style={styles.createButtonText}>
            ⚡ Create New Parlay
          </Text>
          {remainingSlots <= 0 && (
            <Text style={styles.createButtonSubtext}>
              Free tier limit reached
            </Text>
          )}
        </TouchableOpacity>

        {parlays.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyEmoji}>⚡</Text>
            <Text style={styles.emptyTitle}>No Parlays Yet</Text>
            <Text style={styles.emptyDescription}>
              Create your first parlay to get started!
            </Text>
          </View>
        ) : (
          <View style={styles.parlaysContainer}>
            {parlays.map(renderParlayCard)}
          </View>
        )}

        <View style={styles.infoBox}>
          <Text style={styles.infoTitle}>💡 How It Works</Text>
          <Text style={styles.infoText}>
            1. Create a parlay with custom filters{'\n'}
            2. Save it to your library{'\n'}
            3. Place bet in your sportsbook{'\n'}
            4. Mark as "Placed" to track{'\n'}
            5. Get auto-graded results (Premium)
          </Text>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    backgroundColor: '#1F2937',
    padding: 20,
    paddingTop: 60,
    paddingBottom: 20,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#9CA3AF',
  },
  scrollContent: {
    padding: 16,
  },
  createButton: {
    backgroundColor: '#3B82F6',
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  createButtonDisabled: {
    backgroundColor: '#9CA3AF',
  },
  createButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  createButtonSubtext: {
    color: '#FFFFFF',
    fontSize: 12,
    marginTop: 4,
    opacity: 0.8,
  },
  parlaysContainer: {
    marginBottom: 20,
  },
  parlayCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    overflow: 'hidden',
  },
  parlayHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    padding: 16,
  },
  parlayTitleContainer: {
    flex: 1,
    marginRight: 12,
  },
  parlayTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 4,
  },
  parlaySubtitle: {
    fontSize: 13,
    color: '#6B7280',
  },
  parlayBadges: {
    gap: 6,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  riskBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  badgeText: {
    color: '#FFFFFF',
    fontSize: 11,
    fontWeight: 'bold',
  },
  parlayDetails: {
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    backgroundColor: '#F9FAFB',
  },
  legsHeader: {
    padding: 12,
    backgroundColor: '#F3F4F6',
  },
  legsHeaderText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6B7280',
    textTransform: 'uppercase',
  },
  legContainer: {
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  legHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  legNumber: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#3B82F6',
    color: '#FFFFFF',
    textAlign: 'center',
    lineHeight: 24,
    fontSize: 14,
    fontWeight: 'bold',
    marginRight: 12,
  },
  legInfo: {
    flex: 1,
  },
  legPlayer: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 2,
  },
  legDetails: {
    fontSize: 13,
    color: '#6B7280',
    marginBottom: 4,
  },
  legConfidence: {
    fontSize: 12,
    color: '#3B82F6',
    fontWeight: '600',
  },
  actionsContainer: {
    flexDirection: 'row',
    padding: 12,
    gap: 8,
  },
  actionButton: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    padding: 10,
    borderRadius: 8,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#D1D5DB',
  },
  primaryButton: {
    backgroundColor: '#3B82F6',
    borderColor: '#3B82F6',
  },
  dangerButton: {
    backgroundColor: '#FFFFFF',
    borderColor: '#EF4444',
  },
  actionButtonText: {
    color: '#1F2937',
    fontSize: 13,
    fontWeight: '600',
  },
  primaryButtonText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '600',
  },
  dangerButtonText: {
    color: '#EF4444',
    fontSize: 13,
    fontWeight: '600',
  },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    marginBottom: 20,
  },
  emptyEmoji: {
    fontSize: 64,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8,
  },
  emptyDescription: {
    fontSize: 15,
    color: '#6B7280',
    textAlign: 'center',
  },
  infoBox: {
    backgroundColor: '#EFF6FF',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#BFDBFE',
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#4B5563',
    lineHeight: 22,
  },
});
