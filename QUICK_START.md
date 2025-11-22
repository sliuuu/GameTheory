# Quick Start Guide

## 1. Start the Backend API

```bash
cd /Users/samuelliu/Development/GameTheory

# Install FastAPI if not already installed
pip install fastapi uvicorn

# Start the API server
python3 -m uvicorn api_backend:app --host 0.0.0.0 --port 8001 --reload
```

The API will run on `http://localhost:8001`

## 2. Set Up and Start the Frontend

```bash
cd /Users/samuelliu/Development/GameTheory/frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will run on `http://localhost:5173` (Vite default port)

## 3. Test the Setup

1. Open `http://localhost:5173` in your browser
2. You should see the Dashboard with:
   - Market data cards (9 cards showing returns)
   - Prediction matrix showing Nash equilibrium
   - Date selector to change analysis date

## What's Included

✅ **Dashboard View**
- Market overview cards for all 9 assets
- Nash equilibrium prediction matrix
- Date selector for historical analysis

⏳ **Coming Soon**
- Backtest view with results table
- Sensitivity analysis with charts
- Historical data visualization

## Troubleshooting

### Backend not starting?
- Make sure all Python dependencies are installed
- Check if port 8001 is available (port 8000 may be in use)
- Verify the Python modules are in the correct path

### Frontend not connecting to API?
- Make sure the backend is running on port 8001
- Check the proxy configuration in `vite.config.ts` (should point to port 8001)
- Look for CORS errors in the browser console
- Frontend runs on port 5173 (Vite default) if port 3000 is in use

### Dependencies not installing?
- Make sure Node.js (v18+) is installed
- Try deleting `node_modules` and `package-lock.json`, then `npm install` again

## Next Steps

1. Test the dashboard with different dates
2. Check the browser console for any errors
3. Explore the code structure in `frontend/src/`
4. Add more features following the component patterns

