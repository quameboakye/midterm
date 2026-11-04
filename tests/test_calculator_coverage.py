import pytest
from unittest.mock import MagicMock

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError
from app.operations import OperationFactory


@pytest.fixture
def calc(tmp_path, monkeypatch):
    hist_dir = tmp_path / "history"
    hist_file = hist_dir / "calculator_history.csv"

    def force(name, value):
        monkeypatch.setattr(
            CalculatorConfig, name, property(lambda self: value, lambda self, v: None)
        )

    force("history_dir", hist_dir)
    force("history_file", hist_file)
    return Calculator(CalculatorConfig(base_dir=tmp_path))


def do_add(calc, a="2", b="3"):
    calc.set_operation(OperationFactory.create_operation("add"))
    return calc.perform_operation(a, b)


def test_init_survives_load_history_failure(monkeypatch, tmp_path):
    def boom(self):
        raise RuntimeError("cannot load")

    monkeypatch.setattr(Calculator, "load_history", boom)
    c = Calculator(CalculatorConfig(base_dir=tmp_path))
    assert c.history == []


def test_setup_logging_failure(monkeypatch, capsys, tmp_path):
    def boom(*a, **k):
        raise RuntimeError("log setup failed")

    monkeypatch.setattr("app.calculator.logging.basicConfig", boom)
    with pytest.raises(RuntimeError):
        Calculator(CalculatorConfig(base_dir=tmp_path))
    assert "Error setting up logging" in capsys.readouterr().out


def test_history_trimmed_to_max_size(monkeypatch, calc):
    monkeypatch.setattr(calc.config, "max_history_size", 1)
    do_add(calc, "1", "1")
    do_add(calc, "2", "2")
    assert len(calc.history) == 1


def test_perform_operation_wraps_unexpected_error(calc):
    bad_op = MagicMock()
    bad_op.execute.side_effect = RuntimeError("kaboom")
    calc.set_operation(bad_op)
    with pytest.raises(OperationError, match="Operation failed: kaboom"):
        calc.perform_operation("1", "2")


def test_save_empty_history(calc):
    calc.save_history()
    assert calc.config.history_file.exists()


def test_save_history_failure(monkeypatch, calc):
    def boom(*a, **k):
        raise OSError("disk error")

    monkeypatch.setattr("app.calculator.pd.DataFrame.to_csv", boom)
    with pytest.raises(OperationError, match="Failed to save history"):
        calc.save_history()


def test_load_empty_history_file(calc):
    calc.save_history()       
    calc.load_history()
    assert calc.history == []


def test_load_history_failure(monkeypatch, calc):
    calc.save_history()       

    def boom(*a, **k):
        raise ValueError("corrupt csv")

    monkeypatch.setattr("app.calculator.pd.read_csv", boom)
    with pytest.raises(OperationError, match="Failed to load history"):
        calc.load_history()


def test_get_history_dataframe(monkeypatch, calc):
    do_add(calc)
    fake_pd = MagicMock()
    monkeypatch.setattr("app.calculator.pd", fake_pd)
    calc.get_history_dataframe()
    rows = fake_pd.DataFrame.call_args[0][0]
    assert len(rows) == 1
    assert set(rows[0]) == {"operation", "operand1", "operand2", "result", "timestamp"}


def test_show_history(calc):
    do_add(calc)
    entries = calc.show_history()
    assert len(entries) == 1
    assert "(2, 3)" in entries[0]


def test_undo_with_empty_stack(calc):
    assert calc.undo() is False


def test_redo_with_empty_stack(calc):
    assert calc.redo() is False