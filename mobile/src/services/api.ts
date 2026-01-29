/**
 * API Service for connecting to FastAPI backend
 */

import axios, { AxiosInstance } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { PropAnalysis, Parlay, LineAdjustmentRequest, LineAdjustmentResponse } from '../types';

// API Configuration
const API_BASE_URL = __DEV__
  ? 'http://192.168.1.207:8000'  // Development - local network IP
  : 'https://your-production-api.com';  // Production

const API_KEY = 'dev_test_key_12345';  // TODO: Store securely in production

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
      },
    });

    // Request interceptor for debugging
    this.client.interceptors.request.use(
      (config) => {
        console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('[API] Request error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for debugging
    this.client.interceptors.response.use(
      (response) => {
        console.log(`[API] Response ${response.status} from ${response.config.url}`);
        return response;
      },
      (error) => {
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
