import logging
from pathlib import Path
from app.calculator_config import CalculatorConfig

class Logger:
    _instance = None

    def __new__(cls, config: CalculatorConfig = None):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize(config or CalculatorConfig())
        return cls._instance

    def _initialize(self, config: CalculatorConfig):
        self.config = config
        log_path = Path(self.config.log_file)
        
        # Ensure the log directory exists
        log_path.parent.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger("CalculatorLogger")
        self.logger.setLevel(logging.INFO)

        # Prevent adding duplicate handlers if initialized multiple times
        if not self.logger.handlers:  # pragma: no cover
            # File Handler using configuration
            file_handler = logging.FileHandler(
                str(log_path), encoding=self.config.default_encoding
            )
            file_handler.setLevel(logging.INFO)

            # Formatter
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s [%(filename)s:%(lineno)d] - %(message)s"
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    @classmethod
    def get_logger(cls):
        if cls._instance is None:  # pragma: no cover
            cls()
        return cls._instance.logger