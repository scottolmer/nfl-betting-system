
/**
 * Midnight Glass Implementation - Refined
 * A premium dark mode theme with enhanced glassmorphism and subtle gradients.
 */

export const theme = {
  colors: {
    // Backgrounds: Deeper, richer blacks for OLED-like pop
    background: '#0B1120',  // Darker Slate-950/Black mix
    backgroundDark: '#020617', // Pure Slate-950

    // Glass Surfaces: More sophisticated transparency stacks
    glassLow: 'rgba(30, 41, 59, 0.4)',  // Subtle card bg
    glassHigh: 'rgba(51, 65, 85, 0.3)', // Lighter highlight
    glassBorder: 'rgba(148, 163, 184, 0.1)', // Very subtle crisp border
    glassInput: 'rgba(15, 23, 42, 0.65)', // Input specific

    // Text: Calibrated for reading on dark
    textPrimary: '#F1F5F9', // Slate 100 - softer than pure white
    textSecondary: '#94A3B8', // Slate 400
    textTertiary: '#475569', // Slate 600 - for deep secondary

    // Accents: "Neon" variants for glow effects
    primary: '#3B82F6',
    primaryGlow: 'rgba(59, 130, 246, 0.5)',
    success: '#10B981', // Emerald 500 - more modern green
    successGlow: 'rgba(16, 185, 129, 0.4)',
    danger: '#F43F5E', // Rose 500 - more modern red
    dangerGlow: 'rgba(244, 63, 94, 0.4)',
    warning: '#F59E0B', // Amber 500 - caution/borderline
    gold: '#F59E0B', // Amber 500

    // Chat Specific
    userBubble: '#2563EB', // Stronger blue for user
    agentBubble: 'transparent',

    // Gradients
    gradients: {
      background: ['#0B1120', '#020617'] as string[],
      primaryButton: ['#3B82F6', '#2563EB'] as string[],
      card: ['rgba(30, 41, 59, 0.4)', 'rgba(15, 23, 42, 0.4)'] as string[],
      success: ['rgba(16, 185, 129, 0.2)', 'rgba(0,0,0,0)'] as string[], // Subtle green fade
    }
  },

  spacing: {
    xs: 4,
    s: 8,
    m: 16,
    l: 24,
    xl: 32,
    xxl: 40,
    header: 60, // Custom spacing for headers
  },

  borderRadius: {
    s: 8,
    m: 16, // Modern standard card radius
    l: 24,
    xl: 32,
    pill: 100,
  },

  // Shadows for non-flat feel
  shadows: {
    glow: {
      shadowColor: '#3B82F6',
      shadowOffset: { width: 0, height: 0 },
      shadowOpacity: 0.4,
      shadowRadius: 10,
      elevation: 5,
    },
    card: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.3,
      shadowRadius: 8,
      elevation: 4,
    }
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
      color: '#CBD5E1', // Slate 300
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
      fontFamily: 'System', // Fallback for monospace feel
    }
  }
} as const;

export type Theme = typeof theme;
