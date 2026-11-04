from pathlib import Path

import pytest

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.input_validators import InputValidator
from app.operations import Modulus


@pytest.fixture
def calc(tmp_path, monkeypatch):
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", str(tmp_path / "h.csv"))
    config = CalculatorConfig(base_dir=tmp_path, auto_save=False, default_encoding="utf-8")
    return Calculator(config)


def history_path(calc) -> Path:
    return calc.config.history_file


def test_empty_history_file_is_treated_as_empty_history(calc):
    history_path(calc).write_text("", encoding="utf-8")
    calc.load_history()
    assert calc.history == []


def test_corrupt_csv_gives_clear_message(calc):
    history_path(calc).write_text("a,b\n1,2\n1,2,3,4\n", encoding="utf-8")
    with pytest.raises(OperationError, match="not valid CSV"):
        calc.load_history()


def test_missing_columns_gives_clear_message(calc):
    history_path(calc).write_text("x,y\n1,2\n", encoding="utf-8")
    with pytest.raises(OperationError, match="missing column"):
        calc.load_history()


def test_wrong_encoding_gives_clear_message(calc):
    history_path(calc).write_bytes(b"\xff\xfe\xfa\n1\n")
    with pytest.raises(OperationError, match="cannot be read as utf-8"):
        calc.load_history()


def test_save_permission_error_gives_clear_message(calc, monkeypatch):
    def deny(*a, **k):
        raise PermissionError("denied")

    monkeypatch.setattr("app.calculator.pd.DataFrame.to_csv", deny)
    with pytest.raises(OperationError, match="permission denied"):
        calc.save_history()


def test_decimal_overflow_gives_readable_message(calc):
    calc.set_operation(Modulus())
    with pytest.raises(OperationError, match="too large"):
        calc.perform_operation("1e500", "3")


def test_nan_is_rejected_with_hint():
    with pytest.raises(ValidationError, match="Infinity and NaN are not allowed"):
        InputValidator.validate_number("NaN", CalculatorConfig())


def test_infinity_is_rejected_with_hint():
    with pytest.raises(ValidationError, match="Infinity and NaN are not allowed"):
        InputValidator.validate_number("Infinity", CalculatorConfig())


def test_invalid_number_message_tells_user_what_to_enter():
    with pytest.raises(ValidationError, match="Enter a plain number"):
        InputValidator.validate_number("abc", CalculatorConfig())
