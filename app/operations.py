from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict
from app.exceptions import ValidationError
from app.logger import Logger

logger = Logger.get_logger()


class Operation(ABC):

    @abstractmethod
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        pass  # pragma: no cover

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        pass

    def __str__(self) -> str:
        return self.__class__.__name__


class Addition(Operation):

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        result = a + b
        logger.info(f"Executed {self.__class__.__name__}: {a} + {b} = {result}")
        return result


class Subtraction(Operation):

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        result = a - b
        logger.info(f"Executed {self.__class__.__name__}: {a} - {b} = {result}")
        return result


class Multiplication(Operation):

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        result = a * b
        logger.info(f"Executed {self.__class__.__name__}: {a} * {b} = {result}")
        return result


class Division(Operation):

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if b == 0:
            logger.error(f"Validation Error in Division: Division by zero attempted with operands {a} and {b}")
            raise ValidationError("Division by zero is not allowed")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        result = a / b
        logger.info(f"Executed {self.__class__.__name__}: {a} / {b} = {result}")
        return result


class Power(Operation):

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if b < 0:
            logger.error(f"Validation Error in Power: Negative exponent attempted with operands {a} and {b}")
            raise ValidationError("Negative exponents not supported")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        result = Decimal(pow(float(a), float(b)))
        logger.info(f"Executed {self.__class__.__name__}: {a} ** {b} = {result}")
        return result


class Root(Operation):

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if a < 0:
            logger.error(f"Validation Error in Root: Negative base for root attempted with operands {a} and {b}")
            raise ValidationError("Cannot calculate root of negative number")
        if b == 0:
            logger.error(f"Validation Error in Root: Zero root attempted with operands {a} and {b}")
            raise ValidationError("Zero root is undefined")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        result = Decimal(pow(float(a), 1 / float(b)))
        logger.info(f"Executed {self.__class__.__name__}: {b} root of {a} = {result}")
        return result


class Modulus(Operation):
    """Remainder of a divided by b."""

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if b == 0:
            logger.error(f"Validation Error in Modulus: Modulus by zero attempted with operands {a} and {b}")
            raise ValidationError("Modulus by zero is not allowed")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        result = a % b
        logger.info(f"Executed {self.__class__.__name__}: {a} % {b} = {result}")
        return result


class IntegerDivision(Operation):
    """Quotient of a divided by b, with the fractional part discarded."""

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if b == 0:
            logger.error(f"Validation Error in IntegerDivision: Integer division by zero attempted with operands {a} and {b}")
            raise ValidationError("Integer division by zero is not allowed")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        result = a // b
        logger.info(f"Executed {self.__class__.__name__}: {a} // {b} = {result}")
        return result


class Percentage(Operation):
    """Percentage(a, b) = (a / b) * 100."""

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if b == 0:
            logger.error(f"Validation Error in Percentage: Percentage with a zero base attempted with operands {a} and {b}")
            raise ValidationError("Percentage with a zero base is not allowed")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        result = (a / b) * 100
        logger.info(f"Executed {self.__class__.__name__}: ({a} / {b}) * 100 = {result}")
        return result


class AbsoluteDifference(Operation):
    """|a - b|."""

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        result = abs(a - b)
        logger.info(f"Executed {self.__class__.__name__}: |{a} - {b}| = {result}")
        return result


class OperationFactory:

    _operations: Dict[str, type] = {
        'add': Addition,
        'subtract': Subtraction,
        'multiply': Multiplication,
        'divide': Division,
        'power': Power,
        'root': Root,
        'modulus': Modulus,
        'int_divide': IntegerDivision,
        'percentage': Percentage,
        'abs_diff': AbsoluteDifference,
    }

    @classmethod
    def register_operation(cls, name: str, operation_class: type) -> None:
        if not issubclass(operation_class, Operation):
            logger.warning(f"Failed to register operation '{name}': class does not inherit from Operation")
            raise TypeError("Operation class must inherit from Operation")
        cls._operations[name.lower()] = operation_class
        logger.info(f"Successfully registered new operation type: '{name.lower()}'")

    @classmethod
    def create_operation(cls, operation_type: str) -> Operation:
        operation_class = cls._operations.get(operation_type.lower())
        if not operation_class:
            logger.error(f"Unknown operation requested: '{operation_type}'")
            raise ValueError(f"Unknown operation: {operation_type}")
        logger.info(f"Created operation instance for: '{operation_type.lower()}'")
        return operation_class()
