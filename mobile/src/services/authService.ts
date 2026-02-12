/**
 * Authentication service: JWT storage, login/register flows, token refresh.
 * Uses AsyncStorage for token persistence (swap to expo-secure-store for production).
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import { AuthTokens, UserProfile } from '../types';

const API_BASE_URL = __DEV__
  ? 'http://192.168.1.207:8000'
  : 'https://your-production-api.com';

const TOKEN_KEY = 'auth_tokens';

class AuthService {
  private tokens: AuthTokens | null = null;

  /** Load tokens from storage on app start. */
  async init(): Promise<AuthTokens | null> {
    try {
      const stored = await AsyncStorage.getItem(TOKEN_KEY);
      if (stored) {
        this.tokens = JSON.parse(stored);
      }
    } catch {
      this.tokens = null;
    }
    return this.tokens;
  }

  /** Get the current access token for API calls. */
  getAccessToken(): string | null {
    return this.tokens?.access_token ?? null;
  }

  /** Register a new user. */
  async register(email: string, password: string, displayName?: string): Promise<AuthTokens> {
    const resp = await axios.post<AuthTokens>(`${API_BASE_URL}/api/auth/register`, {
      email,
      password,
      display_name: displayName,
    });
    this.tokens = resp.data;
    await this.persistTokens();
    return resp.data;
  }

  /** Login with email + password. */
  async login(email: string, password: string): Promise<AuthTokens> {
    const form = new URLSearchParams();
    form.append('username', email);
    form.append('password', password);

    const resp = await axios.post<AuthTokens>(`${API_BASE_URL}/api/auth/login`, form.toString(), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    this.tokens = resp.data;
    await this.persistTokens();
    return resp.data;
  }

  /** Refresh the access token using the refresh token. */
  async refresh(): Promise<AuthTokens | null> {
    if (!this.tokens?.refresh_token) return null;

    try {
      const resp = await axios.post<AuthTokens>(`${API_BASE_URL}/api/auth/refresh`, {
        refresh_token: this.tokens.refresh_token,
      });
      this.tokens = resp.data;
      await this.persistTokens();
      return resp.data;
    } catch {
      // Refresh failed — force re-login
      await this.logout();
      return null;
    }
  }

  /** Get current user profile. */
  async getProfile(): Promise<UserProfile> {
    const resp = await axios.get<UserProfile>(`${API_BASE_URL}/api/auth/me`, {
      headers: { Authorization: `Bearer ${this.tokens?.access_token}` },
    });
    return resp.data;
  }

  /** Clear tokens and log out. */
  async logout(): Promise<void> {
    this.tokens = null;
    await AsyncStorage.removeItem(TOKEN_KEY);
  }

  /** Check if user is authenticated (has tokens). */
  isAuthenticated(): boolean {
    return this.tokens?.access_token != null;
  }

  private async persistTokens(): Promise<void> {
    if (this.tokens) {
      await AsyncStorage.setItem(TOKEN_KEY, JSON.stringify(this.tokens));
    }
  }
}

export const authService = new AuthService();
