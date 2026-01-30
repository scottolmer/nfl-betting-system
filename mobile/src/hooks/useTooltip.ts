/**
 * useTooltip Hook
 * Custom hook for managing tooltip modal state
 */

import { useState } from 'react';
import { TOOLTIPS, TooltipContent } from '../constants/tooltips';

interface UseTooltipReturn {
  isVisible: boolean;
  tooltipContent: TooltipContent | null;
  showTooltip: (tooltipKey: string) => void;
  hideTooltip: () => void;
}

export function useTooltip(): UseTooltipReturn {
  const [isVisible, setIsVisible] = useState(false);
  const [tooltipContent, setTooltipContent] = useState<TooltipContent | null>(null);

  const showTooltip = (tooltipKey: string) => {
    const content = TOOLTIPS[tooltipKey];
    if (content) {
      setTooltipContent(content);
      setIsVisible(true);
    } else {
      console.warn(`Tooltip key "${tooltipKey}" not found in TOOLTIPS`);
    }
  };

  const hideTooltip = () => {
    setIsVisible(false);
    // Keep content for a smooth fade-out, clear after animation
    setTimeout(() => {
      setTooltipContent(null);
    }, 300);
  };

  return {
    isVisible,
    tooltipContent,
    showTooltip,
    hideTooltip,
  };
}

/**
 * useTooltipState Hook
 * Simpler version for single tooltip state management
 */
export function useTooltipState(initialState = false) {
  const [isOpen, setIsOpen] = useState(initialState);

  const open = () => setIsOpen(true);
  const close = () => setIsOpen(false);
  const toggle = () => setIsOpen(!isOpen);

  return {
    isOpen,
    open,
    close,
    toggle,
  };
}
