/**
 * Player service: search, card data, projections.
 */

import axios from 'axios';
import { Player, PlayerProjection, BookOddsEntry, BestPrices, LineMovementEntry } from '../types';
import { authService } from './authService';

const API_BASE_URL = __DEV__
  ? 'http://192.168.1.207:8000'
  : 'https://your-production-api.com';

function authHeaders() {
  const token = authService.getAccessToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

class PlayerService {
  /** Search players by name with optional filters. */
  async search(query: string, position?: string, team?: string, limit = 20): Promise<Player[]> {
    const resp = await axios.get<Player[]>(`${API_BASE_URL}/api/players/search`, {
      params: { q: query, position, team, limit },
    });
    return resp.data;
  }

  /** Get a single player by ID. */
  async getById(playerId: number): Promise<Player> {
    const resp = await axios.get<Player>(`${API_BASE_URL}/api/players/${playerId}`);
    return resp.data;
  }

  /** Get projections for a player. */
  async getProjections(playerId: number, week?: number): Promise<PlayerProjection[]> {
    const resp = await axios.get<PlayerProjection[]>(
      `${API_BASE_URL}/api/players/${playerId}/projections`,
      { params: { week } },
    );
    return resp.data;
  }

  /** Get all book odds for a player. */
  async getOdds(playerId: number, week?: number): Promise<BookOddsEntry[]> {
    const resp = await axios.get<BookOddsEntry[]>(
      `${API_BASE_URL}/api/odds/player/${playerId}`,
      { params: { week } },
    );
    return resp.data;
  }

  /** Get best over/under prices across all books. */
  async getBestPrices(playerId: number, statType: string, week: number): Promise<BestPrices> {
    const resp = await axios.get<BestPrices>(`${API_BASE_URL}/api/odds/best-prices`, {
      params: { player_id: playerId, stat_type: statType, week },
    });
    return resp.data;
  }

  /** Get line movement history. */
  async getLineMovement(playerId: number, statType: string, week: number): Promise<LineMovementEntry[]> {
    const resp = await axios.get<LineMovementEntry[]>(
      `${API_BASE_URL}/api/odds/movement/${playerId}`,
      { params: { stat_type: statType, week } },
    );
    return resp.data;
  }

  /** Sync a team roster from ESPN (requires auth). */
  async syncRoster(teamAbbr: string): Promise<{ team: string; players_synced: number }> {
    const resp = await axios.post(
      `${API_BASE_URL}/api/players/sync/${teamAbbr}`,
      {},
      { headers: authHeaders() },
    );
    return resp.data;
  }
}

export const playerService = new PlayerService();
