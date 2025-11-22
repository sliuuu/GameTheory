import axios from 'axios';
import type { NashEquilibrium, BacktestResult, BacktestSummary, SensitivityResult } from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 120 seconds timeout for market data fetching
});

export const marketDataApi = {
  getMarketData: async (date?: string, days: number = 14) => {
    const response = await api.get('/market-data', {
      params: { date, days },
    });
    return response.data;
  },
};

export const predictionsApi = {
  getPredictions: async (date?: string, useOptimized: boolean = false): Promise<NashEquilibrium> => {
    const response = await api.get('/predictions', {
      params: { date, use_optimized: useOptimized },
    });
    return response.data;
  },
};

export const backtestApi = {
  startBacktest: async (startDate: string, endDate: string, freq: string = 'W-FRI') => {
    const response = await api.post('/backtest', {
      start_date: startDate,
      end_date: endDate,
      freq,
    });
    return response.data as {
      job_id: string;
      status: string;
      message: string;
    };
  },
  getJobStatus: async (jobId: string) => {
    const response = await api.get(`/backtest/status/${jobId}`);
    return response.data as {
      job_id: string;
      status: 'pending' | 'running' | 'completed' | 'failed';
      progress: number;
      current_step: string;
      current_step_num: number;
      total_steps: number;
      result?: {
        results: BacktestResult[];
        summary: BacktestSummary;
        total_weeks: number;
        accuracy: number;
      };
      error?: string;
    };
  },
  // Legacy method for backward compatibility
  runBacktest: async (startDate: string, endDate: string, freq: string = 'W-FRI') => {
    const jobResponse = await backtestApi.startBacktest(startDate, endDate, freq);
    // Poll until complete (for synchronous behavior)
    return new Promise((resolve, reject) => {
      const pollInterval = setInterval(async () => {
        try {
          const status = await backtestApi.getJobStatus(jobResponse.job_id);
          if (status.status === 'completed' && status.result) {
            clearInterval(pollInterval);
            resolve(status.result);
          } else if (status.status === 'failed') {
            clearInterval(pollInterval);
            reject(new Error(status.error || 'Backtest failed'));
          }
        } catch (error) {
          clearInterval(pollInterval);
          reject(error);
        }
      }, 1000);
    });
  },
};

export const sensitivityApi = {
  runAnalysis: async (noiseLevels?: number[], nRuns: number = 100) => {
    const response = await api.post('/sensitivity-analysis', {
      noise_levels: noiseLevels,
      n_runs: nRuns,
    });
    return response.data as {
      results: SensitivityResult[];
    };
  },
};

export const cacheApi = {
  getStats: async () => {
    const response = await api.get('/cache/stats');
    return response.data;
  },
  clearCache: async (olderThanDays?: number) => {
    const response = await api.delete('/cache', {
      params: { older_than_days: olderThanDays },
    });
    return response.data;
  },
};

export interface NewsSource {
  name: string;
  url: string;
}

export interface GeopoliticalEvent {
  date: string;
  type: string;
  title: string;
  description: string;
  impact: string;
  countries: string[];
  market_impact: string;
  relevance_score: number;
  news_sources?: NewsSource[];
}

export interface GeopoliticalEventsResponse {
  date: string;
  events: GeopoliticalEvent[];
}

export const geopoliticalEventsApi = {
  getEvents: async (date?: string): Promise<GeopoliticalEventsResponse> => {
    const response = await api.get('/geopolitical-events', {
      params: { date },
    });
    return response.data;
  },
};

export default api;

