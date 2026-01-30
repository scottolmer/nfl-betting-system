/**
 * Analytics Utilities
 * Track user events and app usage (placeholder for future analytics integration)
 */

/**
 * Analytics event types
 */
export enum AnalyticsEvent {
  // Onboarding
  ONBOARDING_STARTED = 'onboarding_started',
  ONBOARDING_COMPLETED = 'onboarding_completed',
  ONBOARDING_SKIPPED = 'onboarding_skipped',
  TUTORIAL_VIEWED = 'tutorial_viewed',
  TUTORIAL_RESET = 'tutorial_reset',

  // Navigation
  SCREEN_VIEW = 'screen_view',
  TAB_CHANGED = 'tab_changed',

  // Props & Parlays
  PROP_VIEWED = 'prop_viewed',
  PROP_DETAIL_OPENED = 'prop_detail_opened',
  PARLAY_CREATED = 'parlay_created',
  PARLAY_SAVED = 'parlay_saved',
  PARLAY_DELETED = 'parlay_deleted',
  PARLAY_MARKED_PLACED = 'parlay_marked_placed',
  LINE_ADJUSTED = 'line_adjusted',

  // Filters & Search
  FILTER_APPLIED = 'filter_applied',
  CONFIDENCE_FILTER_CHANGED = 'confidence_filter_changed',
  POSITION_FILTER_CHANGED = 'position_filter_changed',

  // Help & Education
  TOOLTIP_OPENED = 'tooltip_opened',
  HELP_BANNER_DISMISSED = 'help_banner_dismissed',
  HELP_BANNER_DONT_SHOW_AGAIN = 'help_banner_dont_show_again',

  // Engagement
  APP_OPENED = 'app_opened',
  APP_BACKGROUNDED = 'app_backgrounded',
  REFRESH_TRIGGERED = 'refresh_triggered',
}

/**
 * Analytics properties interface
 */
export interface AnalyticsProperties {
  [key: string]: string | number | boolean | undefined;
}

/**
 * Analytics tracking class
 */
class Analytics {
  private enabled: boolean = true;
  private debugMode: boolean = __DEV__;

  /**
   * Track an event
   */
  track(event: AnalyticsEvent, properties?: AnalyticsProperties): void {
    if (!this.enabled) return;

    if (this.debugMode) {
      console.log('[Analytics]', event, properties || {});
    }

    // TODO: Integrate with analytics service (Firebase, Amplitude, etc.)
    // Example: amplitude.track(event, properties);
  }

  /**
   * Track screen view
   */
  trackScreenView(screenName: string, properties?: AnalyticsProperties): void {
    this.track(AnalyticsEvent.SCREEN_VIEW, {
      screen_name: screenName,
      ...properties,
    });
  }

  /**
   * Track onboarding completion
   */
  trackOnboardingCompleted(stepCount: number, timeSpent?: number): void {
    this.track(AnalyticsEvent.ONBOARDING_COMPLETED, {
      step_count: stepCount,
      time_spent: timeSpent,
    });
  }

  /**
   * Track parlay creation
   */
  trackParlayCreated(
    legCount: number,
    combinedConfidence: number,
    riskLevel: string,
    sportsbook?: string
  ): void {
    this.track(AnalyticsEvent.PARLAY_CREATED, {
      leg_count: legCount,
      combined_confidence: combinedConfidence,
      risk_level: riskLevel,
      sportsbook: sportsbook,
    });
  }

  /**
   * Track tooltip interaction
   */
  trackTooltipOpened(tooltipKey: string, screenName: string): void {
    this.track(AnalyticsEvent.TOOLTIP_OPENED, {
      tooltip_key: tooltipKey,
      screen_name: screenName,
    });
  }

  /**
   * Track filter changes
   */
  trackFilterApplied(filterType: string, filterValue: string | number): void {
    this.track(AnalyticsEvent.FILTER_APPLIED, {
      filter_type: filterType,
      filter_value: filterValue.toString(),
    });
  }

  /**
   * Track help banner interaction
   */
  trackHelpBannerDismissed(bannerId: string, dontShowAgain: boolean): void {
    this.track(
      dontShowAgain
        ? AnalyticsEvent.HELP_BANNER_DONT_SHOW_AGAIN
        : AnalyticsEvent.HELP_BANNER_DISMISSED,
      {
        banner_id: bannerId,
      }
    );
  }

  /**
   * Set user properties
   */
  setUserProperty(key: string, value: string | number | boolean): void {
    if (!this.enabled) return;

    if (this.debugMode) {
      console.log('[Analytics] User Property:', key, value);
    }

    // TODO: Integrate with analytics service
    // Example: amplitude.setUserProperty(key, value);
  }

  /**
   * Enable/disable tracking
   */
  setEnabled(enabled: boolean): void {
    this.enabled = enabled;
  }

  /**
   * Enable/disable debug mode
   */
  setDebugMode(debug: boolean): void {
    this.debugMode = debug;
  }
}

// Export singleton instance
export const analytics = new Analytics();

/**
 * Helper function to track errors
 */
export function trackError(
  error: Error,
  context?: string,
  additionalInfo?: AnalyticsProperties
): void {
  console.error(`[Error${context ? ` - ${context}` : ''}]:`, error);

  analytics.track('error_occurred' as AnalyticsEvent, {
    error_message: error.message,
    error_stack: error.stack,
    context: context,
    ...additionalInfo,
  });
}

/**
 * Helper function to track timing
 */
export class PerformanceTimer {
  private startTime: number;
  private eventName: string;

  constructor(eventName: string) {
    this.eventName = eventName;
    this.startTime = Date.now();
  }

  end(properties?: AnalyticsProperties): void {
    const duration = Date.now() - this.startTime;

    analytics.track(`${this.eventName}_completed` as AnalyticsEvent, {
      duration_ms: duration,
      ...properties,
    });
  }
}

/**
 * Usage example:
 *
 * // Track simple event
 * analytics.track(AnalyticsEvent.PROP_VIEWED, { player_name: 'Patrick Mahomes' });
 *
 * // Track screen view
 * analytics.trackScreenView('HomeScreen');
 *
 * // Track parlay creation
 * analytics.trackParlayCreated(3, 65.4, 'MEDIUM', 'DraftKings Pick 6');
 *
 * // Track performance
 * const timer = new PerformanceTimer('load_props');
 * // ... do work ...
 * timer.end({ prop_count: 50 });
 */
