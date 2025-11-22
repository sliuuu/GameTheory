import { format } from 'date-fns';
import { useAppStore } from '../../store/appStore';
import { usePredictions } from '../../hooks/usePredictions';
import { useGeopoliticalEvents } from '../../hooks/useGeopoliticalEvents';
import MarketOverviewCard from './MarketOverviewCard';
import CountryMarketCard from './CountryMarketCard';
import PredictionMatrix from './PredictionMatrix';
import FinancialIndices from './FinancialIndices';
import GeopoliticalEvents from './GeopoliticalEvents';
import LoadingSpinner from '../common/LoadingSpinner';

const Dashboard = () => {
  const { currentDate, setCurrentDate, useOptimizedModel, setUseOptimizedModel } = useAppStore();
  const { data: predictions, isLoading, error, refetch, isFetching } = usePredictions(currentDate, useOptimizedModel);
  const { data: eventsData, isLoading: eventsLoading, error: eventsError } = useGeopoliticalEvents(currentDate);

  const marketCards = [
    { name: 'Japan', key: 'Japan' as const, color: '#BC002D' },
    { name: 'China', key: 'China' as const, color: '#DE2910' },
    { name: 'USA', key: 'USA' as const, color: '#002868' },
    { name: 'Germany', key: 'Germany' as const, color: '#000000' },
    { name: 'Taiwan', key: 'Taiwan' as const, color: '#000095' },
    { name: 'USD/CNY', key: 'USDCNY' as const, color: '#6B7280' },
    { name: 'USD/JPY', key: 'USDJPY' as const, color: '#6B7280' },
    { name: 'Gold', key: 'Gold' as const, color: '#F59E0B' },
    { name: 'VIX', key: 'VIX' as const, color: '#EF4444' },
  ];

  if (isLoading && !predictions) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="text-center py-20">
        <p className="text-red-600">Error loading predictions: {error.message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Date Selector and Model Toggle */}
      <div className="bg-white p-4 rounded-lg shadow-sm">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Analysis Date</h2>
          <div className="flex items-center gap-3">
            <input
              type="date"
              value={format(currentDate, 'yyyy-MM-dd')}
              onChange={(e) => {
                const newDate = new Date(e.target.value);
                setCurrentDate(newDate);
                // Refetch will happen automatically due to queryKey change
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={() => refetch()}
              disabled={isFetching}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {isFetching ? (
                <>
                  <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Loading...
                </>
              ) : (
                <>
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Refresh
                </>
              )}
            </button>
          </div>
        </div>
        {/* Model Toggle */}
        <div className="flex items-center gap-3 pt-3 border-t border-gray-200">
          <span className="text-sm font-medium text-gray-700">Model:</span>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={useOptimizedModel}
              onChange={(e) => setUseOptimizedModel(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            <span className="ml-3 text-sm font-medium text-gray-700">
              {useOptimizedModel ? 'Optimized (Country-Specific)' : 'Basic (Improved)'}
            </span>
          </label>
          {useOptimizedModel && (
            <span className="text-xs text-gray-500 ml-2">
              Includes constraints, capabilities, and alliances
            </span>
          )}
        </div>
      </div>

      {/* Country Market Cards with Prices and Index Proxies */}
      {predictions && predictions.market_context && predictions.prices && predictions.country_proxies && (
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <h2 className="text-xl font-semibold mb-4">Country Market Indices</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {['USA', 'China', 'Japan', 'Germany', 'Taiwan'].map((country) => {
              const proxy = predictions.country_proxies?.[country];
              const price = proxy ? predictions.prices?.[proxy.symbol] ?? null : null;
              const percentageChange = predictions.market_context?.[country] ?? 0;
              const countryColors: Record<string, string> = {
                'USA': '#002868',
                'China': '#DE2910',
                'Japan': '#BC002D',
                'Germany': '#000000',
                'Taiwan': '#000095'
              };
              
              return (
                <CountryMarketCard
                  key={country}
                  country={country}
                  price={price}
                  percentageChange={percentageChange}
                  indexName={proxy?.index || 'N/A'}
                  ticker={proxy?.ticker || 'N/A'}
                  color={countryColors[country] || '#6B7280'}
                />
              );
            })}
          </div>
        </div>
      )}

      {/* Financial Indices */}
      {predictions && predictions.market_context && (
        <FinancialIndices marketContext={predictions.market_context} />
      )}

      {/* Geopolitical Events */}
      <GeopoliticalEvents
        events={eventsData?.events || []}
        isLoading={eventsLoading}
        error={eventsError}
      />

      {/* Market Data Cards (Original) */}
      {predictions && predictions.market_context && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-3 gap-4">
            {marketCards.map(({ name, key, color }) => {
              const value = predictions.market_context?.[key] ?? 0;
              return (
                <MarketOverviewCard
                  key={key}
                  name={name}
                  value={value}
                  trend={value > 0 ? 'up' : 'down'}
                  color={color}
                />
              );
            })}
          </div>

          {/* Predictions Panel */}
          <PredictionMatrix equilibrium={predictions} />
        </>
      )}
    </div>
  );
};

export default Dashboard;

