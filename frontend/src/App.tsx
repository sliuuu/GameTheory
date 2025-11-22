import { useAppStore } from './store/appStore';
import Dashboard from './components/dashboard/Dashboard';
import BacktestView from './components/backtest/BacktestView';
import SensitivityView from './components/sensitivity/SensitivityView';
import HistoricalView from './components/historical/HistoricalView';
import Header from './components/common/Header';

function App() {
  const { activeView } = useAppStore();

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-8">
        {activeView === 'dashboard' && <Dashboard />}
        {activeView === 'backtest' && <BacktestView />}
        {activeView === 'sensitivity' && <SensitivityView />}
        {activeView === 'historical' && <HistoricalView />}
      </main>
    </div>
  );
}

export default App;

