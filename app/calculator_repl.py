from decimal import Decimal, localcontext
import logging
from colorama import init, Fore, Style

from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.operations import OperationFactory

# Initialize colorama for cross-platform support with auto-reset
init(autoreset=True)


def format_display_result(result, precision: int):
    """Normalize a Decimal result and round it to at most `precision` decimal places."""
    if isinstance(result, Decimal):
        result = result.normalize()
        if result.as_tuple().exponent < -precision:
            with localcontext() as ctx:
                ctx.prec = len(result.as_tuple().digits) + precision + 1
                result = result.quantize(Decimal(1).scaleb(-precision)).normalize()
    return result


def calculator_repl():
    try:
        calc = Calculator()

        calc.add_observer(LoggingObserver())
        calc.add_observer(AutoSaveObserver(calc))

        print(Fore.CYAN + Style.BRIGHT + "Calculator started. Type 'help' for commands.")

        while True:
            try:
                command = input(Fore.YELLOW + "\nEnter command: " + Style.RESET_ALL).lower().strip()

                if command == 'help':
                    print(Fore.CYAN + "\nAvailable commands:")
                    print(Fore.CYAN + "   add, subtract, multiply, divide, power, root - Perform calculations")
                    print(Fore.CYAN + "   modulus, int_divide, percentage (or percent), abs_diff - Perform calculations")
                    print(Fore.CYAN + "   history - Show calculation history")
                    print(Fore.CYAN + "   clear - Clear calculation history")
                    print(Fore.CYAN + "   undo - Undo the last calculation")
                    print(Fore.CYAN + "   redo - Redo the last undone calculation")
                    print(Fore.CYAN + "   save - Save calculation history to file")
                    print(Fore.CYAN + "   load - Load calculation history from file")
                    print(Fore.CYAN + "   exit - Exit the calculator")
                    continue

                if command == 'exit':
                    try:
                        calc.save_history()
                        print(Fore.GREEN + "History saved successfully.")
                    except Exception as e:
                        print(Fore.YELLOW + f"Warning: Could not save history: {e}")
                    print(Fore.CYAN + "Goodbye!")
                    break

                if command == 'history':
                    history = calc.show_history()
                    if not history:
                        print(Fore.YELLOW + "No calculations in history")
                    else:
                        print(Fore.CYAN + "\nCalculation History:")
                        for i, entry in enumerate(history, 1):
                            print(Fore.CYAN + f"{i}. {entry}")
                    continue

                if command == 'clear':
                    calc.clear_history()
                    print(Fore.GREEN + "History cleared")
                    continue

                if command == 'undo':
                    if calc.undo():
                        print(Fore.GREEN + "Operation undone")
                    else:
                        print(Fore.YELLOW + "Nothing to undo")
                    continue

                if command == 'redo':
                    if calc.redo():
                        print(Fore.GREEN + "Operation redone")
                    else:
                        print(Fore.YELLOW + "Nothing to redo")
                    continue

                if command == 'save':
                    try:
                        calc.save_history()
                        print(Fore.GREEN + "History saved successfully")
                    except Exception as e:
                        print(Fore.RED + f"Error saving history: {e}")
                    continue

                if command == 'load':
                    try:
                        calc.load_history()
                        print(Fore.GREEN + "History loaded successfully")
                    except Exception as e:
                        print(Fore.RED + f"Error loading history: {e}")
                    continue

                if command in ['add', 'subtract', 'multiply', 'divide', 'power', 'root',
                               'modulus', 'int_divide', 'percentage', 'percent', 'abs_diff']:
                    try:
                        print(Fore.BLUE + "\nEnter numbers (or 'cancel' to abort):")
                        a = input(Fore.BLUE + "First number: " + Style.RESET_ALL)
                        if a.lower() == 'cancel':
                            print(Fore.YELLOW + "Operation cancelled")
                            continue
                        b = input(Fore.BLUE + "Second number: " + Style.RESET_ALL)
                        if b.lower() == 'cancel':
                            print(Fore.YELLOW + "Operation cancelled")
                            continue

                        # Map 'percent' to 'percentage' for the operation factory
                        op_name = 'percentage' if command == 'percent' else command

                        operation = OperationFactory.create_operation(op_name)
                        calc.set_operation(operation)

                        result = calc.perform_operation(a, b)

                        result = format_display_result(result, calc.config.precision)

                        print(Fore.GREEN + Style.BRIGHT + f"\nResult: {result}")
                    except (ValidationError, OperationError) as e:
                        print(Fore.RED + f"Error: {e}")
                    except Exception as e:
                        print(Fore.RED + f"Unexpected error: {e}")
                    continue

                print(Fore.RED + f"Unknown command: '{command}'. Type 'help' for available commands.")

            except KeyboardInterrupt:
                print(Fore.YELLOW + "\nOperation cancelled")
                continue
            except EOFError:
                print(Fore.CYAN + "\nInput terminated. Exiting...")
                break
            except Exception as e:
                print(Fore.RED + f"Error: {e}")
                continue

    except Exception as e:
        print(Fore.RED + f"Fatal error: {e}")
        logging.error(f"Fatal error in calculator REPL: {e}")
        raise
