"""
Gradio web interface for AI Hedge Fund.
This module creates a Gradio app that provides a user-friendly interface to the hedge fund's
trading and backtesting capabilities.
"""

import os
import sys
import gradio as gr
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pathlib import Path

# Import project modules
# Add project root to path if not already there
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.append(project_root)

# Try direct imports first, fall back to src.* imports if needed
try:
    # Try importing directly (when running from project root)
    from main import run_hedge_fund, create_workflow
    from backtester import Backtester
    from utils.analysts import ANALYST_ORDER
    from utils.display import print_trading_output
    from llm.models import get_llm_order, get_model_info
    from utils.visualize import save_graph_as_png
    
    # Import GUI components
    from gui.components import (
        create_analyst_checkboxes, get_selected_analysts,
        create_model_dropdown, get_model_details,
        create_date_inputs, create_ticker_input,
        create_portfolio_inputs, create_options_inputs,
        create_results_displays, create_backtest_displays,
        update_ticker_tabs, format_signal_class,
        create_select_all_none_buttons
    )
    
    # Import GUI utilities
    from gui.utils import (
        parse_result, format_signals_for_display,
        format_decisions_for_display, format_portfolio_summary,
        extract_reasoning, generate_agent_graph,
        generate_portfolio_chart, format_performance_metrics,
        format_backtest_results, format_backtest_summary,
        generate_signal_distribution_chart
    )
except ImportError:
    # Fall back to src.* imports (when running as a module)
    from src.main import run_hedge_fund, create_workflow
    from src.backtester import Backtester
    from src.utils.analysts import ANALYST_ORDER
    from src.utils.display import print_trading_output
    from src.llm.models import get_llm_order, get_model_info
    from src.utils.visualize import save_graph_as_png
    
    # Import GUI components
    from src.gui.components import (
        create_analyst_checkboxes, get_selected_analysts,
        create_model_dropdown, get_model_details,
        create_date_inputs, create_ticker_input,
        create_portfolio_inputs, create_options_inputs,
        create_results_displays, create_backtest_displays,
        update_ticker_tabs, format_signal_class,
        create_select_all_none_buttons
    )
    
    # Import GUI utilities
    from src.gui.utils import (
        parse_result, format_signals_for_display,
        format_decisions_for_display, format_portfolio_summary,
        extract_reasoning, generate_agent_graph,
        generate_portfolio_chart, format_performance_metrics,
        format_backtest_results, format_backtest_summary,
        generate_signal_distribution_chart
    )

# Set title and theme
TITLE = "AI Hedge Fund"
DESCRIPTION = """
# AI Hedge Fund Analysis Platform

This platform uses AI-powered agents to analyze stocks and make trading decisions.
Each agent specializes in different aspects of market analysis (fundamentals, technicals, sentiment, etc.).

## Features
- **Trading Analysis**: Get real-time analysis and trading recommendations
- **Backtesting**: Simulate trading strategies over historical periods
- **Analytics**: Compare different strategies and analyze performance
"""


def create_trading_tab():
    """Create the trading tab with inputs and outputs."""
    with gr.Tab("Trading"):
        with gr.Row():
            # Left column: Inputs
            with gr.Column(scale=1):
                with gr.Group(elem_classes="input-container"):
                    gr.Markdown("### Trading Configuration")
                    
                    # Ticker input
                    ticker_input = create_ticker_input()
                    
                    # Date range inputs
                    start_date, end_date = create_date_inputs()
                    
                    # Portfolio inputs
                    initial_cash, margin_req = create_portfolio_inputs()
                    
                    gr.Markdown("### Analyst Selection")
                    # Select All/None buttons
                    select_all, select_none = create_select_all_none_buttons()
                    
                    # Analyst checkboxes
                    analyst_checkboxes = create_analyst_checkboxes()
                    
                    gr.Markdown("### Model Selection")
                    # Model dropdown
                    model_dropdown, model_info = create_model_dropdown()
                    
                    # Additional options
                    show_reasoning, show_graph = create_options_inputs()
                    
                    # Run button
                    run_button = gr.Button("Run Analysis", variant="primary")
            
            # Right column: Results
            with gr.Column(scale=2):
                with gr.Group(elem_classes="results-container"):
                    # Status display
                    status, analyst_signals, trading_decisions, portfolio_summary, reasoning, agent_graph = create_results_displays()
                    
                    # Create a container for displaying tabs that will be generated dynamically
                    ticker_tabs = gr.Tabs(visible=False)
                    
                    # Summary section
                    summary_heading = gr.Markdown("### Summary", visible=False, elem_id="summary-heading")
                    portfolio_summary_display = gr.Dataframe(visible=False, label="Portfolio Summary")
        
        # Connect the run button
        # Create a dummy markdown component for summary heading
        summary_heading = gr.Markdown("### Summary", visible=False, elem_id="summary-heading")
        
        run_button.click(
            fn=run_trading_analysis,
            inputs=[
                ticker_input, start_date, end_date,
                initial_cash, margin_req,
                *analyst_checkboxes,  # Unpack the list of checkboxes
                model_dropdown, model_info,
                show_reasoning, show_graph
            ],
            outputs=[
                status, ticker_tabs, summary_heading, portfolio_summary_display
            ],
            concurrency_limit=1  # Ensure only one request at a time
        )
        
        # Ticker input updates the ticker tabs
        ticker_input.change(
            fn=update_ticker_tabs,
            inputs=[ticker_input],
            outputs=[ticker_tabs],
            concurrency_limit=1
        )
        
        # Select All/None buttons
        select_all.click(
            fn=lambda: [True] * len(ANALYST_ORDER),
            inputs=[],
            outputs=analyst_checkboxes,
            concurrency_limit=1
        )
        
        select_none.click(
            fn=lambda: [False] * len(ANALYST_ORDER),
            inputs=[],
            outputs=analyst_checkboxes,
            concurrency_limit=1
        )
    
    return ticker_input, start_date, end_date, initial_cash, margin_req, analyst_checkboxes, model_dropdown, model_info, show_reasoning, show_graph, run_button, status, ticker_tabs, portfolio_summary_display


