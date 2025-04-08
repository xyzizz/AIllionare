# AIllionare

AI-powered automated trading system using CrewAI.

## Features

*   Fetches real-time stock data using yfinance.
*   Calculates technical indicators (MACD) using the TA library.
*   Uses Deepseek LLM for analysis or decision making (placeholder).
*   Executes trades via Longbridge API (placeholder).
*   Sends notifications via WeChat and Email.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd AIllionare
    ```

2.  **Install dependencies:**
    ```bash
    poetry install
    ```

3.  **Configure environment variables:**
    *   Copy `.env.example` to `.env`.
    *   Fill in your API keys and other required credentials in the `.env` file.
      ```bash
      cp .env.example .env
      # Edit .env with your details
      ```

## Usage

```bash
poetry run python src/my_project/main.py
```

## Project Structure

```
AIllionare/
├── .gitignore
├── pyproject.toml
├── README.md
├── .env.example
└── src/
    └── my_project/
        ├── __init__.py
        ├── main.py
        ├── crew.py
        ├── tools/
        │   ├── __init__.py
        │   ├── stock_data_tools.py
        │   ├── trading_tools.py
        │   ├── notification_tools.py
        │   └── llm_tools.py # If needed for specific LLM interactions
        └── config/
            ├── __init__.py
            ├── agents.yaml
            └── tasks.yaml
```

## Contributing

[Details on how to contribute]

## License

[License information]

# AIllionaire Project

## Code Style and Formatting

This project uses [Ruff](https://github.com/astral-sh/ruff) for code formatting and linting, managed through pre-commit hooks.

### Setup

1. Install pre-commit:
```bash
pip install pre-commit
```

2. Install the pre-commit hooks:
```bash
pre-commit install
```

3. The hooks will run automatically when you commit changes, but you can also run them manually:
```bash
pre-commit run --all-files
```

### Ruff Configuration

Ruff is configured in the `pyproject.toml` file with the following settings:

- Line length: 88 characters (same as Black)
- Target Python version: 3.10
- Enabled rule sets: 
  - E: pycodestyle errors
  - F: pyflakes
  - B: flake8-bugbear
  - I: isort
  - UP: pyupgrade
  - N: pep8-naming
  - PL: pylint
  - RUF: ruff-specific rules

### Editor Integration

For the best development experience, integrate Ruff with your editor:

- **VS Code**: Install the [Ruff extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)
- **PyCharm**: Use the [Ruff plugin](https://plugins.jetbrains.com/plugin/20574-ruff)

Ruff will automatically format your code and provide linting suggestions as you work. 