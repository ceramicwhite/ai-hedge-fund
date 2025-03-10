"""
Simple HTML-based GUI for AI Hedge Fund.
This avoids the Pydantic schema generation errors encountered with Gradio 4.26.0.
"""

import os
import sys
import json
import http.server
import socketserver
import webbrowser
import threading
import urllib.parse
from pathlib import Path
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Add the src directory to the Python path to allow imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(src_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import project modules
from src.main import run_hedge_fund, create_workflow
from src.backtester import Backtester
from src.utils.analysts import ANALYST_ORDER
from src.utils.display import print_trading_output
from src.llm.models import get_llm_order, get_model_info
from src.utils.visualize import save_graph_as_png

# Global state to store analysis results
ANALYSIS_RESULTS = {}
BACKTEST_RESULTS = {}
LLM_MODELS = []

def initialize():
    """Initialize global data needed for the UI."""
    global LLM_MODELS
    
    # Get LLM models
    LLM_MODELS = [(display, value, provider) for display, value, provider in get_llm_order()]
    
    # Create data directories
    os.makedirs("./data/graphs", exist_ok=True)


class AIHedgeFundHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler for the AI Hedge Fund UI."""
    
    def __init__(self, *args, **kwargs):
        # Set directory for static files
        self.directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(self._get_html_content().encode())
        elif self.path == "/api/analysts":
            self._send_json_response(ANALYST_ORDER)
        elif self.path == "/api/models":
            self._send_json_response(LLM_MODELS)
        elif self.path == "/api/results":
            self._send_json_response(ANALYSIS_RESULTS)
        elif self.path == "/api/backtest":
            self._send_json_response(BACKTEST_RESULTS)
        elif self.path.startswith("/data/"):
            # Serve files from data directory
            file_path = self.path[1:]  # Remove leading slash
            if os.path.exists(file_path) and os.path.isfile(file_path):
                self.send_response(200)
                self.send_header("Content-type", self._get_content_type(file_path))
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
        elif self.path.startswith("/assets/"):
            # Serve static assets
            file_path = os.path.join(self.directory, self.path[8:])  # Remove "/assets/"
            if os.path.exists(file_path) and os.path.isfile(file_path):
                self.send_response(200)
                self.send_header("Content-type", self._get_content_type(file_path))
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = urllib.parse.parse_qs(post_data)
        
        if self.path == "/api/analyze":
            self._handle_analysis(params)
        elif self.path == "/api/backtest":
            self._handle_backtest(params)
        else:
            self.send_response(404)
            self.end_headers()
    
    def _get_content_type(self, path):
        """Get content type based on file extension."""
        ext = os.path.splitext(path)[1].lower()
        if ext == ".html":
            return "text/html"
        elif ext == ".css":
            return "text/css"
        elif ext == ".js":
            return "application/javascript"
        elif ext == ".json":
            return "application/json"
        elif ext == ".png":
            return "image/png"
        elif ext == ".jpg" or ext == ".jpeg":
            return "image/jpeg"
        elif ext == ".svg":
            return "image/svg+xml"
        else:
            return "application/octet-stream"
    
    def _send_json_response(self, data):
        """Send a JSON response."""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _handle_analysis(self, params):
        """Handle trading analysis request."""
        global ANALYSIS_RESULTS
        
        # Parse parameters
        tickers = params.get("tickers", [""])[0].split(",")
        tickers = [t.strip() for t in tickers if t.strip()]
        start_date = params.get("start_date", [""])[0]
        end_date = params.get("end_date", [""])[0]
        initial_cash = float(params.get("initial_cash", ["100000"])[0])
        margin_req = float(params.get("margin_req", ["0.0"])[0])
        selected_analysts = params.get("analysts", [])  # Get the list of all analysts
        model_name = params.get("model", ["gpt-4o"])[0]
        model_provider = params.get("provider", ["OpenAI"])[0]
        show_reasoning = params.get("show_reasoning", ["false"])[0].lower() == "true"
        show_graph = params.get("show_graph", ["false"])[0].lower() == "true"
        
        # Validate inputs
        if not tickers:
            self._send_json_response({"error": "Please enter at least one ticker symbol"})
            return
        
        if not selected_analysts:
            self._send_json_response({"error": "Please select at least one analyst"})
            return
        
        try:
            # Initialize portfolio
            portfolio = {
                "cash": initial_cash,
                "margin_requirement": margin_req,
                "positions": {
                    ticker: {
                        "long": 0,
                        "short": 0,
                        "long_cost_basis": 0.0,
                        "short_cost_basis": 0.0,
                    } for ticker in tickers
                },
                "realized_gains": {
                    ticker: {
                        "long": 0.0,
                        "short": 0.0,
                    } for ticker in tickers
                }
            }
            
            # Run the hedge fund
            result = run_hedge_fund(
                tickers=tickers,
                start_date=start_date,
                end_date=end_date,
                portfolio=portfolio,
                show_reasoning=show_reasoning,
                selected_analysts=selected_analysts,
                model_name=model_name,
                model_provider=model_provider,
            )
            
            # Store results
            ANALYSIS_RESULTS = result
            
            # Generate agent graph if requested
            if show_graph:
                workflow = create_workflow(selected_analysts)
                agent = workflow.compile()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"./data/graphs/{'_'.join(selected_analysts)}_{timestamp}_graph.png"
                save_graph_as_png(agent, file_path)
                ANALYSIS_RESULTS["graph_path"] = file_path
            
            self._send_json_response({"success": True})
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self._send_json_response({"error": str(e), "details": error_details})
    
    def _handle_backtest(self, params):
        """Handle backtesting request."""
        global BACKTEST_RESULTS
        
        # Parse parameters
        tickers = params.get("tickers", [""])[0].split(",")
        tickers = [t.strip() for t in tickers if t.strip()]
        start_date = params.get("start_date", [""])[0]
        end_date = params.get("end_date", [""])[0]
        initial_cash = float(params.get("initial_cash", ["100000"])[0])
        margin_req = float(params.get("margin_req", ["0.0"])[0])
        selected_analysts = params.get("analysts", [])  # Get the list of all analysts
        model_name = params.get("model", ["gpt-4o"])[0]
        model_provider = params.get("provider", ["OpenAI"])[0]
        
        # Validate inputs
        if not tickers:
            self._send_json_response({"error": "Please enter at least one ticker symbol"})
            return
        
        if not selected_analysts:
            self._send_json_response({"error": "Please select at least one analyst"})
            return
        
        try:
            # Create the backtest instance
            backtester = Backtester(
                agent=run_hedge_fund,
                tickers=tickers,
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_cash,
                model_name=model_name,
                model_provider=model_provider,
                selected_analysts=selected_analysts,
                initial_margin_requirement=margin_req,
            )
            
            # Run the backtest
            performance_metrics = backtester.run_backtest()
            performance_df = backtester.analyze_performance()
            
            # Store results
            BACKTEST_RESULTS = {
                "performance_metrics": performance_metrics,
                "portfolio_values": backtester.portfolio_values,
                "table_rows": backtester.table_rows if hasattr(backtester, 'table_rows') else []
            }
            
            self._send_json_response({"success": True})
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self._send_json_response({"error": str(e), "details": error_details})
    
    def _get_html_content(self):
        """Get the HTML content for the UI."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Hedge Fund</title>
    <style>
        :root {
            --color-green: #00FF00;
            --color-red: #FF0000;
            --color-yellow: #FFFF00;
            --color-cyan: #00FFFF;
            --color-white: #FFFFFF;
            --color-blue: #0000FF;
            --color-bg-dark: #1E1E1E;
            --color-bg-light: #2D2D2D;
            --color-border: #3E3E3E;
            --font-main: Arial, sans-serif;
        }
        
        body {
            font-family: var(--font-main);
            background-color: var(--color-bg-dark);
            color: var(--color-white);
            margin: 0;
            padding: 20px;
        }
        
        h1, h2, h3 {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .tabs {
            display: flex;
            margin-bottom: 20px;
        }
        
        .tab {
            flex: 1;
            padding: 10px;
            text-align: center;
            background-color: var(--color-bg-light);
            cursor: pointer;
            border: 1px solid var(--color-border);
        }
        
        .tab.active {
            background-color: var(--color-cyan);
            color: var(--color-bg-dark);
            font-weight: bold;
        }
        
        .tab-content {
            display: none;
            padding: 20px;
            background-color: var(--color-bg-light);
            border: 1px solid var(--color-border);
        }
        
        .tab-content.active {
            display: block;
        }
        
        .row {
            display: flex;
            margin-bottom: 20px;
        }
        
        .col {
            flex: 1;
            padding: 10px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
        }
        
        input[type="text"],
        input[type="number"],
        input[type="date"],
        select {
            width: 100%;
            padding: 8px;
            margin-bottom: 10px;
            background-color: var(--color-bg-dark);
            color: var(--color-white);
            border: 1px solid var(--color-border);
        }
        
        button {
            padding: 10px 15px;
            background-color: var(--color-cyan);
            color: var(--color-bg-dark);
            border: none;
            cursor: pointer;
            font-weight: bold;
        }
        
        button:hover {
            opacity: 0.8;
        }
        
        .checkbox-list {
            max-height: 200px;
            overflow-y: auto;
            border: 1px solid var(--color-border);
            padding: 10px;
            margin-bottom: 10px;
        }
        
        .checkbox-item {
            margin-bottom: 5px;
        }
        
        .results {
            margin-top: 20px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }
        
        th {
            background-color: var(--color-bg-dark);
            padding: 8px;
            text-align: left;
            border: 1px solid var(--color-border);
        }
        
        td {
            padding: 8px;
            border: 1px solid var(--color-border);
        }
        
        .bullish, .buy, .cover {
            color: var(--color-green);
        }
        
        .bearish, .sell, .short {
            color: var(--color-red);
        }
        
        .neutral, .hold {
            color: var(--color-yellow);
        }
        
        .status {
            padding: 10px;
            margin-bottom: 15px;
            border-radius: 4px;
        }
        
        /* Styling for detailed analyst outputs */
        .analyst-details {
            margin-top: 20px;
        }
        
        .agent-section {
            margin-bottom: 25px;
            border: 1px solid var(--color-border);
            border-radius: 4px;
            padding: 10px;
            background-color: rgba(0, 0, 0, 0.2);
        }
        
        .agent-section h3 {
            text-align: center;
            color: var(--color-cyan);
            border-bottom: 1px solid var(--color-border);
            padding-bottom: 5px;
            margin-top: 0;
        }
        
        .reasoning-details {
            padding: 10px;
        }
        
        .reasoning-section {
            margin-bottom: 15px;
        }
        
        .reasoning-section h4 {
            color: var(--color-white);
            margin-bottom: 5px;
        }
        
        .reasoning-text {
            white-space: pre-wrap;
            line-height: 1.5;
            padding: 10px;
            background-color: rgba(0, 0, 0, 0.1);
            border-radius: 4px;
        }
        
        .reasoning-section ul {
            margin-top: 5px;
            padding-left: 20px;
        }
        
        .reasoning-section li {
            margin-bottom: 5px;
        }
        
        /* For JSON-like display */
        pre.json {
            background-color: rgba(0, 0, 0, 0.2);
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            white-space: pre-wrap;
            font-family: monospace;
        }
        
        /* Analysis Results Display */
        .signals-summary {
            margin-bottom: 25px;
            border: 2px solid var(--color-border);
        }
        
        .signals-summary th {
            background-color: rgba(0, 255, 255, 0.1);
            font-weight: bold;
        }
        
        .portfolio-decision {
            background-color: rgba(0, 0, 0, 0.3);
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
            border-left: 5px solid var(--color-cyan);
        }
        
        .portfolio-decision h3 {
            color: var(--color-cyan);
            border-bottom: 1px solid var(--color-border);
            padding-bottom: 10px;
        }
        
        .portfolio-decision table {
            width: 50%;
            margin: 10px 0;
        }
        
        .agent-signal-table {
            width: 50%;
            margin: 10px 0;
            border: 1px solid var(--color-border);
        }
        
        .agent-signal-table td:first-child {
            font-weight: bold;
            width: 120px;
        }
        
        .error {
            background-color: rgba(255, 0, 0, 0.2);
            border: 1px solid var(--color-red);
        }
        
        .loading {
            background-color: rgba(255, 255, 0, 0.2);
            border: 1px solid var(--color-yellow);
        }
        
        .success {
            background-color: rgba(0, 255, 0, 0.2);
            border: 1px solid var(--color-green);
        }
        
        .hidden {
            display: none;
        }
        
        .ticker-tabs {
            display: flex;
            margin-bottom: 10px;
        }
        
        .ticker-tab {
            padding: 8px 15px;
            background-color: var(--color-bg-dark);
            cursor: pointer;
            border: 1px solid var(--color-border);
            margin-right: 5px;
        }
        
        .ticker-tab.active {
            background-color: var(--color-cyan);
            color: var(--color-bg-dark);
        }
        
        .ticker-content {
            display: none;
            padding: 15px;
            background-color: var(--color-bg-dark);
            border: 1px solid var(--color-border);
        }
        
        .ticker-content.active {
            display: block;
        }
        
        .chart-container {
            height: 400px;
            margin: 20px 0;
            background-color: var(--color-bg-dark);
            border: 1px solid var(--color-border);
            text-align: center;
            line-height: 400px;
        }
        
        #status-display {
            margin-bottom: 20px;
            padding: 10px;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Hedge Fund Analysis Platform</h1>
        <p>This platform uses AI-powered agents to analyze stocks and make trading decisions. Each agent specializes in different aspects of market analysis (fundamentals, technicals, sentiment, etc.).</p>
        
        <div class="tabs">
            <div class="tab active" data-tab="trading">Trading</div>
            <div class="tab" data-tab="backtesting">Backtesting</div>
            <div class="tab" data-tab="analytics">Analytics</div>
        </div>
        
        <div id="status-display" class="hidden"></div>
        
        <!-- Trading Tab -->
        <div id="trading-tab" class="tab-content active">
            <div class="row">
                <div class="col">
                    <h3>Trading Configuration</h3>
                    <label for="tickers">Ticker Symbols (comma-separated)</label>
                    <input type="text" id="tickers" placeholder="AAPL, MSFT, GOOG, etc.">
                    
                    <label for="start-date">Start Date</label>
                    <input type="date" id="start-date">
                    
                    <label for="end-date">End Date</label>
                    <input type="date" id="end-date">
                    
                    <label for="initial-cash">Initial Cash</label>
                    <input type="number" id="initial-cash" value="100000">
                    
                    <label for="margin-req">Margin Requirement</label>
                    <input type="number" id="margin-req" value="0.0" step="0.1" min="0" max="1">
                    
                    <h3>Analyst Selection</h3>
                    <div>
                        <button id="select-all-analysts">Select All</button>
                        <button id="deselect-all-analysts">Deselect All</button>
                    </div>
                    <div id="analyst-list" class="checkbox-list"></div>
                    
                    <h3>Model Selection</h3>
                    <select id="model-selection"></select>
                    
                    <div class="checkbox-item">
                        <input type="checkbox" id="show-reasoning">
                        <label for="show-reasoning">Show Reasoning</label>
                    </div>
                    
                    <div class="checkbox-item">
                        <input type="checkbox" id="show-graph">
                        <label for="show-graph">Show Agent Graph</label>
                    </div>
                    
                    <button id="run-analysis" class="primary">Run Analysis</button>
                </div>
                
                <div class="col">
                    <div id="results-container" class="results hidden">
                        <div id="ticker-tabs" class="ticker-tabs"></div>
                        <div id="ticker-contents"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Backtesting Tab -->
        <div id="backtesting-tab" class="tab-content">
            <div class="row">
                <div class="col">
                    <h3>Backtest Configuration</h3>
                    <label for="backtest-tickers">Ticker Symbols (comma-separated)</label>
                    <input type="text" id="backtest-tickers" placeholder="AAPL, MSFT, GOOG, etc.">
                    
                    <label for="backtest-start-date">Start Date</label>
                    <input type="date" id="backtest-start-date">
                    
                    <label for="backtest-end-date">End Date</label>
                    <input type="date" id="backtest-end-date">
                    
                    <label for="backtest-initial-cash">Initial Cash</label>
                    <input type="number" id="backtest-initial-cash" value="100000">
                    
                    <label for="backtest-margin-req">Margin Requirement</label>
                    <input type="number" id="backtest-margin-req" value="0.0" step="0.1" min="0" max="1">
                    
                    <h3>Analyst Selection</h3>
                    <div>
                        <button id="backtest-select-all-analysts">Select All</button>
                        <button id="backtest-deselect-all-analysts">Deselect All</button>
                    </div>
                    <div id="backtest-analyst-list" class="checkbox-list"></div>
                    
                    <h3>Model Selection</h3>
                    <select id="backtest-model-selection"></select>
                    
                    <button id="run-backtest" class="primary">Run Backtest</button>
                </div>
                
                <div class="col">
                    <div id="backtest-results-container" class="results hidden">
                        <h3>Performance Metrics</h3>
                        <table id="performance-metrics">
                            <thead>
                                <tr>
                                    <th>Metric</th>
                                    <th>Value</th>
                                </tr>
                            </thead>
                            <tbody></tbody>
                        </table>
                        
                        <h3>Portfolio Value</h3>
                        <div id="portfolio-chart" class="chart-container">
                            <p>Chart will appear here after backtest</p>
                        </div>
                        
                        <h3>Trade History</h3>
                        <table id="trade-history">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Ticker</th>
                                    <th>Action</th>
                                    <th>Quantity</th>
                                    <th>Price</th>
                                </tr>
                            </thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Analytics Tab -->
        <div id="analytics-tab" class="tab-content">
            <h3>Strategy Comparison</h3>
            <p><em>Coming soon: Compare the performance of different analyst combinations and models</em></p>
            
            <div class="row">
                <div class="col">
                    <p>This tab will allow you to:</p>
                    <ul>
                        <li>Compare different analyst combinations</li>
                        <li>Evaluate model performance</li>
                        <li>Analyze trading signals across time periods</li>
                        <li>View historical performance metrics</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Initialize date fields with default values
        document.addEventListener("DOMContentLoaded", function() {
            const today = new Date();
            const threeMonthsAgo = new Date();
            threeMonthsAgo.setMonth(today.getMonth() - 3);
            
            document.getElementById("start-date").valueAsDate = threeMonthsAgo;
            document.getElementById("end-date").valueAsDate = today;
            document.getElementById("backtest-start-date").valueAsDate = threeMonthsAgo;
            document.getElementById("backtest-end-date").valueAsDate = today;
            
            // Load analysts
            fetch("/api/analysts")
                .then(response => response.json())
                .then(data => {
                    const analystList = document.getElementById("analyst-list");
                    const backTestAnalystList = document.getElementById("backtest-analyst-list");
                    
                    data.forEach((analyst, index) => {
                        const display = analyst[0];
                        const value = analyst[1];
                        
                        // Trading tab
                        const div = document.createElement("div");
                        div.className = "checkbox-item";
                        div.innerHTML = `
                            <input type="checkbox" id="analyst-${index}" value="${value}" checked>
                            <label for="analyst-${index}">${display}</label>
                        `;
                        analystList.appendChild(div);
                        
                        // Backtesting tab
                        const backDiv = document.createElement("div");
                        backDiv.className = "checkbox-item";
                        backDiv.innerHTML = `
                            <input type="checkbox" id="backtest-analyst-${index}" value="${value}" checked>
                            <label for="backtest-analyst-${index}">${display}</label>
                        `;
                        backTestAnalystList.appendChild(backDiv);
                    });
                });
            
            // Load models
            fetch("/api/models")
                .then(response => response.json())
                .then(data => {
                    const modelSelection = document.getElementById("model-selection");
                    const backTestModelSelection = document.getElementById("backtest-model-selection");
                    
                    data.forEach(model => {
                        const display = model[0];
                        const value = model[1];
                        const provider = model[2];
                        
                        const option = document.createElement("option");
                        option.value = JSON.stringify({model: value, provider: provider});
                        option.textContent = display;
                        modelSelection.appendChild(option);
                        
                        const backOption = option.cloneNode(true);
                        backTestModelSelection.appendChild(backOption);
                    });
                });
            
            // Tab switching
            document.querySelectorAll(".tab").forEach(tab => {
                tab.addEventListener("click", function() {
                    // Hide all tab contents
                    document.querySelectorAll(".tab-content").forEach(content => {
                        content.classList.remove("active");
                    });
                    
                    // Remove active class from all tabs
                    document.querySelectorAll(".tab").forEach(t => {
                        t.classList.remove("active");
                    });
                    
                    // Show selected tab content and mark tab as active
                    this.classList.add("active");
                    document.getElementById(`${this.dataset.tab}-tab`).classList.add("active");
                });
            });
            
            // Select/Deselect All buttons
            document.getElementById("select-all-analysts").addEventListener("click", function() {
                document.querySelectorAll("#analyst-list input[type=checkbox]").forEach(cb => {
                    cb.checked = true;
                });
            });
            
            document.getElementById("deselect-all-analysts").addEventListener("click", function() {
                document.querySelectorAll("#analyst-list input[type=checkbox]").forEach(cb => {
                    cb.checked = false;
                });
            });
            
            document.getElementById("backtest-select-all-analysts").addEventListener("click", function() {
                document.querySelectorAll("#backtest-analyst-list input[type=checkbox]").forEach(cb => {
                    cb.checked = true;
                });
            });
            
            document.getElementById("backtest-deselect-all-analysts").addEventListener("click", function() {
                document.querySelectorAll("#backtest-analyst-list input[type=checkbox]").forEach(cb => {
                    cb.checked = false;
                });
            });
            
            // Run Analysis button
            document.getElementById("run-analysis").addEventListener("click", function() {
                // Show loading status
                const statusDisplay = document.getElementById("status-display");
                statusDisplay.className = "status loading";
                statusDisplay.textContent = "Running analysis... This may take a few minutes.";
                statusDisplay.classList.remove("hidden");
                
                // Hide previous results
                document.getElementById("results-container").classList.add("hidden");
                
                // Get form values
                const tickers = document.getElementById("tickers").value;
                const startDate = document.getElementById("start-date").value;
                const endDate = document.getElementById("end-date").value;
                const initialCash = document.getElementById("initial-cash").value;
                const marginReq = document.getElementById("margin-req").value;
                const showReasoning = document.getElementById("show-reasoning").checked;
                const showGraph = document.getElementById("show-graph").checked;
                
                // Get selected analysts
                const selectedAnalysts = Array.from(document.querySelectorAll("#analyst-list input[type=checkbox]:checked"))
                    .map(cb => cb.value);
                
                // Get selected model
                const modelSelection = JSON.parse(document.getElementById("model-selection").value);
                
                // Build request parameters
                const params = new URLSearchParams();
                params.append("tickers", tickers);
                params.append("start_date", startDate);
                params.append("end_date", endDate);
                params.append("initial_cash", initialCash);
                params.append("margin_req", marginReq);
                params.append("show_reasoning", showReasoning);
                params.append("show_graph", showGraph);
                params.append("model", modelSelection.model);
                params.append("provider", modelSelection.provider);
                
                selectedAnalysts.forEach(analyst => {
                    params.append("analysts", analyst);
                });
                
                // Send request
                fetch("/api/analyze", {
                    method: "POST",
                    body: params
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        statusDisplay.className = "status error";
                        statusDisplay.textContent = `Error: ${data.error}`;
                        return;
                    }
                    
                    // Get results
                    fetch("/api/results")
                        .then(response => response.json())
                        .then(results => {
                            // Show results
                            displayAnalysisResults(results, tickers.split(",").map(t => t.trim()), showReasoning, showGraph);
                            
                            // Update status
                            statusDisplay.className = "status success";
                            statusDisplay.textContent = `Analysis complete using ${modelSelection.provider}/${modelSelection.model}`;
                        });
                })
                .catch(error => {
                    statusDisplay.className = "status error";
                    statusDisplay.textContent = `Error: ${error.message}`;
                });
            });
            
            // Run Backtest button
            document.getElementById("run-backtest").addEventListener("click", function() {
                // Show loading status
                const statusDisplay = document.getElementById("status-display");
                statusDisplay.className = "status loading";
                statusDisplay.textContent = "Running backtest... This may take several minutes.";
                statusDisplay.classList.remove("hidden");
                
                // Hide previous results
                document.getElementById("backtest-results-container").classList.add("hidden");
                
                // Get form values
                const tickers = document.getElementById("backtest-tickers").value;
                const startDate = document.getElementById("backtest-start-date").value;
                const endDate = document.getElementById("backtest-end-date").value;
                const initialCash = document.getElementById("backtest-initial-cash").value;
                const marginReq = document.getElementById("backtest-margin-req").value;
                
                // Get selected analysts
                const selectedAnalysts = Array.from(document.querySelectorAll("#backtest-analyst-list input[type=checkbox]:checked"))
                    .map(cb => cb.value);
                
                // Get selected model
                const modelSelection = JSON.parse(document.getElementById("backtest-model-selection").value);
                
                // Build request parameters
                const params = new URLSearchParams();
                params.append("tickers", tickers);
                params.append("start_date", startDate);
                params.append("end_date", endDate);
                params.append("initial_cash", initialCash);
                params.append("margin_req", marginReq);
                params.append("model", modelSelection.model);
                params.append("provider", modelSelection.provider);
                
                selectedAnalysts.forEach(analyst => {
                    params.append("analysts", analyst);
                });
                
                // Send request
                fetch("/api/backtest", {
                    method: "POST",
                    body: params
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        statusDisplay.className = "status error";
                        statusDisplay.textContent = `Error: ${data.error}`;
                        return;
                    }
                    
                    // Get results
                    fetch("/api/backtest")
                        .then(response => response.json())
                        .then(results => {
                            // Show results
                            displayBacktestResults(results);
                            
                            // Update status
                            statusDisplay.className = "status success";
                            statusDisplay.textContent = `Backtest complete using ${modelSelection.provider}/${modelSelection.model}`;
                        });
                })
                .catch(error => {
                    statusDisplay.className = "status error";
                    statusDisplay.textContent = `Error: ${error.message}`;
                });
            });
        });
        
        function displayAnalysisResults(results, tickers, showReasoning, showGraph) {
                    const decisions = results.decisions || {};
                    const analystSignals = results.analyst_signals || {};
                    
                    // Create tabs for each ticker
                    const tickerTabs = document.getElementById("ticker-tabs");
                    const tickerContents = document.getElementById("ticker-contents");
                    
                    // Clear previous tabs and contents
                    tickerTabs.innerHTML = "";
                    tickerContents.innerHTML = "";
                    
                    // Create tabs and content for each ticker
                    tickers.forEach((ticker, index) => {
                        ticker = ticker.trim();
                        
                        // Create tab
                        const tab = document.createElement("div");
                        tab.className = `ticker-tab ${index === 0 ? "active" : ""}`;
                        tab.dataset.ticker = ticker;
                        tab.textContent = ticker;
                        tickerTabs.appendChild(tab);
                        
                        // Create content
                        const content = document.createElement("div");
                        content.className = `ticker-content ${index === 0 ? "active" : ""}`;
                        content.id = `content-${ticker}`;
                        
                        // Create a summary table of all agents' signals
                        let signalsHTML = `<h3>Analysis Summary: ${ticker}</h3>
                        <table class="signals-summary">
                            <thead>
                                <tr>
                                    <th>Agent</th>
                                    <th>Signal</th>
                                    <th>Confidence</th>
                                </tr>
                            </thead>
                            <tbody>`;
                        
                        // Collect signals for this ticker
                        const tickerSignals = [];
                        for (const agent in analystSignals) {
                            try {
                                if (analystSignals[agent] && typeof analystSignals[agent] === 'object' && analystSignals[agent][ticker]) {
                                    const signal = analystSignals[agent][ticker];
                                    if (signal && typeof signal === 'object' && signal.signal) {
                                        const agentName = agent.replace("_agent", "").replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
                                        const signalType = (signal.signal || "unknown").toUpperCase();
                                        const confidence = signal.confidence || 0;
                                        
                                        // Add signal class for coloring
                                        const signalClass = signalType.toLowerCase();
                                        
                                        tickerSignals.push({agent: agentName, signal: signalType, confidence, signalClass});
                                    }
                                }
                            } catch (error) {
                                console.error(`Error processing signals for agent ${agent}:`, error);
                            }
                        }
                        
                        // Sort signals by agent name
                        tickerSignals.sort((a, b) => a.agent.localeCompare(b.agent));
                        
                        // Add signals to HTML
                        tickerSignals.forEach(signal => {
                            signalsHTML += `<tr>
                                <td>${signal.agent}</td>
                                <td class="${signal.signalClass}">${signal.signal}</td>
                                <td>${signal.confidence}%</td>
                            </tr>`;
                        });
                        
                        signalsHTML += `</tbody></table>`;
        
                        // Add final decision from portfolio manager (place it prominently after the summary table)
                        if (decisions[ticker]) {
                            const decision = decisions[ticker];
                            const action = decision.action.toUpperCase();
                            const quantity = decision.quantity;
                            const confidence = decision.confidence;
                            const reasoning = decision.reasoning;
                            
                            // Add action class for coloring
                            const actionClass = action.toLowerCase();
                            
                            signalsHTML += `
                            <div class="portfolio-decision">
                                <h3>Portfolio Management Decision</h3>
                                <table>
                                    <tbody>
                                        <tr><td>Action</td><td class="${actionClass}">${action}</td></tr>
                                        <tr><td>Quantity</td><td>${quantity}</td></tr>
                                        <tr><td>Confidence</td><td>${confidence}%</td></tr>
                                    </tbody>
                                </table>`;
                            
                            // Add reasoning
                            if (reasoning) {
                                if (typeof reasoning === 'string') {
                                    signalsHTML += `<div class="reasoning-text">${reasoning}</div>`;
                                } else {
                                    signalsHTML += `<div class="reasoning-text">${JSON.stringify(reasoning, null, 2)}</div>`;
                                }
                            }
                            
                            signalsHTML += `</div>`;
                        }
                        
                        // Add detailed analysis sections with each agent's reasoning
                        signalsHTML += `<div class="analyst-details">
                            <h3>Detailed Agent Analysis</h3>`;
                        
                        // Get the full data for each analyst to display detailed reasoning
                        for (const agent in analystSignals) {
                            try {
                                if (analystSignals[agent] && typeof analystSignals[agent] === 'object' && analystSignals[agent][ticker]) {
                                    const signal = analystSignals[agent][ticker];
                                    if (signal && typeof signal === 'object') {
                                        const agentName = agent.replace("_agent", "").replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
                                        
                                        // Add agent header with separator
                                        signalsHTML += `<div class="agent-section">
                                            <h3>========== ${agentName} ==========</h3>
                                            <table class="agent-signal-table">
                                                <tr>
                                                    <td>Signal</td>
                                                    <td class="${signal.signal?.toLowerCase()}">${signal.signal?.toUpperCase() || "N/A"}</td>
                                                </tr>
                                                <tr>
                                                    <td>Confidence</td>
                                                    <td>${signal.confidence || 0}%</td>
                                                </tr>
                                            </table>`;
                                        
                                        // Check if reasoning exists and should be shown
                                        if (showReasoning && signal.reasoning) {
                                            // Format reasoning based on whether it's an object or string
                                            if (typeof signal.reasoning === 'object') {
                                                signalsHTML += `<div class="reasoning-details">`;
                                                
                                                // Format the reasoning object
                                                for (const key in signal.reasoning) {
                                                    try {
                                                        const value = signal.reasoning[key];
                                                        if (typeof value === 'object') {
                                                            // First, sanitize any intrinsic_value fields that might be null
                                                            if (value && typeof value === 'object') {
                                                                // Check if intrinsic_value appears in this object
                                                                if ('intrinsic_value' in value && value.intrinsic_value === null) {
                                                                    value.intrinsic_value = "N/A";
                                                                }
                                                                
                                                                // Check nested objects for intrinsic_value
                                                                for (const nestedKey in value) {
                                                                    if (value[nestedKey] && typeof value[nestedKey] === 'object' &&
                                                                       'intrinsic_value' in value[nestedKey] &&
                                                                       value[nestedKey].intrinsic_value === null) {
                                                                        value[nestedKey].intrinsic_value = "N/A";
                                                                    }
                                                                }
                                                            }
                                                            
                                                            signalsHTML += `<div class="reasoning-section">
                                                                <h4>${key.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}</h4>
                                                                <ul>`;
                                                            
                                                            for (const subKey in value) {
                                                                const subValue = value[subKey];
                                                                if (typeof subValue === 'object') {
                                                                    signalsHTML += `<li><strong>${subKey.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}:</strong>
                                                                        <ul>`;
                                                                    for (const detailKey in subValue) {
                                                                        signalsHTML += `<li><em>${detailKey.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}:</em> ${subValue[detailKey]}</li>`;
                                                                    }
                                                                    signalsHTML += `</ul></li>`;
                                                                } else {
                                                                    signalsHTML += `<li><strong>${subKey.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}:</strong> ${subValue}</li>`;
                                                                }
                                                            }
                                                            
                                                            signalsHTML += `</ul></div>`;
                                                        } else {
                                                            signalsHTML += `<div><strong>${key.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}:</strong> ${value}</div>`;
                                                        }
                                                    } catch (error) {
                                                        console.error(`Error formatting reasoning for key ${key}:`, error);
                                                    }
                                                }
                                                
                                                signalsHTML += `</div>`;
                                            } else {
                                                signalsHTML += `<div class="reasoning-text">${signal.reasoning}</div>`;
                                            }
                                        } else if (!showReasoning) {
                                            signalsHTML += `<div><em>Detailed reasoning hidden (enable "Show Reasoning" to view)</em></div>`;
                                        } else {
                                            signalsHTML += `<div>No detailed reasoning available</div>`;
                                        }
                                        
                                        signalsHTML += `</div>`;
                                    }
                                }
                            } catch (error) {
                                console.error(`Error processing detailed signals for agent ${agent}:`, error);
                            }
                        }
                        
                        signalsHTML += `</div>`;
                
                // Combine all content - we've already included the decision in the signalsHTML
                content.innerHTML = signalsHTML;
                tickerContents.appendChild(content);
            });
            
            // Add summary tab
            const summaryTab = document.createElement("div");
            summaryTab.className = "ticker-tab";
            summaryTab.dataset.ticker = "summary";
            summaryTab.textContent = "Summary";
            tickerTabs.appendChild(summaryTab);
            
            // Create summary content
            const summaryContent = document.createElement("div");
            summaryContent.className = "ticker-content";
            summaryContent.id = "content-summary";
            
            // Add portfolio summary
            let summaryHTML = "<h3>Portfolio Summary</h3><table><thead><tr><th>Ticker</th><th>Action</th><th>Quantity</th><th>Confidence</th></tr></thead><tbody>";
            
            try {
                for (const ticker in decisions) {
                    try {
                        if (decisions[ticker] && typeof decisions[ticker] === 'object') {
                            const decision = decisions[ticker];
                            const action = (decision.action || "unknown").toUpperCase();
                            const quantity = decision.quantity || 0;
                            const confidence = decision.confidence || 0;
                            
                            // Add action class for coloring
                            const actionClass = action.toLowerCase();
                            
                            summaryHTML += `<tr>
                                <td>${ticker}</td>
                                <td class="${actionClass}">${action}</td>
                                <td>${quantity}</td>
                                <td>${confidence}%</td>
                            </tr>`;
                        }
                    } catch (error) {
                        console.error(`Error processing decision for ticker ${ticker}:`, error);
                    }
                }
            } catch (error) {
                console.error("Error processing decisions:", error);
                summaryHTML += `<tr><td colspan="4">Error processing decisions: ${error.message}</td></tr>`;
            }
            
            summaryHTML += `</tbody></table>`;
            
            // Add agent graph if requested
            if (showGraph && results.graph_path) {
                summaryHTML += `<h3>Agent Graph</h3><img src="/${results.graph_path}" style="max-width: 100%;">`;
            }
            
            summaryContent.innerHTML = summaryHTML;
            tickerContents.appendChild(summaryContent);
            
            // Set up tab switching
            document.querySelectorAll(".ticker-tab").forEach(tab => {
                tab.addEventListener("click", function() {
                    // Hide all contents
                    document.querySelectorAll(".ticker-content").forEach(content => {
                        content.classList.remove("active");
                    });
                    
                    // Remove active class from all tabs
                    document.querySelectorAll(".ticker-tab").forEach(t => {
                        t.classList.remove("active");
                    });
                    
                    // Show selected content and mark tab as active
                    this.classList.add("active");
                    document.getElementById(`content-${this.dataset.ticker}`).classList.add("active");
                });
            });
            
            // Show results container
            document.getElementById("results-container").classList.remove("hidden");
        }
        
        function displayBacktestResults(results) {
            const performanceMetrics = results.performance_metrics || {};
            const portfolioValues = results.portfolio_values || [];
            const tableRows = results.table_rows || [];
            
            // Display performance metrics
            const metricsTable = document.getElementById("performance-metrics").querySelector("tbody");
            metricsTable.innerHTML = "";
            
            // Add metrics
            for (const key in performanceMetrics) {
                let value = performanceMetrics[key];
                let valueClass = "";
                
                // Format value based on metric type
                if (key === "sharpe_ratio" || key === "sortino_ratio") {
                    value = value ? value.toFixed(2) : "N/A";
                    valueClass = value > 1 ? "bullish" : "bearish";
                } else if (key === "max_drawdown") {
                    value = value ? value.toFixed(2) + "%" : "N/A";
                    valueClass = "bearish";
                } else if (key === "long_short_ratio") {
                    value = value === Infinity ? "∞ (Long Only)" : (value ? value.toFixed(2) : "N/A");
                } else if (key === "gross_exposure" || key === "net_exposure") {
                    value = value ? "$" + value.toFixed(2) : "N/A";
                    if (key === "net_exposure") {
                        valueClass = value > 0 ? "bullish" : "bearish";
                    }
                }
                
                // Add row to table
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${key.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}</td>
                    <td class="${valueClass}">${value}</td>
                `;
                metricsTable.appendChild(row);
            }
            
            // Display trade history
            const tradeHistoryTable = document.getElementById("trade-history").querySelector("tbody");
            tradeHistoryTable.innerHTML = "";
            
            // Add table rows (simplified)
            tableRows.forEach(row => {
                // Skip summary rows
                if (row[1] && typeof row[1] === "string" && row[1].includes("PORTFOLIO SUMMARY")) {
                    return;
                }
                
                // Extract values (field positions based on format_backtest_row in display.py)
                const date = row[0];
                const ticker = row[1].replace(/\x1b\[\d+m/g, ""); // Remove ANSI color codes
                const action = row[2].replace(/\x1b\[\d+m/g, "");
                const quantity = row[3].replace(/\x1b\[\d+m/g, "");
                const price = row[4].replace(/\x1b\[\d+m/g, "");
                
                // Add action class for coloring
                const actionClass = action.toLowerCase();
                
                // Create row
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${date}</td>
                    <td>${ticker}</td>
                    <td class="${actionClass}">${action}</td>
                    <td>${quantity}</td>
                    <td>${price}</td>
                `;
                tradeHistoryTable.appendChild(tr);
            });
            
            // Note: In a real implementation, we'd create an interactive chart here
            // using a library like Chart.js, Plotly, or D3.js
            document.getElementById("portfolio-chart").innerHTML = 
                "<p>Portfolio chart would be displayed here in a full implementation.</p>" +
                "<p>Values over time: " + portfolioValues.map(pv => "$" + pv["Portfolio Value"].toFixed(2)).join(", ") + "</p>";
            
            // Show results container
            document.getElementById("backtest-results-container").classList.remove("hidden");
        }
    </script>
</body>
</html>
        """


def run_server(port=7860, debug=False):
    """Run the HTTP server."""
    # Initialize global data
    initialize()
    
    # Create handler
    handler = AIHedgeFundHandler
    
    # Create server
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Server running at http://localhost:{port}/")
        
        # Open browser
        webbrowser.open(f"http://localhost:{port}/")
        
        # Serve until interrupted
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped.")


def main():
    """Parse command line arguments and run the server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Launch the AI Hedge Fund Simple GUI")
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=7860, 
        help="Port to run the server on (default: 7860)"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Run in debug mode with additional logging"
    )
    
    args = parser.parse_args()
    
    # Run the server
    run_server(port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()