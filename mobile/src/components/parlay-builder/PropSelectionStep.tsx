/**
 * Prop Selection Step (Step 2)
 * Add props to your parlay with filters
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  TextInput,
  Modal,
  Alert,
} from 'react-native';
import { PropAnalysis, SavedParlayLeg } from '../../types';
import InfoTooltip from '../common/InfoTooltip';
import { theme } from '../../constants/theme';

interface PropSelectionStepProps {
  availableProps: PropAnalysis[];
  selectedLegs: SavedParlayLeg[];
  loading: boolean;
  minConfidence: number;
  selectedPositions: string[];
  onMinConfidenceChange: (value: number) => void;
  onPositionsChange: (positions: string[]) => void;
  onToggleProp: (prop: PropAnalysis) => void;
  onAdjustLine: (leg: SavedParlayLeg, newLine: number) => Promise<void>;
  adjusting: boolean;
}

export default function PropSelectionStep({
  availableProps,
  selectedLegs,
  loading,
  minConfidence,
  selectedPositions,
  onMinConfidenceChange,
  onPositionsChange,
  onToggleProp,
  onAdjustLine,
  adjusting,
}: PropSelectionStepProps) {
  const [showFilters, setShowFilters] = useState(false);
  const [adjustingLeg, setAdjustingLeg] = useState<SavedParlayLeg | null>(null);
  const [adjustedLine, setAdjustedLine] = useState('');

  const positions = ['QB', 'RB', 'WR', 'TE'];

  const isSelected = (prop: PropAnalysis): boolean => {
    return selectedLegs.some(
      (leg) =>
        leg.player_name === prop.player_name && leg.stat_type === prop.stat_type
    );
  };

  const handleAdjustLine = (leg: SavedParlayLeg) => {
    setAdjustingLeg(leg);
    setAdjustedLine(leg.line.toString());
  };

  const handleConfirmAdjustment = async () => {
    if (!adjustingLeg) return;

    const newLine = parseFloat(adjustedLine);
    if (isNaN(newLine)) {
      Alert.alert('Invalid Line', 'Please enter a valid number');
      return;
    }

    if (newLine === adjustingLeg.line) {
      Alert.alert('No Change', 'Line is the same as original');
      return;
    }

    await onAdjustLine(adjustingLeg, newLine);
    setAdjustingLeg(null);
    setAdjustedLine('');
  };

  const handleTogglePosition = (pos: string) => {
    if (selectedPositions.includes(pos)) {
      onPositionsChange(selectedPositions.filter((p) => p !== pos));
    } else {
      onPositionsChange([...selectedPositions, pos]);
    }
  };

  return (
    <View style={styles.container}>
      {/* Line Adjustment Modal */}
      <Modal visible={adjustingLeg !== null} transparent animationType="fade">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Adjust Line for Pick 6</Text>

            {adjustingLeg && (
              <>
                <Text style={styles.modalSubtitle}>
                  {adjustingLeg.player_name} - {adjustingLeg.stat_type}
                </Text>
                <Text style={styles.modalInfo}>
                  Original Line: {adjustingLeg.original_line || adjustingLeg.line}
                </Text>
                <Text style={styles.modalInfo}>
                  Current Confidence: {Math.round(adjustingLeg.confidence)}%
                </Text>

                <View style={styles.modalInputContainer}>
                  <Text style={styles.modalLabel}>New Line:</Text>
                  <TextInput
                    style={styles.modalInput}
                    value={adjustedLine}
                    onChangeText={setAdjustedLine}
                    keyboardType="decimal-pad"
                    placeholder="Enter new line"
                    placeholderTextColor={theme.colors.textTertiary}
                    autoFocus
                  />
                </View>

                <Text style={styles.modalHint}>
                  💡 Pick 6 lines often differ from regular props. Adjust here to get
                  accurate confidence.
                </Text>

                <View style={styles.modalButtons}>
                  <TouchableOpacity
                    style={[styles.modalButton, styles.modalButtonCancel]}
                    onPress={() => {
                      setAdjustingLeg(null);
                      setAdjustedLine('');
                    }}
                    disabled={adjusting}
                  >
                    <Text style={styles.modalButtonCancelText}>Cancel</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[styles.modalButton, styles.modalButtonConfirm]}
                    onPress={handleConfirmAdjustment}
                    disabled={adjusting}
                  >
                    {adjusting ? (
                      <ActivityIndicator color="#FFFFFF" />
                    ) : (
                      <Text style={styles.modalButtonConfirmText}>Adjust Line</Text>
                    )}
                  </TouchableOpacity>
                </View>
              </>
            )}
          </View>
        </View>
      </Modal>

      {/* Filters Bar */}
      <View style={styles.filtersBar}>
        <TouchableOpacity
          style={styles.filterToggle}
          onPress={() => setShowFilters(!showFilters)}
        >
          <Text style={styles.filterToggleText}>
            {showFilters ? '▼' : '▶'} Filters
          </Text>
        </TouchableOpacity>
        <Text style={styles.propsCount}>{availableProps.length} props</Text>
      </View>

      {showFilters && (
        <View style={styles.filtersPanel}>
          <View style={styles.filterSection}>
            <View style={styles.filterHeader}>
              <Text style={styles.filterLabel}>Min Confidence</Text>
              <InfoTooltip tooltipKey="confidence" iconSize={14} />
            </View>
            <View style={styles.confidenceButtons}>
              {[60, 65, 70, 75, 80].map((val) => (
                <TouchableOpacity
                  key={val}
                  style={[
                    styles.confButton,
                    minConfidence === val && styles.confButtonActive,
                  ]}
                  onPress={() => onMinConfidenceChange(val)}
                >
                  <Text
                    style={[
                      styles.confButtonText,
                      minConfidence === val && styles.confButtonTextActive,
                    ]}
                  >
                    {val}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          <View style={styles.filterSection}>
            <Text style={styles.filterLabel}>Positions</Text>
            <View style={styles.positionsRow}>
              {positions.map((pos) => (
                <TouchableOpacity
                  key={pos}
                  style={[
                    styles.positionChip,
                    selectedPositions.includes(pos) && styles.positionChipSelected,
                  ]}
                  onPress={() => handleTogglePosition(pos)}
                >
                  <Text
                    style={[
                      styles.positionChipText,
                      selectedPositions.includes(pos) &&
                        styles.positionChipTextSelected,
                    ]}
                  >
                    {pos}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </View>
      )}

      {/* Selected Legs */}
      {selectedLegs.length > 0 && (
        <View style={styles.selectedSection}>
          <Text style={styles.selectedTitle}>
            Selected ({selectedLegs.length}/6)
          </Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            {selectedLegs.map((leg, index) => (
              <View key={index} style={styles.selectedLegChip}>
                <Text style={styles.selectedLegNumber}>{index + 1}</Text>
                <View style={styles.selectedLegInfo}>
                  <Text style={styles.selectedLegPlayer} numberOfLines={1}>
                    {leg.player_name}
                  </Text>
                  <Text style={styles.selectedLegStat} numberOfLines={1}>
                    {leg.stat_type}
                  </Text>
                </View>
                <TouchableOpacity
                  onPress={() =>
                    onToggleProp({
                      ...leg,
                      agent_analyses: [],
                      top_reasons: [],
                    } as PropAnalysis)
                  }
                  style={styles.removeButton}
                >
                  <Text style={styles.removeButtonText}>✕</Text>
                </TouchableOpacity>
              </View>
            ))}
          </ScrollView>
        </View>
      )}

      {/* Available Props List */}
      <ScrollView style={styles.propsList}>
        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator color={theme.colors.primary} size="large" />
            <Text style={styles.loadingText}>Loading props...</Text>
          </View>
        ) : availableProps.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>
              No props found. Try adjusting your filters.
            </Text>
          </View>
        ) : (
          availableProps.map((prop, index) => {
            const selected = isSelected(prop);
            return (
              <TouchableOpacity
                key={index}
                style={[styles.propCard, selected && styles.propCardSelected]}
                onPress={() => onToggleProp(prop)}
              >
                <View style={styles.propCardContent}>
                  <View style={styles.propInfo}>
                    <Text style={styles.propPlayer}>{prop.player_name}</Text>
                    <Text style={styles.propDetails}>
                      {prop.team} {prop.position} • {prop.stat_type} {prop.bet_type}{' '}
                      {prop.line}
                    </Text>
                    {prop.projection && (
                      <Text style={styles.propProjection}>
                        Proj: {prop.projection.toFixed(1)}
                        {prop.cushion && (
                          <Text
                            style={[
                              styles.propCushion,
                              {
                                color: prop.cushion > 0 ? theme.colors.success : theme.colors.danger,
                              },
                            ]}
                          >
                            {' '}
                            ({prop.cushion > 0 ? '+' : ''}
                            {prop.cushion.toFixed(1)})
                          </Text>
                        )}
                      </Text>
                    )}
                  </View>
                  <View style={styles.propRight}>
                    <Text style={styles.propConfidence}>
                      {Math.round(prop.confidence)}
                    </Text>
                    {selected && <Text style={styles.checkmark}>✓</Text>}
                  </View>
                </View>
              </TouchableOpacity>
            );
          })
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.backgroundElevated,
  },
  filtersBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 12,
    backgroundColor: theme.colors.backgroundCard,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.glassBorder,
  },
  filterToggle: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  filterToggleText: {
    fontSize: 15,
    fontWeight: '600',
    color: theme.colors.primary,
  },
  propsCount: {
    fontSize: 13,
    color: theme.colors.textSecondary,
  },
  filtersPanel: {
    backgroundColor: theme.colors.backgroundCard,
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.glassBorder,
  },
  filterSection: {
    marginBottom: 16,
  },
  filterHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  filterLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.textSecondary,
    marginBottom: 8,
  },
  confidenceButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  confButton: {
    flex: 1,
    backgroundColor: theme.colors.backgroundElevated,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    borderRadius: 8,
    padding: 10,
    alignItems: 'center',
  },
  confButtonActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  confButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.textSecondary,
  },
  confButtonTextActive: {
    color: '#FFFFFF',
  },
  positionsRow: {
    flexDirection: 'row',
    gap: 8,
  },
  positionChip: {
    backgroundColor: theme.colors.backgroundElevated,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    borderRadius: 16,
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  positionChipSelected: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  positionChipText: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.textSecondary,
  },
  positionChipTextSelected: {
    color: '#FFFFFF',
  },
  selectedSection: {
    backgroundColor: theme.colors.backgroundCard,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.glassBorder,
  },
  selectedTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.textSecondary,
    marginBottom: 8,
  },
  selectedLegChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.primaryMuted,
    borderWidth: 1,
    borderColor: theme.colors.primary,
    borderRadius: 8,
    padding: 8,
    marginRight: 8,
    minWidth: 140,
  },
  selectedLegNumber: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: theme.colors.primary,
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: 'bold',
    textAlign: 'center',
    lineHeight: 20,
    marginRight: 8,
  },
  selectedLegInfo: {
    flex: 1,
  },
  selectedLegPlayer: {
    fontSize: 12,
    fontWeight: '600',
    color: theme.colors.textPrimary,
  },
  selectedLegStat: {
    fontSize: 11,
    color: theme.colors.textSecondary,
  },
  removeButton: {
    padding: 4,
  },
  removeButtonText: {
    fontSize: 16,
    color: theme.colors.danger,
  },
  propsList: {
    flex: 1,
  },
  loadingContainer: {
    padding: 40,
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    textAlign: 'center',
  },
  propCard: {
    backgroundColor: theme.colors.backgroundCard,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    borderRadius: 8,
    padding: 12,
    marginHorizontal: 16,
    marginVertical: 6,
  },
  propCardSelected: {
    borderColor: theme.colors.primary,
    borderWidth: 2,
    backgroundColor: theme.colors.primaryMuted,
  },
  propCardContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  propInfo: {
    flex: 1,
  },
  propPlayer: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.textPrimary,
    marginBottom: 2,
  },
  propDetails: {
    fontSize: 13,
    color: theme.colors.textSecondary,
    marginBottom: 2,
  },
  propProjection: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
  propCushion: {
    fontWeight: '600',
  },
  propRight: {
    alignItems: 'center',
    marginLeft: 12,
  },
  propConfidence: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.primary,
  },
  checkmark: {
    fontSize: 16,
    color: theme.colors.success,
    marginTop: 4,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalContent: {
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: 16,
    padding: 24,
    width: '100%',
    maxWidth: 400,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.textPrimary,
    marginBottom: 8,
    textAlign: 'center',
  },
  modalSubtitle: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.textSecondary,
    marginBottom: 16,
    textAlign: 'center',
  },
  modalInfo: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginBottom: 8,
  },
  modalInputContainer: {
    marginVertical: 16,
  },
  modalLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.textSecondary,
    marginBottom: 8,
  },
  modalInput: {
    backgroundColor: theme.colors.backgroundElevated,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    borderRadius: 8,
    padding: 12,
    fontSize: 18,
    color: theme.colors.textPrimary,
    textAlign: 'center',
    fontWeight: 'bold',
  },
  modalHint: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    backgroundColor: theme.colors.backgroundElevated,
    padding: 12,
    borderRadius: 8,
    marginBottom: 20,
    lineHeight: 18,
  },
  modalButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  modalButton: {
    flex: 1,
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  modalButtonCancel: {
    backgroundColor: theme.colors.backgroundElevated,
  },
  modalButtonConfirm: {
    backgroundColor: theme.colors.primary,
  },
  modalButtonCancelText: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.textSecondary,
  },
  modalButtonConfirmText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
});
