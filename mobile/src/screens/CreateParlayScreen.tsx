import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { apiService } from '../services/api';
import { parlayStorage } from '../services/parlayStorage';
import { PropAnalysis, SavedParlay, SavedParlayLeg, Sportsbook } from '../types';
import StepWizard from '../components/parlay-builder/StepWizard';
import ParlaySetupStep from '../components/parlay-builder/ParlaySetupStep';
import PropSelectionStep from '../components/parlay-builder/PropSelectionStep';
import ReviewStep from '../components/parlay-builder/ReviewStep';
import ParlayFloatingSummary from '../components/parlay-builder/ParlayFloatingSummary';
import { theme } from '../constants/theme';

interface CreateParlayScreenProps {
  onClose: () => void;
  onSaved: () => void;
}

export default function CreateParlayScreen({ onClose, onSaved }: CreateParlayScreenProps) {
  // Wizard state
  const [currentStep, setCurrentStep] = useState(1);

  // Step 1: Setup
  const [parlayName, setParlayName] = useState('');
  const [sportsbook, setSportsbook] = useState<Sportsbook>('DraftKings Pick 6');

  // Step 2: Prop Selection
  const [currentWeek] = useState(17); // TODO: Make dynamic
  const [minConfidence, setMinConfidence] = useState(70);
  const [selectedPositions, setSelectedPositions] = useState<string[]>([]);
  const [availableProps, setAvailableProps] = useState<PropAnalysis[]>([]);
  const [selectedLegs, setSelectedLegs] = useState<SavedParlayLeg[]>([]);
  const [loading, setLoading] = useState(false);
  const [adjusting, setAdjusting] = useState(false);

  // Load props when filters change
  useEffect(() => {
    if (currentStep === 2) {
      loadProps();
    }
  }, [currentStep, minConfidence, selectedPositions]);

  const loadProps = async () => {
    setLoading(true);
    try {
      const props = await apiService.getProps({
        week: currentWeek,
        min_confidence: minConfidence,
        positions: selectedPositions.length > 0 ? selectedPositions.join(',') : undefined,
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

  // Calculations
  const calculateCombinedConfidence = (legs: SavedParlayLeg[]): number => {
    if (legs.length === 0) return 0;
    const product = legs.reduce((acc, leg) => acc * (leg.confidence / 100), 1);
    return product * 100;
  };

  const calculateRiskLevel = (
    legs: SavedParlayLeg[],
    confidence: number
  ): 'LOW' | 'MEDIUM' | 'HIGH' => {
    if (legs.length <= 2 && confidence >= 70) return 'LOW';
    if (legs.length <= 4 && confidence >= 60) return 'MEDIUM';
    return 'HIGH';
  };

  const combinedConfidence = calculateCombinedConfidence(selectedLegs);
  const riskLevel = calculateRiskLevel(selectedLegs, combinedConfidence);

  // Prop selection handlers
  const togglePropSelection = (prop: PropAnalysis) => {
    const exists = selectedLegs.find(
      (leg) =>
        leg.player_name === prop.player_name && leg.stat_type === prop.stat_type
    );

    if (exists) {
      setSelectedLegs(
        selectedLegs.filter(
          (leg) =>
            !(leg.player_name === prop.player_name && leg.stat_type === prop.stat_type)
        )
      );
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

  const handleAdjustLine = async (leg: SavedParlayLeg, newLine: number) => {
    setAdjusting(true);

    try {
      const result = await apiService.adjustLine({
        week: currentWeek,
        player_name: leg.player_name,
        stat_type: leg.stat_type,
        bet_type: leg.bet_type,
        original_line: leg.original_line || leg.line,
        new_line: newLine,
      });

      const updatedLegs = selectedLegs.map((l) => {
        if (l.player_name === leg.player_name && l.stat_type === leg.stat_type) {
          return {
            ...l,
            original_line: l.original_line || l.line,
            adjusted_line: newLine,
            line: newLine,
            confidence: result.adjusted_confidence,
            cushion: result.adjusted_cushion,
          };
        }
        return l;
      });

      setSelectedLegs(updatedLegs);

      Alert.alert(
        'Line Adjusted',
        `Confidence: ${Math.round(result.original_confidence)}% → ${Math.round(
          result.adjusted_confidence
        )}% (${result.confidence_change > 0 ? '+' : ''}${Math.round(
          result.confidence_change
        )})\n\n${result.recommendation}`
      );
    } catch (error) {
      console.error('Error adjusting line:', error);
      Alert.alert('Error', 'Failed to adjust line. Please try again.');
    } finally {
      setAdjusting(false);
    }
  };

  // Navigation handlers
  const handleNext = () => {
    if (currentStep === 1) {
      if (!parlayName.trim()) {
        Alert.alert('Name Required', 'Please enter a parlay name');
        return;
      }
      setCurrentStep(2);
    } else if (currentStep === 2) {
      if (selectedLegs.length < 2) {
        Alert.alert('Not Enough Legs', 'Please select at least 2 props');
        return;
      }
      setCurrentStep(3);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
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
        {
          text: 'OK',
          onPress: () => {
            onSaved();
            onClose();
          },
        },
      ]);
    } else {
      Alert.alert('Error', result.error || 'Failed to save parlay');
    }
  };

  // Render current step
  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <ParlaySetupStep
            parlayName={parlayName}
            onParlayNameChange={setParlayName}
            sportsbook={sportsbook}
            onSportsbookChange={setSportsbook}
          />
        );
      case 2:
        return (
          <PropSelectionStep
            availableProps={availableProps}
            selectedLegs={selectedLegs}
            loading={loading}
            minConfidence={minConfidence}
            selectedPositions={selectedPositions}
            onMinConfidenceChange={setMinConfidence}
            onPositionsChange={setSelectedPositions}
            onToggleProp={togglePropSelection}
            onAdjustLine={handleAdjustLine}
            adjusting={adjusting}
          />
        );
      case 3:
        return (
          <ReviewStep
            parlayName={parlayName}
            sportsbook={sportsbook}
            legs={selectedLegs}
            combinedConfidence={combinedConfidence}
            riskLevel={riskLevel}
          />
        );
      default:
        return null;
    }
  };

  const stepLabels = ['Setup', 'Add Props', 'Review'];

  return (
    <View style={styles.container}>
      <StepWizard
        currentStep={currentStep}
        totalSteps={3}
        stepLabels={stepLabels}
        onNext={handleNext}
        onBack={handleBack}
        onCancel={onClose}
        onSave={handleSave}
        nextButtonText={currentStep === 2 ? 'Review' : 'Next'}
        nextButtonDisabled={currentStep === 1 && !parlayName.trim()}
        saveButtonDisabled={selectedLegs.length < 2}
      >
        <View style={styles.stepContent}>
          {/* Show floating summary on step 2 and 3 */}
          {currentStep >= 2 && (
            <ParlayFloatingSummary
              legs={selectedLegs}
              combinedConfidence={combinedConfidence}
              riskLevel={riskLevel}
            />
          )}

          {renderStep()}
        </View>
      </StepWizard>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  stepContent: {
    flex: 1,
  },
});
