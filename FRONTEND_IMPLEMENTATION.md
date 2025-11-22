# Frontend Implementation Guide

## Overview

This document outlines the React-style frontend architecture for the Geopolitical Market Game Tracker. The design follows modern React patterns with TypeScript, state management, and API integration.

## Architecture Summary

### Frontend Stack
- **React 18+** with TypeScript
- **State Management**: Zustand (lightweight) or Redux Toolkit
- **Data Fetching**: TanStack Query (React Query)
- **Charts**: Recharts or Chart.js
- **Styling**: Tailwind CSS or Material-UI
- **Build Tool**: Vite or Create React App

### Backend Stack
- **FastAPI** (Python) - REST API
- **Existing Python modules**: `gametheory.py`, `historical_backtesting.py`
- **Caching**: Already implemented in `data_cache.py`

## File Structure

```
GameTheory/
├── frontend/                    # React frontend (to be created)
│   ├── src/
│   │   ├── components/
│   │   │   ├── dashboard/
│   │   │   ├── backtest/
│   │   │   └── sensitivity/
│   │   ├── hooks/
│   │   ├── store/
│   │   ├── api/
│   │   └── types/
│   └── package.json
├── api_backend.py              # FastAPI server (created)
├── frontend_design.md          # Detailed design doc (created)
├── frontend_examples.tsx       # Example components (created)
└── FRONTEND_IMPLEMENTATION.md  # This file
```

## Quick Start

### 1. Set Up Backend API

```bash
# Install FastAPI and dependencies
pip install fastapi uvicorn python-multipart

# Run the API server
python api_backend.py
# Or: uvicorn api_backend:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### 2. Set Up React Frontend

```bash
# Create React app with TypeScript
npx create-react-app frontend --template typescript
cd frontend

# Or use Vite (faster)
npm create vite@latest frontend -- --template react-ts
cd frontend

# Install dependencies
npm install @tanstack/react-query zustand axios recharts
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Start dev server
npm start  # or npm run dev (Vite)
```

### 3. API Integration

Create `src/api/client.ts`:

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
```

### 4. Key Components to Build

1. **Dashboard** (`src/components/dashboard/Dashboard.tsx`)
   - Market data cards
   - Prediction matrix
   - Date selector

2. **BacktestView** (`src/components/backtest/BacktestView.tsx`)
   - Results table
   - Accuracy chart
   - Summary cards

3. **SensitivityView** (`src/components/sensitivity/SensitivityView.tsx`)
   - Interactive chart
   - Noise level controls
   - Robustness indicators

## API Endpoints

### GET `/api/market-data`
- Query params: `date` (optional), `days` (default: 14)
- Returns: Market data and returns

### GET `/api/predictions`
- Query params: `date` (optional)
- Returns: Nash equilibrium predictions

### POST `/api/backtest`
- Body: `{ start_date, end_date, freq? }`
- Returns: Backtest results and summary

### POST `/api/sensitivity-analysis`
- Body: `{ noise_levels?, n_runs? }`
- Returns: Sensitivity analysis results

### GET `/api/cache/stats`
- Returns: Cache statistics

### DELETE `/api/cache`
- Query params: `older_than_days` (optional)
- Clears cache

## Example Usage

### Fetching Predictions

```typescript
import { useQuery } from '@tanstack/react-query';
import api from './api/client';

const usePredictions = (date: Date) => {
  return useQuery({
    queryKey: ['predictions', date.toISOString()],
    queryFn: async () => {
      const response = await api.get('/api/predictions', {
        params: { date: date.toISOString().split('T')[0] }
      });
      return response.data;
    }
  });
};
```

### Running Backtest

```typescript
import { useMutation } from '@tanstack/react-query';

const useBacktest = () => {
  return useMutation({
    mutationFn: async ({ start, end }: { start: Date; end: Date }) => {
      const response = await api.post('/api/backtest', {
        start_date: start.toISOString().split('T')[0],
        end_date: end.toISOString().split('T')[0],
      });
      return response.data;
    }
  });
};
```

## State Management Pattern

### Zustand Store Example

```typescript
import create from 'zustand';

interface AppState {
  currentDate: Date;
  setCurrentDate: (date: Date) => void;
  activeView: 'dashboard' | 'backtest' | 'sensitivity';
  setActiveView: (view: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
  currentDate: new Date(),
  setCurrentDate: (date) => set({ currentDate: date }),
  activeView: 'dashboard',
  setActiveView: (view) => set({ activeView: view }),
}));
```

## Styling Approach

### Option 1: Tailwind CSS (Recommended)
- Utility-first CSS
- Fast development
- Good for custom designs

### Option 2: Material-UI
- Pre-built components
- Consistent design system
- More opinionated

## Next Steps

1. **Phase 1: Basic Setup**
   - [ ] Set up React project
   - [ ] Configure API client
   - [ ] Create basic layout

2. **Phase 2: Core Features**
   - [ ] Build Dashboard component
   - [ ] Integrate market data display
   - [ ] Add prediction matrix

3. **Phase 3: Advanced Features**
   - [ ] Backtest view
   - [ ] Sensitivity analysis
   - [ ] Charts and visualizations

4. **Phase 4: Polish**
   - [ ] Responsive design
   - [ ] Loading states
   - [ ] Error handling
   - [ ] Animations

## Testing the API

You can test the API endpoints using curl or a tool like Postman:

```bash
# Get market data
curl "http://localhost:8000/api/market-data?date=2024-03-15"

# Get predictions
curl "http://localhost:8000/api/predictions?date=2024-03-15"

# Run backtest
curl -X POST "http://localhost:8000/api/backtest" \
  -H "Content-Type: application/json" \
  -d '{"start_date": "2024-01-01", "end_date": "2024-03-31"}'
```

## Documentation

- **Design Document**: See `frontend_design.md` for detailed component architecture
- **Example Components**: See `frontend_examples.tsx` for code examples
- **API Reference**: See `api_backend.py` for endpoint documentation

## Notes

- The backend uses the existing Python modules, so all game theory logic remains in Python
- Caching is already implemented and will speed up repeated API calls
- The API supports CORS for local development
- Consider adding WebSocket support for real-time updates in the future



