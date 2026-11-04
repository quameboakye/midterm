from decimal import Decimal

import pytest
from dotenv import load_dotenv

from app.calculator_config import CalculatorConfig
from app.exceptions import ConfigurationError


def test_non_integer_max_history_size_env(monkeypatch):
    monkeypatch.setenv("CALCULATOR_MAX_HISTORY_SIZE", "abc")
    with pytest.raises(ConfigurationError, match="CALCULATOR_MAX_HISTORY_SIZE must be an integer"):
        CalculatorConfig()


def test_non_integer_precision_env(monkeypatch):
    monkeypatch.setenv("CALCULATOR_PRECISION", "ten")
    with pytest.raises(ConfigurationError, match="CALCULATOR_PRECISION must be an integer"):
        CalculatorConfig()


def test_non_numeric_max_input_value_env(monkeypatch):
    monkeypatch.setenv("CALCULATOR_MAX_INPUT_VALUE", "abc")
    with pytest.raises(ConfigurationError, match="CALCULATOR_MAX_INPUT_VALUE must be a number"):
        CalculatorConfig()


def test_non_finite_max_input_value_env(monkeypatch):
    monkeypatch.setenv("CALCULATOR_MAX_INPUT_VALUE", "NaN")
    with pytest.raises(ConfigurationError, match="must be a finite number"):
        CalculatorConfig()


def test_zero_max_history_size_is_rejected():
    with pytest.raises(ConfigurationError, match="max_history_size must be positive"):
        CalculatorConfig(max_history_size=0).validate()


def test_zero_precision_is_rejected():
    with pytest.raises(ConfigurationError, match="precision must be positive"):
        CalculatorConfig(precision=0).validate()


def test_zero_max_input_value_is_rejected():
    with pytest.raises(ConfigurationError, match="max_input_value must be positive"):
        CalculatorConfig(max_input_value=Decimal("0")).validate()


def test_invalid_encoding_is_rejected():
    with pytest.raises(ConfigurationError, match="default_encoding"):
        CalculatorConfig(default_encoding="not-a-codec").validate()


def test_values_load_from_dotenv_file(tmp_path, monkeypatch):
    monkeypatch.setenv("CALCULATOR_PRECISION", "1")
    monkeypatch.delenv("CALCULATOR_PRECISION")
    env_file = tmp_path / ".env"
    env_file.write_text("CALCULATOR_PRECISION=7\n")

    load_dotenv(env_file)

    assert CalculatorConfig().precision == 7
