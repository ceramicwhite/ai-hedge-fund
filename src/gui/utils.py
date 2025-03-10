"""
Utility functions for the AI Hedge Fund Gradio UI.
"""

import os
import io
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
from pathlib import Path

# Import project modules
from src.utils.analysts import ANALYST_ORDER
from src.utils.display import sort_analyst_signals, strip_ansi_codes
from src.graph.state import AgentState
from src.utils.visualize import save_graph_as_png


def parse_result(result):
    """Parse the result from the hedge fund run and extract decisions and signals."""
    decisions = result.get("decisions", {})
    analyst_signals = result.get("analyst_signals", {})
    model_name = result.get("model_name", "Unknown model")
    
    return decisions, analyst_signals, model_name


def format_signals_for_display(analyst_signals, ticker):
    """Format analyst signals into a DataFrame for display."""
    if not analyst_signals:
        return pd.DataFrame(columns=["Analyst", "Signal", "Confidence"])
    
    data = []
    for agent, signals in analyst_signals.items():
        if ticker not in signals:
            continue
            
        signal = signals[ticker]
        agent_name = agent.replace("_agent", "").replace("_", " ").title()
        signal_type = signal.get("signal", "").upper()
        confidence = signal.get("confidence", 0)
        
        data.append({
            "Analyst": agent_name,
            "Signal": signal_type,
            "Confidence": f"{confidence}%",
            # Add classes for styling
            "Signal_Class": signal_type.lower(),
            "Confidence_Value": confidence  # Numeric value for sorting
        })
    
    # Sort the signals according to the predefined order
    sorted_data = sorted(data, key=lambda x: [d[0] for d in ANALYST_ORDER].index(x["Analyst"]) 
                         if x["Analyst"] in [d[0] for d in ANALYST_ORDER] else 999)
    
    df = pd.DataFrame(sorted_data)
    if not df.empty:
        df = df[["Analyst", "Signal", "Confidence"]]
    
    return df


def format_decisions_for_display(decisions, ticker):
    """Format trading decisions into a DataFrame for display."""
    if not decisions or ticker not in decisions:
        return pd.DataFrame(columns=["Metric", "Value"])
    
    decision = decisions[ticker]
    action = decision.get("action", "").upper()
    quantity = decision.get("quantity", 0)
    confidence = decision.get("confidence", 0)
    
    data = [
        {"Metric": "Action", "Value": action, "Value_Class": action.lower()},
        {"Metric": "Quantity", "Value": quantity},
        {"Metric": "Confidence", "Value": f"{confidence:.1f}%"}
    ]
    
    return pd.DataFrame(data)


def format_portfolio_summary(decisions):
    """Format portfolio summary into a DataFrame for display."""
    if not decisions:
        return pd.DataFrame(columns=["Ticker", "Action", "Quantity", "Confidence"])
    
    data = []
    for ticker, decision in decisions.items():
        action = decision.get("action", "").upper()
        quantity = decision.get("quantity", 0)
        confidence = decision.get("confidence", 0)
        
        data.append({
            "Ticker": ticker,
            "Action": action,
            "Quantity": quantity,
            "Confidence": f"{confidence:.1f}%",
            "Action_Class": action.lower()
        })
    
    df = pd.DataFrame(data)
    if not df.empty:
        df = df[["Ticker", "Action", "Quantity", "Confidence"]]
    
    return df


def extract_reasoning(decisions, ticker):
    """Extract and format reasoning for a specific ticker."""
    if not decisions or ticker not in decisions:
        return ""
    
    return decisions[ticker].get("reasoning", "No reasoning provided.")


def generate_agent_graph(workflow, selected_analysts):
    """Generate an agent graph visualization and return the path to the saved image."""
    if not selected_analysts:
        return None
    
    # Create a unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"./data/graphs/{'_'.join(selected_analysts)}_{timestamp}_graph.png"
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save the graph as PNG
    save_graph_as_png(workflow, file_path)
    
    return file_path if os.path.exists(file_path) else None


