"""
FastAPI Backend for Geopolitical Market Game Tracker

This provides REST API endpoints for the React frontend.
Run with: uvicorn api_backend:app --reload --port 8001
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional, Dict
import numpy as np
import warnings
import asyncio
from concurrent.futures import ThreadPoolExecutor
warnings.filterwarnings("ignore")

from gametheory import GeopoliticalMarketGame
from historical_backtesting import GeopoliticalMarketGameBacktester
from optimized_gametheory import OptimizedGeopoliticalGame, EquilibriumType
from data_cache import get_cache
from job_manager import get_job_manager, JobStatus
from geopolitical_events import GeopoliticalEventsSource

app = FastAPI(title="Geopolitical Market Game API", version="1.0.0")

# Enable CORS for React frontend
# In Docker, frontend is served from nginx on port 80
import os
cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://localhost:80,http://localhost"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize game instances (will create fresh instances per request to avoid state issues)
# Note: For production, consider using dependency injection or request-scoped instances


# ============================================================================
# PYDANTIC MODELS (Request/Response Schemas)
# ============================================================================

class MarketDataResponse(BaseModel):
    date: str
    data: dict
    returns: dict
    prices: Optional[Dict[str, float]] = None  # Actual index prices
    country_proxies: Optional[Dict[str, Dict[str, str]]] = None  # Country to index mapping

class PredictionResponse(BaseModel):
    date: str
    strategies: List[List[float]]  # 5x4 matrix
    parties: List[str]
    actions: List[str]
    dominant_actions: List[str]
    global_scenario: str
    market_context: dict
    prices: Optional[Dict[str, float]] = None  # Actual index prices
    country_proxies: Optional[Dict[str, Dict[str, str]]] = None  # Country to index mapping

class BacktestRequest(BaseModel):
    start_date: str
    end_date: str
    freq: Optional[str] = "W-FRI"

class BacktestResponse(BaseModel):
    results: List[dict]
    summary: dict
    total_weeks: int
    accuracy: float

class BacktestJobResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: float
    current_step: str
    current_step_num: int
    total_steps: int
    result: Optional[dict] = None
    error: Optional[str] = None

class SensitivityRequest(BaseModel):
    noise_levels: Optional[List[float]] = None
    n_runs: Optional[int] = 100

class SensitivityResponse(BaseModel):
    results: List[dict]
    plot_url: Optional[str] = None

class OptimizedAnalysisRequest(BaseModel):
    equilibrium_type: Optional[str] = "nash"  # "nash", "bayesian", "repeated_game"
    date: Optional[str] = None

class OptimizedAnalysisResponse(BaseModel):
    date: str
    equilibrium_type: str
    strategies: List[List[float]]
    dominant_actions: List[str]
    action_probabilities: dict
    explanations: dict
    comparison: str
    capabilities: dict
    alliances: List[dict]


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Geopolitical Market Game API",
        "version": "1.0.0",
        "endpoints": [
            "/api/market-data",
            "/api/predictions",
            "/api/backtest",
            "/api/sensitivity-analysis",
            "/api/optimized-analysis",
            "/api/cache/stats"
        ]
    }


@app.get("/api/market-data")
async def get_market_data(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    days: int = Query(14, description="Number of days for return calculation")
):
    """
    Get market data for a specific date.
    If no date provided, uses current date.
    """
    try:
        # Create fresh game instance for each request
        game = GeopoliticalMarketGame()
        
        if date:
            game.current_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            game.current_date = datetime.now()
        
        market_data, prices = game.fetch_real_time_data(days=days, include_prices=True)
        
        # Calculate returns
        returns = {k: v * 100 for k, v in market_data.items()}  # Convert to percentage
        
        # Define country to index proxy mapping
        country_proxies = {
            "USA": {
                "index": "S&P 500",
                "ticker": "^GSPC",
                "symbol": "SP500"
            },
            "China": {
                "index": "SSE Composite",
                "ticker": "000001.SS",
                "symbol": "China"
            },
            "Japan": {
                "index": "Nikkei 225",
                "ticker": "^N225",
                "symbol": "Nikkei225"
            },
            "Germany": {
                "index": "DAX",
                "ticker": "^GDAXI",
                "symbol": "DAX"
            },
            "Taiwan": {
                "index": "TAIEX",
                "ticker": "^TWII",
                "symbol": "TAIEX"
            }
        }
        
        return MarketDataResponse(
            date=game.current_date.strftime("%Y-%m-%d"),
            data=market_data,
            returns=returns,
            prices=prices,
            country_proxies=country_proxies
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class NewsSource(BaseModel):
    name: str
    url: str

class GeopoliticalEvent(BaseModel):
    date: str
    type: str
    title: str
    description: str
    impact: str
    countries: List[str]
    market_impact: str
    relevance_score: float
    news_sources: Optional[List[NewsSource]] = None


class GeopoliticalEventsResponse(BaseModel):
    date: str
    events: List[GeopoliticalEvent]


@app.get("/api/geopolitical-events", response_model=GeopoliticalEventsResponse)
async def get_geopolitical_events(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format")
):
    """
    Get top 5 market-moving geopolitical events for the specified date.
    Events are inferred from market conditions and patterns.
    """
    try:
        # Create fresh game instance
        game = GeopoliticalMarketGame()
        
        if date:
            game.current_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            game.current_date = datetime.now()
        
        # Get market data to infer events
        market_data = game.fetch_real_time_data(days=14, use_cache=True)
        
        # Generate events based on market conditions
        events_source = GeopoliticalEventsSource()
        events = events_source.get_events(market_data, game.current_date)
        
        return GeopoliticalEventsResponse(
            date=game.current_date.strftime("%Y-%m-%d"),
            events=[GeopoliticalEvent(**event) for event in events]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/predictions")
async def get_predictions(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    use_optimized: bool = Query(False, description="Use optimized model with country-specific constraints")
):
    """
    Get Nash equilibrium predictions for a specific date.
    Can use either basic or optimized model.
    """
    try:
        if use_optimized:
            # Use optimized model with country-specific constraints
            game = OptimizedGeopoliticalGame()
        else:
            # Use basic model (improved)
            game = GeopoliticalMarketGame()
        
        if date:
            game.current_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            game.current_date = datetime.now()
        
        # Get market context and prices in a single call (optimized)
        market_data, prices = game.fetch_real_time_data(days=14, use_cache=True, include_prices=True)
        market_context = {k: v * 100 for k, v in market_data.items()}
        
        # Define country to index proxy mapping
        country_proxies = {
            "USA": {
                "index": "S&P 500",
                "ticker": "^GSPC",
                "symbol": "SP500"
            },
            "China": {
                "index": "SSE Composite",
                "ticker": "000001.SS",
                "symbol": "China"
            },
            "Japan": {
                "index": "Nikkei 225",
                "ticker": "^N225",
                "symbol": "Nikkei225"
            },
            "Germany": {
                "index": "DAX",
                "ticker": "^GDAXI",
                "symbol": "DAX"
            },
            "Taiwan": {
                "index": "TAIEX",
                "ticker": "^TWII",
                "symbol": "TAIEX"
            }
        }
        
        # Build payoff matrix and solve
        P = game.build_current_payoff_matrix()
        strategies = game.solve_nash_equilibrium(P)
        
        # Determine dominant actions
        # Optimized model uses action_labels dict, basic model uses actions list
        if use_optimized and hasattr(game, 'action_labels'):
            actions_list = [game.action_labels[i] for i in range(4)]
            dominant_actions = [
                game.action_labels[np.argmax(strat)] 
                for strat in strategies
            ]
        else:
            actions_list = game.actions
            dominant_actions = [
                game.actions[np.argmax(strat)] 
                for strat in strategies
            ]
        
        # Global scenario
        scenario_counts = np.zeros(4)
        for i in range(5):
            scenario_counts[np.argmax(strategies[i])] += 1
        global_dominant = np.argmax(scenario_counts)
        global_scenario = actions_list[global_dominant]
        
        return PredictionResponse(
            date=game.current_date.strftime("%Y-%m-%d"),
            strategies=strategies.tolist(),
            parties=game.parties,
            actions=actions_list,
            dominant_actions=dominant_actions,
            global_scenario=global_scenario,
            market_context=market_context,
            prices=prices,
            country_proxies=country_proxies
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/backtest", response_model=BacktestJobResponse)
async def run_backtest(request: BacktestRequest):
    """
    Start a historical backtest job. Returns a job_id for tracking progress.
    Use /api/backtest/status/{job_id} to check progress.
    """
    try:
        job_manager = get_job_manager()
        
        # Create job
        job_id = job_manager.create_job(
            job_type="backtest",
            params={
                "start_date": request.start_date,
                "end_date": request.end_date,
                "freq": request.freq
            }
        )
        
        # Run backtest in background thread
        def run_backtest_task():
            try:
                job_manager.set_status(job_id, JobStatus.RUNNING)
                
                # Create fresh backtester instance
                backtester = GeopoliticalMarketGameBacktester(use_cache=True)
                
                # Progress callback
                def progress_callback(progress, step, current, total):
                    job_manager.update_progress(job_id, progress, step, current, total)
                
                # Run backtest
                results_df = backtester.run_backtest(
                    start_date=request.start_date,
                    end_date=request.end_date,
                    freq=request.freq,
                    progress_callback=progress_callback
                )
                
                # Get summary
                backtester.backtest_results = results_df
                accuracy = (results_df['hawk_dominant'] == results_df['actual_risk_off_next_week']).mean()
                
                # Convert to list of dicts
                results = results_df.to_dict('records')
                for r in results:
                    if isinstance(r['date'], datetime):
                        r['date'] = r['date'].isoformat()
                
                summary = {
                    "total_weeks": len(results_df),
                    "accuracy": float(accuracy),
                    "hawk_weeks_predicted": int(results_df['hawk_dominant'].sum()),
                    "actual_risk_off_weeks": int(results_df['actual_risk_off_next_week'].sum()),
                }
                
                result = {
                    "results": results,
                    "summary": summary,
                    "total_weeks": len(results_df),
                    "accuracy": float(accuracy)
                }
                
                job_manager.set_status(job_id, JobStatus.COMPLETED, result=result)
            except Exception as e:
                job_manager.set_status(job_id, JobStatus.FAILED, error=str(e))
        
        # Start background task
        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(run_backtest_task)
        
        return BacktestJobResponse(
            job_id=job_id,
            status="pending",
            message="Backtest job started. Use /api/backtest/status/{job_id} to check progress."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/backtest/status/{job_id}", response_model=JobStatusResponse)
async def get_backtest_status(job_id: str):
    """
    Get the status of a backtest job.
    """
    try:
        job_manager = get_job_manager()
        job = job_manager.get_job(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return JobStatusResponse(
            job_id=job.job_id,
            status=job.status.value,
            progress=job.progress,
            current_step=job.current_step,
            current_step_num=job.current_step_num,
            total_steps=job.total_steps,
            result=job.result,
            error=job.error
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sensitivity-analysis", response_model=SensitivityResponse)
async def run_sensitivity_analysis(request: SensitivityRequest):
    """
    Run sensitivity analysis on current predictions.
    """
    try:
        # Create fresh backtester instance
        backtester = GeopoliticalMarketGameBacktester(use_cache=True)
        
        # Set current date (use today or most recent market data)
        backtester.current_date = datetime.now()
        
        # Run sensitivity analysis
        if request.noise_levels is None:
            import numpy as np
            noise_levels = np.linspace(0.0, 1.0, 11).tolist()
        else:
            noise_levels = request.noise_levels
        
        results_df = backtester.sensitivity_analysis(
            noise_levels=noise_levels,
            n_runs=request.n_runs
        )
        
        if results_df is None or results_df.empty:
            raise HTTPException(status_code=500, detail="Sensitivity analysis failed")
        
        # Convert to list of dicts
        results = results_df.to_dict('records')
        for r in results:
            # Convert numpy types to Python types
            for k, v in r.items():
                if hasattr(v, 'item'):  # numpy scalar
                    r[k] = float(v)
        
        return SensitivityResponse(
            results=results,
            plot_url=None  # Could save plot and return URL
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/optimized-analysis", response_model=OptimizedAnalysisResponse)
async def get_optimized_analysis(request: OptimizedAnalysisRequest):
    """
    Get optimized geopolitical analysis with country-specific constraints,
    capabilities, alliances, and multiple equilibrium types.
    """
    try:
        # Create optimized game instance
        game = OptimizedGeopoliticalGame()
        
        # Set date if provided
        if request.date:
            game.current_date = datetime.strptime(request.date, "%Y-%m-%d")
        else:
            game.current_date = datetime.now()
        
        # Determine equilibrium type
        eq_type_map = {
            "nash": EquilibriumType.NASH,
            "bayesian": EquilibriumType.BAYESIAN,
            "repeated_game": EquilibriumType.REPEATED_GAME
        }
        eq_type = eq_type_map.get(request.equilibrium_type.lower(), EquilibriumType.NASH)
        
        # Build payoff matrix and analyze
        P = game.build_current_payoff_matrix()
        analysis = game.analyze_equilibrium(P, eq_type)
        comparison = game.compare_countries(analysis)
        
        # Format capabilities
        capabilities_dict = {}
        for country, caps in game.capabilities.items():
            capabilities_dict[country] = {
                "economic_power": caps.economic_power,
                "military_power": caps.military_power,
                "diplomatic_influence": caps.diplomatic_influence,
                "domestic_stability": caps.domestic_stability,
                "export_dependency": caps.export_dependency,
                "energy_dependency": caps.energy_dependency,
                "tech_leadership": caps.tech_leadership,
                "alliance_strength": caps.alliance_strength,
                "constraint_tolerance": caps.constraint_tolerance,
                "available_actions": [game.action_labels[i] for i in game.strategy_sets[country]]
            }
        
        # Format alliances
        alliances_list = []
        for alliance in game.alliances:
            alliances_list.append({
                "country1": alliance.country1,
                "country2": alliance.country2,
                "strength": alliance.strength,
                "type": alliance.type
            })
        
        return OptimizedAnalysisResponse(
            date=game.current_date.strftime("%Y-%m-%d"),
            equilibrium_type=eq_type.value,
            strategies=analysis['strategies'].tolist(),
            dominant_actions=[game.action_labels[a] for a in analysis['dominant_actions']],
            action_probabilities=analysis['action_probabilities'],
            explanations=analysis['explanations'],
            comparison=comparison,
            capabilities=capabilities_dict,
            alliances=alliances_list
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    try:
        cache = get_cache()
        stats = cache.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/cache")
async def clear_cache(older_than_days: Optional[int] = None):
    """Clear cache, optionally only entries older than specified days"""
    try:
        cache = get_cache()
        cache.clear(older_than_days=older_than_days)
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

