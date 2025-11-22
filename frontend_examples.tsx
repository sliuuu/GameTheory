/**
 * Example React Components for Geopolitical Market Game Tracker
 * 
 * These are TypeScript/React examples showing the component structure
 * and data flow patterns for the frontend.
 */

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface MarketData {
  Japan: number;
  China: number;
  USA: number;
  Germany: number;
  Taiwan: number;
  USDCNY: number;
  USDJPY: number;
  Gold: number;
  VIX: number;
}

interface Strategy {
  probabilities: number[]; // [Hawk, De-escalate, Stimulus, Military]
  dominantAction: number;
}

interface NashEquilibrium {
  strategies: Strategy[];
  parties: string[];
  actions: string[];
  globalScenario: string;
  date: string;
}

interface BacktestResult {
  date: string;
  predicted_scenario: string;
  actual_risk_off: boolean;
  correct: boolean;
}

// ============================================================================
// EXAMPLE COMPONENT 1: Market Overview Card
// ============================================================================

import React from 'react';

interface MarketCardProps {
  name: string;
  value: number;
  trend: 'up' | 'down' | 'neutral';
  color: string;
}

export const MarketOverviewCard: React.FC<MarketCardProps> = ({ 
  name, 
  value, 
  trend,
  color 
}) => {
  const isPositive = value > 0;
  const textColor = isPositive ? 'text-green-600' : 'text-red-600';
  const bgColor = isPositive ? 'bg-green-50' : 'bg-red-50';
  const icon = isPositive ? '↑' : '↓';
  
  return (
    <div className={`p-4 rounded-lg shadow-md ${bgColor} hover:shadow-lg transition-shadow cursor-pointer`}>
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-gray-700">{name}</h3>
        <span className={`text-xl ${textColor}`}>{icon}</span>
      </div>
      <p className={`text-3xl font-bold ${textColor}`}>
        {isPositive ? '+' : ''}{value.toFixed(2)}%
      </p>
      <div className="mt-2 h-1 bg-gray-200 rounded-full overflow-hidden">
        <div 
          className={`h-full ${isPositive ? 'bg-green-500' : 'bg-red-500'}`}
          style={{ width: `${Math.min(Math.abs(value) * 10, 100)}%` }}
        />
      </div>
    </div>
  );
};

// ============================================================================
// EXAMPLE COMPONENT 2: Prediction Matrix Table
// ============================================================================

interface PredictionMatrixProps {
  equilibrium: NashEquilibrium;
}