def generate_portfolio_chart(performance_df):
    """Generate an interactive portfolio value chart using Plotly."""
    if performance_df.empty:
        return None
    
    fig = go.Figure()
    
    # Add main portfolio value line
    fig.add_trace(go.Scatter(
        x=performance_df.index,
        y=performance_df["Portfolio Value"],
        mode='lines',
        name='Portfolio Value',
        line=dict(color='cyan', width=2)
    ))
    
    # Add initial capital reference line
    if 'Initial Capital' in performance_df.columns:
        initial_capital = performance_df['Initial Capital'].iloc[0]
        fig.add_trace(go.Scatter(
            x=[performance_df.index.min(), performance_df.index.max()],
            y=[initial_capital, initial_capital],
            mode='lines',
            name='Initial Capital',
            line=dict(color='white', width=1, dash='dash')
        ))
    
    # Layout
    fig.update_layout(
        title='Portfolio Value Over Time',
        xaxis_title='Date',
        yaxis_title='Value ($)',
        template='plotly_dark',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=500
    )
    
    # Add range slider
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    
    return fig


def format_performance_metrics(metrics):
    """Format performance metrics into a DataFrame for display."""
    if not metrics:
        return pd.DataFrame(columns=["Metric", "Value"])
    
    data = []
    
    # Format each metric with appropriate styling
    for key, value in metrics.items():
        if key == 'sharpe_ratio':
            value_str = f"{value:.2f}" if value is not None else "N/A"
            class_name = "bullish" if value and value > 1 else "bearish"
            data.append({"Metric": "Sharpe Ratio", "Value": value_str, "Value_Class": class_name})
        
        elif key == 'sortino_ratio':
            value_str = f"{value:.2f}" if value is not None else "N/A"
            class_name = "bullish" if value and value > 1 else "bearish"
            data.append({"Metric": "Sortino Ratio", "Value": value_str, "Value_Class": class_name})
        
        elif key == 'max_drawdown':
            value_str = f"{value:.2f}%" if value is not None else "N/A"
            class_name = "bearish" 
            data.append({"Metric": "Max Drawdown", "Value": value_str, "Value_Class": class_name})
        
        elif key == 'long_short_ratio':
            if value == float('inf'):
                value_str = "∞ (Long Only)"
            else:
                value_str = f"{value:.2f}" if value is not None else "N/A"
            data.append({"Metric": "Long/Short Ratio", "Value": value_str})
        
        elif key == 'gross_exposure':
            value_str = f"${value:,.2f}" if value is not None else "N/A"
            data.append({"Metric": "Gross Exposure", "Value": value_str})
        
        elif key == 'net_exposure':
            value_str = f"${value:,.2f}" if value is not None else "N/A"
            class_name = "bullish" if value and value > 0 else "bearish"
            data.append({"Metric": "Net Exposure", "Value": value_str, "Value_Class": class_name})
    
    return pd.DataFrame(data)


def format_backtest_results(table_rows):
    """Format backtest results into a DataFrame for display."""
    if not table_rows:
        return pd.DataFrame()
    
    # Extract ticker rows (excluding summary rows)
    ticker_rows = []
    for row in table_rows:
        if not isinstance(row[1], str) or "PORTFOLIO SUMMARY" not in row[1]:
            # Extract only the text content, removing any formatting codes
            cleaned_row = [strip_ansi_codes(str(cell)) if isinstance(cell, str) else cell for cell in row]
            ticker_rows.append(cleaned_row)
    
    # Create DataFrame
    columns = [
        "Date", "Ticker", "Action", "Quantity", "Price", 
        "Shares", "Position Value", "Bullish", "Bearish", "Neutral"
    ]
    
    df = pd.DataFrame(ticker_rows, columns=columns)
    
    return df


