from unittest.mock import MagicMock, patch

from app.calculator_repl import calculator_repl


def test_repl_prints_result_that_is_not_a_decimal(capsys):
    fake_calc = MagicMock()
    fake_calc.perform_operation.return_value = "7"
    inputs = iter(["add", "3", "4", "exit"])

    with patch("app.calculator_repl.Calculator", return_value=fake_calc), \
         patch("builtins.input", lambda _="": next(inputs)):
        calculator_repl()

    assert "Result: 7" in capsys.readouterr().out