export const PredictionMatrix: React.FC<PredictionMatrixProps> = ({ equilibrium }) => {
  const actionColors = ['#EF4444', '#10B981', '#F59E0B', '#7C2D12'];
  const actionLabels = ['Hawk', 'De-escalate', 'Stimulus', 'Military'];
  
  return (
    <div className="overflow-x-auto bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4">Nash Equilibrium Predictions</h2>
      <table className="min-w-full">
        <thead>
          <tr className="border-b-2 border-gray-300">
            <th className="text-left py-3 px-4 font-semibold">Country</th>
            {equilibrium.actions.map((action, idx) => (
              <th key={idx} className="text-center py-3 px-4 font-semibold">
                {action}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {equilibrium.parties.map((party, partyIdx) => {
            const strategy = equilibrium.strategies[partyIdx];
            const maxProb = Math.max(...strategy.probabilities);
            
            return (
              <tr key={party} className="border-b border-gray-200 hover:bg-gray-50">
                <td className="py-3 px-4 font-semibold">{party}</td>
                {strategy.probabilities.map((prob, actionIdx) => {
                  const isDominant = prob === maxProb;
                  const percentage = (prob * 100).toFixed(1);
                  
                  return (
                    <td 
                      key={actionIdx} 
                      className={`py-3 px-4 ${isDominant ? 'bg-blue-50 font-semibold' : ''}`}
                    >
                      <div className="flex items-center space-x-2">
                        <div className="flex-1">
                          <div className="flex justify-between text-sm mb-1">
                            <span>{percentage}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="h-2 rounded-full transition-all"
                              style={{
                                width: `${percentage}%`,
                                backgroundColor: actionColors[actionIdx]
                              }}
                            />
                          </div>
                        </div>
                        {isDominant && (
                          <span className="text-blue-600 text-xs">★</span>
                        )}
                      </div>
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
        <p className="text-sm text-gray-600">
          <span className="font-semibold">Most Likely Scenario:</span>{' '}
          <span className="text-blue-700 font-bold">{equilibrium.globalScenario}</span>
        </p>
      </div>
    </div>
  );
};

// ============================================================================
// EXAMPLE COMPONENT 3: Dashboard (Main View)
// ============================================================================

interface DashboardProps {
  marketData: MarketData | null;
  predictions: NashEquilibrium | null;
  loading: boolean;
  currentDate: Date;
  onDateChange: (date: Date) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({
  marketData,
  predictions,
  loading,
  currentDate,
  onDateChange
}) => {
  const marketCards = [
    { name: 'Japan', key: 'Japan' as keyof MarketData, color: '#BC002D' },
    { name: 'China', key: 'China' as keyof MarketData, color: '#DE2910' },
    { name: 'USA', key: 'USA' as keyof MarketData, color: '#002868' },
    { name: 'Germany', key: 'Germany' as keyof MarketData, color: '#000000' },
    { name: 'Taiwan', key: 'Taiwan' as keyof MarketData, color: '#000095' },
    { name: 'USD/CNY', key: 'USDCNY' as keyof MarketData, color: '#6B7280' },
    { name: 'USD/JPY', key: 'USDJPY' as keyof MarketData, color: '#6B7280' },
    { name: 'Gold', key: 'Gold' as keyof MarketData, color: '#F59E0B' },
    { name: 'VIX', key: 'VIX' as keyof MarketData, color: '#EF4444' },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Date Selector */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Geopolitical Market Game Tracker</h1>
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium">Analysis Date:</label>
          <input
            type="date"
            value={currentDate.toISOString().split('T')[0]}
            onChange={(e) => onDateChange(new Date(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Market Data Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-3 gap-4">
        {marketData && marketCards.map(({ name, key, color }) => (
          <MarketOverviewCard
            key={key}
            name={name}
            value={marketData[key] * 100} // Convert to percentage
            trend={marketData[key] > 0 ? 'up' : 'down'}
            color={color}
          />
        ))}
      </div>

      {/* Predictions Panel */}
      {predictions && (
        <PredictionMatrix equilibrium={predictions} />
      )}

      {/* Market Context Summary */}
      {marketData && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-semibold mb-2">Market Context (14-day returns)</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
            {Object.entries(marketData).map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="text-gray-600">{key}:</span>
                <span className={value > 0 ? 'text-green-600' : 'text-red-600'}>
                  {value > 0 ? '+' : ''}{(value * 100).toFixed(2)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// ============================================================================
// EXAMPLE COMPONENT 4: Backtest Results Table
// ============================================================================

interface BacktestViewProps {
  results: BacktestResult[];
  summary: {
    accuracy: number;
    totalWeeks: number;
    correctPredictions: number;
  };
}

export const BacktestView: React.FC<BacktestViewProps> = ({ results, summary }) => {
  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm font-medium text-gray-600">Overall Accuracy</h3>
          <p className="text-3xl font-bold text-blue-600 mt-2">
            {(summary.accuracy * 100).toFixed(1)}%
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm font-medium text-gray-600">Total Weeks</h3>
          <p className="text-3xl font-bold text-gray-800 mt-2">
            {summary.totalWeeks}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm font-medium text-gray-600">Correct Predictions</h3>
          <p className="text-3xl font-bold text-green-600 mt-2">
            {summary.correctPredictions}
          </p>
        </div>
      </div>

      {/* Results Table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Predicted Scenario
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Actual Risk-Off
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Result
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {results.map((result, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(result.date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {result.predicted_scenario}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {result.actual_risk_off ? (
                      <span className="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                        Risk-Off
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                        Risk-On
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {result.correct ? (
                      <span className="text-green-600 font-semibold">✓ Correct</span>
                    ) : (
                      <span className="text-red-600 font-semibold">✗ Wrong</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// EXAMPLE: React Query Hook for Data Fetching
// ============================================================================

import { useQuery, useMutation } from '@tanstack/react-query';

export const useMarketPredictions = (date: Date) => {
  return useQuery({
    queryKey: ['predictions', date.toISOString()],
    queryFn: async () => {
      const response = await fetch(`/api/predictions?date=${date.toISOString()}`);
      if (!response.ok) throw new Error('Failed to fetch predictions');
      return response.json() as Promise<NashEquilibrium>;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useBacktest = () => {
  return useMutation({
    mutationFn: async ({ start, end }: { start: Date; end: Date }) => {
      const response = await fetch('/api/backtest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start_date: start.toISOString().split('T')[0],
          end_date: end.toISOString().split('T')[0],
        }),
      });
      if (!response.ok) throw new Error('Backtest failed');
      return response.json();
    },
  });
};



