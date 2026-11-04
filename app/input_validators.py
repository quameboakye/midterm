from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any
from app.calculator_config import CalculatorConfig
from app.exceptions import ValidationError

NUMBER_HINT = "Enter a plain number such as 12, -3.5 or 1e3."


@dataclass
class InputValidator:

    @staticmethod
    def validate_number(value: Any, config: CalculatorConfig) -> Decimal:
        try:
            if isinstance(value, str):
                value = value.strip()
            number = Decimal(str(value))
            if not number.is_finite():
                raise ValidationError(
                    f"Invalid number format: {value}. "
                    f"Infinity and NaN are not allowed. {NUMBER_HINT}"
                )
            if abs(number) > config.max_input_value:
                raise ValidationError(
                    f"Value exceeds maximum allowed: {config.max_input_value}. "
                    f"Enter a number between -{config.max_input_value} and {config.max_input_value}."
                )
            return number.normalize()
        except InvalidOperation as e:
            raise ValidationError(f"Invalid number format: {value}. {NUMBER_HINT}") from e