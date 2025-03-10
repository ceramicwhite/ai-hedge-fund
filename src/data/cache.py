import os
import json
from pathlib import Path

class Cache:
    """Cache for API responses with persistent storage."""

    def __init__(self):
        self._base_dir = Path("./data")
        self._prices_cache: dict[str, list[dict[str, any]]] = {}
        self._financial_metrics_cache: dict[str, list[dict[str, any]]] = {}
        # Change line_items structure to support more complex queries
        self._line_items_cache: dict[str, dict[str, list[dict[str, any]]]] = {}
        self._insider_trades_cache: dict[str, list[dict[str, any]]] = {}
        self._company_news_cache: dict[str, list[dict[str, any]]] = {}
        
        # Initialize by loading cache from disk
        self._load_cache()
    
    def _ensure_ticker_dir(self, ticker: str) -> Path:
        """Ensure the ticker directory exists and return its path."""
        ticker_dir = self._base_dir / ticker
        ticker_dir.mkdir(parents=True, exist_ok=True)
        return ticker_dir
    
    def _load_cache(self):
        """Load cached data from disk for all tickers."""
        if not self._base_dir.exists():
            self._base_dir.mkdir(exist_ok=True)
            return
        
        # Load data for each ticker directory
        for ticker_dir in self._base_dir.iterdir():
            if not ticker_dir.is_dir():
                continue
            
            ticker = ticker_dir.name
            
            # Load prices
            self._load_file(ticker_dir / "prices.json", lambda data: self._prices_cache.update({ticker: data}))
            
            # Load financial metrics
            self._load_file(ticker_dir / "financial_metrics.json", lambda data: self._financial_metrics_cache.update({ticker: data}))
            
            # Load line items - different structure
            self._load_file(ticker_dir / "line_items.json", lambda data: self._line_items_cache.update({ticker: data}))
            
            # Load insider trades
            self._load_file(ticker_dir / "insider_trades.json", lambda data: self._insider_trades_cache.update({ticker: data}))
            
            # Load company news
            self._load_file(ticker_dir / "company_news.json", lambda data: self._company_news_cache.update({ticker: data}))
    
    def _load_file(self, file_path: Path, update_func):
        """Load a JSON file and update cache with its data."""
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                update_func(data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading cache file {file_path}: {e}")
    
    def _save_file(self, file_path: Path, data):
        """Save data to a JSON file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Error saving cache file {file_path}: {e}")

    def _merge_data(self, existing: list[dict] | None, new_data: list[dict], key_field: str) -> list[dict]:
        """Merge existing and new data, avoiding duplicates based on a key field."""
        if not existing:
            return new_data
        
        # Create a set of existing keys for O(1) lookup
        existing_keys = {item[key_field] for item in existing}
        
        # Only add items that don't exist yet
        merged = existing.copy()
        merged.extend([item for item in new_data if item[key_field] not in existing_keys])
        return merged

    def get_prices(self, ticker: str) -> list[dict[str, any]] | None:
        """Get cached price data if available."""
        return self._prices_cache.get(ticker)

    def set_prices(self, ticker: str, data: list[dict[str, any]]):
        """Append new price data to cache and save to disk."""
        self._prices_cache[ticker] = self._merge_data(
            self._prices_cache.get(ticker),
            data,
            key_field="time"
        )
        
        # Save to disk
        ticker_dir = self._ensure_ticker_dir(ticker)
        self._save_file(ticker_dir / "prices.json", self._prices_cache[ticker])

    def get_financial_metrics(self, ticker: str) -> list[dict[str, any]]:
        """Get cached financial metrics if available."""
        return self._financial_metrics_cache.get(ticker)

    def set_financial_metrics(self, ticker: str, data: list[dict[str, any]]):
        """Append new financial metrics to cache and save to disk."""
        self._financial_metrics_cache[ticker] = self._merge_data(
            self._financial_metrics_cache.get(ticker),
            data,
            key_field="report_period"
        )
        
        # Save to disk
        ticker_dir = self._ensure_ticker_dir(ticker)
        self._save_file(ticker_dir / "financial_metrics.json", self._financial_metrics_cache[ticker])

    def get_line_items(self, ticker: str, line_items: list[str], end_date: str, period: str = "ttm") -> list[dict[str, any]] | None:
        """Get cached line items if available for the specific query."""
        ticker_data = self._line_items_cache.get(ticker, {})
        if not ticker_data:
            return None
            
        # Create a key for this specific line items query
        query_key = f"{end_date}_{period}_{','.join(sorted(line_items))}"
        
        # Return cached data if available
        return ticker_data.get(query_key)
    
    def set_line_items(self, ticker: str, line_items: list[str], end_date: str, period: str, data: list[dict[str, any]]):
        """Add line items to cache and save to disk."""
        # Create a key for this specific line items query
        query_key = f"{end_date}_{period}_{','.join(sorted(line_items))}"
        
        # Initialize ticker dictionary if needed
        if ticker not in self._line_items_cache:
            self._line_items_cache[ticker] = {}
            
        # Store the data
        self._line_items_cache[ticker][query_key] = data
        
        # Save to disk
        ticker_dir = self._ensure_ticker_dir(ticker)
        self._save_file(ticker_dir / "line_items.json", self._line_items_cache[ticker])

    def get_insider_trades(self, ticker: str) -> list[dict[str, any]] | None:
        """Get cached insider trades if available."""
        return self._insider_trades_cache.get(ticker)

    def set_insider_trades(self, ticker: str, data: list[dict[str, any]]):
        """Append new insider trades to cache and save to disk."""
        self._insider_trades_cache[ticker] = self._merge_data(
            self._insider_trades_cache.get(ticker),
            data,
            key_field="filing_date"  # Could also use transaction_date if preferred
        )
        
        # Save to disk
        ticker_dir = self._ensure_ticker_dir(ticker)
        self._save_file(ticker_dir / "insider_trades.json", self._insider_trades_cache[ticker])

    def get_company_news(self, ticker: str) -> list[dict[str, any]] | None:
        """Get cached company news if available."""
        return self._company_news_cache.get(ticker)

    def set_company_news(self, ticker: str, data: list[dict[str, any]]):
        """Append new company news to cache and save to disk."""
        self._company_news_cache[ticker] = self._merge_data(
            self._company_news_cache.get(ticker),
            data,
            key_field="date"
        )
        
        # Save to disk
        ticker_dir = self._ensure_ticker_dir(ticker)
        self._save_file(ticker_dir / "company_news.json", self._company_news_cache[ticker])


# Global cache instance
_cache = Cache()


def get_cache() -> Cache:
    """Get the global cache instance."""
    return _cache
