import os
import sys
import json
from pathlib import Path
import shutil
from datetime import datetime

# Add the project root to sys.path to make imports work
sys.path.insert(0, os.path.abspath('.'))

# Local imports
from src.tools.api import (
    get_prices,
    get_financial_metrics,
    search_line_items,
    get_insider_trades,
    get_company_news,
)
from src.data.cache import get_cache

def clear_cache_directory():
    """Clear the cache directory for testing purposes."""
    cache_dir = Path("./data")
    if cache_dir.exists():
        print(f"Clearing cache directory: {cache_dir}")
        shutil.rmtree(cache_dir)

def test_persistent_cache():
    """Test that the persistent cache is working correctly."""
    # Parameters for testing
    ticker = "AAPL"
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = "2023-01-01"
    
    # Clear any existing cache
    clear_cache_directory()
    
    print(f"\n--- Testing Persistent Cache for {ticker} ---")
    
    # First API call - should fetch from API and cache results
    print("\n1. Initial API Call (should fetch from API):")
    
    # Test prices
    print("\nTesting prices:")
    prices = get_prices(ticker, start_date, end_date)
    print(f"Retrieved {len(prices)} price records")
    
    # Test financial metrics
    print("\nTesting financial metrics:")
    metrics = get_financial_metrics(ticker, end_date)
    print(f"Retrieved {len(metrics)} financial metric records")
    
    # Test line items
    print("\nTesting line items:")
    line_items = ["revenue", "net_income", "total_assets"]
    items = search_line_items(ticker, line_items, end_date)
    print(f"Retrieved {len(items)} line item records")
    
    # Test insider trades
    print("\nTesting insider trades:")
    trades = get_insider_trades(ticker, end_date, start_date)
    print(f"Retrieved {len(trades)} insider trade records")
    
    # Test company news
    print("\nTesting company news:")
    news = get_company_news(ticker, end_date, start_date)
    print(f"Retrieved {len(news)} company news records")
    
    # Verify cache files exist
    cache_dir = Path(f"./data/{ticker}")
    print(f"\nVerifying cache files in {cache_dir}:")
    
    expected_files = [
        "prices.json",
        "financial_metrics.json", 
        "line_items.json", 
        "insider_trades.json", 
        "company_news.json"
    ]
    
    for file in expected_files:
        path = cache_dir / file
        if path.exists():
            print(f"✅ {file} exists with size {path.stat().st_size} bytes")
        else:
            print(f"❌ {file} does not exist")
    
    # Second API call - should use cached data
    print("\n2. Second API Call (should use cache):")
    
    # Test prices again
    print("\nTesting prices again:")
    prices2 = get_prices(ticker, start_date, end_date)
    print(f"Retrieved {len(prices2)} price records from cache")
    
    # Test line items again - critical since this was not cached before
    print("\nTesting line items again:")
    items2 = search_line_items(ticker, line_items, end_date)
    print(f"Retrieved {len(items2)} line item records from cache")
    
    print("\n--- Persistent Cache Test Complete ---")

if __name__ == "__main__":
    test_persistent_cache()