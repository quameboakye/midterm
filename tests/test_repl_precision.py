from decimal import Decimal

from app.calculator_repl import format_display_result


def test_long_fraction_is_rounded_to_precision():
    assert format_display_result(Decimal("0.333333333333333"), 4) == Decimal("0.3333")


def test_short_fraction_is_left_alone():
    assert format_display_result(Decimal("2.5"), 4) == Decimal("2.5")


def test_integer_result_is_unchanged():
    assert str(format_display_result(Decimal("5"), 4)) == "5"


def test_non_decimal_result_is_returned_as_is():
    assert format_display_result("7", 4) == "7"


def test_large_number_with_fraction_does_not_raise():
    big = Decimal("12345678901234567890123.456789")
    assert format_display_result(big, 2) == Decimal("12345678901234567890123.46")
