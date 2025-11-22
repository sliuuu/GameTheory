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
    def __init__(self, cache_dir=None):
        """
        Initialize the cache manager.
        
        Parameters:
        -----------
        cache_dir : str, optional
            Directory to store cache files. If None, uses environment variable
            CACHE_DIR or defaults to ".market_data_cache"
        """
        if cache_dir is None:
            cache_dir = os.getenv("CACHE_DIR", ".market_data_cache")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
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
        key_str = f"{ticker}_{start_date}_{end_date}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cache_file(self, cache_key):
        """Get the file path for a cache key."""
        return self.cache_dir / f"{cache_key}.pkl"
    
    def get(self, ticker, start_date, end_date):
        """
        Get cached data for a ticker and date range.
        
        Parameters:
        -----------
        ticker : str
            Stock ticker symbol
        start_date : datetime or str
            Start date
        end_date : datetime or str
            End date
        
        Returns:
        --------
        pd.DataFrame or None
            Cached data if available, None otherwise
        """
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        cache_key = self._get_cache_key(ticker, start_date, end_date)
        
        if cache_key in self.cache_index:
            cache_file = self._get_cache_file(cache_key)
            if cache_file.exists():
                try:
                    with open(cache_file, 'rb') as f:
                        data = pickle.load(f)
                    # Verify the data matches the requested range
                    if data is not None and not data.empty:
                        data_start = data.index.min()
                        data_end = data.index.max()
                        if data_start <= start_date and data_end >= end_date:
                            return data
                except Exception as e:
                    print(f"Warning: Could not load cache file {cache_file}: {e}")
                    # Remove from index if file is corrupted
                    del self.cache_index[cache_key]
                    self._save_index()
        
        return None
    
    def put(self, ticker, start_date, end_date, data):
        """
        Cache data for a ticker and date range.
        
        Parameters:
        -----------
        ticker : str
            Stock ticker symbol
        start_date : datetime or str
            Start date
        end_date : datetime or str
            End date
        data : pd.DataFrame
            Data to cache
        """
        if data is None or data.empty:
            return
        
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
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
                'cached_at': datetime.now(),
                'file_size': cache_file.stat().st_size
            }
            self._save_index()
        except Exception as e:
            print(f"Warning: Could not save cache file {cache_file}: {e}")
    
    def clear(self, older_than_days=None):
        """
        Clear cache entries.
        
        Parameters:
        -----------
        older_than_days : int, optional
            If provided, only clear entries older than this many days
        """
        if older_than_days is None:
            # Clear all
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
                if metadata.get('cached_at', datetime.now()) < cutoff_date:
                    cache_file = self._get_cache_file(cache_key)
                    if cache_file.exists():
                        cache_file.unlink()
                    to_remove.append(cache_key)
            
            for cache_key in to_remove:
                del self.cache_index[cache_key]
            
            if to_remove:
                self._save_index()
    
    def get_stats(self):
        """Get cache statistics."""
        total_size = 0
        total_entries = len(self.cache_index)
        
        for cache_key in self.cache_index:
            cache_file = self._get_cache_file(cache_key)
            if cache_file.exists():
                total_size += cache_file.stat().st_size
        
        return {
            'total_entries': total_entries,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir)
        }


# Global cache instance
_cache_instance = None

def get_cache(cache_dir=None):
    """Get or create the global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = MarketDataCache(cache_dir)
    return _cache_instance
