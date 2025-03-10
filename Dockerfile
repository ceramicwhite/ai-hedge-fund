FROM python:3.13-slim

ENV PATH="${PATH}:/root/.local/bin"

WORKDIR /ai-hedge-fund

COPY pyproject.toml poetry.lock ./

RUN apt update && apt install -y build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install poetry \
    && poetry install

COPY . .

ENTRYPOINT ["poetry", "run", "python", "-u", "src/main.py"]

CMD ["--ticker", "AAPL"] 