/**
 * API Service for connecting to FastAPI backend
 */

import axios, { AxiosInstance } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { PropAnalysis, Parlay, LineAdjustmentRequest, LineAdjustmentResponse } from '../types';
import { authService } from './authService';

// API Configuration
const API_BASE_URL = __DEV__
  ? 'http://192.168.1.207:8000'  // Development - local network IP
  : 'https://your-production-api.com';  // Production

const API_KEY = 'dev_test_key_12345';  // Fallback for non-auth endpoints

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 300000,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
      },
    });
    console.log(`[API] Service initialized with timeout: ${this.client.defaults.timeout}ms`);

    // Request interceptor: attach JWT if available, log request
    this.client.interceptors.request.use(
      (config) => {
        const token = authService.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('[API] Request error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor: auto-refresh on 401
    this.client.interceptors.response.use(
      (response) => {
        console.log(`[API] Response ${response.status} from ${response.config.url}`);
        return response;
      },
      async (error) => {
        const originalRequest = error.config;
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          const refreshed = await authService.refresh();
          if (refreshed) {
            originalRequest.headers.Authorization = `Bearer ${refreshed.access_token}`;
            return this.client(originalRequest);
          }
        }
        console.error('[API] Response error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Get analyzed props for a specific week
   */
  async getProps(params: {
    week: number;
    min_confidence?: number;
    max_confidence?: number;
    teams?: string;
    positions?: string;
    stat_type?: string;
    bet_type?: 'OVER' | 'UNDER';
    limit?: number;
    preferred_book?: string;
  }): Promise<PropAnalysis[]> {
    try {
      const response = await this.client.get<PropAnalysis[]>('/api/props/analyze', {
        params,
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching props:', error);
      throw error;
    }
  }

  /**
   * Get top N props by confidence
   */
  async getTopProps(params: {
    week: number;
    limit?: number;
    bet_type?: 'OVER' | 'UNDER';
  }): Promise<PropAnalysis[]> {
    try {
      const response = await this.client.get<PropAnalysis[]>('/api/props/top', {
        params,
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching top props:', error);
      throw error;
    }
  }

  /**
   * Get props for a specific team
   */
  async getTeamProps(params: {
    team_abbr: string;
    week: number;
    limit?: number;
  }): Promise<PropAnalysis[]> {
    try {
      const response = await this.client.get<PropAnalysis[]>(
        `/api/props/team/${params.team_abbr}`,
        {
          params: {
            week: params.week,
            limit: params.limit,
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching team props:', error);
      throw error;
    }
  }

  /**
   * Adjust line and recalculate confidence (for Pick 6)
   */
  async adjustLine(request: LineAdjustmentRequest): Promise<LineAdjustmentResponse> {
    try {
      const response = await this.client.post<LineAdjustmentResponse>(
        '/api/props/adjust-line',
        request
      );
      return response.data;
    } catch (error) {
      console.error('Error adjusting line:', error);
      throw error;
    }
  }

  /**
   * Get pre-built parlays for a week
   */
  async getPrebuiltParlays(params: {
    week: number;
    min_confidence?: number;
    team?: string;
  }): Promise<Parlay[]> {
    try {
      const response = await this.client.get<Parlay[]>('/api/parlays/prebuilt', {
        params,
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching parlays:', error);
      throw error;
    }
  }

  /**
   * Get historical stat values for a player (game-by-game)
   */
  async getPlayerHistory(params: {
    player_name: string;
    stat_type: string;
    week: number;
    line?: number;
  }): Promise<{
    values: number[];
    week_labels?: string[];
    average: number | null;
    total_games: number;
    line?: number;
    over_count?: number;
    under_count?: number;
    hit_rate_pct?: number;
    message?: string;
  }> {
    try {
      const response = await this.client.get('/api/props/player-history', {
        params,
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching player history:', error);
      return { values: [], average: null, total_games: 0 };
    }
  }


  /**
   * Get raw betting odds for a player/stat
   */
  async getOdds(params: {
    week: number;
    player_name: string;
    stat_type: string;
  }): Promise<import('../types').RawBookOdds[]> {
    try {
      const response = await this.client.get('/api/props/odds', {
        params,
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching odds:', error);
      return [];
    }
  }

  /**
   * Get recent news for a player
   */
  async getPlayerNews(player_name: string, limit: number = 5): Promise<{
    title: string;
    url: string;
    source: string;
    published_at: string;
  }[]> {
    try {
      const response = await this.client.get(`/api/props/news/${encodeURIComponent(player_name)}`, {
        params: { limit },
        timeout: 15000 // news fetches Google RSS server-side, needs headroom
      });
      return response.data.articles || [];
    } catch (error) {
      console.error('Error fetching player news:', error);
      return [];
    }
  }


  /**
   * Grade a user-constructed parlay
   */
  async gradeParlay(legs: import('../types').ParlayLeg[]): Promise<import('../types').ParlayGradeResponse> {
    try {
      // Map frontend legs to backend request format if needed
      // The frontend ParlayLeg is compatible with ParlayGradeRequest mostly, but check fields
      const requestLegs = legs.map(leg => ({
        player_name: leg.player_name,
        team: leg.team,
        opponent: leg.opponent,
        stat_type: leg.stat_type,
        bet_type: leg.bet_type,
        line: leg.line,
        confidence: leg.confidence,
        position: 'UNKNOWN' // Frontend ParlayLeg might not have position, backend defaults to UNKNOWN
      }));

      const response = await this.client.post<import('../types').ParlayGradeResponse>(
        '/api/parlays/grade',
        requestLegs
      );
      return response.data;
    } catch (error) {
      console.error('Error grading parlay:', error);
      throw error;
    }
  }

  /**
   * Check API health
   */
  async checkHealth(): Promise<{ status: string; service: string; version: string }> {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const apiService = new ApiService();
