# Frontend UI Design - Geopolitical Market Game Tracker

## Architecture Overview

### Tech Stack Recommendation
- **Framework**: React 18+ with TypeScript
- **State Management**: Zustand or Redux Toolkit (lightweight state)
- **Data Fetching**: React Query / TanStack Query (for API calls and caching)
- **Visualization**: Recharts or Chart.js (for market data charts)
- **UI Components**: Material-UI (MUI) or Tailwind CSS + Headless UI
- **Backend API**: FastAPI (Python) or Flask REST API
- **Real-time Updates**: WebSockets (optional, for live market data)

---

## Component Structure

### 1. Layout Components

```
App
├── Header
│   ├── Logo/Title
│   ├── DateSelector (current_date picker)
│   └── SettingsMenu
├── Sidebar (optional)
│   ├── Navigation
│   └── QuickStats
└── MainContent
    ├── Dashboard (default view)
    ├── BacktestView
    ├── SensitivityAnalysisView
    └── HistoricalView
```

### 2. Core Components

#### **Dashboard Component** (Main View)
```typescript
interface DashboardProps {
  currentDate: Date;
  marketData: MarketData;
  predictions: NashEquilibrium;
}

Components:
- MarketOverviewCards (9 cards: Japan, China, USA, Germany, Taiwan, USDCNY, USDJPY, Gold, VIX)
- PredictionPanel (shows Nash equilibrium results)
- ActionDistributionChart (bar chart per country)
- GlobalScenarioIndicator (most likely scenario)
- MarketTrendChart (14-day returns visualization)
```

#### **MarketOverviewCard Component**
```typescript
interface MarketCardProps {
  name: string;
  ticker: string;
  return: number; // 14-day return
  trend: 'up' | 'down' | 'neutral';
  color: string; // country-specific color
}

Features:
- Large percentage display
- Mini sparkline chart
- Color-coded (green/red)
- Click to expand details
```

#### **PredictionPanel Component**
```typescript
interface PredictionPanelProps {
  strategies: StrategyMatrix; // 5x4 matrix
  parties: string[];
  actions: string[];
  dominantScenario: string;
}

Features:
- Interactive table/matrix view
- Probability bars for each action
- Highlight dominant action per country
- Tooltip on hover showing full distribution
```

#### **ActionDistributionChart Component**
```typescript
// Stacked bar chart or grouped bar chart
- X-axis: Countries (Japan, China, USA, Germany, Taiwan)
- Y-axis: Probability (0-100%)
- 4 bars per country (Hawk, De-escalate, Stimulus, Military)
- Color-coded by action type
```

#### **BacktestView Component**
```typescript
interface BacktestViewProps {
  results: BacktestResult[];
  summary: BacktestSummary;
}

Components:
- BacktestControls (date range picker, run button)
- AccuracyChart (rolling accuracy over time)
- ResultsTable (week-by-week predictions vs actual)
- SummaryCards (accuracy %, hit rates, etc.)
- TimelineView (visual timeline of predictions)
```

#### **SensitivityAnalysisView Component**
```typescript
interface SensitivityViewProps {
  analysisResults: SensitivityData;
}

Components:
- NoiseLevelSlider (interactive parameter control)
- SensitivityChart (line chart showing probability vs noise)
- RobustnessIndicator (visual gauge)
- CountrySensitivityTable
- RecommendationsPanel
```

#### **HistoricalView Component**
```typescript
Components:
- DateRangeSelector
- MarketDataTimeline (interactive chart)
- PayoffMatrixEvolution (animated or step-through)
- ScenarioTimeline (color-coded by predicted scenario)
```

---

## State Management

### Global State (Zustand Store)

