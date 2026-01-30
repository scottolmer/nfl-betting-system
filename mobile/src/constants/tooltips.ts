/**
 * Centralized tooltip content for the app
 * All educational content and explanations in one place
 */

export interface TooltipContent {
  title: string;
  description: string;
  example?: string;
}

export const TOOLTIPS: Record<string, TooltipContent> = {
  confidence: {
    title: 'Confidence Score',
    description: 'Calculated by 9 specialized AI agents analyzing stats, matchups, trends, and more. Higher scores indicate stronger predictions.',
    example: '80+ = Elite, 75-79 = Strong, 70-74 = Solid',
  },

  cushion: {
    title: 'Cushion',
    description: 'The difference between our projection and the betting line. A larger cushion means more room for the bet to hit.',
    example: 'Line: 250 yards, Projection: 265 yards = +15 cushion',
  },

  projection: {
    title: 'Projection',
    description: 'Our AI models predict this is what the player will actually achieve in the game.',
    example: 'If we project 275 yards and the line is 250, we recommend OVER',
  },

  dvoa: {
    title: 'DVOA (Defense-adjusted Value Over Average)',
    description: 'Advanced metric measuring team efficiency. Positive DVOA = above average, negative = below average. Used by our agents to evaluate matchups.',
    example: 'Offense DVOA +15% vs Defense DVOA -10% = great matchup',
  },

  parlays: {
    title: 'Parlays',
    description: 'A parlay combines multiple prop bets into one ticket. All legs must hit to win, but payouts are much higher than single bets.',
    example: '3-leg parlay at +600 odds means $10 bet wins $60',
  },

  riskLevel: {
    title: 'Risk Level',
    description: 'Calculated from combined confidence and number of legs. More legs or lower confidence = higher risk.',
    example: 'LOW = 2-3 legs with 75+ confidence, HIGH = 5+ legs or sub-70 confidence',
  },

  combinedConfidence: {
    title: 'Combined Confidence',
    description: 'The probability that ALL legs in your parlay will hit. Calculated by multiplying individual leg confidences together.',
    example: '3 legs at 80% each = 51% combined (0.8 × 0.8 × 0.8)',
  },

  lineAdjustment: {
    title: 'Line Adjustment',
    description: 'See how confidence changes if you take a different line than what our analysis used. Useful when your sportsbook has different odds.',
    example: 'Original line 250 yards (80% conf) → 260 yards (73% conf)',
  },

  targetShare: {
    title: 'Target Share',
    description: 'Percentage of team targets/carries this player receives. Higher share = more opportunities to hit the prop.',
    example: '25% target share = gets 1 out of every 4 passes',
  },

  hitRate: {
    title: 'Hit Rate',
    description: 'How often props at this confidence level actually hit. Based on historical backtesting of our model.',
    example: '80% confidence props hit about 75-80% of the time',
  },

  draftkingsPick6: {
    title: 'Why DraftKings Pick 6?',
    description: 'Pick 6 contests have better odds than traditional parlays and only require 2+ picks. Perfect for prop betting with guaranteed payouts.',
    example: '2-pick entry = 3x payout, 6-pick = 25x payout',
  },

  correlation: {
    title: 'Correlation',
    description: 'How props relate to each other. QB passing yards and WR receiving yards are correlated (both benefit if team passes a lot).',
    example: 'Correlated: QB yards + WR yards. Uncorrelated: Players from different games',
  },

  statType: {
    title: 'Stat Type',
    description: 'The specific statistic being bet on. Different positions have different available props.',
    example: 'QB: Passing Yards, Passing TDs. RB: Rushing Yards, Receptions',
  },

  betType: {
    title: 'Over/Under',
    description: 'OVER = player will exceed the line. UNDER = player will stay below the line.',
    example: 'OVER 250 yards = bet wins if player gets 251+',
  },

  opponent: {
    title: 'Opponent Matchup',
    description: 'Who the player is facing. Our agents analyze opponent defense rankings, tendencies, and recent performance.',
    example: 'WR vs #32 ranked pass defense = favorable matchup',
  },

  agentAnalyses: {
    title: 'Agent Analyses',
    description: 'Each of our 9 AI agents (Stats, Trends, Matchup, etc.) provides independent analysis. View all their reasoning here.',
    example: 'Stats Agent: 80% - "Averaging 285 yards in last 3 games"',
  },

  preBuildParlays: {
    title: 'Pre-Built Parlays',
    description: 'Curated combinations of props that work well together. Analyzed for correlation, confidence, and balance.',
    example: 'High-confidence 3-leg parlays optimized for DraftKings Pick 6',
  },

  myParlays: {
    title: 'My Parlays',
    description: 'Your custom-built parlays. Create with filters, save for later, mark as placed, and track results.',
    example: 'Build a 4-leg parlay, save it, then copy to your sportsbook',
  },

  sportsbook: {
    title: 'Sportsbook',
    description: 'Which betting platform you plan to use. Lines may vary slightly between sportsbooks.',
    example: 'DraftKings Pick 6, PrizePicks, Underdog Fantasy, etc.',
  },

  week: {
    title: 'NFL Week',
    description: 'Which week of the NFL season. Props are analyzed fresh each week based on updated stats and matchups.',
    example: 'Week 17 = regular season finale, Week 18 = final week',
  },
};

// Quick reference for onboarding content
export const ONBOARDING_CONTENT = {
  welcome: {
    title: 'Welcome to NFL Betting Analysis',
    subtitle: 'AI-Powered Prop Predictions',
    description: 'Get confident prop bet recommendations analyzed by 9 specialized AI agents. Built specifically for DraftKings Pick 6 and other prop betting platforms.',
  },

  howItWorks: {
    title: 'Three Ways to Use the App',
    options: [
      {
        icon: '🎯',
        title: 'Browse Top Picks',
        description: 'See the highest confidence props for the week, ranked and ready to bet.',
      },
      {
        icon: '🎰',
        title: 'Use Pre-Built Parlays',
        description: 'Copy optimized parlay combinations curated by our AI.',
      },
      {
        icon: '⚡',
        title: 'Build Custom Parlays',
        description: 'Create your own with advanced filters and live confidence scoring.',
      },
    ],
  },

  confidenceSystem: {
    title: 'Understanding Confidence Scores',
    tiers: [
      {
        emoji: '🔥',
        range: '80+',
        label: 'Elite',
        description: 'Highest conviction picks with strong edge',
        color: '#22C55E',
      },
      {
        emoji: '⭐',
        range: '75-79',
        label: 'Strong',
        description: 'Solid picks with good analytical support',
        color: '#F59E0B',
      },
      {
        emoji: '✅',
        range: '70-74',
        label: 'Solid',
        description: 'Decent edge but slightly more risk',
        color: '#3B82F6',
      },
    ],
    footer: 'Scores calculated by 9 AI agents analyzing stats, trends, matchups, and more.',
  },
};
