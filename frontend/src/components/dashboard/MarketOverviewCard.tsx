interface MarketCardProps {
  name: string;
  value: number;
  trend?: 'up' | 'down' | 'neutral';
  color: string;
}

const MarketOverviewCard = ({ name, value, color }: MarketCardProps) => {
  // Handle undefined/null values
  const safeValue = value ?? 0;
  const isPositive = safeValue > 0;
  const textColor = isPositive ? 'text-green-600' : 'text-red-600';
  const bgColor = isPositive ? 'bg-green-50' : 'bg-red-50';
  const icon = isPositive ? '↑' : '↓';

  return (
    <div
      className={`p-4 rounded-lg shadow-md ${bgColor} hover:shadow-lg transition-shadow cursor-pointer border-l-4`}
      style={{ borderLeftColor: color }}
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-gray-700">{name}</h3>
        <span className={`text-xl ${textColor}`}>{icon}</span>
      </div>
      <p className={`text-3xl font-bold ${textColor}`}>
        {isPositive ? '+' : ''}{safeValue.toFixed(2)}%
      </p>
      <div className="mt-2 h-1 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${isPositive ? 'bg-green-500' : 'bg-red-500'}`}
          style={{ width: `${Math.min(Math.abs(safeValue) * 10, 100)}%` }}
        />
      </div>
    </div>
  );
};

export default MarketOverviewCard;

