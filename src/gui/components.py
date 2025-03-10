"""
Reusable UI components for the AI Hedge Fund Gradio UI.
"""

import os
import gradio as gr
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from utils.analysts import ANALYST_ORDER
from llm.models import get_llm_order, get_model_info


def create_analyst_checkboxes():
    """Create a set of checkboxes for analyst selection."""
    # Create checkbox inputs for each analyst
    analyst_checkboxes = []
    
    for display, value in ANALYST_ORDER:
        checkbox = gr.Checkbox(
            label=display,
            value=True,  # Default to selected
            elem_id=f"analyst-{value}"
        )
        analyst_checkboxes.append(checkbox)
    
    return analyst_checkboxes


def get_selected_analysts(checkbox_values):
    """Get the list of selected analysts from checkbox values."""
    # Need to map checkbox values back to the analyst IDs
    selected_analysts = []
    
    for i, (display, value) in enumerate(ANALYST_ORDER):
        if checkbox_values[i]:
            selected_analysts.append(value)
    
    return selected_analysts


def create_model_dropdown():
    """Create a dropdown for LLM model selection."""
    # Get current LLM options
    llm_order = get_llm_order()
    
    # Check if environment variables are set
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    openrouter_model = os.getenv("OPENROUTER_MODEL")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_MODEL")
    
    # Use environment variables if available
    model_info = None
    if openrouter_api_key and openrouter_model:
        model_choices = [(f"OpenRouter - {openrouter_model}", openrouter_model, "OpenRouter")]
    elif openai_api_key and openai_model:
        model_choices = [(f"OpenAI - {openai_model}", openai_model, "OpenAI")]
    else:
        # Otherwise use the available models
        model_choices = [(display, value, provider) for display, value, provider in llm_order]
    
    # Create the dropdown
    model_dropdown = gr.Dropdown(
        choices=[choice[0] for choice in model_choices],
        value=model_choices[0][0] if model_choices else None,
        label="LLM Model",
        info="Select which language model to use for analysis"
    )
    
    # Hidden state to store model info
    model_info = gr.State(value=model_choices)
    
    return model_dropdown, model_info


def get_model_details(selected_model, model_info_state):
    """Get the model name and provider from the selection."""
    # Find the matching model in the model_info_state
    for display, model_name, provider in model_info_state:
        if display == selected_model:
            return model_name, provider
    
    # Default fallback
    return "gpt-4o", "OpenAI"


def create_date_inputs():
    """Create date input components with defaults."""
    today = datetime.now()
    three_months_ago = today - relativedelta(months=3)
    
    # Format default dates as strings
    default_start = three_months_ago.strftime("%Y-%m-%d")
    default_end = today.strftime("%Y-%m-%d")
    
    # Use textbox with pattern matching instead of Date component
    start_date = gr.Textbox(
        value=default_start,
        label="Start Date (YYYY-MM-DD)",
        info="Beginning of the analysis period",
        placeholder="YYYY-MM-DD",
        max_lines=1
    )
    
    end_date = gr.Textbox(
        value=default_end,
        label="End Date (YYYY-MM-DD)",
        info="End of the analysis period",
        placeholder="YYYY-MM-DD",
        max_lines=1
    )
    
    return start_date, end_date


def create_ticker_input():
    """Create ticker symbol input component."""
    return gr.Textbox(
        label="Ticker Symbols",
        placeholder="AAPL, MSFT, GOOG, etc.",
        info="Enter comma-separated ticker symbols",
        lines=1
    )


def create_portfolio_inputs():
    """Create portfolio configuration input components."""
    initial_cash = gr.Number(
        value=100000.0,
        label="Initial Cash",
        info="Starting cash position",
        minimum=0
    )
    
    margin_req = gr.Number(
        value=0.0,
        label="Margin Requirement",
        info="Initial margin requirement (e.g., 0.5 for 50%)",
        minimum=0,
        maximum=1
    )
    
    return initial_cash, margin_req


def create_options_inputs():
    """Create additional options input components."""
    show_reasoning = gr.Checkbox(
        label="Show Reasoning",
        value=False,
        info="Display the detailed reasoning behind each decision"
    )
    
    show_graph = gr.Checkbox(
        label="Show Agent Graph",
        value=False,
        info="Visualize the workflow of analyst agents"
    )
    
    return show_reasoning, show_graph


