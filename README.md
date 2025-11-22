# Geopolitical Market Game Tracker

A sophisticated web application that applies game theory to analyze geopolitical events and their impact on financial markets. The system uses Nash equilibrium predictions to forecast country-level strategic behaviors and correlates them with real-time market movements.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![React](https://img.shields.io/badge/React-18+-61dafb.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178c6.svg)

## 🌟 Features

### Real-Time Dashboard
- **Country Market Indices**: Live tracking of major financial indices (S&P 500, Nikkei 225, DAX, TAIEX, Hang Seng) with actual prices and percentage changes
- **Nash Equilibrium Predictions**: Game theory-based predictions for 5 countries (USA, China, Japan, Germany, Taiwan) showing probability distributions across 4 strategic actions
- **Geopolitical Events**: Top 5 market-moving events with direct links to news sources (Reuters, Bloomberg, Financial Times)
- **Financial Indices**: Real-time tracking of major indices, gold prices, and currency pairs
- **Market Overview**: Comprehensive view of market movements across all tracked assets

### Analysis Tools
- **Historical Backtesting**: Test predictions against historical data with accuracy metrics
- **Sensitivity Analysis**: Monte Carlo simulation to assess prediction robustness
- **Optimized Model**: Country-specific game theory model with constraints, capabilities, and alliance effects
- **Date Selection**: Analyze any historical date with cached market data

### Technical Highlights
- **Dual Model System**: Basic improved model and optimized country-specific model
- **Data Caching**: Efficient caching system for market data to reduce API calls
- **Background Jobs**: Asynchronous processing for long-running analyses
- **Real-Time Updates**: Live data fetching from yfinance API
- **Responsive UI**: Modern React interface with Tailwind CSS

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+ and npm
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sliuuu/GameTheory.git
   cd GameTheory
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Running the Application

**Option 1: Use the startup script (Recommended)**
```bash
bash START_SERVERS.sh
```

**Option 2: Manual startup**

Terminal 1 - Backend:
```bash
python3 -m uvicorn api_backend:app --host 0.0.0.0 --port 8001 --reload
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

### Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

## 📊 How It Works

### Game Theory Model

The system models geopolitical interactions as a strategic game where each country (USA, China, Japan, Germany, Taiwan) can choose from 4 actions:
1. **Hawkish Rhetoric / Sanctions**
2. **De-escalate / Dialogue**
3. **Economic Stimulus**
4. **Military Posturing**

### Nash Equilibrium Calculation

For each country, the system:
1. Fetches real-time market data (14-day returns)
2. Builds a payoff matrix based on market conditions and country-specific factors
3. Solves for mixed-strategy Nash equilibrium
4. Displays probability distributions for each action

### Market Data Sources

- **S&P 500** (^GSPC) → USA
- **SSE Composite** (000001.SS) → China
- **Nikkei 225** (^N225) → Japan
- **DAX** (^GDAXI) → Germany
- **TAIEX** (^TWII) → Taiwan
- **Gold** (GC=F), **VIX** (^VIX), **Currency pairs** (USD/CNY, USD/JPY)

## 🏗️ Project Structure

```
GameTheory/
├── api_backend.py              # FastAPI backend server
├── gametheory.py               # Core game theory model
├── optimized_gametheory.py     # Country-specific optimized model
├── geopolitical_events.py      # Event generation and news sources
├── historical_backtesting.py   # Backtesting functionality
├── sensitivity_analysis.py     # Monte Carlo sensitivity analysis
├── data_cache.py               # Market data caching system
├── job_manager.py              # Background job processing
├── requirements.txt            # Python dependencies
├── START_SERVERS.sh            # Startup script
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── dashboard/      # Dashboard components
│   │   │   ├── backtest/       # Backtesting UI
│   │   │   ├── sensitivity/    # Sensitivity analysis UI
│   │   │   └── historical/     # Historical analysis UI
│   │   ├── hooks/              # React Query hooks
│   │   ├── store/              # Zustand state management
│   │   └── types/              # TypeScript types
│   ├── package.json
│   └── vite.config.ts
│
└── README.md                   # This file
```

## 📖 Usage Guide

### Dashboard
1. Select a date using the date picker (defaults to current date)
2. Toggle between "Basic (Improved)" and "Optimized (Country-Specific)" models
3. View real-time predictions, market data, and geopolitical events
4. Click news source links to read related articles

### Historical Backtesting
1. Navigate to the "Backtest" tab
2. Select start and end dates
3. Click "Run Backtest" to analyze historical accuracy
4. View results with accuracy metrics and prediction distributions

### Sensitivity Analysis
1. Navigate to the "Sensitivity" tab
2. Adjust noise levels and number of runs
3. Click "Run Analysis" to test prediction robustness
4. View sensitivity plots and statistics

### Historical Analysis
1. Navigate to the "Historical" tab
2. Select a date range
3. View historical predictions and market movements over time

## 🔧 Configuration

### Backend Configuration
- **Port**: Default 8001 (configurable in `START_SERVERS.sh`)
- **Cache**: Market data is cached in `.market_data_cache/`
- **API Timeout**: 120 seconds for market data fetching

### Frontend Configuration
- **Port**: Default 5173 (Vite default)
- **API Proxy**: Configured in `frontend/vite.config.ts`
- **State Persistence**: Dashboard state saved in localStorage

## 🧪 API Endpoints

- `GET /api/predictions` - Get Nash equilibrium predictions
- `GET /api/market-data` - Get market data and prices
- `GET /api/geopolitical-events` - Get top 5 market-moving events
- `POST /api/backtest` - Start historical backtesting job
- `GET /api/backtest/status/{job_id}` - Get backtest job status
- `POST /api/sensitivity-analysis` - Run sensitivity analysis
- `GET /api/cache/stats` - Get cache statistics
- `DELETE /api/cache` - Clear cache

See full API documentation at http://localhost:8001/docs

## 📦 Dependencies

### Backend
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `numpy` - Numerical computations
- `pandas` - Data manipulation
- `yfinance` - Market data fetching
- `scipy` - Optimization algorithms

### Frontend
- `react` - UI framework
- `typescript` - Type safety
- `vite` - Build tool
- `tailwindcss` - Styling
- `@tanstack/react-query` - Data fetching
- `zustand` - State management
- `recharts` - Data visualization
- `axios` - HTTP client

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Market data provided by yfinance
- News sources: Reuters, Bloomberg, Financial Times
- Built with FastAPI, React, and modern web technologies

## 📧 Contact

For questions or issues, please open an issue on GitHub.

---

**Note**: This is a research/educational tool. Predictions are based on mathematical models and should not be used as financial advice.