def create_backtesting_tab():
    """Create the backtesting tab with inputs and outputs."""
    with gr.Tab("Backtesting"):
        with gr.Row():
            # Left column: Inputs
            with gr.Column(scale=1):
                with gr.Group(elem_classes="input-container"):
                    gr.Markdown("### Backtest Configuration")
                    
                    # Ticker input
                    backtest_ticker_input = create_ticker_input()
                    
                    # Date range inputs
                    backtest_start_date, backtest_end_date = create_date_inputs()
                    
                    # Portfolio inputs
                    backtest_initial_cash, backtest_margin_req = create_portfolio_inputs()
                    
                    gr.Markdown("### Analyst Selection")
                    # Select All/None buttons
                    backtest_select_all, backtest_select_none = create_select_all_none_buttons()
                    
                    # Analyst checkboxes
                    backtest_analyst_checkboxes = create_analyst_checkboxes()
                    
                    gr.Markdown("### Model Selection")
                    # Model dropdown
                    backtest_model_dropdown, backtest_model_info = create_model_dropdown()
                    
                    # Run button
                    backtest_run_button = gr.Button("Run Backtest", variant="primary")
            
            # Right column: Results
            with gr.Column(scale=2):
                with gr.Group(elem_classes="results-container"):
                    # Status display
                    backtest_status = gr.Markdown("", elem_id="backtest-status")
                    
                    # Backtest result displays
                    portfolio_chart, performance_metrics, trade_history, signal_distribution = create_backtest_displays()
        
        # Connect the run button - ensure all outputs are actual Gradio components
        backtest_run_button.click(
            fn=run_backtesting,
            inputs=[
                backtest_ticker_input, backtest_start_date, backtest_end_date,
                backtest_initial_cash, backtest_margin_req,
                *backtest_analyst_checkboxes,  # Unpack the list of checkboxes
                backtest_model_dropdown, backtest_model_info
            ],
            outputs=[
                backtest_status, portfolio_chart, performance_metrics,
                trade_history, signal_distribution
            ],
            concurrency_limit=1  # Ensure only one request at a time
        )
        
        # Select All/None buttons
        backtest_select_all.click(
            fn=lambda: [True] * len(ANALYST_ORDER),
            inputs=[],
            outputs=backtest_analyst_checkboxes,
            concurrency_limit=1
        )
        
        backtest_select_none.click(
            fn=lambda: [False] * len(ANALYST_ORDER),
            inputs=[],
            outputs=backtest_analyst_checkboxes,
            concurrency_limit=1
        )
    
    return backtest_ticker_input, backtest_start_date, backtest_end_date, backtest_initial_cash, backtest_margin_req, backtest_analyst_checkboxes, backtest_model_dropdown, backtest_model_info, backtest_run_button, backtest_status, portfolio_chart, performance_metrics, trade_history, signal_distribution


def create_analytics_tab():
    """Create the analytics tab for comparing strategies."""
    with gr.Tab("Analytics"):
        gr.Markdown("### Strategy Comparison")
        gr.Markdown("*Coming soon: Compare the performance of different analyst combinations and models*")
        
        # Placeholder for future analytics features
        with gr.Row():
            with gr.Column():
                gr.Markdown("This tab will allow you to:")
                gr.Markdown("- Compare different analyst combinations")
                gr.Markdown("- Evaluate model performance")
                gr.Markdown("- Analyze trading signals across time periods")
                gr.Markdown("- View historical performance metrics")


