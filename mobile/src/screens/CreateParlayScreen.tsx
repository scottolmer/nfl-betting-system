import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  ActivityIndicator,
  Modal,
} from 'react-native';
import { apiService } from '../services/api';
import { parlayStorage } from '../services/parlayStorage';
import { PropAnalysis, SavedParlay, SavedParlayLeg, Sportsbook, PropFilters } from '../types';

interface CreateParlayScreenProps {
  onClose: () => void;
  onSaved: () => void;
}

export default function CreateParlayScreen({ onClose, onSaved }: CreateParlayScreenProps) {
  const [parlayName, setParlayName] = useState('');
  const [sportsbook, setSportsbook] = useState<Sportsbook>('DraftKings Pick 6');
  const [currentWeek] = useState(17); // TODO: Make dynamic

  // Filters
  const [minConfidence, setMinConfidence] = useState(60);
  const [selectedPositions, setSelectedPositions] = useState<string[]>([]);
  const [selectedTeams, setSelectedTeams] = useState<string[]>([]);

  // Props and selections
  const [availableProps, setAvailableProps] = useState<PropAnalysis[]>([]);
  const [selectedLegs, setSelectedLegs] = useState<SavedParlayLeg[]>([]);
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  // Line adjustment
  const [adjustingLeg, setAdjustingLeg] = useState<SavedParlayLeg | null>(null);
  const [adjustedLine, setAdjustedLine] = useState('');
  const [adjusting, setAdjusting] = useState(false);

  useEffect(() => {
    loadProps();
  }, [minConfidence, selectedPositions, selectedTeams]);

  const loadProps = async () => {
    setLoading(true);
    try {
      const props = await apiService.getProps({
        week: currentWeek,
        min_confidence: minConfidence,
        positions: selectedPositions.length > 0 ? selectedPositions.join(',') : undefined,
        teams: selectedTeams.length > 0 ? selectedTeams.join(',') : undefined,
        limit: 50,
      });
      setAvailableProps(props);
    } catch (error) {
      console.error('Error loading props:', error);
      Alert.alert('Error', 'Failed to load props');
    } finally {
      setLoading(false);
    }
  };

  const calculateCombinedConfidence = (legs: SavedParlayLeg[]): number => {
    if (legs.length === 0) return 0;
    const product = legs.reduce((acc, leg) => acc * (leg.confidence / 100), 1);
    return product * 100;
  };

  const calculateRiskLevel = (legs: SavedParlayLeg[], confidence: number): 'LOW' | 'MEDIUM' | 'HIGH' => {
    if (legs.length <= 2 && confidence >= 70) return 'LOW';
    if (legs.length <= 4 && confidence >= 60) return 'MEDIUM';
    return 'HIGH';
  };

  const togglePropSelection = (prop: PropAnalysis) => {
    const exists = selectedLegs.find(
      leg => leg.player_name === prop.player_name && leg.stat_type === prop.stat_type
    );

    if (exists) {
      setSelectedLegs(selectedLegs.filter(
        leg => !(leg.player_name === prop.player_name && leg.stat_type === prop.stat_type)
      ));
    } else {
      if (selectedLegs.length >= 6) {
        Alert.alert('Max Legs Reached', 'Maximum 6 legs per parlay');
        return;
      }

      const newLeg: SavedParlayLeg = {
        player_name: prop.player_name,
        team: prop.team,
        position: prop.position,
        stat_type: prop.stat_type,
        line: prop.line,
        bet_type: prop.bet_type,
        opponent: prop.opponent,
        confidence: prop.confidence,
        projection: prop.projection,
        cushion: prop.cushion,
      };
      setSelectedLegs([...selectedLegs, newLeg]);
    }
  };

  const isSelected = (prop: PropAnalysis): boolean => {
    return selectedLegs.some(
      leg => leg.player_name === prop.player_name && leg.stat_type === prop.stat_type
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

    setAdjusting(true);

    try {
      // Call backend API to recalculate confidence
      const result = await apiService.adjustLine({
        week: currentWeek,
        player_name: adjustingLeg.player_name,
        stat_type: adjustingLeg.stat_type,
        bet_type: adjustingLeg.bet_type,
        original_line: adjustingLeg.original_line || adjustingLeg.line,
        new_line: newLine,
      });

      // Update the leg with adjusted values
      const updatedLegs = selectedLegs.map(leg => {
        if (leg.player_name === adjustingLeg.player_name && leg.stat_type === adjustingLeg.stat_type) {
          return {
            ...leg,
            original_line: leg.original_line || leg.line,
            adjusted_line: newLine,
            line: newLine,
            confidence: result.adjusted_confidence,
            cushion: result.adjusted_cushion,
          };
        }
        return leg;
      });

      setSelectedLegs(updatedLegs);
      setAdjustingLeg(null);
      setAdjustedLine('');

      Alert.alert(
        'Line Adjusted',
        `Confidence: ${Math.round(result.original_confidence)}% → ${Math.round(result.adjusted_confidence)}% (${result.confidence_change > 0 ? '+' : ''}${Math.round(result.confidence_change)})\n\n${result.recommendation}`
      );
    } catch (error) {
      console.error('Error adjusting line:', error);
      Alert.alert('Error', 'Failed to adjust line. Please try again.');
    } finally {
      setAdjusting(false);
    }
  };

  const handleCancelAdjustment = () => {
    setAdjustingLeg(null);
    setAdjustedLine('');
  };

  const handleSave = async () => {
    if (!parlayName.trim()) {
      Alert.alert('Name Required', 'Please enter a parlay name');
      return;
    }

    if (selectedLegs.length < 2) {
      Alert.alert('Not Enough Legs', 'Please select at least 2 props');
      return;
    }

    const combinedConfidence = calculateCombinedConfidence(selectedLegs);
    const riskLevel = calculateRiskLevel(selectedLegs, combinedConfidence);

    const newParlay: SavedParlay = {
      id: Date.now().toString(),
      name: parlayName.trim(),
      week: currentWeek,
      legs: selectedLegs,
      combined_confidence: combinedConfidence,
      risk_level: riskLevel,
      sportsbook,
      status: 'draft',
      created_at: new Date().toISOString(),
    };

    const result = await parlayStorage.saveParlay(newParlay);

    if (result.success) {
      Alert.alert('Success', 'Parlay saved!', [
        { text: 'OK', onPress: () => {
          onSaved();
          onClose();
        }}
      ]);
    } else {
      Alert.alert('Error', result.error || 'Failed to save parlay');
    }
  };

  const combinedConfidence = calculateCombinedConfidence(selectedLegs);
  const riskLevel = calculateRiskLevel(selectedLegs, combinedConfidence);

  const positions = ['QB', 'RB', 'WR', 'TE'];
  const sportsbooks: Sportsbook[] = [
    'DraftKings Pick 6',
    'FanDuel Pick 6',
    'Underdog Fantasy',
    'PrizePicks',
    'BetMGM',
    'Caesars',
  ];

  return (
    <View style={styles.container}>
      {/* Line Adjustment Modal */}
      <Modal
        visible={adjustingLeg !== null}
        transparent
        animationType="fade"
      >
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
                  💡 Pick 6 lines often differ from regular props. Adjust here to get accurate confidence.
                </Text>

                <View style={styles.modalButtons}>
                  <TouchableOpacity
                    style={[styles.modalButton, styles.modalButtonCancel]}
                    onPress={handleCancelAdjustment}
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

      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={onClose} style={styles.closeButton}>
          <Text style={styles.closeButtonText}>✕</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Create Parlay</Text>
        <TouchableOpacity onPress={handleSave} style={styles.saveButton}>
          <Text style={styles.saveButtonText}>Save</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content}>
        {/* Parlay Info */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Parlay Details</Text>

          <TextInput
            style={styles.input}
            placeholder="Parlay Name (e.g., Sunday Morning Special)"
            value={parlayName}
            onChangeText={setParlayName}
            placeholderTextColor="#9CA3AF"
          />

          <View style={styles.sportsbookSelector}>
            <Text style={styles.label}>Sportsbook:</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.chipRow}>
              {sportsbooks.map((book) => (
                <TouchableOpacity
                  key={book}
                  style={[styles.chip, sportsbook === book && styles.chipSelected]}
                  onPress={() => setSportsbook(book)}
                >
                  <Text style={[styles.chipText, sportsbook === book && styles.chipTextSelected]}>
                    {book}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        </View>

        {/* Selected Legs */}
        {selectedLegs.length > 0 && (
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>
                Your Parlay ({selectedLegs.length} legs)
              </Text>
              <View style={styles.confidenceBadge}>
                <Text style={styles.confidenceBadgeText}>
                  {Math.round(combinedConfidence)}% • {riskLevel}
                </Text>
              </View>
            </View>

            {selectedLegs.map((leg, index) => (
              <View key={index} style={styles.selectedLeg}>
                <Text style={styles.legNumber}>{index + 1}</Text>
                <View style={styles.legContent}>
                  <Text style={styles.legPlayer}>{leg.player_name}</Text>
                  <Text style={styles.legDetails}>
                    {leg.stat_type} {leg.bet_type} {leg.line}
                    {leg.adjusted_line && leg.adjusted_line !== leg.original_line && (
                      <Text style={styles.adjustedIndicator}> (adjusted from {leg.original_line})</Text>
                    )}
                  </Text>
                  <TouchableOpacity
                    style={styles.adjustButton}
                    onPress={() => handleAdjustLine(leg)}
                  >
                    <Text style={styles.adjustButtonText}>✏️ Adjust Line</Text>
                  </TouchableOpacity>
                </View>
                <TouchableOpacity
                  onPress={() => togglePropSelection({ ...leg, agent_analyses: [], top_reasons: [] } as PropAnalysis)}
                >
                  <Text style={styles.removeButton}>✕</Text>
                </TouchableOpacity>
              </View>
            ))}
          </View>
        )}

        {/* Filters */}
        <View style={styles.section}>
          <TouchableOpacity
            style={styles.filterToggle}
            onPress={() => setShowFilters(!showFilters)}
          >
            <Text style={styles.sectionTitle}>Filters</Text>
            <Text style={styles.filterToggleIcon}>{showFilters ? '▼' : '▶'}</Text>
          </TouchableOpacity>

          {showFilters && (
            <View style={styles.filtersContainer}>
              <View style={styles.filterRow}>
                <Text style={styles.label}>Min Confidence: {minConfidence}</Text>
                <View style={styles.confidenceButtons}>
                  {[60, 65, 70, 75, 80].map((val) => (
                    <TouchableOpacity
                      key={val}
                      style={[styles.confButton, minConfidence === val && styles.confButtonActive]}
                      onPress={() => setMinConfidence(val)}
                    >
                      <Text style={[styles.confButtonText, minConfidence === val && styles.confButtonTextActive]}>
                        {val}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>

              <View style={styles.filterRow}>
                <Text style={styles.label}>Positions:</Text>
                <View style={styles.chipRow}>
                  {positions.map((pos) => (
                    <TouchableOpacity
                      key={pos}
                      style={[styles.chip, selectedPositions.includes(pos) && styles.chipSelected]}
                      onPress={() => {
                        if (selectedPositions.includes(pos)) {
                          setSelectedPositions(selectedPositions.filter(p => p !== pos));
                        } else {
                          setSelectedPositions([...selectedPositions, pos]);
                        }
                      }}
                    >
                      <Text style={[styles.chipText, selectedPositions.includes(pos) && styles.chipTextSelected]}>
                        {pos}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>
            </View>
          )}
        </View>

        {/* Available Props */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            Available Props ({availableProps.length})
          </Text>

          {loading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator color="#3B82F6" />
            </View>
          ) : (
            availableProps.map((prop, index) => (
              <TouchableOpacity
                key={index}
                style={[styles.propCard, isSelected(prop) && styles.propCardSelected]}
                onPress={() => togglePropSelection(prop)}
              >
                <View style={styles.propHeader}>
                  <View style={styles.propInfo}>
                    <Text style={styles.propPlayer}>{prop.player_name}</Text>
                    <Text style={styles.propDetails}>
                      {prop.team} {prop.position} • {prop.stat_type} {prop.bet_type} {prop.line}
                    </Text>
                  </View>
                  <View style={styles.propConfidence}>
                    <Text style={styles.confidenceText}>{Math.round(prop.confidence)}</Text>
                    {isSelected(prop) && (
                      <Text style={styles.checkmark}>✓</Text>
                    )}
                  </View>
                </View>
              </TouchableOpacity>
            ))
          )}
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
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#1F2937',
    padding: 16,
    paddingTop: 50,
  },
  closeButton: {
    padding: 8,
  },
  closeButtonText: {
    color: '#FFFFFF',
    fontSize: 24,
    fontWeight: 'bold',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  saveButton: {
    backgroundColor: '#3B82F6',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  saveButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  content: {
    flex: 1,
  },
  section: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 12,
  },
  input: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    color: '#1F2937',
  },
  sportsbookSelector: {
    marginTop: 12,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#4B5563',
    marginBottom: 8,
  },
  chipRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  chip: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 16,
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginRight: 8,
  },
  chipSelected: {
    backgroundColor: '#3B82F6',
    borderColor: '#3B82F6',
  },
  chipText: {
    fontSize: 13,
    color: '#4B5563',
    fontWeight: '500',
  },
  chipTextSelected: {
    color: '#FFFFFF',
  },
  confidenceBadge: {
    backgroundColor: '#3B82F6',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  confidenceBadgeText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: 'bold',
  },
  selectedLeg: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
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
  legContent: {
    flex: 1,
  },
  legPlayer: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1F2937',
  },
  legDetails: {
    fontSize: 13,
    color: '#6B7280',
  },
  removeButton: {
    fontSize: 20,
    color: '#EF4444',
    padding: 4,
  },
  filterToggle: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  filterToggleIcon: {
    fontSize: 16,
    color: '#6B7280',
  },
  filtersContainer: {
    marginTop: 12,
  },
  filterRow: {
    marginBottom: 16,
  },
  confidenceButtons: {
    flexDirection: 'row',
    marginTop: 8,
  },
  confButton: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    padding: 10,
    alignItems: 'center',
    marginRight: 8,
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
  loadingContainer: {
    padding: 40,
    alignItems: 'center',
  },
  propCard: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
  },
  propCardSelected: {
    borderColor: '#3B82F6',
    borderWidth: 2,
    backgroundColor: '#EFF6FF',
  },
  propHeader: {
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
  },
  propConfidence: {
    alignItems: 'center',
    marginLeft: 12,
  },
  confidenceText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#3B82F6',
  },
  checkmark: {
    fontSize: 16,
    color: '#22C55E',
    marginTop: 4,
  },
  adjustButton: {
    marginTop: 6,
    paddingVertical: 4,
    paddingHorizontal: 8,
    backgroundColor: '#EFF6FF',
    borderRadius: 6,
    alignSelf: 'flex-start',
  },
  adjustButtonText: {
    fontSize: 12,
    color: '#3B82F6',
    fontWeight: '600',
  },
  adjustedIndicator: {
    fontSize: 11,
    color: '#F59E0B',
    fontStyle: 'italic',
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
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
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
  },
  modalButton: {
    flex: 1,
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  modalButtonCancel: {
    backgroundColor: '#F3F4F6',
    marginRight: 12,
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
