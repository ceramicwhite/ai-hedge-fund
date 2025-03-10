import sys
import json
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, ".")

# Import the necessary modules
from src.utils.display import print_trading_output, save_output_to_file

def test_logging():
    """Test the logging functionality."""
    # Create a small mock result
    mock_result = {
        "decisions": {
            "AAPL": {
                "action": "BUY",
                "quantity": 10,
                "confidence": 85.5,
                "reasoning": "Strong fundamentals and positive technical indicators."
            },
            "GOOGL": {
                "action": "HOLD",
                "quantity": 0,
                "confidence": 60.0,
                "reasoning": "Market uncertainty suggests holding current position."
            }
        },
        "analyst_signals": {
            "fundamentals_agent": {
                "AAPL": {
                    "signal": "bullish",
                    "confidence": 80,
                    "reasoning": {}
                },
                "GOOGL": {
                    "signal": "neutral",
                    "confidence": 55,
                    "reasoning": {}
                }
            },
            "technicals_agent": {
                "AAPL": {
                    "signal": "bullish",
                    "confidence": 90,
                    "reasoning": {}
                },
                "GOOGL": {
                    "signal": "neutral",
                    "confidence": 65,
                    "reasoning": {}
                }
            }
        }
    }
    
    # Print and capture the output
    output = print_trading_output(mock_result)
    
    # Save the output to files for each ticker
    for ticker in mock_result["decisions"].keys():
        save_output_to_file(ticker, output)
    
    # Verify that the files were created
    print("\nVerifying log files:")
    for ticker in mock_result["decisions"].keys():
        report_dir = Path(f"./data/{ticker}/reports")
        if report_dir.exists():
            log_files = list(report_dir.glob("*.txt"))
            if log_files:
                latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
                print(f"✅ Log file created for {ticker}: {latest_log.name}")
                
                # Read the first few lines to verify content
                with open(latest_log, 'r') as f:
                    head = ''.join([f.readline() for _ in range(5)])
                print(f"  Preview: {head[:100]}...")
            else:
                print(f"❌ No log files found for {ticker}")
        else:
            print(f"❌ Report directory not created for {ticker}")
    
    print("\nTest completed.")

if __name__ == "__main__":
    test_logging()