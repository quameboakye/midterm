import datetime
from unittest.mock import MagicMock

from app.calculator_memento import CalculatorMemento


def test_to_dict():
    calc = MagicMock()
    calc.to_dict.return_value = {"op": "add"}
    ts = datetime.datetime(2026, 10, 5, 12, 0, 0)

    memento = CalculatorMemento(history=[calc], timestamp=ts)

    assert memento.to_dict() == {
        "history": [{"op": "add"}],
        "timestamp": ts.isoformat(),
    }


def test_from_dict(monkeypatch):
    class FakeCalculation:
        @staticmethod
        def from_dict(data):
            return ("calc", data["op"])

    monkeypatch.setattr("app.calculator_memento.Calculation", FakeCalculation)
    ts = datetime.datetime(2026, 10, 5, 12, 0, 0)

    memento = CalculatorMemento.from_dict(
        {"history": [{"op": "add"}], "timestamp": ts.isoformat()}
    )

    assert memento.history == [("calc", "add")]
    assert memento.timestamp == ts
