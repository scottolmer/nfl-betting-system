
/**
 * Props.Cash + PropsBot.AI Inspired Theme
 * OLED black backgrounds, cyan-green accent (#0AE2A3), glassmorphism with glow effects.
 */

export const theme = {
  colors: {
    // Backgrounds: Pure OLED black for maximum contrast
    background: '#000000',
    backgroundDark: '#000000',
    backgroundCard: '#111111',
    backgroundElevated: '#1A1A1A',

    // Glass Surfaces: Sophisticated transparency on black
    glassLow: 'rgba(17, 17, 17, 0.7)',
    glassHigh: 'rgba(34, 34, 34, 0.5)',
    glassBorder: 'rgba(255, 255, 255, 0.06)',
    glassBorderActive: 'rgba(10, 226, 163, 0.35)',
    glassInput: 'rgba(17, 17, 17, 0.8)',

    // Text: Calibrated for OLED black
    textPrimary: '#F1F5F9',
    textSecondary: '#94A3B8',
    textTertiary: '#475569',

    // Primary Accent: PropsBot cyan-green
    primary: '#0AE2A3',
    primaryGlow: 'rgba(10, 226, 163, 0.30)',
    primaryMuted: 'rgba(10, 226, 163, 0.12)',

    // Semantic Colors
    success: '#10B981',
    successGlow: 'rgba(16, 185, 129, 0.4)',
    successMuted: 'rgba(16, 185, 129, 0.12)',
    danger: '#EF4444',
    dangerGlow: 'rgba(239, 68, 68, 0.4)',
    dangerMuted: 'rgba(239, 68, 68, 0.12)',
    warning: '#F59E0B',
    warningMuted: 'rgba(245, 158, 11, 0.12)',
    gold: '#F59E0B',

    // Chart Colors (Props.Cash style)
    chartHit: '#10B981',
    chartMiss: '#EF4444',
    chartNeutral: '#374151',
    chartLine: '#0AE2A3',
    chartArea: 'rgba(10, 226, 163, 0.15)',

    // Chat
    userBubble: '#0AE2A3',
    agentBubble: 'transparent',

    // Gradients
    gradients: {
      background: ['#000000', '#000000'] as const,
      primaryButton: ['#0AE2A3', '#059669'] as const,
      card: ['rgba(17, 17, 17, 0.9)', 'rgba(10, 10, 10, 0.9)'] as const,
      success: ['rgba(16, 185, 129, 0.2)', 'rgba(0,0,0,0)'] as const,
      heroCard: ['rgba(10, 226, 163, 0.08)', 'rgba(0, 0, 0, 0)'] as const,
      cyanGreen: ['#0AE2A3', '#10B981'] as const,
    }
  },

  spacing: {
    xs: 4,
    s: 8,
    m: 16,
    l: 24,
    xl: 32,
    xxl: 40,
    header: 60,
  },

  borderRadius: {
    s: 8,
    m: 16,
    l: 24,
    xl: 32,
    pill: 100,
  },

  shadows: {
    glow: {
      shadowColor: '#0AE2A3',
      shadowOffset: { width: 0, height: 0 },
      shadowOpacity: 0.4,
      shadowRadius: 12,
      elevation: 6,
    },
    glowSuccess: {
      shadowColor: '#10B981',
      shadowOffset: { width: 0, height: 0 },
      shadowOpacity: 0.35,
      shadowRadius: 10,
      elevation: 5,
    },
    glowDanger: {
      shadowColor: '#EF4444',
      shadowOffset: { width: 0, height: 0 },
      shadowOpacity: 0.35,
      shadowRadius: 10,
      elevation: 5,
    },
    card: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.5,
      shadowRadius: 8,
      elevation: 4,
    },
    cardElevated: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 8 },
      shadowOpacity: 0.6,
      shadowRadius: 16,
      elevation: 8,
    },
  },

  animation: {
    fast: 150,
    normal: 300,
    slow: 500,
    spring: { damping: 15, stiffness: 150 },
  },

  typography: {
    h1: {
      fontSize: 32,
      fontWeight: '800' as const,
      letterSpacing: -1,
      color: '#F1F5F9',
      lineHeight: 38,
    },
    h2: {
      fontSize: 24,
      fontWeight: '700' as const,
      letterSpacing: -0.5,
      color: '#F1F5F9',
      lineHeight: 32,
    },
    h3: {
      fontSize: 20,
      fontWeight: '600' as const,
      color: '#F1F5F9',
      letterSpacing: -0.5,
    },
    body: {
      fontSize: 16,
      fontWeight: '400' as const,
      color: '#CBD5E1',
      lineHeight: 24,
    },
    caption: {
      fontSize: 13,
      fontWeight: '500' as const,
      color: '#64748B',
      letterSpacing: 0.5,
      textTransform: 'uppercase' as const,
    },
    label: {
      fontSize: 14,
      fontWeight: '600' as const,
      color: '#F1F5F9',
    },
    mono: {
      fontSize: 14,
      fontWeight: '500' as const,
      color: '#94A3B8',
      fontFamily: 'System',
    },
    scoreXL: {
      fontSize: 36,
      fontWeight: '800' as const,
      color: '#F1F5F9',
      letterSpacing: -1,
    },
    scoreLG: {
      fontSize: 28,
      fontWeight: '700' as const,
      color: '#F1F5F9',
      letterSpacing: -0.5,
    },
  }
} as const;

export type Theme = typeof theme;
