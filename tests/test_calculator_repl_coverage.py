import pytest
from unittest.mock import MagicMock

from app.calculator_repl import calculator_repl
from app.exceptions import OperationError, ValidationError


def run_repl(monkeypatch, capsys, inputs):
    it = iter(inputs)

    def fake_input(prompt=""):
        item = next(it)
        if isinstance(item, type) and issubclass(item, BaseException):
            raise item()
        return item

    monkeypatch.setattr("builtins.input", fake_input)
    calculator_repl()
    return capsys.readouterr().out


@pytest.fixture
def calc(monkeypatch):
    fake = MagicMock()
    fake.show_history.return_value = []
    monkeypatch.setattr("app.calculator_repl.Calculator", lambda: fake)
    monkeypatch.setattr("app.calculator_repl.LoggingObserver", lambda: MagicMock())
    monkeypatch.setattr("app.calculator_repl.AutoSaveObserver", lambda c: MagicMock())
    return fake


def test_exit_save_failure(monkeypatch, capsys, calc):
    calc.save_history.side_effect = Exception("disk full")
    out = run_repl(monkeypatch, capsys, ["exit"])
    assert "Warning: Could not save history: disk full" in out
    assert "Goodbye!" in out


def test_history_empty(monkeypatch, capsys, calc):
    out = run_repl(monkeypatch, capsys, ["history", "exit"])
    assert "No calculations in history" in out


def test_history_with_entries(monkeypatch, capsys, calc):
    calc.show_history.return_value = ["Addition(2, 3) = 5", "Subtraction(5, 1) = 4"]
    out = run_repl(monkeypatch, capsys, ["history", "exit"])
    assert "1. Addition(2, 3) = 5" in out
    assert "2. Subtraction(5, 1) = 4" in out


def test_clear(monkeypatch, capsys, calc):
    out = run_repl(monkeypatch, capsys, ["clear", "exit"])
    calc.clear_history.assert_called_once()
    assert "History cleared" in out


@pytest.mark.parametrize("result, expected", [(True, "Operation undone"), (False, "Nothing to undo")])
def test_undo(monkeypatch, capsys, calc, result, expected):
    calc.undo.return_value = result
    assert expected in run_repl(monkeypatch, capsys, ["undo", "exit"])


@pytest.mark.parametrize("result, expected", [(True, "Operation redone"), (False, "Nothing to redo")])
def test_redo(monkeypatch, capsys, calc, result, expected):
    calc.redo.return_value = result
    assert expected in run_repl(monkeypatch, capsys, ["redo", "exit"])


def test_save_success(monkeypatch, capsys, calc):
    assert "History saved successfully" in run_repl(monkeypatch, capsys, ["save", "exit"])


def test_save_error(monkeypatch, capsys, calc):
    calc.save_history.side_effect = Exception("nope")
    assert "Error saving history: nope" in run_repl(monkeypatch, capsys, ["save", "exit"])


def test_load_success(monkeypatch, capsys, calc):
    assert "History loaded successfully" in run_repl(monkeypatch, capsys, ["load", "exit"])


def test_load_error(monkeypatch, capsys, calc):
    calc.load_history.side_effect = Exception("missing")
    assert "Error loading history: missing" in run_repl(monkeypatch, capsys, ["load", "exit"])


def test_cancel_first_number(monkeypatch, capsys, calc):
    out = run_repl(monkeypatch, capsys, ["add", "cancel", "exit"])
    assert "Operation cancelled" in out
    calc.perform_operation.assert_not_called()


def test_cancel_second_number(monkeypatch, capsys, calc):
    out = run_repl(monkeypatch, capsys, ["add", "5", "CANCEL", "exit"])
    assert "Operation cancelled" in out
    calc.perform_operation.assert_not_called()


def test_operation_validation_error(monkeypatch, capsys, calc):
    calc.perform_operation.side_effect = ValidationError("bad input")
    assert "Error: bad input" in run_repl(monkeypatch, capsys, ["add", "x", "1", "exit"])


def test_operation_operation_error(monkeypatch, capsys, calc):
    calc.perform_operation.side_effect = OperationError("div by zero")
    assert "Error: div by zero" in run_repl(monkeypatch, capsys, ["divide", "1", "0", "exit"])


def test_operation_unexpected_error(monkeypatch, capsys, calc):
    calc.perform_operation.side_effect = RuntimeError("weird")
    assert "Unexpected error: weird" in run_repl(monkeypatch, capsys, ["add", "1", "2", "exit"])


def test_unknown_command(monkeypatch, capsys, calc):
    out = run_repl(monkeypatch, capsys, ["bogus", "exit"])
    assert "Unknown command: 'bogus'" in out


def test_keyboard_interrupt(monkeypatch, capsys, calc):
    out = run_repl(monkeypatch, capsys, [KeyboardInterrupt, "exit"])
    assert "Operation cancelled" in out


def test_eof_error(monkeypatch, capsys, calc):
    out = run_repl(monkeypatch, capsys, [EOFError])
    assert "Input terminated. Exiting..." in out


def test_unexpected_error_in_loop(monkeypatch, capsys, calc):
    calc.show_history.side_effect = RuntimeError("boom")
    out = run_repl(monkeypatch, capsys, ["history", "exit"])
    assert "Error: boom" in out


def test_fatal_error_on_init(monkeypatch, capsys):
    def broken():
        raise RuntimeError("init failed")

    monkeypatch.setattr("app.calculator_repl.Calculator", broken)
    with pytest.raises(RuntimeError):
        calculator_repl()
    assert "Fatal error: init failed" in capsys.readouterr().out