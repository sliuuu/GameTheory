import type { NashEquilibrium } from '../../types';

interface PredictionMatrixProps {
  equilibrium: NashEquilibrium;
}

const PredictionMatrix = ({ equilibrium }: PredictionMatrixProps) => {
  const actionColors = ['#EF4444', '#10B981', '#F59E0B', '#7C2D12'];

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4">Nash Equilibrium Predictions</h2>
      <div className="overflow-x-auto">
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
              const maxProb = Math.max(...strategy);

              return (
                <tr key={party} className="border-b border-gray-200 hover:bg-gray-50">
                  <td className="py-3 px-4 font-semibold">{party}</td>
                  {strategy.map((prob, actionIdx) => {
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
                                  backgroundColor: actionColors[actionIdx],
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
      </div>
      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
        <p className="text-sm text-gray-600">
          <span className="font-semibold">Most Likely Scenario:</span>{' '}
          <span className="text-blue-700 font-bold">
            {equilibrium.global_scenario}
          </span>
        </p>
      </div>
    </div>
  );
};

export default PredictionMatrix;