```typescript
interface AppState {
  // Current analysis state
  currentDate: Date;
  marketData: MarketData | null;
  predictions: NashEquilibrium | null;
  loading: boolean;
  
  // Backtest state
  backtestResults: BacktestResult[] | null;
  backtestSummary: BacktestSummary | null;
  backtestLoading: boolean;
  
  // Sensitivity analysis state
  sensitivityResults: SensitivityData | null;
  sensitivityLoading: boolean;
  
  // UI state
  activeView: 'dashboard' | 'backtest' | 'sensitivity' | 'historical';
  selectedCountry: string | null;
  selectedDateRange: [Date, Date] | null;
  
  // Actions
  setCurrentDate: (date: Date) => void;
  fetchMarketData: (date: Date) => Promise<void>;
  runBacktest: (start: Date, end: Date) => Promise<void>;
  runSensitivityAnalysis: (params: SensitivityParams) => Promise<void>;
}
```

### API Integration (React Query)

```typescript
// Custom hooks for data fetching
useMarketData(date: Date) // Fetches current market data
usePredictions(date: Date) // Fetches Nash equilibrium
useBacktest(start: Date, end: Date) // Runs backtest
useSensitivityAnalysis(params) // Runs sensitivity analysis
useHistoricalData(ticker, start, end) // Fetches historical data
```

---

## Data Flow

```
User Action
    ↓
Component Event Handler
    ↓
Zustand Action / React Query Mutation
    ↓
API Call (FastAPI/Flask)
    ↓
Python Backend (gametheory.py)
    ↓
Response (JSON)
    ↓
State Update / Cache Update
    ↓
Component Re-render
```

---

## API Endpoints Design

### REST API Structure

```python
# FastAPI example
GET  /api/market-data?date=2024-03-15&days=14
POST /api/predictions
     Body: { "date": "2024-03-15" }
     Response: { "strategies": [...], "scenario": "..." }

POST /api/backtest
     Body: { "start_date": "2024-01-01", "end_date": "2024-12-31" }
     Response: { "results": [...], "summary": {...} }

POST /api/sensitivity-analysis
     Body: { "noise_levels": [0, 0.1, ...], "n_runs": 100 }
     Response: { "results": [...], "plot_url": "..." }

GET  /api/historical?ticker=^GSPC&start=2024-01-01&end=2024-12-31
GET  /api/cache/stats
DELETE /api/cache
```

---

## UI/UX Design Principles