def run_trading_analysis(ticker_input, start_date, end_date, initial_cash, margin_req, *args):
    """
    Run trading analysis based on user inputs and display results.
    
    Note: args contains both analyst checkboxes and other inputs due to unpacking
    """
    try:
        # Parse tickers
        if not ticker_input:
            return (
                "Error: Please enter at least one ticker symbol",  # Status text
                None,   # Ticker tabs
                "",     # Summary heading (empty)
                None    # Portfolio summary data
            )
        
        tickers = [t.strip() for t in ticker_input.split(",")]
        
        # Get analyst selections (first len(ANALYST_ORDER) elements of args)
        analyst_values = args[:len(ANALYST_ORDER)]
        selected_analysts = get_selected_analysts(analyst_values)
        
        if not selected_analysts:
            return (
                "Error: Please select at least one analyst",  # Status text
                None,   # Ticker tabs
                "",     # Summary heading (empty)
                None    # Portfolio summary data
            )
        
        # Get other parameters (remaining elements of args)
        remaining_args = args[len(ANALYST_ORDER):]
        model_dropdown, model_info, show_reasoning, show_graph = remaining_args
        
        # Get model name and provider
        model_name, model_provider = get_model_details(model_dropdown, model_info)
        
        # Format dates (already in string format now)
        start_date_str = start_date
        end_date_str = end_date
        
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
        
        # Create progress status
        status_value = "Running analysis... This may take a few minutes."
        
        # Run the hedge fund
        result = run_hedge_fund(
            tickers=tickers,
            start_date=start_date_str,
            end_date=end_date_str,
            portfolio=portfolio,
            show_reasoning=show_reasoning,
            selected_analysts=selected_analysts,
            model_name=model_name,
            model_provider=model_provider,
        )
        
        # Parse the result
        decisions, analyst_signals, model_name = parse_result(result)
        
        # Create ticker tabs with content
        tabs = []
        for ticker in tickers:
            with gr.Tab(label=ticker):
                with gr.Column():
                    # Analyst signals for this ticker
                    signals_df = format_signals_for_display(analyst_signals, ticker)
                    gr.Dataframe(value=format_signal_class(signals_df), label=f"Analyst Signals: {ticker}")
                    
                    # Trading decision for this ticker
                    decision_df = format_decisions_for_display(decisions, ticker)
                    gr.Dataframe(value=format_signal_class(decision_df), label=f"Trading Decision: {ticker}")
                    
                    # Reasoning if requested
                    if show_reasoning:
                        reasoning_text = extract_reasoning(decisions, ticker)
                        gr.Textbox(value=reasoning_text, label=f"Reasoning: {ticker}", lines=6)
                    
            tabs.append(gr.Tab(label=ticker))
        
        # Add summary tab
        with gr.Tab(label="Summary"):
            # Portfolio summary
            summary_df = format_portfolio_summary(decisions)
            gr.Dataframe(value=format_signal_class(summary_df), label="Portfolio Summary")
            
            # Agent graph if requested
            if show_graph:
                # Create the workflow with selected analysts
                workflow = create_workflow(selected_analysts)
                agent = workflow.compile()
                
                # Generate and save the graph
                graph_path = generate_agent_graph(agent, selected_analysts)
                if graph_path:
                    gr.Image(value=graph_path, label="Agent Graph")
        
        tabs.append(gr.Tab(label="Summary"))
        
        # Prepare main portfolio summary
        summary_df = format_portfolio_summary(decisions)
        
        # Return actual values, not update functions
        return (
            f"Analysis complete using {model_name}",  # Status text
            tabs,                                    # Ticker tabs
            "### Summary",                           # Summary heading
            format_signal_class(summary_df)          # Portfolio summary data
        )
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        
        return (
            f"Error: {str(e)}\n\n```\n{error_details}\n```",  # Status text
            None,   # Ticker tabs
            "",     # Summary heading (empty)
            None    # Portfolio summary data
        )


