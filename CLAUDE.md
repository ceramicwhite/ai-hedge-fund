# AI Hedge Fund - Developer Guidelines

## Build & Run Commands
- Install dependencies: `poetry install`
- Run with single ticker: `poetry run python src/main.py --ticker AAPL`
- Run with multiple tickers: `poetry run python src/main.py --ticker AAPL,MSFT,NVDA`
- Run with reasoning: `poetry run python src/main.py --ticker AAPL --show-reasoning`
- Run backtester: `poetry run python src/backtester.py --ticker AAPL`
- Run tests: `poetry run pytest`
- Run single test: `poetry run pytest path/to/test_file.py::test_function_name`
- Lint code: `poetry run black . && poetry run isort . && poetry run flake8 .`

## Code Style Guidelines
- **Formatting**: Black with line length 420
- **Imports**: Use isort for organization
- **Types**: Strong typing with Pydantic models and type hints
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Docstrings**: Required for all functions explaining purpose and parameters
- **Error Handling**: Use try/except with fallback values, avoid uncaught exceptions
- **LLM Calls**: Use `call_llm` helper with proper error handling and fallbacks
- **Progress Tracking**: Use `progress.update_status` to show operation status

## Project Architecture
- **Agents**: Independent specialized investment strategy agents
- **State Management**: LangGraph for workflow orchestration
- **Data Processing**: Financial metrics and structured analysis
- **Visualization**: Rich terminal output with colorama and rich