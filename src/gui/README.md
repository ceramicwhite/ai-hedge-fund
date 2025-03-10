# AI Hedge Fund - Gradio UI

This directory contains the Gradio web interface for the AI Hedge Fund project. The UI provides a user-friendly way to interact with the hedge fund's trading and backtesting capabilities.

## Features

The Gradio UI offers three main tabs:

1. **Trading** - Analyze stocks and get trading recommendations
   - Select AI analysts for different perspectives
   - Choose language models (LLMs)
   - Get color-coded signals and decisions
   - View reasoning behind trading decisions
   - See agent relationship graphs

2. **Backtesting** - Test strategies over historical periods
   - Simulate trading on historical data
   - View performance metrics (Sharpe ratio, Sortino ratio, etc.)
   - Visualize portfolio value changes over time
   - See trade history and signal distributions

3. **Analytics** - Compare different strategies (coming soon)
   - Compare analyst combinations
   - Evaluate model performance
   - Analyze signals across time periods

## Installation

### Prerequisites

Make sure you have all the required dependencies installed:

```bash
# Using Poetry (recommended)
poetry install

# Or using pip
pip install -e .
```

The UI requires the following main dependencies:
- gradio
- plotly
- pandas
- numpy
- matplotlib

These are automatically installed if you use Poetry with the updated pyproject.toml.

## Running the UI

There are two ways to launch the Gradio UI:

### Option 1: Using the run_ui.py script (recommended)

```bash
# From the project root
python src/run_ui.py

# With additional options
python src/run_ui.py --port 8080 --share --debug
```

Command line options:
- `--port` - Specify the port to run on (default: 7860)
- `--share` - Create a shareable link accessible over the internet
- `--debug` - Run in debug mode with additional logging

### Option 2: Directly running the Gradio app module

```bash
# From the project root
python -m src.gui.gradio_app
```

## Usage Guide

### Trading Analysis

1. Enter one or more ticker symbols (comma-separated, e.g., "AAPL, MSFT, GOOG")
2. Select a date range (default is the last 3 months)
3. Configure initial portfolio parameters (cash, margin requirements)
4. Select which AI analysts to include in the analysis
5. Choose a language model
6. Toggle options for showing reasoning and agent graphs
7. Click "Run Analysis"
8. View the results in the tabbed interface

### Backtesting

1. Enter ticker symbols
2. Set a historical date range
3. Configure initial portfolio parameters
4. Select analysts and model
5. Click "Run Backtest"
6. Analyze the performance charts and metrics

## Customization

The UI is built with flexibility in mind and can be customized:

- **Style**: Edit the `src/gui/assets/style.css` file to change the appearance
- **Layout**: Modify the components in `src/gui/gradio_app.py`
- **Components**: Add or modify reusable components in `src/gui/components.py`

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Make sure you're running the scripts from the project root directory and that all dependencies are installed.

2. **"No module named 'gradio'"**: Install Gradio with:
   ```bash
   pip install gradio
   ```

3. **LLM API key errors**: Make sure you've set up your .env file with the appropriate API keys:
   ```
   OPENAI_API_KEY=your_key_here
   # or
   OPENROUTER_API_KEY=your_key_here
   ```

4. **"No analysts selected"**: You need to select at least one analyst for the analysis to run.

5. **Missing data**: The backtester needs historical data, which may require internet access to fetch from APIs.

### Getting Help

If you encounter issues not covered here:
1. Check the terminal for detailed error messages
2. Enable debug mode with `--debug` flag for more information
3. Check that your Python environment has all required dependencies

## Extending the UI

The UI is designed to be extensible. To add new features:

1. Add new utility functions in `src/gui/utils.py`
2. Create new UI components in `src/gui/components.py`
3. Integrate them into the main app in `src/gui/gradio_app.py`