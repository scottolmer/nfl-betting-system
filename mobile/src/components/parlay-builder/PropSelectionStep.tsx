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
                    placeholderTextColor="#9CA3AF"
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
            <ActivityIndicator color="#3B82F6" size="large" />
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
                                color: prop.cushion > 0 ? '#22C55E' : '#EF4444',
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
    backgroundColor: '#F9FAFB',
  },
  filtersBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  filterToggle: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  filterToggleText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#3B82F6',
  },
  propsCount: {
    fontSize: 13,
    color: '#6B7280',
  },
  filtersPanel: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
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
    color: '#4B5563',
    marginBottom: 8,
  },
  confidenceButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  confButton: {
    flex: 1,
    backgroundColor: '#F3F4F6',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    padding: 10,
    alignItems: 'center',
  },
  confButtonActive: {
    backgroundColor: '#3B82F6',
    borderColor: '#3B82F6',
  },
  confButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#4B5563',
  },
  confButtonTextActive: {
    color: '#FFFFFF',
  },
  positionsRow: {
    flexDirection: 'row',
    gap: 8,
  },
  positionChip: {
    backgroundColor: '#F3F4F6',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 16,
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  positionChipSelected: {
    backgroundColor: '#3B82F6',
    borderColor: '#3B82F6',
  },
  positionChipText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#4B5563',
  },
  positionChipTextSelected: {
    color: '#FFFFFF',
  },
  selectedSection: {
    backgroundColor: '#FFFFFF',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  selectedTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#4B5563',
    marginBottom: 8,
  },
  selectedLegChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#EFF6FF',
    borderWidth: 1,
    borderColor: '#3B82F6',
    borderRadius: 8,
    padding: 8,
    marginRight: 8,
    minWidth: 140,
  },
  selectedLegNumber: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: '#3B82F6',
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
    color: '#1F2937',
  },
  selectedLegStat: {
    fontSize: 11,
    color: '#6B7280',
  },
  removeButton: {
    padding: 4,
  },
  removeButtonText: {
    fontSize: 16,
    color: '#EF4444',
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
    color: '#6B7280',
  },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
  },
  propCard: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 8,
    padding: 12,
    marginHorizontal: 16,
    marginVertical: 6,
  },
  propCardSelected: {
    borderColor: '#3B82F6',
    borderWidth: 2,
    backgroundColor: '#EFF6FF',
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
    color: '#1F2937',
    marginBottom: 2,
  },
  propDetails: {
    fontSize: 13,
    color: '#6B7280',
    marginBottom: 2,
  },
  propProjection: {
    fontSize: 12,
    color: '#4B5563',
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
    color: '#3B82F6',
  },
  checkmark: {
    fontSize: 16,
    color: '#22C55E',
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
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 24,
    width: '100%',
    maxWidth: 400,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8,
    textAlign: 'center',
  },
  modalSubtitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#4B5563',
    marginBottom: 16,
    textAlign: 'center',
  },
  modalInfo: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 8,
  },
  modalInputContainer: {
    marginVertical: 16,
  },
  modalLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#4B5563',
    marginBottom: 8,
  },
  modalInput: {
    backgroundColor: '#F9FAFB',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    padding: 12,
    fontSize: 18,
    color: '#1F2937',
    textAlign: 'center',
    fontWeight: 'bold',
  },
  modalHint: {
    fontSize: 12,
    color: '#6B7280',
    backgroundColor: '#F3F4F6',
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
    backgroundColor: '#F3F4F6',
  },
  modalButtonConfirm: {
    backgroundColor: '#3B82F6',
  },
  modalButtonCancelText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#4B5563',
  },
  modalButtonConfirmText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
});