def format_backtest_summary(table_rows):
    """Extract and format the summary information from backtest results."""
    if not table_rows:
        return pd.DataFrame()
    
    # Extract summary rows
    summary_rows = []
    for row in table_rows:
        if isinstance(row[1], str) and "PORTFOLIO SUMMARY" in row[1]:
            # Clean the row of ANSI codes
            cleaned_row = [strip_ansi_codes(str(cell)) if isinstance(cell, str) else cell for cell in row]
            summary_rows.append(cleaned_row)
    
    if not summary_rows:
        return pd.DataFrame()
    
    # Get the latest summary row
    latest_summary = summary_rows[-1]
    
    # Extract values (this assumes the format matches what's in display.py)
    try:
        # Extract values using regex if needed
        cash_balance = latest_summary[7].replace("$", "").replace(",", "")
        position_value = latest_summary[6].replace("$", "").replace(",", "")
        total_value = latest_summary[8].replace("$", "").replace(",", "")
        return_pct = latest_summary[9].replace("+", "").replace("%", "")
        
        # Optional metrics
        sharpe_ratio = latest_summary[10] if len(latest_summary) > 10 and latest_summary[10] else "N/A"
        sortino_ratio = latest_summary[11] if len(latest_summary) > 11 and latest_summary[11] else "N/A"
        max_drawdown = latest_summary[12].replace("%", "") if len(latest_summary) > 12 and latest_summary[12] else "N/A"
    except (IndexError, AttributeError):
        # Fallback if the format doesn't match
        return pd.DataFrame([
            {"Metric": "Cash Balance", "Value": "Error extracting value"},
            {"Metric": "Total Position Value", "Value": "Error extracting value"},
            {"Metric": "Total Value", "Value": "Error extracting value"},
            {"Metric": "Return", "Value": "Error extracting value"}
        ])
    
    data = [
        {"Metric": "Cash Balance", "Value": f"${float(cash_balance):,.2f}"},
        {"Metric": "Total Position Value", "Value": f"${float(position_value):,.2f}"},
        {"Metric": "Total Value", "Value": f"${float(total_value):,.2f}"},
        {"Metric": "Return", "Value": f"{float(return_pct):+.2f}%", 
         "Value_Class": "bullish" if float(return_pct) >= 0 else "bearish"}
    ]
    
    # Add optional metrics if available
    if sharpe_ratio != "N/A":
        sharpe_value = float(sharpe_ratio.replace(",", ""))
        data.append({
            "Metric": "Sharpe Ratio", 
            "Value": f"{sharpe_value:.2f}", 
            "Value_Class": "bullish" if sharpe_value > 1 else "bearish"
        })
    
    if sortino_ratio != "N/A":
        sortino_value = float(sortino_ratio.replace(",", ""))
        data.append({
            "Metric": "Sortino Ratio", 
            "Value": f"{sortino_value:.2f}", 
            "Value_Class": "bullish" if sortino_value > 1 else "bearish"
        })
    
    if max_drawdown != "N/A":
        drawdown_value = float(max_drawdown.replace(",", ""))
        data.append({
            "Metric": "Max Drawdown", 
            "Value": f"{drawdown_value:.2f}%", 
            "Value_Class": "bearish"
        })
    
    return pd.DataFrame(data)


def generate_signal_distribution_chart(analyst_signals):
    """Generate a chart showing the distribution of signals (bullish/bearish/neutral) by analyst."""
    if not analyst_signals:
        return None
    
    # Collect signal counts
    signal_counts = {}
    for agent, signals in analyst_signals.items():
        agent_name = agent.replace("_agent", "").replace("_", " ").title()
        signal_counts[agent_name] = {"Bullish": 0, "Bearish": 0, "Neutral": 0}
        
        for ticker, signal_data in signals.items():
            signal_type = signal_data.get("signal", "").capitalize()
            if signal_type in ["Bullish", "Bearish", "Neutral"]:
                signal_counts[agent_name][signal_type] += 1
    
    # Convert to DataFrame for plotting
    data = []
    for agent, counts in signal_counts.items():
        for signal_type, count in counts.items():
            data.append({
                "Analyst": agent,
                "Signal Type": signal_type,
                "Count": count
            })
    
    df = pd.DataFrame(data)
    if df.empty:
        return None
    
    # Create the grouped bar chart
    fig = px.bar(
        df, 
        x="Analyst", 
        y="Count", 
        color="Signal Type",
        color_discrete_map={
            "Bullish": "green",
            "Bearish": "red",
            "Neutral": "yellow"
        },
        title="Signal Distribution by Analyst",
        barmode="group"
    )
    
    fig.update_layout(
        template="plotly_dark",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400
    )
    
    return fig