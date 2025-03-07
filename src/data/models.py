from pydantic import BaseModel
from typing import List, Optional, Dict, Union, Any


class Price(BaseModel):
    open: float
    close: float
    high: float
    low: float
    volume: int
    time: str


class PriceResponse(BaseModel):
    ticker: str
    prices: List[Price]


class FinancialMetrics(BaseModel):
    ticker: str
    report_period: str
    period: str
    currency: str
    market_cap: Optional[float]
    enterprise_value: Optional[float]
    price_to_earnings_ratio: Optional[float]
    price_to_book_ratio: Optional[float]
    price_to_sales_ratio: Optional[float]
    enterprise_value_to_ebitda_ratio: Optional[float]
    enterprise_value_to_revenue_ratio: Optional[float]
    free_cash_flow_yield: Optional[float]
    peg_ratio: Optional[float]
    gross_margin: Optional[float]
    operating_margin: Optional[float]
    net_margin: Optional[float]
    return_on_equity: Optional[float]
    return_on_assets: Optional[float]
    return_on_invested_capital: Optional[float]
    asset_turnover: Optional[float]
    inventory_turnover: Optional[float]
    receivables_turnover: Optional[float]
    days_sales_outstanding: Optional[float]
    operating_cycle: Optional[float]
    working_capital_turnover: Optional[float]
    current_ratio: Optional[float]
    quick_ratio: Optional[float]
    cash_ratio: Optional[float]
    operating_cash_flow_ratio: Optional[float]
    debt_to_equity: Optional[float]
    debt_to_assets: Optional[float]
    interest_coverage: Optional[float]
    revenue_growth: Optional[float]
    earnings_growth: Optional[float]
    book_value_growth: Optional[float]
    earnings_per_share_growth: Optional[float]
    free_cash_flow_growth: Optional[float]
    operating_income_growth: Optional[float]
    ebitda_growth: Optional[float]
    payout_ratio: Optional[float]
    earnings_per_share: Optional[float]
    book_value_per_share: Optional[float]
    free_cash_flow_per_share: Optional[float]


class FinancialMetricsResponse(BaseModel):
    financial_metrics: List[FinancialMetrics]


class LineItem(BaseModel):
    ticker: str
    report_period: str
    period: str
    currency: str

    # Allow additional fields dynamically
    model_config = {"extra": "allow"}


class LineItemResponse(BaseModel):
    search_results: List[LineItem]


class InsiderTrade(BaseModel):
    ticker: str
    issuer: Optional[str]
    name: Optional[str]
    title: Optional[str]
    is_board_director: Optional[bool]
    transaction_date: Optional[str]
    transaction_shares: Optional[float]
    transaction_price_per_share: Optional[float]
    transaction_value: Optional[float]
    shares_owned_before_transaction: Optional[float]
    shares_owned_after_transaction: Optional[float]
    security_title: Optional[str]
    filing_date: str


class InsiderTradeResponse(BaseModel):
    insider_trades: List[InsiderTrade]


class CompanyNews(BaseModel):
    ticker: str
    title: str
    author: str
    source: str
    date: str
    url: str
    sentiment: Optional[str] = None


class CompanyNewsResponse(BaseModel):
    news: List[CompanyNews]


class Position(BaseModel):
    cash: float = 0.0
    shares: int = 0
    ticker: str


class Portfolio(BaseModel):
    positions: Dict[str, Position]  # ticker -> Position mapping
    total_cash: float = 0.0


class AnalystSignal(BaseModel):
    signal: Optional[str] = None
    confidence: Optional[float] = None
    reasoning: Optional[Union[Dict[str, Any], str]] = None
    max_position_size: Optional[float] = None  # For risk management signals


class TickerAnalysis(BaseModel):
    ticker: str
    analyst_signals: Dict[str, AnalystSignal]  # agent_name -> signal mapping


class AgentStateData(BaseModel):
    tickers: List[str]
    portfolio: Portfolio
    start_date: str
    end_date: str
    ticker_analyses: Dict[str, TickerAnalysis]  # ticker -> analysis mapping


class AgentStateMetadata(BaseModel):
    show_reasoning: bool = False
    model_config = {"extra": "allow"}
