"""
Cache Management Utility

Use this script to manage the market data cache:
- View cache statistics
- Clear cache (all or old entries)
- Inspect cached data
"""

import argparse
from data_cache import get_cache
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(description='Manage market data cache')
    parser.add_argument('--stats', action='store_true', help='Show cache statistics')
    parser.add_argument('--clear', action='store_true', help='Clear all cache')
    parser.add_argument('--clear-old', type=int, metavar='DAYS', 
                       help='Clear cache entries older than N days')
    
    args = parser.parse_args()
    
    cache = get_cache()
    
    if args.stats or (not args.clear and not args.clear_old):
        # Show stats by default
        stats = cache.get_stats()
        print("="*60)
        print("MARKET DATA CACHE STATISTICS")
        print("="*60)
        print(f"Total entries: {stats['total_entries']}")
        print(f"Total size: {stats['total_size_mb']:.2f} MB")
        print(f"Cache directory: {stats['cache_dir']}")
        print()
        
        if stats['total_entries'] > 0:
            print("Cache is active. Subsequent backtests will use cached data.")
            print("This significantly speeds up repeated runs.")
        else:
            print("Cache is empty. First run will download all data.")
    
    if args.clear:
        cache.clear()
        print("Cache cleared successfully.")
    
    if args.clear_old:
        cache.clear(older_than_days=args.clear_old)
        print(f"Cleared cache entries older than {args.clear_old} days.")
        stats = cache.get_stats()
        print(f"Remaining entries: {stats['total_entries']}")


if __name__ == "__main__":
    main()



