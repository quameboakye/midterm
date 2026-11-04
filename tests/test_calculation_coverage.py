from decimal import Decimal

import pytest

from app.calculation import Calculation
from app.exceptions import OperationError


def test_calculation_failure_is_wrapped():
    with pytest.raises(OperationError, match="Calculation failed"):
        Calculation("Power", Decimal("10"), Decimal("1000"))


def test_str():
    calc = Calculation("Addition", Decimal("2"), Decimal("3"))
    assert str(calc) == "Addition(2, 3) = 5"


def test_repr():
    calc = Calculation("Addition", Decimal("2"), Decimal("3"))
    text = repr(calc)
    assert text.startswith("Calculation(operation='Addition'")
    assert "operand1=2" in text
    assert "operand2=3" in text
    assert "result=5" in text


def test_eq_with_non_calculation():
    calc = Calculation("Addition", Decimal("2"), Decimal("3"))
    assert calc.__eq__("not a calculation") is NotImplemented
    assert calc != "not a calculation"
    assert calc != 5