/**
 * Info Tooltip Component
 * Shows a [?] icon that opens an explanation modal when tapped
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  Modal,
  StyleSheet,
  ScrollView,
} from 'react-native';
import { TOOLTIPS, TooltipContent } from '../../constants/tooltips';
import { theme } from '../../constants/theme';

interface InfoTooltipProps {
  tooltipKey: string;
  iconSize?: number;
  iconColor?: string;
}

export default function InfoTooltip({
  tooltipKey,
  iconSize = 16,
  iconColor = theme.colors.textTertiary,
}: InfoTooltipProps) {
  const [modalVisible, setModalVisible] = useState(false);
  const tooltip = TOOLTIPS[tooltipKey];

  if (!tooltip) {
    console.warn(`Tooltip key "${tooltipKey}" not found in TOOLTIPS`);
    return null;
  }

  return (
    <>
      <TouchableOpacity
        onPress={() => setModalVisible(true)}
        style={styles.iconButton}
        hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
      >
        <View
          style={[
            styles.iconContainer,
            { width: iconSize, height: iconSize, borderColor: iconColor },
          ]}
        >
          <Text style={[styles.icon, { fontSize: iconSize * 0.7, color: iconColor }]}>
            ?
          </Text>
        </View>
      </TouchableOpacity>

      <TooltipModal
        visible={modalVisible}
        tooltip={tooltip}
        onClose={() => setModalVisible(false)}
      />
    </>
  );
}

interface TooltipModalProps {
  visible: boolean;
  tooltip: TooltipContent;
  onClose: () => void;
}

function TooltipModal({ visible, tooltip, onClose }: TooltipModalProps) {
  return (
    <Modal
      visible={visible}
      animationType="fade"
      transparent
      onRequestClose={onClose}
    >
      <TouchableOpacity
        style={styles.modalOverlay}
        activeOpacity={1}
        onPress={onClose}
      >
        <View style={styles.modalContent}>
          <ScrollView showsVerticalScrollIndicator={false}>
            <Text style={styles.modalTitle}>{tooltip.title}</Text>
            <Text style={styles.modalDescription}>{tooltip.description}</Text>
            {tooltip.example && (
              <View style={styles.exampleContainer}>
                <Text style={styles.exampleLabel}>Example:</Text>
                <Text style={styles.exampleText}>{tooltip.example}</Text>
              </View>
            )}
          </ScrollView>

          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Text style={styles.closeButtonText}>Got it</Text>
          </TouchableOpacity>
        </View>
      </TouchableOpacity>
    </Modal>
  );
}

const styles = StyleSheet.create({
  iconButton: {
    marginLeft: 4,
  },
  iconContainer: {
    borderWidth: 1.5,
    borderRadius: 100,
    justifyContent: 'center',
    alignItems: 'center',
  },
  icon: {
    fontWeight: 'bold',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalContent: {
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: 16,
    padding: 24,
    maxWidth: 400,
    width: '100%',
    maxHeight: '80%',
  },
  modalTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: theme.colors.textPrimary,
    marginBottom: 12,
  },
  modalDescription: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    lineHeight: 24,
    marginBottom: 16,
  },
  exampleContainer: {
    backgroundColor: theme.colors.backgroundElevated,
    padding: 16,
    borderRadius: 8,
    marginBottom: 16,
  },
  exampleLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.textSecondary,
    marginBottom: 6,
  },
  exampleText: {
    fontSize: 14,
    color: theme.colors.textPrimary,
    lineHeight: 20,
  },
  closeButton: {
    backgroundColor: theme.colors.primary,
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  closeButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});
