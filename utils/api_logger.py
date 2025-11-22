"""
API Request/Response Logger for persistent history tracking.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from utils.paths import get_api_history_dir


class APILogger:
    def __init__(self):
        self.history_dir = get_api_history_dir()
        self.history_dir.mkdir(parents=True, exist_ok=True)
    
    def log_request(self, endpoint: str, method: str, params: Dict[str, Any], 
                   response: Dict[str, Any], status_code: int = 200,
                   response_time_ms: Optional[float] = None):
        """
        Log an API request and response.
        
        Parameters:
        -----------
        endpoint : str
            API endpoint path
        method : str
            HTTP method (GET, POST, etc.)
        params : dict
            Request parameters
        response : dict
            Response data
        status_code : int
            HTTP status code
        response_time_ms : float, optional
            Response time in milliseconds
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "params": params,
            "status_code": status_code,
            "response_time_ms": response_time_ms,
            "response_size": len(json.dumps(response)) if response else 0
        }
        
        # Save to daily log file
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = self.history_dir / f"api_history_{date_str}.jsonl"
        
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Warning: Could not log API request: {e}")
    
    def get_history(self, date: Optional[str] = None, endpoint: Optional[str] = None):
        """
        Retrieve API history.
        
        Parameters:
        -----------
        date : str, optional
            Date in YYYY-MM-DD format. If None, uses today.
        endpoint : str, optional
            Filter by endpoint. If None, returns all endpoints.
        
        Returns:
        --------
        list
            List of log entries
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        log_file = self.history_dir / f"api_history_{date}.jsonl"
        
        if not log_file.exists():
            return []
        
        entries = []
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    entry = json.loads(line.strip())
                    if endpoint is None or entry.get('endpoint') == endpoint:
                        entries.append(entry)
        except Exception as e:
            print(f"Warning: Could not read API history: {e}")
        
        return entries
    
    def get_stats(self, date: Optional[str] = None):
        """
        Get statistics for API usage.
        
        Parameters:
        -----------
        date : str, optional
            Date in YYYY-MM-DD format. If None, uses today.
        
        Returns:
        --------
        dict
            Statistics including total requests, average response time, etc.
        """
        entries = self.get_history(date)
        
        if not entries:
            return {
                "total_requests": 0,
                "avg_response_time_ms": 0,
                "endpoints": {}
            }
        
        total_requests = len(entries)
        response_times = [e.get('response_time_ms', 0) for e in entries if e.get('response_time_ms')]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        endpoint_counts = {}
        for entry in entries:
            ep = entry.get('endpoint', 'unknown')
            endpoint_counts[ep] = endpoint_counts.get(ep, 0) + 1
        
        return {
            "total_requests": total_requests,
            "avg_response_time_ms": avg_response_time,
            "endpoints": endpoint_counts
        }


# Global API logger instance
_api_logger_instance = None

def get_api_logger():
    """Get or create the global API logger instance."""
    global _api_logger_instance
    if _api_logger_instance is None:
        _api_logger_instance = APILogger()
    return _api_logger_instance

