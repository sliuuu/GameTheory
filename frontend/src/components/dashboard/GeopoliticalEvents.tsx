import { GeopoliticalEvent } from '../../api/client';
import LoadingSpinner from '../common/LoadingSpinner';

interface GeopoliticalEventsProps {
  events: GeopoliticalEvent[];
  isLoading?: boolean;
  error?: Error | null;
}

const GeopoliticalEvents = ({ events, isLoading, error }: GeopoliticalEventsProps) => {
  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'very_high':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getMarketImpactIcon = (impact: string) => {
    switch (impact) {
      case 'positive':
        return '📈';
      case 'negative':
        return '📉';
      case 'mixed':
        return '📊';
      default:
        return '📊';
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h2 className="text-xl font-semibold mb-4">Top 5 Market-Moving Geopolitical Events</h2>
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h2 className="text-xl font-semibold mb-4">Top 5 Market-Moving Geopolitical Events</h2>
        <p className="text-red-600">Error loading events: {error.message}</p>
      </div>
    );
  }

  if (!events || events.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h2 className="text-xl font-semibold mb-4">Top 5 Market-Moving Geopolitical Events</h2>
        <p className="text-gray-500">No events available for this date.</p>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm">
      <h2 className="text-xl font-semibold mb-4">Top 5 Market-Moving Geopolitical Events</h2>
      <div className="space-y-4">
        {events.map((event, index) => (
          <div
            key={index}
            className="border-l-4 border-blue-500 pl-4 py-3 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-2xl">{getMarketImpactIcon(event.market_impact)}</span>
                  <h3 className="font-semibold text-lg">{event.title}</h3>
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded border ${getImpactColor(
                      event.impact
                    )}`}
                  >
                    {event.impact.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
                <p className="text-gray-600 text-sm mb-2">{event.description}</p>
                <div className="flex items-center gap-4 text-xs text-gray-500 mb-2">
                  <span className="font-medium">Type: {event.type}</span>
                  <span>Countries: {event.countries.join(', ')}</span>
                  <span>Market Impact: {event.market_impact}</span>
                </div>
                {event.news_sources && event.news_sources.length > 0 && (
                  <div className="flex items-center gap-3 mt-2 pt-2 border-t border-gray-200">
                    <span className="text-xs font-medium text-gray-600">News Sources:</span>
                    <div className="flex items-center gap-2 flex-wrap">
                      {event.news_sources.map((source, idx) => (
                        <a
                          key={idx}
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 hover:text-blue-800 hover:underline font-medium"
                        >
                          {source.name}
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GeopoliticalEvents;



