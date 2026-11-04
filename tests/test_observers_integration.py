import pandas as pd
import pytest

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.history import AutoSaveObserver, HistoryObserver, LoggingObserver
from app.operations import Addition


@pytest.fixture
def calc(tmp_path):
    calculator = Calculator(CalculatorConfig(base_dir=tmp_path, auto_save=True))
    calculator.set_operation(Addition())
    return calculator


def test_logging_observer_writes_calculation_to_log_file(calc):
    calc.add_observer(LoggingObserver())
    calc.perform_operation("2", "3")

    log_text = calc.config.log_file.read_text()
    assert "Calculation performed: Addition" in log_text
    assert "= 5" in log_text


def test_autosave_observer_writes_csv_on_new_calculation(calc):
    calc.add_observer(AutoSaveObserver(calc))
    calc.perform_operation("2", "3")

    df = pd.read_csv(calc.config.history_file, encoding=calc.config.default_encoding)
    assert len(df) == 1
    assert df.iloc[0]["operation"] == "Addition"
    assert df.iloc[0]["result"] == 5


def test_all_registered_observers_are_notified(calc):
    seen = []

    class Recorder(HistoryObserver):
        def update(self, calculation):
            seen.append(calculation)

    calc.add_observer(Recorder())
    calc.add_observer(Recorder())
    calc.perform_operation("2", "3")

    assert len(seen) == 2
    assert seen[0] is calc.history[0]


def test_failing_observer_does_not_break_operation_or_other_observers(calc):
    seen = []

    class Broken(HistoryObserver):
        def update(self, calculation):
            raise RuntimeError("boom")

    class Recorder(HistoryObserver):
        def update(self, calculation):
            seen.append(calculation)

    calc.add_observer(Broken())
    calc.add_observer(Recorder())

    result = calc.perform_operation("2", "3")

    assert result == 5
    assert len(calc.history) == 1
    assert len(seen) == 1
    assert "Observer Broken failed: boom" in calc.config.log_file.read_text()
