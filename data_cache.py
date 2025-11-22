"""
Data Cache Manager for Market Data

Caches yfinance data to avoid redundant downloads and speed up backtesting.
"""

import os
import pickle
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pathlib import Path


class MarketDataCache:
    def __init__(self, cache_dir=".market_data_cache"):
        """
        Initialize the cache manager.
        
        Parameters:
        -----------
        cache_dir : str
            Directory to store cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_index_file = self.cache_dir / "cache_index.pkl"
        self.cache_index = self._load_index()
    
    def _load_index(self):
        """Load the cache index (metadata about cached data)."""
        if self.cache_index_file.exists():
            try:
                with open(self.cache_index_file, 'rb') as f:
                    return pickle.load(f)
            except:
                return {}
        return {}
    
    def _save_index(self):
        """Save the cache index."""
        try:
            with open(self.cache_index_file, 'wb') as f:
                pickle.dump(self.cache_index, f)
        except Exception as e:
            print(f"Warning: Could not save cache index: {e}")
    
    def _get_cache_key(self, ticker, start_date, end_date):
        """Generate a cache key for a ticker and date range."""
        start_str = start_date.strftime('%Y%m%d')
        end_str = end_date.strftime('%Y%m%d')
        key_str = f"{ticker}_{start_str}_{end_str}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cache_file(self, cache_key):
        """Get the file path for a cache key."""
        return self.cache_dir / f"{cache_key}.pkl"
    
    def get(self, ticker, start_date, end_date):
        """
        Get data from cache if available.
        
        Parameters:
        -----------
        ticker : str
            Stock ticker symbol
        start_date : datetime
            Start date
        end_date : datetime
            End date
        
        Returns:
        --------
        DataFrame or None if not in cache
        """
        cache_key = self._get_cache_key(ticker, start_date, end_date)
        
        if cache_key in self.cache_index:
            cache_file = self._get_cache_file(cache_key)
            if cache_file.exists():
                try:
                    with open(cache_file, 'rb') as f:
                        data = pickle.load(f)
                    # Verify the data covers the requested range
                    if data is not None and not data.empty:
                        data_start = data.index.min().to_pydatetime() if hasattr(data.index.min(), 'to_pydatetime') else data.index.min()
                        data_end = data.index.max().to_pydatetime() if hasattr(data.index.max(), 'to_pydatetime') else data.index.max()
                        
                        # Check if cached data covers the requested range (with some tolerance)
                        if data_start <= start_date + timedelta(days=2) and data_end >= end_date - timedelta(days=2):
                            return data
                except Exception as e:
                    # If cache file is corrupted, remove it from index
                    if cache_file.exists():
                        cache_file.unlink()
                    del self.cache_index[cache_key]
                    self._save_index()
        
        return None
    
    def put(self, ticker, start_date, end_date, data):
        """
        Store data in cache.
        
        Parameters:
        -----------
        ticker : str
            Stock ticker symbol
        start_date : datetime
            Start date
        end_date : datetime
            End date
        data : DataFrame
            Data to cache
        """
        if data is None or data.empty:
            return
        
        cache_key = self._get_cache_key(ticker, start_date, end_date)
        cache_file = self._get_cache_file(cache_key)
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            
            # Update index
            self.cache_index[cache_key] = {
                'ticker': ticker,
                'start_date': start_date,
                'end_date': end_date,
                'cached_date': datetime.now(),
                'rows': len(data)
            }
            self._save_index()
        except Exception as e:
            print(f"Warning: Could not cache data for {ticker}: {e}")
    
    def clear(self, older_than_days=None):
        """
        Clear cache, optionally only entries older than specified days.
        
        Parameters:
        -----------
        older_than_days : int, optional
            Only clear entries older than this many days. If None, clear all.
        """
        if older_than_days is None:
            # Clear everything
            for cache_key in list(self.cache_index.keys()):
                cache_file = self._get_cache_file(cache_key)
                if cache_file.exists():
                    cache_file.unlink()
            self.cache_index = {}
            self._save_index()
        else:
            # Clear old entries
            cutoff_date = datetime.now() - timedelta(days=older_than_days)
            to_remove = []
            for cache_key, metadata in self.cache_index.items():
                if metadata['cached_date'] < cutoff_date:
                    cache_file = self._get_cache_file(cache_key)
                    if cache_file.exists():
                        cache_file.unlink()
                    to_remove.append(cache_key)
            
            for key in to_remove:
                del self.cache_index[key]
            self._save_index()
    
    def get_stats(self):
        """Get cache statistics."""
        total_files = len(self.cache_index)
        total_size = sum(
            self._get_cache_file(key).stat().st_size 
            for key in self.cache_index 
            if self._get_cache_file(key).exists()
        )
        return {
            'total_entries': total_files,
            'total_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir)
        }


# Global cache instance
_global_cache = None

def get_cache():
    """Get or create the global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = MarketDataCache()
    return _global_cache