def run_backtesting(ticker_input, start_date, end_date, initial_cash, margin_req, *args):
    """
    Run backtesting based on user inputs and display results.
    
    Note: args contains both analyst checkboxes and other inputs due to unpacking
    """
    try:
        # Parse tickers
        if not ticker_input:
            return (
                "Error: Please enter at least one ticker symbol",  # Status text
                None,   # Portfolio chart
                None,   # Performance metrics
                None,   # Trade history
                None    # Signal distribution
            )
        
        tickers = [t.strip() for t in ticker_input.split(",")]
        
        # Get analyst selections (first len(ANALYST_ORDER) elements of args)
        analyst_values = args[:len(ANALYST_ORDER)]
        selected_analysts = get_selected_analysts(analyst_values)
        
        if not selected_analysts:
            return (
                "Error: Please select at least one analyst",  # Status text
                None,   # Portfolio chart
                None,   # Performance metrics
                None,   # Trade history
                None    # Signal distribution
            )
        
        # Get other parameters (remaining elements of args)
        remaining_args = args[len(ANALYST_ORDER):]
        model_dropdown, model_info = remaining_args
        
        # Get model name and provider
        model_name, model_provider = get_model_details(model_dropdown, model_info)
        
        # Format dates (already in string format now)
        start_date_str = start_date
        end_date_str = end_date
        
        # Create progress status
        status_value = "Running backtest... This may take several minutes."
        
        # Create the backtest instance
        backtester = Backtester(
            agent=run_hedge_fund,
            tickers=tickers,
            start_date=start_date_str,
            end_date=end_date_str,
            initial_capital=initial_cash,
            model_name=model_name,
            model_provider=model_provider,
            selected_analysts=selected_analysts,
            initial_margin_requirement=margin_req,
        )
        
        # Run the backtest
        performance_metrics = backtester.run_backtest()
        performance_df = backtester.analyze_performance()
        
        # Format results for display
        metrics_df = format_performance_metrics(performance_metrics)
        portfolio_value_chart = generate_portfolio_chart(performance_df)
        
        # Update status
        status_value = f"Backtest complete using {model_provider}/{model_name}"
        
        # Signal distribution chart - extract from analyst_signals in the final result
        collected_signals = {}
        for i in range(len(backtester.portfolio_values) - 1):
            if hasattr(backtester, 'analyst_signals_history') and i < len(backtester.analyst_signals_history):
                signals = backtester.analyst_signals_history[i]
                for agent, ticker_signals in signals.items():
                    if agent not in collected_signals:
                        collected_signals[agent] = {}
                    collected_signals[agent].update(ticker_signals)
        
        signal_chart = generate_signal_distribution_chart(collected_signals)
        
        # Format trade history - if table_rows isn't directly available, we'll create a simplified version
        if hasattr(backtester, 'table_rows'):
            table_rows = backtester.table_rows
        else:
            # Create simplified trade history from portfolio values
            table_rows = []
            for i, pv in enumerate(backtester.portfolio_values[1:], 1):  # Skip the initial value
                date = pv["Date"].strftime("%Y-%m-%d")
                # Add a row for each ticker with basic info
                for ticker in tickers:
                    table_rows.append([
                        date,
                        ticker,
                        "N/A",  # Action
                        0,      # Quantity
                        0,      # Price
                        0,      # Shares
                        0,      # Position value
                        0,      # Bullish count
                        0,      # Bearish count
                        0       # Neutral count
                    ])
        
        trade_history_df = format_backtest_results(table_rows)
        
        return (
            status_value,               # Status text
            portfolio_value_chart,      # Portfolio chart
            metrics_df,                 # Performance metrics
            trade_history_df,           # Trade history
            signal_chart                # Signal distribution
        )
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        
        return (
            f"Error: {str(e)}\n\n```\n{error_details}\n```",  # Status text
            None,   # Portfolio chart
            None,   # Performance metrics
            None,   # Trade history
            None    # Signal distribution
        )


def create_ui():
    """Create the main Gradio interface."""
    # Create directories for saved graphs if they don't exist
    os.makedirs("./data/graphs", exist_ok=True)
    
    with gr.Blocks(css="src/gui/assets/style.css", theme=gr.themes.Soft(), analytics_enabled=False) as app:
        gr.Markdown(DESCRIPTION)
        
        with gr.Tabs() as tabs:
            # Create tabs
            trading_components = create_trading_tab()
            backtesting_components = create_backtesting_tab()
            create_analytics_tab()
        
        # Footer
        gr.Markdown("---")
        gr.Markdown("© 2025 AI Hedge Fund | Powered by LLMs and Agent Networks")
    
    return app


def main():
    """Main entry point for the Gradio app."""
    # Create the UI
    app = create_ui()
    
    # Launch the app with simplified server settings to avoid Pydantic schema validation errors
    app.launch(
        server_name="127.0.0.1",        # Use localhost
        server_port=7860,               # Default Gradio port
        share=False,
        inbrowser=True,
        prevent_thread_lock=True,       # Prevent thread locking issues
        show_api=False,                 # Disable API docs that use Pydantic
        max_threads=1                   # Limit concurrency to avoid issues
    )


if __name__ == "__main__":
    main()
