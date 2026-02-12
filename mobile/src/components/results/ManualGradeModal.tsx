/**
 * Manual Grade Modal
 * Allow users to manually enter parlay results
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  TouchableOpacity,
  TextInput,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { SavedParlay } from '../../types';
import { theme } from '../../constants/theme';

interface ManualGradeModalProps {
  visible: boolean;
  parlay: SavedParlay | null;
  onClose: () => void;
  onGrade: (parlayId: string, legsHit: number, legsTotal: number) => Promise<void>;
}

export default function ManualGradeModal({
  visible,
  parlay,
  onClose,
  onGrade,
}: ManualGradeModalProps) {
  const [legsHit, setLegsHit] = useState('');
  const [grading, setGrading] = useState(false);

  const handleGrade = async () => {
    if (!parlay) return;

    const legsHitNum = parseInt(legsHit, 10);
    const legsTotal = parlay.legs.length;

    if (isNaN(legsHitNum) || legsHitNum < 0 || legsHitNum > legsTotal) {
      Alert.alert('Invalid Input', `Please enter a number between 0 and ${legsTotal}`);
      return;
    }

    setGrading(true);

    try {
      await onGrade(parlay.id, legsHitNum, legsTotal);
      setLegsHit('');
      onClose();
      Alert.alert('Success', 'Parlay graded successfully');
    } catch (error) {
      console.error('Error grading parlay:', error);
      Alert.alert('Error', 'Failed to grade parlay');
    } finally {
      setGrading(false);
    }
  };

  const handleQuickSelect = (value: number) => {
    setLegsHit(value.toString());
  };

  if (!parlay) return null;

  const legsTotal = parlay.legs.length;

  return (
    <Modal
      visible={visible}
      transparent
      animationType="fade"
      onRequestClose={onClose}
    >
      <View style={styles.overlay}>
        <View style={styles.modal}>
          <View style={styles.header}>
            <Text style={styles.title}>Grade Parlay</Text>
            <TouchableOpacity onPress={onClose} style={styles.closeButton}>
              <Ionicons name="close" size={24} color={theme.colors.textSecondary} />
            </TouchableOpacity>
          </View>

          <View style={styles.content}>
            <Text style={styles.parlayName}>{parlay.name}</Text>
            <Text style={styles.parlayInfo}>
              {legsTotal} legs • Week {parlay.week}
            </Text>

            <Text style={styles.question}>How many legs hit?</Text>

            <View style={styles.quickSelect}>
              {Array.from({ length: legsTotal + 1 }, (_, i) => i).map(num => (
                <TouchableOpacity
                  key={num}
                  style={[
                    styles.quickButton,
                    legsHit === num.toString() && styles.quickButtonActive,
                  ]}
                  onPress={() => handleQuickSelect(num)}
                >
                  <Text
                    style={[
                      styles.quickButtonText,
                      legsHit === num.toString() && styles.quickButtonTextActive,
                    ]}
                  >
                    {num}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            <Text style={styles.orText}>or enter manually</Text>

            <TextInput
              style={styles.input}
              placeholder={`Enter 0-${legsTotal}`}
              value={legsHit}
              onChangeText={setLegsHit}
              keyboardType="number-pad"
              maxLength={2}
            />

            {legsHit !== '' && (
              <View style={styles.resultPreview}>
                <Text style={styles.resultText}>
                  Result:{' '}
                  <Text
                    style={[
                      styles.resultValue,
                      parseInt(legsHit) === legsTotal
                        ? styles.resultWon
                        : styles.resultLost,
                    ]}
                  >
                    {parseInt(legsHit) === legsTotal ? 'WON' : 'LOST'}
                  </Text>
                </Text>
              </View>
            )}
          </View>

          <View style={styles.actions}>
            <TouchableOpacity
              style={[styles.button, styles.cancelButton]}
              onPress={onClose}
              disabled={grading}
            >
              <Text style={styles.cancelButtonText}>Cancel</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[
                styles.button,
                styles.gradeButton,
                (legsHit === '' || grading) && styles.buttonDisabled,
              ]}
              onPress={handleGrade}
              disabled={legsHit === '' || grading}
            >
              <Text style={styles.gradeButtonText}>
                {grading ? 'Grading...' : 'Grade Parlay'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modal: {
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: 16,
    width: '100%',
    maxWidth: 400,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 8,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.glassBorder,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: theme.colors.textPrimary,
  },
  closeButton: {
    padding: 4,
  },
  content: {
    padding: 20,
  },
  parlayName: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.textPrimary,
    marginBottom: 4,
  },
  parlayInfo: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginBottom: 20,
  },
  question: {
    fontSize: 15,
    fontWeight: '500',
    color: theme.colors.textPrimary,
    marginBottom: 12,
  },
  quickSelect: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 16,
  },
  quickButton: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 8,
    backgroundColor: theme.colors.backgroundElevated,
    borderWidth: 2,
    borderColor: 'transparent',
    minWidth: 50,
    alignItems: 'center',
  },
  quickButtonActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  quickButtonText: {
    fontSize: 15,
    fontWeight: '600',
    color: theme.colors.textSecondary,
  },
  quickButtonTextActive: {
    color: '#FFFFFF',
  },
  orText: {
    fontSize: 13,
    color: theme.colors.textTertiary,
    textAlign: 'center',
    marginBottom: 12,
  },
  input: {
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 15,
    color: theme.colors.textPrimary,
  },
  resultPreview: {
    marginTop: 16,
    padding: 12,
    backgroundColor: theme.colors.backgroundElevated,
    borderRadius: 8,
  },
  resultText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    textAlign: 'center',
  },
  resultValue: {
    fontWeight: '700',
    fontSize: 16,
  },
  resultWon: {
    color: theme.colors.success,
  },
  resultLost: {
    color: theme.colors.danger,
  },
  actions: {
    flexDirection: 'row',
    gap: 12,
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: theme.colors.glassBorder,
  },
  button: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  cancelButton: {
    backgroundColor: theme.colors.backgroundElevated,
  },
  cancelButtonText: {
    fontSize: 15,
    fontWeight: '600',
    color: theme.colors.textSecondary,
  },
  gradeButton: {
    backgroundColor: theme.colors.primary,
  },
  gradeButtonText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  buttonDisabled: {
    opacity: 0.5,
  },
});
