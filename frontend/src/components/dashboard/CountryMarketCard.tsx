interface CountryMarketCardProps {
  country: string;
  price: number | null;
  percentageChange: number;
  indexName: string;
  ticker: string;
  color: string;
}

const CountryMarketCard = ({ 
  country, 
  price, 
  percentageChange, 
  indexName, 
  ticker,
  color 
}: CountryMarketCardProps) => {
  const isPositive = percentageChange > 0;
  const textColor = isPositive ? 'text-green-600' : 'text-red-600';
  const bgColor = isPositive ? 'bg-green-50' : 'bg-red-50';
  const icon = isPositive ? '↑' : '↓';

  const formatPrice = (value: number | null): string => {
    if (value === null || value === 0) return 'N/A';
    // Format based on typical index ranges
    if (value > 10000) return value.toLocaleString('en-US', { maximumFractionDigits: 0 });
    if (value > 100) return value.toLocaleString('en-US', { maximumFractionDigits: 2 });
    return value.toLocaleString('en-US', { maximumFractionDigits: 4 });
  };

  return (
    <div
      className={`p-4 rounded-lg shadow-md ${bgColor} hover:shadow-lg transition-shadow cursor-pointer border-l-4`}
      style={{ borderLeftColor: color }}
    >
      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="font-semibold text-gray-700">{country}</h3>
          <p className="text-xs text-gray-500 mt-1">
            {indexName} ({ticker})
          </p>
        </div>
        <span className={`text-xl ${textColor}`}>{icon}</span>
      </div>
      
      <div className="space-y-1">
        <div>
          <p className="text-xs text-gray-500">Index Price</p>
          <p className="text-2xl font-bold text-gray-800">
            {formatPrice(price)}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500">14-Day Change</p>
          <p className={`text-xl font-semibold ${textColor}`}>
            {isPositive ? '+' : ''}{percentageChange.toFixed(2)}%
          </p>
        </div>
      </div>
      
      <div className="mt-3 h-1 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${isPositive ? 'bg-green-500' : 'bg-red-500'}`}
          style={{ width: `${Math.min(Math.abs(percentageChange) * 10, 100)}%` }}
        />
      </div>
    </div>
  );
};

export default CountryMarketCard;



