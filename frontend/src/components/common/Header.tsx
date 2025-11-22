import { useAppStore } from '../../store/appStore';

const Header = () => {
  const { activeView, setActiveView } = useAppStore();

  const navItems = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'backtest', label: 'Backtest' },
    { id: 'sensitivity', label: 'Sensitivity' },
    { id: 'historical', label: 'Historical' },
  ] as const;

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-gray-900">
              Geopolitical Market Game Tracker
            </h1>
          </div>
          <nav className="flex space-x-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveView(item.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeView === item.id
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                {item.label}
              </button>
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;



