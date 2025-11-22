import MarketOverviewCard from './MarketOverviewCard';
import { MarketData } from '../../types';

interface FinancialIndicesProps {
  marketContext: MarketData;
}

const FinancialIndices = ({ marketContext }: FinancialIndicesProps) => {
  const indices = [
    { name: 'S&P 500', key: 'SP500', fallbackKey: 'USA', color: '#002868' },
    { name: 'Nikkei 225', key: 'Nikkei225', fallbackKey: 'Japan', color: '#BC002D' },
    { name: 'DAX', key: 'DAX', fallbackKey: 'Germany', color: '#000000' },
    { name: 'TAIEX', key: 'TAIEX', fallbackKey: 'Taiwan', color: '#000095' },
    { name: 'Hang Seng', key: 'HangSeng', color: '#DE2910' },
    { name: 'Gold', key: 'Gold', color: '#F59E0B' },
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm">
      <h2 className="text-xl font-semibold mb-4">Real-Time Financial Indices</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {indices.map(({ name, key, fallbackKey, color }) => {
          const value = marketContext?.[key] ?? marketContext?.[fallbackKey || ''] ?? 0;
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
    </div>
  );
};

export default FinancialIndices;



