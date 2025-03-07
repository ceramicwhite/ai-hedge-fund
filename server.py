import os
import json
import argparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Import necessary modules from the hedge fund project
from src.main import run_hedge_fund
from src.backtester import Backtester

# Add the current directory to the Python path
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

app = Flask(__name__, static_folder='./build', static_url_path='/')
CORS(app)  # Enable CORS for all routes

@app.route('/')
def index():
    """Serve the React app."""
    return app.send_static_file('index.html')

@app.route('/api/run-hedge-fund', methods=['POST'])
def api_run_hedge_fund():
    """Run the hedge fund with specified parameters."""
    try:
        data = request.json
        
        # Extract parameters from request
        tickers = data.get('tickers', '').split(',')
        start_date = data.get('startDate')
        end_date = data.get('endDate', datetime.now().strftime("%Y-%m-%d"))
        initial_capital = float(data.get('initialCapital', 100000.0))
        selected_analysts = data.get('selectedAnalysts', [])
        model_name = data.get('modelName', 'gpt-4o')
        model_provider = data.get('modelProvider', 'OpenAI')
        show_reasoning = data.get('showReasoning', False)
        
        # Initialize portfolio
        portfolio = {
            "cash": initial_capital,
            "margin_requirement": 0.0,
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
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/run-backtest', methods=['POST'])
def api_run_backtest():
    """Run a backtest with specified parameters."""
    try:
        data = request.json
        
        # Extract parameters from request
        tickers = data.get('tickers', '').split(',')
        start_date = data.get('startDate')
        end_date = data.get('endDate', datetime.now().strftime("%Y-%m-%d"))
        initial_capital = float(data.get('initialCapital', 100000.0))
        selected_analysts = data.get('selectedAnalysts', [])
        model_name = data.get('modelName', 'gpt-4o')
        model_provider = data.get('modelProvider', 'OpenAI')
        margin_requirement = float(data.get('marginRequirement', 0.0))
        
        # Create and run the backtester
        backtester = Backtester(
            agent=run_hedge_fund,
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            model_name=model_name,
            model_provider=model_provider,
            selected_analysts=selected_analysts,
            initial_margin_requirement=margin_requirement,
        )
        
        # Run the backtest
        performance_metrics = backtester.run_backtest()
        
        # Convert portfolio history to a list for JSON serialization
        portfolio_history = []
        for item in backtester.portfolio_values:
            # Convert datetime object to string if needed
            date = item['Date'].strftime("%Y-%m-%d") if isinstance(item['Date'], datetime) else item['Date']
            portfolio_history.append({
                'date': date,
                'value': item['Portfolio Value'],
                'cash': backtester.portfolio['cash'],
                'invested': item['Portfolio Value'] - backtester.portfolio['cash'],
            })
        
        # Generate response data
        result = {
            'portfolioHistory': portfolio_history,
            'finalPortfolioValue': backtester.portfolio_values[-1]['Portfolio Value'] if backtester.portfolio_values else initial_capital,
            'decisions': backtester.decisions if hasattr(backtester, 'decisions') else {},
            'analystSignals': backtester.analyst_signals if hasattr(backtester, 'analyst_signals') else {},
            'performanceMetrics': performance_metrics,
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-api-keys', methods=['POST'])
def check_api_keys():
    """Verify API keys and update environment variables."""
    try:
        data = request.json
        
        # Update environment variables with the provided API keys
        api_keys = {
            'OPENAI_API_KEY': data.get('openaiApiKey'),
            'ANTHROPIC_API_KEY': data.get('anthropicApiKey'),
            'GROQ_API_KEY': data.get('groqApiKey'),
            'FINANCIAL_DATASETS_API_KEY': data.get('financialDatasetsApiKey'),
        }
        
        # Only set keys that have values
        for key, value in api_keys.items():
            if value:
                os.environ[key] = value
        
        # Verify if required keys are set
        missing_keys = []
        if not os.environ.get('OPENAI_API_KEY') and not os.environ.get('ANTHROPIC_API_KEY') and not os.environ.get('GROQ_API_KEY'):
            missing_keys.append("At least one of OPENAI_API_KEY, ANTHROPIC_API_KEY, or GROQ_API_KEY")
        
        # You might want to perform additional validation for each key
        
        if missing_keys:
            return jsonify({'valid': False, 'missing': missing_keys})
        
        return jsonify({'valid': True})
    
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 500

@app.route('/api/get-available-models', methods=['GET'])
def get_available_models():
    """Return available LLM models based on API keys set."""
    try:
        # Import models.py to get the available models
        try:
            from src.llm.models import AVAILABLE_MODELS
        except ImportError:
            # Fallback if direct import fails
            import sys
            import os
            sys.path.insert(0, os.path.abspath('.'))
            from src.llm.models import AVAILABLE_MODELS
        
        # Determine which models are available based on API keys
        available_models = []
        for model in AVAILABLE_MODELS:
            if model.provider.value == 'OpenAI' and os.environ.get('OPENAI_API_KEY'):
                available_models.append({
                    'value': model.model_name,
                    'display': f"[OpenAI] {model.model_name}"
                })
            elif model.provider.value == 'Anthropic' and os.environ.get('ANTHROPIC_API_KEY'):
                available_models.append({
                    'value': model.model_name,
                    'display': f"[Anthropic] {model.model_name}"
                })
            elif model.provider.value == 'Groq' and os.environ.get('GROQ_API_KEY'):
                available_models.append({
                    'value': model.model_name,
                    'display': f"[Groq] {model.model_name}"
                })
        
        return jsonify(available_models)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-available-analysts', methods=['GET'])
def get_available_analysts():
    """Return available analyst agents."""
    try:
        # Import analyst configuration
        try:
            from src.utils.analysts import ANALYST_CONFIG
        except ImportError:
            # Fallback if direct import fails
            import sys
            import os
            sys.path.insert(0, os.path.abspath('.'))
            from src.utils.analysts import ANALYST_CONFIG
        
        available_analysts = [
            {
                'value': key,
                'display': config['display_name']
            }
            for key, config in ANALYST_CONFIG.items()
        ]
        
        return jsonify(available_analysts)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the AI Hedge Fund Flask server')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    
    args = parser.parse_args()
    
    app.run(host='0.0.0.0', port=args.port, debug=args.debug)