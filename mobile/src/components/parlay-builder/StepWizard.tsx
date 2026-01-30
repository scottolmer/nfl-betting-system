/**
 * Step Wizard Component
 * Manages step navigation and overall wizard state
 */

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import ProgressStepper from './ProgressStepper';

interface StepWizardProps {
  currentStep: number;
  totalSteps: number;
  stepLabels: string[];
  children: React.ReactNode;
  onNext?: () => void;
  onBack?: () => void;
  onCancel?: () => void;
  onSave?: () => void;
  nextButtonText?: string;
  nextButtonDisabled?: boolean;
  saveButtonDisabled?: boolean;
}

export default function StepWizard({
  currentStep,
  totalSteps,
  stepLabels,
  children,
  onNext,
  onBack,
  onCancel,
  onSave,
  nextButtonText = 'Next',
  nextButtonDisabled = false,
  saveButtonDisabled = false,
}: StepWizardProps) {
  const isFirstStep = currentStep === 1;
  const isLastStep = currentStep === totalSteps;

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={onCancel} style={styles.cancelButton}>
          <Text style={styles.cancelButtonText}>✕</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Create Parlay</Text>
        <View style={styles.placeholder} />
      </View>

      {/* Progress Stepper */}
      <ProgressStepper
        currentStep={currentStep}
        totalSteps={totalSteps}
        stepLabels={stepLabels}
      />

      {/* Step Content */}
      <View style={styles.content}>{children}</View>

      {/* Navigation Footer */}
      <View style={styles.footer}>
        {!isFirstStep && (
          <TouchableOpacity
            style={[styles.button, styles.backButton]}
            onPress={onBack}
          >
            <Text style={styles.backButtonText}>← Back</Text>
          </TouchableOpacity>
        )}

        {isLastStep ? (
          <TouchableOpacity
            style={[
              styles.button,
              styles.saveButton,
              saveButtonDisabled && styles.buttonDisabled,
              !isFirstStep && styles.buttonFlex,
            ]}
            onPress={onSave}
            disabled={saveButtonDisabled}
          >
            <Text style={styles.saveButtonText}>💾 Save Parlay</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity
            style={[
              styles.button,
              styles.nextButton,
              nextButtonDisabled && styles.buttonDisabled,
              !isFirstStep && styles.buttonFlex,
            ]}
            onPress={onNext}
            disabled={nextButtonDisabled}
          >
            <Text style={styles.nextButtonText}>{nextButtonText} →</Text>
          </TouchableOpacity>
        )}
      </View>
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
    paddingHorizontal: 16,
    paddingTop: 50,
    paddingBottom: 16,
  },
  cancelButton: {
    padding: 8,
    width: 40,
  },
  cancelButtonText: {
    color: '#FFFFFF',
    fontSize: 24,
    fontWeight: 'bold',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  placeholder: {
    width: 40,
  },
  content: {
    flex: 1,
  },
  footer: {
    flexDirection: 'row',
    padding: 16,
    paddingBottom: 32,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    gap: 12,
  },
  button: {
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonFlex: {
    flex: 1,
  },
  backButton: {
    backgroundColor: '#F3F4F6',
    borderWidth: 1,
    borderColor: '#D1D5DB',
  },
  backButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#4B5563',
  },
  nextButton: {
    backgroundColor: '#3B82F6',
    flex: 1,
  },
  nextButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  saveButton: {
    backgroundColor: '#22C55E',
  },
  saveButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  buttonDisabled: {
    opacity: 0.5,
  },
});