### 1. **Color Scheme**
- **Countries**: 
  - Japan: Red (#BC002D)
  - China: Red (#DE2910)
  - USA: Blue (#002868)
  - Germany: Black (#000000)
  - Taiwan: Blue (#000095)
- **Actions**:
  - Hawkish: Red/Orange gradient
  - De-escalate: Green/Blue gradient
  - Stimulus: Yellow/Green gradient
  - Military: Dark Red/Black gradient
- **Market Data**: 
  - Positive: Green (#10B981)
  - Negative: Red (#EF4444)
  - Neutral: Gray (#6B7280)

### 2. **Visual Hierarchy**
- **Primary**: Current predictions (large, prominent)
- **Secondary**: Market data overview (cards)
- **Tertiary**: Historical analysis (tables, charts)

### 3. **Interactivity**
- Hover tooltips for detailed information
- Click to drill down (country → detailed view)
- Date range sliders for historical analysis
- Real-time updates (if WebSocket enabled)

### 4. **Responsive Design**
- Mobile-first approach
- Collapsible sidebar on mobile
- Stack cards vertically on small screens
- Touch-friendly controls

---

## Key Features

### 1. **Real-time Dashboard**
- Live market data display
- Auto-refresh every 5 minutes (configurable)
- Alert notifications for significant changes

### 2. **Interactive Predictions**
- Click on country to see detailed strategy breakdown
- Hover over action to see payoff calculation
- Compare predictions across dates

### 3. **Backtest Visualization**
- Interactive timeline
- Filter by accuracy (correct/wrong predictions)
- Export results to CSV/PDF

### 4. **Sensitivity Analysis**
- Interactive noise level slider
- Real-time chart updates
- Download sensitivity plot

### 5. **Historical Analysis**
- Multi-ticker comparison charts
- Overlay predictions on market data
- Correlation analysis

---

## Component Examples

### Example 1: MarketOverviewCard

```tsx
const MarketOverviewCard: React.FC<MarketCardProps> = ({ 
  name, 
  return: returnValue, 
  trend 
}) => {
  const color = trend === 'up' ? 'text-green-600' : 'text-red-600';
  const bgColor = trend === 'up' ? 'bg-green-50' : 'bg-red-50';
  
  return (
    <Card className={`p-4 ${bgColor} hover:shadow-lg transition-shadow`}>
      <div className="flex justify-between items-start">
        <div>
          <h3 className="font-semibold text-gray-700">{name}</h3>
          <p className={`text-2xl font-bold ${color} mt-2`}>
            {returnValue > 0 ? '+' : ''}{returnValue.toFixed(2)}%
          </p>
        </div>
        <TrendIcon trend={trend} />
      </div>
      <MiniSparkline data={historicalData} />
    </Card>
  );
};
```

### Example 2: PredictionMatrix

```tsx
const PredictionMatrix: React.FC<PredictionMatrixProps> = ({ 
  strategies, 
  parties, 
  actions 
}) => {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full">
        <thead>
          <tr>
            <th>Country</th>
            {actions.map(action => (
              <th key={action} className="text-center">{action}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {parties.map((party, i) => (
            <tr key={party}>
              <td className="font-semibold">{party}</td>
              {strategies[i].map((prob, j) => {
                const isDominant = prob === Math.max(...strategies[i]);
                return (
                  <td key={j} className={isDominant ? 'bg-blue-100' : ''}>
                    <ProbabilityBar 
                      value={prob} 
                      label={`${(prob * 100).toFixed(0)}%`}
                      color={actionColors[j]}
                    />
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

---

## Implementation Phases

### Phase 1: MVP (Minimum Viable Product)
1. Basic dashboard with market data cards
2. Simple prediction display (table format)
3. Date selector
4. Basic API integration

### Phase 2: Enhanced Visualization
1. Interactive charts (Recharts)
2. Backtest view with results table
3. Sensitivity analysis view
4. Improved UI/UX

### Phase 3: Advanced Features
1. Real-time updates (WebSockets)
2. Historical analysis tools
3. Export functionality
4. User preferences/settings

### Phase 4: Polish
1. Animations and transitions
2. Mobile optimization
3. Performance optimization
4. Documentation

---

## File Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Card.tsx
│   │   │   ├── Button.tsx
│   │   │   └── LoadingSpinner.tsx
│   │   ├── dashboard/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── MarketOverviewCard.tsx
│   │   │   ├── PredictionPanel.tsx
│   │   │   └── ActionDistributionChart.tsx
│   │   ├── backtest/
│   │   │   ├── BacktestView.tsx
│   │   │   ├── AccuracyChart.tsx
│   │   │   └── ResultsTable.tsx
│   │   └── sensitivity/
│   │       ├── SensitivityView.tsx
│   │       └── SensitivityChart.tsx
│   ├── hooks/
│   │   ├── useMarketData.ts
│   │   ├── usePredictions.ts
│   │   └── useBacktest.ts
│   ├── store/
│   │   └── appStore.ts (Zustand)
│   ├── api/
│   │   └── client.ts (Axios/Fetch wrapper)
│   ├── types/
│   │   └── index.ts (TypeScript interfaces)
│   └── App.tsx
├── public/
└── package.json
```

---

## Next Steps

1. **Set up React project** with TypeScript
2. **Create API wrapper** (FastAPI/Flask backend)
3. **Build core components** (Dashboard, Cards)
4. **Integrate data fetching** (React Query)
5. **Add visualizations** (Charts)
6. **Implement state management** (Zustand)
7. **Polish UI/UX** (Styling, animations)

---

## Considerations

### Performance
- Memoize expensive calculations
- Virtualize long lists (backtest results)
- Lazy load components
- Optimize chart rendering

### Accessibility
- ARIA labels
- Keyboard navigation
- Screen reader support
- Color contrast compliance

### Testing
- Unit tests (Jest + React Testing Library)
- Integration tests
- E2E tests (Playwright/Cypress)

### Deployment
- Build optimization
- Environment variables
- API endpoint configuration
- CDN for static assets



