# Advanced Calculator

A command-line calculator built with Python. It uses several design patterns (Factory, Memento, Observer), loads its settings from a `.env` file, saves its history to CSV with `pandas`, and is tested with `pytest` at 100% coverage.

---

## Setup

```bash
git clone <repository-url>
cd midterm
python3 -m venv venv
source venv/bin/activate      # Mac/Linux/WSL
venv\Scripts\activate.bat     # Windows
pip install -r requirements.txt
cp .env.example .env
```

## Run

```bash
python main.py
```

## Commands

| Command | Description |
|---|---|
| `add`, `subtract`, `multiply`, `divide` | Basic arithmetic |
| `power` | Raise the first number to the power of the second |
| `root` | nth root: first number is the value, second is the root |
| `modulus` | Remainder of the first number divided by the second |
| `int_divide` | Integer division, discarding the fractional part |
| `percentage` | `(a / b) * 100` |
| `abs_diff` | Absolute difference `|a - b|` |
| `history` | Show calculation history |
| `undo` / `redo` | Revert or restore the last calculation |
| `clear` | Clear history |
| `save` / `load` | Save history to CSV or load it |
| `help` | List commands |
| `exit` | Save history and quit |

Each operation asks for two numbers. Type `cancel` at either prompt to abort.

## Design patterns

- **Factory:** `OperationFactory` in `app/operations.py` creates operation objects by command name. Unknown names raise a clear error.
- **Memento:** `CalculatorMemento` stores snapshots of the history. `undo_stack` and `redo_stack` in `Calculator` give undo and redo. A new calculation clears the redo stack, and undo/redo also auto-save when enabled.
- **Observer:** `LoggingObserver` writes each calculation (operation, operands, result) to the log file. `AutoSaveObserver` saves the history to CSV through `pandas` after each calculation. A failing observer is logged and does not stop the others.

## Configuration

Settings are loaded from `.env` with `python-dotenv`. Copy `.env.example` to `.env` and edit it. If a variable is missing, the default is used. Invalid values raise a `ConfigurationError` on startup.

| Variable | Default | Purpose |
|---|---|---|
| `CALCULATOR_LOG_DIR` | `logs` | Directory for log files |
| `CALCULATOR_HISTORY_DIR` | `history` | Directory for history files |
| `CALCULATOR_MAX_HISTORY_SIZE` | `1000` | Maximum history entries |
| `CALCULATOR_AUTO_SAVE` | `true` | Auto-save history (`true` or `false`) |
| `CALCULATOR_PRECISION` | `10` | Decimal places shown in results |
| `CALCULATOR_MAX_INPUT_VALUE` | `1e999` | Largest accepted input |
| `CALCULATOR_DEFAULT_ENCODING` | `utf-8` | Encoding for the history CSV |

## Error handling

Custom exceptions live in `app/exceptions.py`: `CalculatorError` (base), `ValidationError`, `OperationError` and `ConfigurationError`.

- Inputs must be finite numbers within the configured limit. Text, empty input, `NaN` and `Infinity` are rejected with a message explaining what to enter.
- Division, modulus, integer division and percentage reject a zero divisor. Roots reject negative numbers and a zero root. Power rejects negative exponents.
- CSV problems are reported specifically: an empty file is treated as empty history, and corrupt files, missing columns, wrong encoding and permission errors each give a message saying how to fix them.

## Tests

```bash
pytest --cov=app --cov-fail-under=100
```

GitHub Actions runs this command on every push and pull request to `main`.

## Project layout

```
app/
  calculation.py         Calculation record and result computation
  calculator.py          Calculator, history, undo/redo, observers
  calculator_config.py   Configuration loaded from .env
  calculator_memento.py  Memento for undo/redo
  calculator_repl.py     Command-line interface
  exceptions.py          Custom exceptions
  history.py             Observer classes
  input_validators.py    Input validation
  operations.py          Operations and OperationFactory
tests/                   pytest suite
main.py                  Entry point
```