import { useState } from 'react';
import { format } from 'date-fns';
import { useAppStore } from '../../store/appStore';
import { sensitivityApi } from '../../api/client';
import { useQuery } from '@tanstack/react-query';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';

const SensitivityView = () => {
  const { currentDate } = useAppStore();
  const [nRuns, setNRuns] = useState(100);
  const [noiseLevels, setNoiseLevels] = useState<number[]>([]);
  const [customNoiseLevels, setCustomNoiseLevels] = useState('');

  // Generate default noise levels (0.0 to 1.0 in 11 steps)
  const defaultNoiseLevels = Array.from({ length: 11 }, (_, i) => i * 0.1);

  const { data: sensitivityData, isLoading, error, refetch } = useQuery({
    queryKey: ['sensitivity', currentDate, nRuns, noiseLevels.length > 0 ? noiseLevels : defaultNoiseLevels],
    queryFn: () => sensitivityApi.runAnalysis(
      noiseLevels.length > 0 ? noiseLevels : undefined,
      nRuns
    ),
    enabled: false, // Don't auto-run
  });

  const handleRunAnalysis = () => {
    refetch();
  };

  const handleCustomNoiseLevels = (value: string) => {
    setCustomNoiseLevels(value);
    try {
      const levels = value.split(',').map(s => parseFloat(s.trim())).filter(n => !isNaN(n));
      if (levels.length > 0) {
        setNoiseLevels(levels);
      } else {
        setNoiseLevels([]);
      }
    } catch {
      setNoiseLevels([]);
    }
  };

  // Prepare chart data
  const chartData = sensitivityData?.results?.map((result: any) => ({
    noise: result.noise_level,
    globalHawk: (result.Global_Hawk_Scenario || 0) * 100,
    globalDeescalate: (result.Global_Deescalate_Scenario || 0) * 100,
    japanHawk: (result.Japan_Hawk || 0) * 100,
    chinaHawk: (result.China_Hawk || 0) * 100,
    usaHawk: (result.USA_Hawk || 0) * 100,
  })) || [];

  // Calculate robustness metrics
  const robustnessMetrics = sensitivityData?.results ? (() => {
    const results = sensitivityData.results;
    const baseline = results[0];
    
    // Find where probabilities drop below 50%
    const hawkStable = results.filter((r: any) => (r.Global_Hawk_Scenario || 0) > 0.5);
    const deescStable = results.filter((r: any) => (r.Global_Deescalate_Scenario || 0) > 0.5);
    
    const maxNoiseHawk = hawkStable.length > 0 ? Math.max(...hawkStable.map((r: any) => r.noise_level)) : 0;
    const maxNoiseDeesc = deescStable.length > 0 ? Math.max(...deescStable.map((r: any) => r.noise_level)) : 0;
    
    return {
      baselineHawk: (baseline?.Global_Hawk_Scenario || 0) * 100,
      baselineDeescalate: (baseline?.Global_Deescalate_Scenario || 0) * 100,
      maxNoiseHawk,
      maxNoiseDeesc,
      isRobust: maxNoiseHawk > 0.3 || maxNoiseDeesc > 0.3,
    };
  })() : null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold mb-2">Sensitivity Analysis</h2>
        <p className="text-gray-600 text-sm">
          Test model robustness by analyzing how predictions change with varying levels of market data uncertainty
        </p>
        <p className="text-xs text-gray-500 mt-2">
          Analysis Date: {format(currentDate, 'MMMM dd, yyyy')}
        </p>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Monte Carlo Runs
            </label>
            <input
              type="number"
              min="10"
              max="500"
              value={nRuns}
              onChange={(e) => setNRuns(parseInt(e.target.value) || 100)}
              disabled={isLoading}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            <p className="text-xs text-gray-500 mt-1">More runs = more accurate but slower (10-500)</p>
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Noise Levels (optional, comma-separated)
            </label>
            <input
              type="text"
              value={customNoiseLevels}
              onChange={(e) => handleCustomNoiseLevels(e.target.value)}
              placeholder="Leave empty for default (0.0 to 1.0 in 11 steps)"
              disabled={isLoading}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            <p className="text-xs text-gray-500 mt-1">
              Default: {defaultNoiseLevels.map(n => n.toFixed(1)).join(', ')}
            </p>
          </div>
        </div>
        <div className="mt-4">
          <button
            onClick={handleRunAnalysis}
            disabled={isLoading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Running Analysis...
              </>
            ) : (
              <>
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                Run Sensitivity Analysis
              </>
            )}
          </button>
        </div>
      </div>

      {/* Robustness Metrics */}
      {robustnessMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
            <h3 className="text-sm font-medium text-gray-600 mb-1">Baseline Hawk</h3>
            <p className="text-3xl font-bold text-blue-600">
              {robustnessMetrics.baselineHawk.toFixed(1)}%
            </p>
            <p className="text-xs text-gray-500 mt-1">At zero noise</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
            <h3 className="text-sm font-medium text-gray-600 mb-1">Baseline De-escalate</h3>
            <p className="text-3xl font-bold text-green-600">
              {robustnessMetrics.baselineDeescalate.toFixed(1)}%
            </p>
            <p className="text-xs text-gray-500 mt-1">At zero noise</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-orange-500">
            <h3 className="text-sm font-medium text-gray-600 mb-1">Hawk Robustness</h3>
            <p className="text-3xl font-bold text-orange-600">
              {robustnessMetrics.maxNoiseHawk.toFixed(2)}
            </p>
            <p className="text-xs text-gray-500 mt-1">Max noise level (&gt;50%)</p>
          </div>
          <div className={`bg-white rounded-lg shadow-md p-6 border-l-4 ${robustnessMetrics.isRobust ? 'border-green-500' : 'border-yellow-500'}`}>
            <h3 className="text-sm font-medium text-gray-600 mb-1">Overall Robustness</h3>
            <p className={`text-3xl font-bold ${robustnessMetrics.isRobust ? 'text-green-600' : 'text-yellow-600'}`}>
              {robustnessMetrics.isRobust ? '✓ Robust' : '⚠ Sensitive'}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {robustnessMetrics.isRobust 
                ? 'Predictions stable to noise' 
                : 'Predictions sensitive to noise'}
            </p>
          </div>
        </div>
      )}

      {/* Charts */}
      {sensitivityData && (
        <div className="space-y-6">
          {/* Global Scenario Probabilities */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold mb-4">Global Scenario Probabilities vs Noise Level</h3>
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorHawk" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EF4444" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#EF4444" stopOpacity={0.1}/>
                  </linearGradient>
                  <linearGradient id="colorDeescalate" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="noise" 
                  label={{ value: 'Noise Level', position: 'insideBottom', offset: -5 }}
                />
                <YAxis 
                  label={{ value: 'Probability (%)', angle: -90, position: 'insideLeft' }}
                  domain={[0, 100]}
                />
                <Tooltip 
                  formatter={(value: number) => `${value.toFixed(1)}%`}
                  labelFormatter={(label) => `Noise Level: ${label}`}
                />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="globalHawk" 
                  stroke="#EF4444" 
                  fillOpacity={1} 
                  fill="url(#colorHawk)"
                  name="Global Hawk Scenario"
                />
                <Area 
                  type="monotone" 
                  dataKey="globalDeescalate" 
                  stroke="#10B981" 
                  fillOpacity={1} 
                  fill="url(#colorDeescalate)"
                  name="Global De-escalate Scenario"
                />
                <Line 
                  type="monotone" 
                  dataKey="globalHawk" 
                  stroke="#EF4444" 
                  strokeWidth={2}
                  dot={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="globalDeescalate" 
                  stroke="#10B981" 
                  strokeWidth={2}
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Country-Level Hawk Probabilities */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold mb-4">Country-Level Hawk Probability vs Noise Level</h3>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="noise" 
                  label={{ value: 'Noise Level', position: 'insideBottom', offset: -5 }}
                />
                <YAxis 
                  label={{ value: 'Hawk Probability (%)', angle: -90, position: 'insideLeft' }}
                  domain={[0, 100]}
                />
                <Tooltip 
                  formatter={(value: number) => `${value.toFixed(1)}%`}
                  labelFormatter={(label) => `Noise Level: ${label}`}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="japanHawk" 
                  stroke="#BC002D" 
                  strokeWidth={2}
                  name="Japan"
                  dot={{ r: 3 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="chinaHawk" 
                  stroke="#DE2910" 
                  strokeWidth={2}
                  name="China"
                  dot={{ r: 3 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="usaHawk" 
                  stroke="#002868" 
                  strokeWidth={2}
                  name="USA"
                  dot={{ r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Insights */}
          {robustnessMetrics && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold mb-4">Key Insights</h3>
              <div className="space-y-3">
                {robustnessMetrics.baselineHawk > 50 ? (
                  <div className="p-4 bg-red-50 border-l-4 border-red-400 rounded">
                    <h4 className="font-semibold text-red-800 mb-2">🦅 Global Hawk Scenario Dominant</h4>
                    <p className="text-sm text-red-700">
                      Baseline prediction shows <strong>{(robustnessMetrics.baselineHawk).toFixed(1)}%</strong> probability of global hawk scenario.
                      {robustnessMetrics.maxNoiseHawk > 0.3 ? (
                        <span> This prediction remains robust (stays above 50%) up to noise level <strong>{robustnessMetrics.maxNoiseHawk.toFixed(2)}</strong>, indicating high confidence.</span>
                      ) : (
                        <span> However, this prediction is sensitive to noise (drops below 50% at low noise levels), suggesting lower confidence.</span>
                      )}
                    </p>
                  </div>
                ) : robustnessMetrics.baselineDeescalate > 50 ? (
                  <div className="p-4 bg-green-50 border-l-4 border-green-400 rounded">
                    <h4 className="font-semibold text-green-800 mb-2">🕊️ Global De-escalate Scenario Dominant</h4>
                    <p className="text-sm text-green-700">
                      Baseline prediction shows <strong>{(robustnessMetrics.baselineDeescalate).toFixed(1)}%</strong> probability of global de-escalate scenario.
                      {robustnessMetrics.maxNoiseDeesc > 0.3 ? (
                        <span> This prediction remains robust (stays above 50%) up to noise level <strong>{robustnessMetrics.maxNoiseDeesc.toFixed(2)}</strong>, indicating high confidence.</span>
                      ) : (
                        <span> However, this prediction is sensitive to noise (drops below 50% at low noise levels), suggesting lower confidence.</span>
                      )}
                    </p>
                  </div>
                ) : (
                  <div className="p-4 bg-yellow-50 border-l-4 border-yellow-400 rounded">
                    <h4 className="font-semibold text-yellow-800 mb-2">⚠️ Mixed Signals</h4>
                    <p className="text-sm text-yellow-700">
                      Baseline predictions show mixed signals with no clear dominant scenario. 
                      Hawk probability: <strong>{(robustnessMetrics.baselineHawk).toFixed(1)}%</strong>, 
                      De-escalate probability: <strong>{(robustnessMetrics.baselineDeescalate).toFixed(1)}%</strong>.
                      Monitor market conditions closely as the situation is uncertain.
                    </p>
                  </div>
                )}
                
                <div className="p-4 bg-blue-50 border-l-4 border-blue-400 rounded">
                  <h4 className="font-semibold text-blue-800 mb-2">📊 Interpretation Guide</h4>
                  <ul className="text-sm text-blue-700 space-y-1 list-disc list-inside">
                    <li><strong>Noise Level:</strong> Represents uncertainty in market data (0 = no noise, 1 = high noise)</li>
                    <li><strong>Robustness:</strong> Higher noise tolerance (&gt;0.3) indicates more reliable predictions</li>
                    <li><strong>Probability Drop:</strong> When probabilities fall below 50%, the scenario is no longer dominant</li>
                    <li><strong>Recommendation:</strong> {robustnessMetrics.isRobust 
                      ? 'High confidence - predictions are stable to data uncertainty'
                      : 'Low confidence - predictions are sensitive, monitor market data closely'}
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <p className="text-sm text-red-700 mt-1">{error.message || 'An error occurred during sensitivity analysis'}</p>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!sensitivityData && !isLoading && !error && (
        <div className="bg-gray-50 rounded-lg p-12 text-center">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-gray-900">No Sensitivity Analysis Results</h3>
          <p className="mt-2 text-sm text-gray-600">
            Configure the analysis parameters and click "Run Sensitivity Analysis" to test model robustness
          </p>
        </div>
      )}
    </div>
  );
};

export default SensitivityView;

