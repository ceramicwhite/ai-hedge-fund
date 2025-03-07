import React, { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/alert';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { ArrowUpRight, ArrowDownRight, DollarSign, Briefcase, TrendingUp, BarChart2, Calendar, Settings, Activity, RefreshCw } from 'lucide-react';
import _ from 'lodash';

const AIHedgeFundDashboard = () => {
  // Application state
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

  // Mock data for the UI demonstration
  useEffect(() => {
    // Mock portfolio history data
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

  // Generate mock portfolio history data for demonstration
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

  // Generate mock analyst signals for demonstration
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
    
    // In a real implementation, this would call the backend to execute the hedge fund
    // For now, we'll simulate a delay and update with new mock data
    setTimeout(() => {
      // Generate new mock data
      const newHistory = generateMockPortfolioHistory();
      setPortfolioHistory(newHistory);
      
      // Update portfolio value
      setPortfolioValue(newHistory[newHistory.length - 1].value);
      
      // Generate new mock signals
      const newSignals = generateMockAnalystSignals();
      setAnalystSignals(newSignals);
      
      setIsRunning(false);
    }, 2000);
  };

  // Handler for "Run Backtest" button
  const handleRunBacktest = () => {
    setIsRunning(true);
    
    // In a real implementation, this would call the backend to execute the backtest
    // For now, we'll simulate a delay and update with new mock data
    setTimeout(() => {
      // Generate new mock data over the selected period
      const newHistory = generateMockPortfolioHistory();
      setPortfolioHistory(newHistory);
      
      // Update portfolio value
      setPortfolioValue(newHistory[newHistory.length - 1].value);
      
      setIsRunning(false);
    }, 3000);
  };

  // Calculate performance metrics
  const calculatePerformance = () => {
    if (portfolioHistory.length < 2) return { returnPct: 0, sharpe: 0, sortino: 0, maxDrawdown: 0 };
    
    const initial = portfolioHistory[0].value;
    const final = portfolioHistory[portfolioHistory.length - 1].value;
    const returnPct = ((final - initial) / initial) * 100;
    
    // Calculate daily returns
    const dailyReturns = [];
    for (let i = 1; i < portfolioHistory.length; i++) {
      dailyReturns.push((portfolioHistory[i].value - portfolioHistory[i-1].value) / portfolioHistory[i-1].value);
    }
    
    // Calculate Sharpe ratio (simplified)
    const avgReturn = _.mean(dailyReturns);
    const stdDev = Math.sqrt(_.sum(_.map(dailyReturns, r => Math.pow(r - avgReturn, 2))) / dailyReturns.length);
    const sharpe = (avgReturn / stdDev) * Math.sqrt(252); // Annualized
    
    // Calculate max drawdown
    let maxDrawdown = 0;
    let peak = portfolioHistory[0].value;
    
    for (const day of portfolioHistory) {
      if (day.value > peak) peak = day.value;
      const drawdown = (peak - day.value) / peak;
      if (drawdown > maxDrawdown) maxDrawdown = drawdown;
    }
    
    return {
      returnPct: returnPct.toFixed(2),
      sharpe: sharpe.toFixed(2),
      sortino: (sharpe * 1.2).toFixed(2), // Simplified approximation
      maxDrawdown: (maxDrawdown * 100).toFixed(2)
    };
  };

  // Performance metrics
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

  // Signal color mapping
  const getSignalColor = (signal) => {
    if (!signal) return 'gray';
    
    switch(signal.toLowerCase()) {
      case 'bullish': return 'green';
      case 'bearish': return 'red';
      case 'neutral': return 'orange';
      default: return 'gray';
    }
  };

  // Action color mapping
  const getActionColor = (action) => {
    if (!action) return 'gray';
    
    switch(action.toUpperCase()) {
      case 'BUY': return 'green';
      case 'SELL': return 'red';
      case 'HOLD': return 'blue';
      case 'SHORT': return 'purple';
      case 'COVER': return 'teal';
      default: return 'gray';
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
    <div className="flex flex-col min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-blue-600 text-white p-4 shadow-md">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold flex items-center">
            <Briefcase className="mr-2" /> AI Hedge Fund Dashboard
          </h1>
          <Button variant="outline" onClick={() => setShowApiKeySetup(!showApiKeySetup)}>
            <Settings className="mr-2 h-4 w-4" /> API Settings
          </Button>
        </div>
      </header>

      {/* API Key Setup Modal */}
      {showApiKeySetup && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>API Configuration</CardTitle>
              <CardDescription>Set up your API keys to use the hedge fund</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">OpenAI API Key</label>
                <Input type="password" placeholder="sk-..." />
              </div>
              <div>
                <label className="text-sm font-medium">Anthropic API Key</label>
                <Input type="password" placeholder="sk-ant-..." />
              </div>
              <div>
                <label className="text-sm font-medium">Groq API Key</label>
                <Input type="password" placeholder="gsk_..." />
              </div>
              <div>
                <label className="text-sm font-medium">Financial Datasets API Key</label>
                <Input type="password" placeholder="Your API key for financial data" />
              </div>
            </CardContent>
            <CardFooter className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowApiKeySetup(false)}>Cancel</Button>
              <Button onClick={() => setShowApiKeySetup(false)}>Save Configuration</Button>
            </CardFooter>
          </Card>
        </div>
      )}

      {/* Main Content */}
      <main className="flex-1 container mx-auto p-4">
        <Tabs defaultValue="dashboard">
          <TabsList className="mb-4">
            <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
            <TabsTrigger value="run">Run Fund</TabsTrigger>
            <TabsTrigger value="backtest">Backtest</TabsTrigger>
            <TabsTrigger value="analysis">Analysis</TabsTrigger>
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard" className="space-y-4">
            {/* Portfolio Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-500">Portfolio Value</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center">
                    <DollarSign className="h-5 w-5 text-gray-500 mr-2" />
                    <span className="text-2xl font-bold">${portfolioValue.toLocaleString()}</span>
                  </div>
                  <div className="mt-1 flex items-center">
                    {performance.returnPct >= 0 ? (
                      <ArrowUpRight className="h-4 w-4 text-green-500 mr-1" />
                    ) : (
                      <ArrowDownRight className="h-4 w-4 text-red-500 mr-1" />
                    )}
                    <span className={performance.returnPct >= 0 ? "text-green-500" : "text-red-500"}>
                      {performance.returnPct}%
                    </span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-500">Sharpe Ratio</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center">
                    <Activity className="h-5 w-5 text-gray-500 mr-2" />
                    <span className="text-2xl font-bold">{performance.sharpe}</span>
                  </div>
                  <div className="mt-1 text-sm text-gray-500">
                    Risk-adjusted performance
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-500">Max Drawdown</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center">
                    <TrendingUp className="h-5 w-5 text-gray-500 mr-2" />
                    <span className="text-2xl font-bold">{performance.maxDrawdown}%</span>
                  </div>
                  <div className="mt-1 text-sm text-gray-500">
                    Maximum loss from peak
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-500">Active Positions</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center">
                    <BarChart2 className="h-5 w-5 text-gray-500 mr-2" />
                    <span className="text-2xl font-bold">{Object.keys(decisions).length}</span>
                  </div>
                  <div className="mt-1 text-sm text-gray-500">
                    {Object.keys(decisions).join(", ")}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Portfolio Performance Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Portfolio Performance</CardTitle>
                <CardDescription>Historical portfolio value over time</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={portfolioHistory} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip 
                        formatter={(value) => [`$${value.toLocaleString()}`, 'Value']}
                        labelFormatter={(label) => `Date: ${label}`}
                      />
                      <Legend />
                      <Line type="monotone" dataKey="value" stroke="#3b82f6" name="Portfolio Value" strokeWidth={2} />
                      <Line type="monotone" dataKey="cash" stroke="#10b981" name="Cash" strokeWidth={1} strokeDasharray="5 5" />
                      <Line type="monotone" dataKey="invested" stroke="#6366f1" name="Invested" strokeWidth={1} strokeDasharray="3 3" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Recent Trading Activity */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Trading Activity</CardTitle>
                <CardDescription>Latest trades and decisions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="px-4 py-2 text-left">Ticker</th>
                        <th className="px-4 py-2 text-left">Action</th>
                        <th className="px-4 py-2 text-right">Quantity</th>
                        <th className="px-4 py-2 text-right">Confidence</th>
                        <th className="px-4 py-2 text-left">Reasoning</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(decisions).map(([ticker, decision]) => (
                        <tr key={ticker} className="border-b">
                          <td className="px-4 py-2 font-medium">{ticker}</td>
                          <td className="px-4 py-2">
                            <span
                              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${getActionColor(decision.action)}-100 text-${getActionColor(decision.action)}-800`}
                              style={{ 
                                backgroundColor: `${getActionColor(decision.action) === 'green' ? '#dcfce7' : 
                                  getActionColor(decision.action) === 'red' ? '#fee2e2' : 
                                  getActionColor(decision.action) === 'blue' ? '#dbeafe' : 
                                  getActionColor(decision.action) === 'purple' ? '#f3e8ff' : 
                                  getActionColor(decision.action) === 'teal' ? '#ccfbf1' : '#f3f4f6'}`,
                                color: `${getActionColor(decision.action) === 'green' ? '#14532d' : 
                                  getActionColor(decision.action) === 'red' ? '#7f1d1d' : 
                                  getActionColor(decision.action) === 'blue' ? '#1e3a8a' : 
                                  getActionColor(decision.action) === 'purple' ? '#581c87' : 
                                  getActionColor(decision.action) === 'teal' ? '#134e4a' : '#1f2937'}`
                              }}
                            >
                              {decision.action}
                            </span>
                          </td>
                          <td className="px-4 py-2 text-right">{decision.quantity}</td>
                          <td className="px-4 py-2 text-right">{decision.confidence}%</td>
                          <td className="px-4 py-2 text-sm max-w-xs truncate">{decision.reasoning}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Run Fund Tab */}
          <TabsContent value="run" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Run AI Hedge Fund</CardTitle>
                <CardDescription>Configure and run your AI hedge fund</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Ticker Selection */}
                <div>
                  <label className="block text-sm font-medium mb-2">Stock Tickers (comma-separated)</label>
                  <Input 
                    value={tickers} 
                    onChange={(e) => setTickers(e.target.value)}
                    placeholder="AAPL,MSFT,GOOGL"
                  />
                  <p className="mt-1 text-sm text-gray-500">
                    Enter stock symbols separated by commas
                  </p>
                </div>

                {/* Date Range Selection */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Start Date</label>
                    <Input 
                      type="date" 
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">End Date</label>
                    <Input 
                      type="date" 
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                    />
                  </div>
                </div>

                {/* Initial Capital */}
                <div>
                  <label className="block text-sm font-medium mb-2">Initial Capital</label>
                  <Input 
                    type="number" 
                    value={initialCapital}
                    onChange={(e) => setInitialCapital(parseFloat(e.target.value))}
                    placeholder="100000"
                  />
                </div>

                {/* Analyst Selection */}
                <div>
                  <label className="block text-sm font-medium mb-2">Select Analysts</label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {availableAnalysts.map(analyst => (
                      <div 
                        key={analyst.value}
                        className={`px-3 py-2 rounded-md cursor-pointer text-sm transition-colors
                          ${selectedAnalysts.includes(analyst.value) 
                            ? 'bg-blue-100 text-blue-800 border border-blue-300' 
                            : 'bg-gray-100 hover:bg-gray-200 text-gray-700 border border-gray-200'
                          }`}
                        onClick={() => toggleAnalyst(analyst.value)}
                      >
                        {analyst.display}
                      </div>
                    ))}
                  </div>
                </div>

                {/* LLM Model Selection */}
                <div>
                  <label className="block text-sm font-medium mb-2">LLM Model</label>
                  <select 
                    className="w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                  >
                    {availableModels.map(model => (
                      <option key={model.value} value={model.value}>{model.display}</option>
                    ))}
                  </select>
                </div>
              </CardContent>
              <CardFooter>
                <Button 
                  className="w-full"
                  onClick={handleRunHedgeFund}
                  disabled={isRunning}
                >
                  {isRunning ? (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                      Running...
                    </>
                  ) : (
                    'Run Hedge Fund'
                  )}
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>

          {/* Backtest Tab */}
          <TabsContent value="backtest" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Backtest Strategy</CardTitle>
                <CardDescription>Evaluate the performance of your trading strategy</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Ticker Selection */}
                <div>
                  <label className="block text-sm font-medium mb-2">Stock Tickers (comma-separated)</label>
                  <Input 
                    value={tickers} 
                    onChange={(e) => setTickers(e.target.value)}
                    placeholder="AAPL,MSFT,GOOGL"
                  />
                </div>

                {/* Date Range Selection */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Start Date</label>
                    <Input 
                      type="date" 
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">End Date</label>
                    <Input 
                      type="date" 
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                    />
                  </div>
                </div>

                {/* Initial Capital */}
                <div>
                  <label className="block text-sm font-medium mb-2">Initial Capital</label>
                  <Input 
                    type="number" 
                    value={initialCapital}
                    onChange={(e) => setInitialCapital(parseFloat(e.target.value))}
                    placeholder="100000"
                  />
                </div>

                {/* Analyst Selection */}
                <div>
                  <label className="block text-sm font-medium mb-2">Select Analysts</label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {availableAnalysts.map(analyst => (
                      <div 
                        key={analyst.value}
                        className={`px-3 py-2 rounded-md cursor-pointer text-sm transition-colors
                          ${selectedAnalysts.includes(analyst.value) 
                            ? 'bg-blue-100 text-blue-800 border border-blue-300' 
                            : 'bg-gray-100 hover:bg-gray-200 text-gray-700 border border-gray-200'
                          }`}
                        onClick={() => toggleAnalyst(analyst.value)}
                      >
                        {analyst.display}
                      </div>
                    ))}
                  </div>
                </div>

                {/* LLM Model Selection */}
                <div>
                  <label className="block text-sm font-medium mb-2">LLM Model</label>
                  <select 
                    className="w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                  >
                    {availableModels.map(model => (
                      <option key={model.value} value={model.value}>{model.display}</option>
                    ))}
                  </select>
                </div>

                {/* Additional Backtest Settings */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Margin Requirement</label>
                    <Input type="number" placeholder="0.0" />
                    <p className="mt-1 text-sm text-gray-500">0.5 = 50% margin required</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Show Reasoning</label>
                    <div className="flex items-center mt-2">
                      <input type="checkbox" className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
                      <span className="ml-2 text-sm text-gray-700">Display detailed reasoning from each analyst</span>
                    </div>
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Button 
                  className="w-full"
                  onClick={handleRunBacktest}
                  disabled={isRunning}
                >
                  {isRunning ? (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                      Running Backtest...
                    </>
                  ) : (
                    'Run Backtest'
                  )}
                </Button>
              </CardFooter>
            </Card>

            {portfolioHistory.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Backtest Results</CardTitle>
                  <CardDescription>Performance metrics and statistics</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <div className="text-sm font-medium text-gray-500">Total Return</div>
                      <div className={`text-xl font-bold ${performance.returnPct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {performance.returnPct}%
                      </div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-500">Sharpe Ratio</div>
                      <div className="text-xl font-bold">{performance.sharpe}</div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-500">Sortino Ratio</div>
                      <div className="text-xl font-bold">{performance.sortino}</div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-500">Max Drawdown</div>
                      <div className="text-xl font-bold text-red-600">{performance.maxDrawdown}%</div>
                    </div>
                  </div>

                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={portfolioHistory} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip 
                          formatter={(value) => [`$${value.toLocaleString()}`, 'Value']}
                          labelFormatter={(label) => `Date: ${label}`}
                        />
                        <Legend />
                        <Line type="monotone" dataKey="value" stroke="#3b82f6" name="Portfolio Value" strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Analysis Tab */}
          <TabsContent value="analysis" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Analyst Signals</CardTitle>
                <CardDescription>Breakdown of signals from each analyst</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="px-4 py-2 text-left">Analyst</th>
                        {Object.keys(decisions).map(ticker => (
                          <th key={ticker} className="px-4 py-2 text-center">{ticker}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(analystSignals).map(([analystKey, signals]) => {
                        const displayName = analystKey.replace('_agent', '').replace(/_/g, ' ');
                        
                        return (
                          <tr key={analystKey} className="border-b">
                            <td className="px-4 py-2 font-medium">{displayName}</td>
                            {Object.keys(decisions).map(ticker => {
                              const signal = signals[ticker] || { signal: 'unknown', confidence: 0 };
                              return (
                                <td key={ticker} className="px-4 py-2 text-center">
                                  <div className="flex flex-col items-center">
                                    <span
                                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium`}
                                      style={{ 
                                        backgroundColor: `${getSignalColor(signal.signal) === 'green' ? '#dcfce7' : 
                                          getSignalColor(signal.signal) === 'red' ? '#fee2e2' : 
                                          getSignalColor(signal.signal) === 'orange' ? '#ffedd5' : '#f3f4f6'}`,
                                        color: `${getSignalColor(signal.signal) === 'green' ? '#14532d' : 
                                          getSignalColor(signal.signal) === 'red' ? '#7f1d1d' : 
                                          getSignalColor(signal.signal) === 'orange' ? '#7c2d12' : '#1f2937'}`
                                      }}
                                    >
                                      {signal.signal || 'N/A'}
                                    </span>
                                    <span className="text-xs text-gray-500 mt-1">{signal.confidence || 0}%</span>
                                  </div>
                                </td>
                              );
                            })}
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Signal Distribution</CardTitle>
                <CardDescription>Breakdown of bullish vs. bearish signals</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
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
                      margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
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
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-4">
        <div className="container mx-auto px-4 text-center text-sm text-gray-500">
          AI Hedge Fund - For educational purposes only. Not financial advice.
        </div>
      </footer>
    </div>
  );
};

export default AIHedgeFundDashboard;