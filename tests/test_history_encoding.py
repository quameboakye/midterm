from decimal import Decimal

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.operations import Addition


def test_history_is_saved_and_loaded_with_configured_encoding(tmp_path, monkeypatch):
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", str(tmp_path / "h.csv"))
    config = CalculatorConfig(base_dir=tmp_path, auto_save=False, default_encoding="utf-16")

    calc = Calculator(config)
    calc.set_operation(Addition())
    calc.perform_operation("2", "3")
    calc.save_history()

    assert (tmp_path / "h.csv").read_bytes()[:2] in (b"\xff\xfe", b"\xfe\xff")

    reloaded = Calculator(config)
    assert [c.result for c in reloaded.history] == [Decimal("5")]