def create_results_displays():
    """Create output components for displaying results."""
    # Status indicator
    status = gr.Markdown("", elem_id="status-display")
    
    # Analyst signals table
    analyst_signals = gr.Dataframe(
        headers=["Analyst", "Signal", "Confidence"],
        label="Analyst Signals",
        visible=False
    )
    
    # Trading decisions table
    trading_decisions = gr.Dataframe(
        headers=["Metric", "Value"],
        label="Trading Decisions",
        visible=False
    )
    
    # Portfolio summary table
    portfolio_summary = gr.Dataframe(
        headers=["Ticker", "Action", "Quantity", "Confidence"],
        label="Portfolio Summary",
        visible=False
    )
    
    # Reasoning text area
    reasoning = gr.Textbox(
        label="Reasoning",
        lines=6,
        visible=False
    )
    
    # Agent graph visualization
    agent_graph = gr.Image(
        label="Agent Graph",
        visible=False
    )
    
    return status, analyst_signals, trading_decisions, portfolio_summary, reasoning, agent_graph


def create_backtest_displays():
    """Create output components for displaying backtest results."""
    # Portfolio chart
    portfolio_chart = gr.Plot(
        label="Portfolio Performance",
        visible=False
    )
    
    # Performance metrics table
    performance_metrics = gr.Dataframe(
        headers=["Metric", "Value"],
        label="Performance Metrics",
        visible=False
    )
    
    # Trade history table
    trade_history = gr.Dataframe(
        label="Trade History",
        visible=False
    )
    
    # Signal distribution chart
    signal_distribution = gr.Plot(
        label="Signal Distribution",
        visible=False
    )
    
    return portfolio_chart, performance_metrics, trade_history, signal_distribution


def update_ticker_tabs(ticker_input):
    """Create tabs for each ticker based on input."""
    if not ticker_input:
        return gr.Tabs.update(visible=False)
    
    tickers = [t.strip() for t in ticker_input.split(",")]
    
    tabs = []
    for ticker in tickers:
        tabs.append(gr.Tab(label=ticker))
    
    # Add a "Summary" tab
    tabs.append(gr.Tab(label="Summary"))
    
    return gr.Tabs.update(visible=True, tabs=tabs)


def format_signal_class(df):
    """
    Format a DataFrame to highlight signals with appropriate CSS classes.
    This function adds CSS classes to specific cells in the DataFrame based on their values.
    """
    if df.empty:
        return df
    
    # Check if the necessary columns exist
    if 'Signal' in df.columns:
        # Create a copy to avoid modifying the original
        styled_df = df.copy()
        
        # Apply styling based on signal values
        for i, row in styled_df.iterrows():
            signal = row.get('Signal', '').lower()
            if signal in ['bullish', 'buy', 'cover']:
                styled_df.at[i, 'Signal'] = f'<span class="bullish">{row["Signal"]}</span>'
            elif signal in ['bearish', 'sell', 'short']:
                styled_df.at[i, 'Signal'] = f'<span class="bearish">{row["Signal"]}</span>'
            elif signal in ['neutral', 'hold']:
                styled_df.at[i, 'Signal'] = f'<span class="neutral">{row["Signal"]}</span>'
        
        return styled_df
    
    # If 'Action' column exists (for portfolio summary)
    if 'Action' in df.columns:
        styled_df = df.copy()
        
        for i, row in styled_df.iterrows():
            action = row.get('Action', '').lower()
            if action in ['buy', 'cover']:
                styled_df.at[i, 'Action'] = f'<span class="bullish">{row["Action"]}</span>'
            elif action in ['sell', 'short']:
                styled_df.at[i, 'Action'] = f'<span class="bearish">{row["Action"]}</span>'
            elif action in ['hold']:
                styled_df.at[i, 'Action'] = f'<span class="neutral">{row["Action"]}</span>'
        
        return styled_df
    
    # For metrics tables that have Value_Class column
    if 'Metric' in df.columns and 'Value' in df.columns and 'Value_Class' in df.columns:
        styled_df = df.copy()
        
        for i, row in styled_df.iterrows():
            value_class = row.get('Value_Class', '')
            if value_class:
                styled_df.at[i, 'Value'] = f'<span class="{value_class}">{row["Value"]}</span>'
        
        # Remove the Value_Class column before displaying
        return styled_df.drop(columns=['Value_Class'])
    
    return df


def create_select_all_none_buttons():
    """Create 'Select All' and 'Select None' buttons for analysts."""
    with gr.Row():
        select_all = gr.Button("Select All Analysts", size="sm")
        select_none = gr.Button("Deselect All Analysts", size="sm")
    
    return select_all, select_none