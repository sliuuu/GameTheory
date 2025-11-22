import { useState, useEffect, useRef } from 'react';
import { format, subMonths, subWeeks } from 'date-fns';
import { backtestApi } from '../../api/client';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

const JOB_STORAGE_KEY = 'backtest_job_id';
const COLORS = ['#10B981', '#EF4444', '#F59E0B', '#3B82F6'];

const BacktestView = () => {
  // Default to past dates (3 months ago to 1 week ago)
  const defaultEnd = subWeeks(new Date(), 1);
  const defaultStart = subMonths(defaultEnd, 3);
  const [startDate, setStartDate] = useState(format(defaultStart, 'yyyy-MM-dd'));
  const [endDate, setEndDate] = useState(format(defaultEnd, 'yyyy-MM-dd'));
  const [freq, setFreq] = useState<'W-FRI' | 'D' | 'M'>('W-FRI');
  const [jobId, setJobId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('');
  const [jobStatus, setJobStatus] = useState<'pending' | 'running' | 'completed' | 'failed' | null>(null);
  const [backtestData, setBacktestData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const pollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const notificationPermissionRef = useRef<NotificationPermission | null>(null);

  // Request notification permission on mount
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission().then((permission) => {
        notificationPermissionRef.current = permission;
      });
    } else if ('Notification' in window) {
      notificationPermissionRef.current = Notification.permission;
    }

    // Check for existing job on mount
    const storedJobId = localStorage.getItem(JOB_STORAGE_KEY);
    if (storedJobId) {
      setJobId(storedJobId);
      checkJobStatus(storedJobId);
    }

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  const showNotification = (title: string, body: string) => {
    if ('Notification' in window && notificationPermissionRef.current === 'granted') {
      new Notification(title, {
        body,
        icon: '/favicon.ico',
      });
    }
  };

  const checkJobStatus = async (id: string) => {
    try {
      const status = await backtestApi.getJobStatus(id);
      setJobStatus(status.status);
      setProgress(status.progress);
      setCurrentStep(status.current_step || '');

      if (status.status === 'completed' && status.result) {
        setBacktestData(status.result);
        setJobStatus('completed');
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
        localStorage.removeItem(JOB_STORAGE_KEY);
        showNotification(
          'Backtest Complete',
          `Analysis finished with ${(status.result.accuracy * 100).toFixed(1)}% accuracy over ${status.result.total_weeks} weeks`
        );
      } else if (status.status === 'failed') {
        setError(status.error || 'Backtest failed');
        setJobStatus('failed');
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
        localStorage.removeItem(JOB_STORAGE_KEY);
        showNotification('Backtest Failed', status.error || 'An error occurred during analysis');
      } else if (status.status === 'running' || status.status === 'pending') {
        // Continue polling
        if (!pollIntervalRef.current) {
          pollIntervalRef.current = setInterval(() => checkJobStatus(id), 2000);
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to check job status');
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    }
  };

  const handleRunBacktest = async () => {
    setError(null);
    setBacktestData(null);
    setProgress(0);
    setCurrentStep('');
    setJobStatus(null);

    try {
      const response = await backtestApi.startBacktest(startDate, endDate, freq);
      setJobId(response.job_id);
      setJobStatus('pending');
      localStorage.setItem(JOB_STORAGE_KEY, response.job_id);
      
      // Start polling
      checkJobStatus(response.job_id);
    } catch (err: any) {
      setError(err.message || 'Failed to start backtest');
    }
  };

  const handleCancel = () => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
    setJobStatus(null);
    setProgress(0);
    setCurrentStep('');
    localStorage.removeItem(JOB_STORAGE_KEY);
  };

  // Prepare chart data
  const chartData = backtestData?.results?.map((result: any) => ({
    date: format(new Date(result.date), 'MMM dd'),
    accuracy: result.hawk_dominant === result.actual_risk_off_next_week ? 1 : 0,
    predicted: result.hawk_dominant ? 'Hawk' : 'Dove',
    actual: result.actual_risk_off_next_week ? 'Risk-Off' : 'Risk-On',
  })) || [];

  // Prepare scenario distribution over time
  const scenarioData = backtestData?.results?.map((result: any) => ({
    date: format(new Date(result.date), 'MMM dd'),
    hawk: result.hawk_dominant ? 1 : 0,
    dove: result.hawk_dominant ? 0 : 1,
  })) || [];

  // Accuracy distribution for pie chart
  const accuracyData = backtestData ? [
    { name: 'Correct', value: backtestData.results.filter((r: any) => r.hawk_dominant === r.actual_risk_off_next_week).length },
    { name: 'Incorrect', value: backtestData.results.filter((r: any) => r.hawk_dominant !== r.actual_risk_off_next_week).length },
  ] : [];

  const isRunning = jobStatus === 'running' || jobStatus === 'pending';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold mb-2">Backtest Analysis</h2>
        <p className="text-gray-600 text-sm">
          Evaluate model performance by comparing predictions against historical market outcomes
        </p>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Start Date
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              disabled={isRunning}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              End Date
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              disabled={isRunning}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Frequency
            </label>
            <select
              value={freq}
              onChange={(e) => setFreq(e.target.value as 'W-FRI' | 'D' | 'M')}
              disabled={isRunning}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              <option value="W-FRI">Weekly (Friday)</option>
              <option value="D">Daily</option>
              <option value="M">Monthly</option>
            </select>
          </div>
          <div className="flex items-end gap-2">
            <button
              onClick={handleRunBacktest}
              disabled={isRunning}
              className="flex-1 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {isRunning ? 'Running...' : 'Run Backtest'}
            </button>
            {isRunning && (
              <button
                onClick={handleCancel}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                title="Cancel backtest"
              >
                ✕
              </button>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        {isRunning && (
          <div className="mt-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">
                {currentStep || 'Initializing...'}
              </span>
              <span className="text-sm font-medium text-gray-700">
                {Math.round(progress * 100)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-blue-600 h-3 rounded-full transition-all duration-300 ease-out"
                style={{ width: `${progress * 100}%` }}
              />
            </div>
            {jobId && (
              <p className="text-xs text-gray-500 mt-2">
                Job ID: {jobId.substring(0, 8)}... • You can navigate away and return later
              </p>
            )}
          </div>
        )}
      </div>

      {/* Summary Cards */}
      {backtestData?.summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
            <h3 className="text-sm font-medium text-gray-600 mb-1">Total Weeks</h3>
            <p className="text-3xl font-bold text-gray-800">
              {backtestData.summary.total_weeks}
            </p>
            <p className="text-xs text-gray-500 mt-1">Data points analyzed</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
            <h3 className="text-sm font-medium text-gray-600 mb-1">Accuracy</h3>
            <p className="text-3xl font-bold text-green-600">
              {(backtestData.summary.accuracy * 100).toFixed(1)}%
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {backtestData.results.filter((r: any) => r.hawk_dominant === r.actual_risk_off_next_week).length} correct predictions
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-orange-500">
            <h3 className="text-sm font-medium text-gray-600 mb-1">Hawk Predicted</h3>
            <p className="text-3xl font-bold text-orange-600">
              {backtestData.summary.hawk_weeks_predicted}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {((backtestData.summary.hawk_weeks_predicted / backtestData.summary.total_weeks) * 100).toFixed(1)}% of weeks
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-red-500">
            <h3 className="text-sm font-medium text-gray-600 mb-1">Risk-Off Weeks</h3>
            <p className="text-3xl font-bold text-red-600">
              {backtestData.summary.actual_risk_off_weeks}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {((backtestData.summary.actual_risk_off_weeks / backtestData.summary.total_weeks) * 100).toFixed(1)}% of weeks
            </p>
          </div>
        </div>
      )}

      {/* Charts */}
      {backtestData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Accuracy Over Time */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold mb-4">Prediction Accuracy Over Time</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 1]} tickFormatter={(value) => value === 1 ? '✓' : '✗'} />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="accuracy" 
                  stroke="#10B981" 
                  strokeWidth={2}
                  name="Accuracy"
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Accuracy Distribution */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold mb-4">Accuracy Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={accuracyData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {accuracyData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Scenario Distribution */}
          <div className="bg-white rounded-lg shadow-md p-6 lg:col-span-2">
            <h3 className="text-xl font-semibold mb-4">Predicted Scenario Distribution Over Time</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={scenarioData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="hawk" stackId="a" fill="#EF4444" name="Hawkish" />
                <Bar dataKey="dove" stackId="a" fill="#10B981" name="De-escalate" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Results Table */}
      {backtestData && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
            <h3 className="text-xl font-semibold">Detailed Results</h3>
            <p className="text-sm text-gray-600 mt-1">
              Showing predictions vs actual market outcomes for each week
            </p>
          </div>
          <div className="overflow-x-auto max-h-96">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50 sticky top-0">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Predicted Scenario
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actual Market
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Result
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {backtestData.results.map((result: any, idx: number) => {
                  const isCorrect = result.hawk_dominant === result.actual_risk_off_next_week;
                  return (
                    <tr key={idx} className={`hover:bg-gray-50 ${isCorrect ? 'bg-green-50/30' : 'bg-red-50/30'}`}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {format(new Date(result.date), 'MMM dd, yyyy')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {result.hawk_dominant ? (
                          <span className="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                            🦅 Hawkish
                          </span>
                        ) : (
                          <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                            🕊️ De-escalate
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {result.actual_risk_off_next_week ? (
                          <span className="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                            ⚠️ Risk-Off
                          </span>
                        ) : (
                          <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                            ✅ Risk-On
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {isCorrect ? (
                          <span className="text-green-600 font-semibold flex items-center gap-1">
                            <span>✓</span> Correct
                          </span>
                        ) : (
                          <span className="text-red-600 font-semibold flex items-center gap-1">
                            <span>✗</span> Incorrect
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
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
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!backtestData && !isRunning && !error && (
        <div className="bg-gray-50 rounded-lg p-12 text-center">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-gray-900">No Backtest Results</h3>
          <p className="mt-2 text-sm text-gray-600">
            Select a date range and frequency, then click "Run Backtest" to analyze model performance
          </p>
        </div>
      )}
    </div>
  );
};

export default BacktestView;

