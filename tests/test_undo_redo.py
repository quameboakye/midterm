from decimal import Decimal
from unittest.mock import patch

import pytest

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.operations import Addition


@pytest.fixture
def calc(tmp_path):
    calculator = Calculator(CalculatorConfig(base_dir=tmp_path))
    calculator.set_operation(Addition())
    return calculator


def add(calc, a, b):
    return calc.perform_operation(str(a), str(b))


def test_undo_restores_previous_state(calc):
    add(calc, 1, 2)
    add(calc, 3, 4)
    assert len(calc.history) == 2

    assert calc.undo() is True
    assert len(calc.history) == 1
    assert calc.history[0].result == Decimal("3")
    assert len(calc.undo_stack) == 1
    assert len(calc.redo_stack) == 1


def test_redo_restores_undone_calculation(calc):
    add(calc, 1, 2)
    add(calc, 3, 4)
    calc.undo()

    assert calc.redo() is True
    assert len(calc.history) == 2
    assert calc.history[1].result == Decimal("7")
    assert len(calc.undo_stack) == 2
    assert calc.redo_stack == []


def test_new_calculation_clears_redo_stack(calc):
    add(calc, 1, 2)
    calc.undo()
    assert len(calc.redo_stack) == 1

    add(calc, 5, 6)
    assert calc.redo_stack == []
    assert calc.redo() is False
    assert [c.result for c in calc.history] == [Decimal("11")]


def test_undo_all_the_way_back(calc):
    add(calc, 1, 1)
    add(calc, 2, 2)
    add(calc, 3, 3)

    assert calc.undo() and calc.undo() and calc.undo()
    assert calc.history == []
    assert calc.undo() is False

    assert calc.redo() and calc.redo() and calc.redo()
    assert [c.result for c in calc.history] == [Decimal("2"), Decimal("4"), Decimal("6")]
    assert calc.redo() is False


def test_undo_snapshot_is_independent_of_later_changes(calc):
    add(calc, 1, 2)
    calc.undo()
    calc.redo()
    add(calc, 3, 4)
    calc.undo()
    assert [c.result for c in calc.history] == [Decimal("3")]


def test_undo_and_redo_autosave_when_enabled(calc):
    add(calc, 1, 2)
    calc.config.auto_save = True
    with patch.object(calc, "save_history") as save:
        calc.undo()
        calc.redo()
    assert save.call_count == 2


def test_undo_does_not_save_when_autosave_disabled(calc):
    add(calc, 1, 2)
    calc.config.auto_save = False
    with patch.object(calc, "save_history") as save:
        calc.undo()
    save.assert_not_called()


def test_autosave_failure_does_not_break_undo(calc):
    add(calc, 1, 2)
    calc.config.auto_save = True
    with patch.object(calc, "save_history", side_effect=Exception("disk full")):
        assert calc.undo() is True
    assert calc.history == []
