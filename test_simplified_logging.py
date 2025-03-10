import os
import sys
import io
import json
import re
from pathlib import Path
from datetime import datetime
from tabulate import tabulate


def strip_ansi_codes(text):
    """Remove ANSI color codes for writing to plain text files."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def ensure_report_directory(ticker):
    """
    Ensure that the report directory exists for a given ticker.
    
    Args:
        ticker (str): The ticker symbol
        
    Returns:
        Path: Path object pointing to the report directory
    """
    report_dir = Path(f"./data/{ticker}/reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir


def save_output_to_file(ticker, content):
    """
    Save content to a dated log file in the ticker's reports directory.
    
    Args:
        ticker (str): The ticker symbol
        content (str): The content to save (without ANSI color codes)
    """
    report_dir = ensure_report_directory(ticker)
    
    # Generate filename with current date and time
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{timestamp}.txt"
    file_path = report_dir / filename
    
    # Remove ANSI color codes for clean log files
    clean_content = strip_ansi_codes(content)
    
    # Write to file
    with open(file_path, 'w') as f:
        f.write(clean_content)
    
    print(f"\nLog saved to: {file_path}")


def test_logging():
    """Test the logging functionality with simplified mocked data."""
    # Create a small mock result
    mock_result = {
        "AAPL": {
            "action": "BUY",
            "quantity": 10,
            "confidence": 85.5,
            "reason": "Strong fundamentals and positive technical indicators."
        },
        "GOOGL": {
            "action": "HOLD",
            "quantity": 0,
            "confidence": 60.0,
            "reason": "Market uncertainty suggests holding current position."
        }
    }
    
    # Mock model information
    model_name = "anthropic/claude-3.7-sonnet:thinking"
    
    # Generate simple output
    output = f"AI Hedge Fund Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {model_name}\n\n"
    
    for ticker, decision in mock_result.items():
        output += f"\nAnalysis for {ticker}\n"
        output += f"{'=' * 50}\n\n"
        
        output += f"TRADING DECISION: [{ticker}]\n"
        decision_data = [
            ["Action", decision["action"]],
            ["Quantity", decision["quantity"]],
            ["Confidence", f"{decision['confidence']}%"],
        ]
        output += tabulate(decision_data, tablefmt="grid", colalign=("left", "right"))
        
        output += f"\n\nReasoning: {decision['reason']}\n"
    
    # Print the output to console
    print(output)
    
    # Save the output to files for each ticker
    for ticker in mock_result.keys():
        save_output_to_file(ticker, output)
    
    # Verify that the files were created
    print("\nVerifying log files:")
    for ticker in mock_result.keys():
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