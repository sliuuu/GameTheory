# Geopolitical Market Game Tracker - Frontend

React + TypeScript frontend for the Geopolitical Market Game Tracker.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Make sure the backend API is running:
```bash
# In the parent directory
python3 -m uvicorn api_backend:app --host 0.0.0.0 --port 8001 --reload
```

3. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173` (Vite default port)

## Project Structure

```
src/
├── components/
│   ├── common/        # Shared components (Header, LoadingSpinner)
│   ├── dashboard/     # Dashboard components
│   ├── backtest/      # Backtest view components
│   └── sensitivity/   # Sensitivity analysis components
├── hooks/             # Custom React hooks
├── store/             # Zustand state management
├── api/               # API client
├── types/             # TypeScript type definitions
└── App.tsx            # Main app component
```

## Features

- ✅ Dashboard with market data cards
- ✅ Nash equilibrium prediction matrix
- ✅ Date selector for historical analysis
- ⏳ Backtest view (coming soon)
- ⏳ Sensitivity analysis (coming soon)
- ⏳ Historical view (coming soon)

## Tech Stack

- React 18
- TypeScript
- Vite
- Tailwind CSS
- TanStack Query (React Query)
- Zustand
- Recharts (for future charts)

