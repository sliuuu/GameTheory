import { useState, useEffect, useRef } from 'react';
import { format, subMonths } from 'date-fns';
import { backtestApi } from '../../api/client';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

const JOB_STORAGE_KEY = 'backtest_job_id';

const HistoricalView = () => {
  // Default to past dates (6 months ago to 1 month ago)
  const defaultEnd = subMonths(new Date(), 1);
  const defaultStart = subMonths(defaultEnd, 6);
  const [startDate, setStartDate] = useState(format(defaultStart, 'yyyy-MM-dd'));
  const [endDate, setEndDate] = useState(format(defaultEnd, 'yyyy-MM-dd'));
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
        showNotification('Backtest Complete', `Analysis finished with ${(status.result.accuracy * 100).toFixed(1)}% accuracy`);
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
      const response = await backtestApi.startBacktest(startDate, endDate);
      setJobId(response.job_id);
      setJobStatus('pending');
      localStorage.setItem(JOB_STORAGE_KEY, response.job_id);
      
      // Start polling
      checkJobStatus(response.job_id);
    } catch (err: any) {
      setError(err.message || 'Failed to start backtest');
    }
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

  const isRunning = jobStatus === 'running' || jobStatus === 'pending';

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold mb-4">Historical Analysis</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
          <div className="flex items-end">
            <button
              onClick={handleRunBacktest}
              disabled={isRunning}
              className="w-full px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {isRunning ? 'Running...' : 'Run Analysis'}
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        {isRunning && (
          <div className="mt-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">
                {currentStep || 'Processing...'}
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
                Job ID: {jobId.substring(0, 8)}... You can navigate away and return later.
              </p>
            )}
          </div>
        )}
      </div>

      {/* Summary Cards */}
      {backtestData?.summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-sm font-medium text-gray-600">Total Weeks</h3>
            <p className="text-3xl font-bold text-gray-800 mt-2">
              {backtestData.summary.total_weeks}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-sm font-medium text-gray-600">Accuracy</h3>
            <p className="text-3xl font-bold text-green-600 mt-2">
              {(backtestData.summary.accuracy * 100).toFixed(1)}%
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-sm font-medium text-gray-600">Hawk Predicted</h3>
            <p className="text-3xl font-bold text-orange-600 mt-2">
              {backtestData.summary.hawk_weeks_predicted}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-sm font-medium text-gray-600">Risk-Off Weeks</h3>
            <p className="text-3xl font-bold text-red-600 mt-2">
              {backtestData.summary.actual_risk_off_weeks}
            </p>
          </div>
        </div>
      )}

      {/* Charts */}
      {backtestData && (
        <div className="space-y-6">
          {/* Accuracy Over Time */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold mb-4">Prediction Accuracy Over Time</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 1]} tickFormatter={(value) => value === 1 ? 'Correct' : 'Wrong'} />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="accuracy" 
                  stroke="#10B981" 
                  strokeWidth={2}
                  name="Accuracy (1=Correct, 0=Wrong)"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Scenario Distribution */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold mb-4">Predicted Scenario Distribution</h3>
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

          {/* Results Table */}
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-xl font-semibold">Detailed Results</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Predicted
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Actual
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Result
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {backtestData.results.slice(0, 20).map((result: any, idx: number) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {format(new Date(result.date), 'MMM dd, yyyy')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {result.hawk_dominant ? (
                          <span className="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                            Hawk
                          </span>
                        ) : (
                          <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                            Dove
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {result.actual_risk_off_next_week ? (
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
                        {result.hawk_dominant === result.actual_risk_off_next_week ? (
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
            {backtestData.results.length > 20 && (
              <div className="px-6 py-4 bg-gray-50 text-sm text-gray-600">
                Showing first 20 of {backtestData.results.length} results
              </div>
            )}
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600">Error: {error}</p>
        </div>
      )}

      {!backtestData && !isRunning && !error && (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <p className="text-gray-600">Select a date range and click "Run Analysis" to view historical data</p>
          {!('Notification' in window) && (
            <p className="text-sm text-gray-500 mt-2">
              Note: Browser notifications are not supported in this browser
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default HistoricalView;
