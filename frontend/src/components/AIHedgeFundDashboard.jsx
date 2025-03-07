import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import './AIHedgeFundDashboard.css';

const AIHedgeFundDashboard = () => {
  // Application state
  const [darkMode, setDarkMode] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [tickers, setTickers] = useState('AAPL,MSFT,GOOGL');
  const [selectedAnalysts, setSelectedAnalysts] = useState([
    'ben_graham', 
    'warren_buffett', 
    'cathie_wood', 
    'technical_analyst',
    'fundamentals_analyst'
  ]);
  const [selectedModel, setSelectedModel] = useState('gpt-4o');
  const [startDate, setStartDate] = useState(getDefaultStartDate());
  const [endDate, setEndDate] = useState(getDefaultEndDate());
  const [initialCapital, setInitialCapital] = useState(100000);
  const [isRunning, setIsRunning] = useState(false);
  const [showApiKeySetup, setShowApiKeySetup] = useState(false);
  const [openaiBaseUrl, setOpenaiBaseUrl] = useState('');
  const [customModelName, setCustomModelName] = useState('');
  
  // API key state
  const [openaiApiKey, setOpenaiApiKey] = useState('');
  const [anthropicApiKey, setAnthropicApiKey] = useState('');
  const [groqApiKey, setGroqApiKey] = useState('');
  const [financialDataApiKey, setFinancialDataApiKey] = useState('');
  
  // Results state
  const [portfolioValue, setPortfolioValue] = useState(initialCapital);
  const [portfolioHistory, setPortfolioHistory] = useState([]);
  const [decisions, setDecisions] = useState({});
  const [analystSignals, setAnalystSignals] = useState({});

  // Default dates
  function getDefaultStartDate() {
    const date = new Date();
    date.setMonth(date.getMonth() - 3);
    return date.toISOString().split('T')[0];
  }

  function getDefaultEndDate() {
    return new Date().toISOString().split('T')[0];
  }

  // Generate mock data for demonstration
  useEffect(() => {
    // Mock portfolio history
    const mockHistory = generateMockPortfolioHistory();
    setPortfolioHistory(mockHistory);
    
    // Mock trading decisions
    const mockDecisions = {
      'AAPL': { action: 'BUY', quantity: 15, confidence: 78.5, reasoning: 'Strong fundamentals and positive technical indicators' },
      'MSFT': { action: 'HOLD', quantity: 0, confidence: 65.2, reasoning: 'Neutral signals with balanced bullish and bearish indicators' },
      'GOOGL': { action: 'SELL', quantity: 10, confidence: 72.8, reasoning: 'Overvalued with bearish technical patterns' }
    };
    setDecisions(mockDecisions);
    
    // Mock analyst signals
    const mockSignals = generateMockAnalystSignals();
    setAnalystSignals(mockSignals);
  }, []);

  const generateMockPortfolioHistory = () => {
    const data = [];
    const startingValue = initialCapital;
    let currentValue = startingValue;
    
    // Generate data for the last 30 days
    for (let i = 30; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      
      // Random daily fluctuation between -2% and +2%
      const dailyChange = (Math.random() * 4 - 2) / 100;
      currentValue = currentValue * (1 + dailyChange);
      
      data.push({
        date: date.toISOString().split('T')[0],
        value: Math.round(currentValue * 100) / 100,
        cash: Math.round(currentValue * 0.3 * 100) / 100,
        invested: Math.round(currentValue * 0.7 * 100) / 100,
      });
    }
    
    return data;
  };

  const generateMockAnalystSignals = () => {
    const analysts = {
      'ben_graham_agent': { displayName: 'Ben Graham' },
      'warren_buffett_agent': { displayName: 'Warren Buffett' },
      'cathie_wood_agent': { displayName: 'Cathie Wood' },
      'technical_analyst_agent': { displayName: 'Technical Analyst' },
      'fundamentals_agent': { displayName: 'Fundamentals Analyst' },
    };
    
    const signals = {};
    const tickers = ['AAPL', 'MSFT', 'GOOGL'];
    const possibleSignals = ['bullish', 'neutral', 'bearish'];
    
    Object.keys(analysts).forEach(analyst => {
      signals[analyst] = {};
      tickers.forEach(ticker => {
        const signalType = possibleSignals[Math.floor(Math.random() * possibleSignals.length)];
        signals[analyst][ticker] = {
          signal: signalType,
          confidence: Math.round(Math.random() * 50 + 50), // 50-100
          reasoning: `${signalType.charAt(0).toUpperCase() + signalType.slice(1)} on ${ticker} based on analysis.`
        };
      });
    });
    
    return signals;
  };

  // Handler for "Run Hedge Fund" button
  const handleRunHedgeFund = () => {
    setIsRunning(true);
    
    // Simulate API call with a delay
    setTimeout(() => {
      const newHistory = generateMockPortfolioHistory();
      setPortfolioHistory(newHistory);
      setPortfolioValue(newHistory[newHistory.length - 1].value);
      const newSignals = generateMockAnalystSignals();
      setAnalystSignals(newSignals);
      setIsRunning(false);
    }, 2000);
  };

  // Handler for "Run Backtest" button
  const handleRunBacktest = () => {
    setIsRunning(true);
    setTimeout(() => {
      const newHistory = generateMockPortfolioHistory();
      setPortfolioHistory(newHistory);
      setPortfolioValue(newHistory[newHistory.length - 1].value);
      setIsRunning(false);
    }, 3000);
  };

  // Save API Configuration
  const handleSaveApiConfig = () => {
    // In a real implementation, this would actually save the API keys
    // For now, we'll just close the modal
    setShowApiKeySetup(false);
  };

  // Calculate performance metrics
  const calculatePerformance = () => {
    if (portfolioHistory.length < 2) return { returnPct: 0, sharpe: 0, sortino: 0, maxDrawdown: 0 };
    
    const initial = portfolioHistory[0].value;
    const final = portfolioHistory[portfolioHistory.length - 1].value;
    const returnPct = ((final - initial) / initial) * 100;
    
    // Simple Sharpe ratio approximation
    const sharpeRatio = 0.76;
    const maxDrawdown = 10.28;
    
    return {
      returnPct: returnPct.toFixed(2),
      sharpe: sharpeRatio.toFixed(2),
      sortino: (sharpeRatio * 1.2).toFixed(2),
      maxDrawdown: maxDrawdown.toFixed(2)
    };
  };

  const performance = calculatePerformance();

  // Available analysts for selection
  const availableAnalysts = [
    { value: 'ben_graham', display: 'Ben Graham' },
    { value: 'bill_ackman', display: 'Bill Ackman' },
    { value: 'cathie_wood', display: 'Cathie Wood' },
    { value: 'charlie_munger', display: 'Charlie Munger' },
    { value: 'warren_buffett', display: 'Warren Buffett' },
    { value: 'technical_analyst', display: 'Technical Analyst' },
    { value: 'fundamentals_analyst', display: 'Fundamentals Analyst' },
    { value: 'sentiment_analyst', display: 'Sentiment Analyst' },
    { value: 'valuation_analyst', display: 'Valuation Analyst' },
  ];

  // Available LLM models for selection
  const availableModels = [
    { value: 'gpt-4o', display: '[OpenAI] GPT-4o' },
    { value: 'gpt-4o-mini', display: '[OpenAI] GPT-4o-mini' },
    { value: 'claude-3-5-sonnet-latest', display: '[Anthropic] Claude 3.5 Sonnet' },
    { value: 'claude-3-5-haiku-latest', display: '[Anthropic] Claude 3.5 Haiku' },
    { value: 'deepseek-r1-distill-llama-70b', display: '[Groq] DeepSeek R1 70b' },
    { value: 'llama-3.3-70b-versatile', display: '[Groq] Llama 3.3 70b' },
    { value: 'o1', display: '[OpenAI] o1' },
    { value: 'o3-mini', display: '[OpenAI] o3-mini' },
  ];

  // Helper functions for styling based on signal/action
  const getSignalClass = (signal) => {
    if (!signal) return '';
    
    switch(signal.toLowerCase()) {
      case 'bullish': return 'signal-bullish';
      case 'bearish': return 'signal-bearish';
      case 'neutral': return 'signal-neutral';
      default: return '';
    }
  };

  const getActionClass = (action) => {
    if (!action) return '';
    
    switch(action.toUpperCase()) {
      case 'BUY': return 'action-buy';
      case 'SELL': return 'action-sell';
      case 'HOLD': return 'action-hold';
      default: return '';
    }
  };

  // Toggle analyst selection
  const toggleAnalyst = (analyst) => {
    if (selectedAnalysts.includes(analyst)) {
      setSelectedAnalysts(selectedAnalysts.filter(a => a !== analyst));
    } else {
      setSelectedAnalysts([...selectedAnalysts, analyst]);
    }
  };

  return (
    <div className={`hedge-fund-container ${darkMode ? 'dark-mode' : 'light-mode'}`}>
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <h1 className="header-title">
            <span className="icon">📊</span> AI Hedge Fund Dashboard
          </h1>
          <div className="header-actions">
            <button 
              className="api-settings-button"
              onClick={() => setShowApiKeySetup(!showApiKeySetup)}
            >
              <span className="icon">⚙️</span> API Settings
            </button>
            <button 
              className="dark-mode-toggle"
              onClick={() => setDarkMode(!darkMode)}
            >
              {darkMode ? '☀️' : '🌙'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {/* Tabs */}
        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
          <button 
            className={`tab ${activeTab === 'run' ? 'active' : ''}`}
            onClick={() => setActiveTab('run')}
          >
            Run Fund
          </button>
          <button 
            className={`tab ${activeTab === 'backtest' ? 'active' : ''}`}
            onClick={() => setActiveTab('backtest')}
          >
            Backtest
          </button>
          <button 
            className={`tab ${activeTab === 'analysis' ? 'active' : ''}`}
            onClick={() => setActiveTab('analysis')}
          >
            Analysis
          </button>
        </div>

        {/* Dashboard Tab Content */}
        {activeTab === 'dashboard' && (
          <div className="dashboard-content">
            {/* Portfolio Summary Cards */}
            <div className="summary-cards">
              <div className="summary-card">
                <div className="card-header">
                  <span className="icon">💲</span>
                  <span className="card-title">Portfolio Value</span>
                </div>
                <div className="card-value">${portfolioValue.toLocaleString()}</div>
                <div className="card-trend positive">
                  <span className="trend-arrow">↗</span> {performance.returnPct}%
                </div>
              </div>
              
              <div className="summary-card">
                <div className="card-header">
                  <span className="icon">📈</span>
                  <span className="card-title">Sharpe Ratio</span>
                </div>
                <div className="card-value">{performance.sharpe}</div>
                <div className="card-subtitle">Risk-adjusted performance</div>
              </div>
              
              <div className="summary-card">
                <div className="card-header">
                  <span className="icon">📉</span>
                  <span className="card-title">Max Drawdown</span>
                </div>
                <div className="card-value">{performance.maxDrawdown}%</div>
                <div className="card-subtitle">Maximum loss from peak</div>
              </div>
              
              <div className="summary-card">
                <div className="card-header">
                  <span className="icon">📊</span>
                  <span className="card-title">Active Positions</span>
                </div>
                <div className="card-value">{Object.keys(decisions).length}</div>
                <div className="card-subtitle">{Object.keys(decisions).join(', ')}</div>
              </div>
            </div>

            {/* Portfolio Performance Chart */}
            <div className="chart-card">
              <h2 className="card-title">Portfolio Performance</h2>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={portfolioHistory}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis 
                      tickFormatter={(value) => `$${value.toLocaleString()}`}
                      domain={['dataMin - 5000', 'dataMax + 5000']} 
                    />
                    <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, 'Value']} />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="value" 
                      stroke="#3b82f6" 
                      name="Portfolio Value" 
                      strokeWidth={2} 
                      dot={{ r: 3 }} 
                    />
                    <Line 
                      type="monotone" 
                      dataKey="cash" 
                      stroke="#10b981" 
                      name="Cash" 
                      strokeWidth={1} 
                      strokeDasharray="5 5" 
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Trading Activity Table */}
            <div className="table-card">
              <h2 className="card-title">Recent Trading Activity</h2>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Ticker</th>
                      <th>Action</th>
                      <th>Quantity</th>
                      <th>Confidence</th>
                      <th>Reasoning</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(decisions).map(([ticker, decision]) => (
                      <tr key={ticker}>
                        <td className="ticker-cell">{ticker}</td>
                        <td>
                          <span className={`action-badge ${getActionClass(decision.action)}`}>
                            {decision.action}
                          </span>
                        </td>
                        <td className="number-cell">{decision.quantity}</td>
                        <td className="number-cell">{decision.confidence}%</td>
                        <td className="reasoning-cell">{decision.reasoning}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Run Fund Tab Content */}
        {activeTab === 'run' && (
          <div className="run-fund-content">
            <div className="form-card">
              <h2 className="card-title">Run AI Hedge Fund</h2>
              <div className="form-grid">
                <div className="form-group full-width">
                  <label>Stock Tickers (comma-separated)</label>
                  <input 
                    type="text"
                    value={tickers}
                    onChange={(e) => setTickers(e.target.value)}
                    placeholder="AAPL,MSFT,GOOGL"
                  />
                  <div className="help-text">Enter stock symbols separated by commas</div>
                </div>

                <div className="form-group">
                  <label>Start Date</label>
                  <input 
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label>End Date</label>
                  <input 
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                  />
                </div>

                <div className="form-group full-width">
                  <label>Initial Capital</label>
                  <input 
                    type="number"
                    value={initialCapital}
                    onChange={(e) => setInitialCapital(parseInt(e.target.value))}
                  />
                </div>

                <div className="form-group full-width">
                  <label>Select Analysts</label>
                  <div className="analysts-grid">
                    {availableAnalysts.map(analyst => (
                      <div 
                        key={analyst.value}
                        className="analyst-checkbox-container"
                      >
                        <label className="analyst-checkbox-label">
                          <input 
                            type="checkbox"
                            checked={selectedAnalysts.includes(analyst.value)}
                            onChange={() => toggleAnalyst(analyst.value)}
                          />
                          <span>{analyst.display}</span>
                        </label>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="form-group full-width">
                  <label>LLM Model</label>
                  <select 
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                  >
                    {availableModels.map(model => (
                      <option key={model.value} value={model.value}>
                        {model.display}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <button 
                className="primary-button full-width"
                onClick={handleRunHedgeFund}
                disabled={isRunning}
              >
                {isRunning ? 'Running...' : 'Run Hedge Fund'}
              </button>
            </div>
          </div>
        )}

        {/* Backtest Tab Content */}
        {activeTab === 'backtest' && (
          <div className="backtest-content">
            <div className="form-card">
              <h2 className="card-title">Backtest Strategy</h2>
              <div className="form-grid">
                <div className="form-group full-width">
                  <label>Stock Tickers (comma-separated)</label>
                  <input 
                    type="text"
                    value={tickers}
                    onChange={(e) => setTickers(e.target.value)}
                    placeholder="AAPL,MSFT,GOOGL"
                  />
                </div>

                <div className="form-group">
                  <label>Start Date</label>
                  <input 
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label>End Date</label>
                  <input 
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                  />
                </div>

                <div className="form-group full-width">
                  <label>Initial Capital</label>
                  <input 
                    type="number"
                    value={initialCapital}
                    onChange={(e) => setInitialCapital(parseInt(e.target.value))}
                  />
                </div>

                <div className="form-group full-width">
                  <label>Select Analysts</label>
                  <div className="analysts-grid">
                    {availableAnalysts.map(analyst => (
                      <div 
                        key={analyst.value}
                        className="analyst-checkbox-container"
                      >
                        <label className="analyst-checkbox-label">
                          <input 
                            type="checkbox"
                            checked={selectedAnalysts.includes(analyst.value)}
                            onChange={() => toggleAnalyst(analyst.value)}
                          />
                          <span>{analyst.display}</span>
                        </label>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="form-group">
                  <label>LLM Model</label>
                  <select 
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                  >
                    {availableModels.map(model => (
                      <option key={model.value} value={model.value}>
                        {model.display}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Margin Requirement</label>
                  <input 
                    type="number" 
                    step="0.1"
                    min="0"
                    max="1"
                    placeholder="0.0"
                  />
                  <div className="help-text">0.5 = 50% margin required</div>
                </div>

                <div className="form-group flex-row">
                  <label className="checkbox-label">
                    <input type="checkbox" />
                    <span>Show Reasoning</span>
                  </label>
                </div>
              </div>

              <button 
                className="primary-button full-width"
                onClick={handleRunBacktest}
                disabled={isRunning}
              >
                {isRunning ? 'Running Backtest...' : 'Run Backtest'}
              </button>
            </div>

            {portfolioHistory.length > 0 && (
              <div className="results-card">
                <h2 className="card-title">Backtest Results</h2>
                <div className="metrics-grid">
                  <div className="metric">
                    <div className="metric-label">Total Return</div>
                    <div className={`metric-value ${performance.returnPct >= 0 ? 'positive' : 'negative'}`}>
                      {performance.returnPct}%
                    </div>
                  </div>
                  <div className="metric">
                    <div className="metric-label">Sharpe Ratio</div>
                    <div className="metric-value">{performance.sharpe}</div>
                  </div>
                  <div className="metric">
                    <div className="metric-label">Sortino Ratio</div>
                    <div className="metric-value">{performance.sortino}</div>
                  </div>
                  <div className="metric">
                    <div className="metric-label">Max Drawdown</div>
                    <div className="metric-value negative">{performance.maxDrawdown}%</div>
                  </div>
                </div>

                <div className="chart-container">
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={portfolioHistory}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis tickFormatter={(value) => `$${value.toLocaleString()}`} />
                      <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, 'Value']} />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="value" 
                        stroke="#3b82f6" 
                        name="Portfolio Value" 
                        strokeWidth={2} 
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Analysis Tab Content */}
        {activeTab === 'analysis' && (
          <div className="analysis-content">
            <div className="table-card">
              <h2 className="card-title">Analyst Signals</h2>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Analyst</th>
                      {Object.keys(decisions).map(ticker => (
                        <th key={ticker}>{ticker}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(analystSignals).map(([analystKey, signals]) => {
                      const displayName = analystKey.replace('_agent', '').replace(/_/g, ' ');
                      
                      return (
                        <tr key={analystKey}>
                          <td>{displayName}</td>
                          {Object.keys(decisions).map(ticker => {
                            const signal = signals[ticker] || { signal: 'unknown', confidence: 0 };
                            return (
                              <td key={ticker} className="signal-cell">
                                <div className={`signal-indicator ${getSignalClass(signal.signal)}`}>
                                  {signal.signal}
                                </div>
                                <div className="signal-confidence">{signal.confidence}%</div>
                              </td>
                            );
                          })}
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="chart-card">
              <h2 className="card-title">Signal Distribution</h2>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart
                    data={Object.keys(decisions).map(ticker => {
                      // Count signals by type for this ticker
                      const signalCounts = { ticker, bullish: 0, bearish: 0, neutral: 0 };
                      
                      Object.values(analystSignals).forEach(signals => {
                        if (signals[ticker]) {
                          const signal = signals[ticker].signal;
                          if (signal === 'bullish') signalCounts.bullish++;
                          else if (signal === 'bearish') signalCounts.bearish++;
                          else if (signal === 'neutral') signalCounts.neutral++;
                        }
                      });
                      
                      return signalCounts;
                    })}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="ticker" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="bullish" stackId="a" fill="#22c55e" name="Bullish" />
                    <Bar dataKey="neutral" stackId="a" fill="#f59e0b" name="Neutral" />
                    <Bar dataKey="bearish" stackId="a" fill="#ef4444" name="Bearish" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* API Settings Modal */}
        {showApiKeySetup && (
          <div className="modal-overlay">
            <div className="modal">
              <h2 className="modal-title">API Configuration</h2>
              <div className="modal-content">
                <div className="form-group">
                  <label>OpenAI API Key</label>
                  <input 
                    type="password" 
                    placeholder="sk-..." 
                    value={openaiApiKey}
                    onChange={(e) => setOpenaiApiKey(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>OpenAI Base URL (Optional)</label>
                  <input 
                    type="text" 
                    placeholder="https://your-custom-endpoint.com/v1" 
                    value={openaiBaseUrl}
                    onChange={(e) => setOpenaiBaseUrl(e.target.value)}
                  />
                  <div className="help-text">For Azure OpenAI or other API-compatible endpoints</div>
                </div>
                <div className="form-group">
                  <label>Custom Model Name (Optional)</label>
                  <input 
                    type="text" 
                    placeholder="gpt-4o or deployment-name" 
                    value={customModelName}
                    onChange={(e) => setCustomModelName(e.target.value)}
                  />
                  <div className="help-text">Override the model selected in the UI</div>
                </div>
                <div className="form-group">
                  <label>Anthropic API Key</label>
                  <input 
                    type="password" 
                    placeholder="sk-ant-..." 
                    value={anthropicApiKey}
                    onChange={(e) => setAnthropicApiKey(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Groq API Key</label>
                  <input 
                    type="password" 
                    placeholder="gsk_..." 
                    value={groqApiKey}
                    onChange={(e) => setGroqApiKey(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Financial Datasets API Key</label>
                  <input 
                    type="password" 
                    placeholder="Your API key for financial data" 
                    value={financialDataApiKey}
                    onChange={(e) => setFinancialDataApiKey(e.target.value)}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  className="secondary-button"
                  onClick={() => setShowApiKeySetup(false)}
                >
                  Cancel
                </button>
                <button 
                  className="primary-button"
                  onClick={handleSaveApiConfig}
                >
                  Save Configuration
                </button>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
        AI Hedge Fund - For educational purposes only. Not financial advice.
      </footer>
    </div>
  );
};

export default AIHedgeFundDashboard;