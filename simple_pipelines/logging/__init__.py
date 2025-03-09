from typing import Callable, Any, List, Optional
from enum import Enum, auto
import os

class LogLevel(Enum):
    """Defines log levels."""
    INFO = auto()
    SUCCESS = auto()
    ERROR = auto()
    WARNING = auto()


class Logger:
    def __init__(self, publish_function: Callable[[str], None] = print, levels: Optional[List[LogLevel]] = None):
        """
        Logger class with predefined levels (INFO, SUCCESS, ERROR) and filtering.
        
        :param publish_function: Function to publish logs (default: print)
        :param levels: List of log levels to publish (default: all levels)
        """
        self.publish_function = publish_function
        self.levels = levels or [LogLevel.INFO, LogLevel.SUCCESS, LogLevel.ERROR, LogLevel.WARNING]

    def log(self, level: LogLevel, message: str, **kwargs: Any) -> None:
        """Logs a message only if its level is in the allowed list."""
        if level in self.levels:
            formatted_message = f"[{level.name}] {message} " + " | ".join(f"{k}: {v}" for k, v in kwargs.items())
            self.publish_function(formatted_message)

    def info(self, message: str, **kwargs: Any) -> None:
        """Logs an INFO level message."""
        self.log(LogLevel.INFO, message, **kwargs)

    def success(self, message: str, **kwargs: Any) -> None:
        """Logs a SUCCESS level message."""
        self.log(LogLevel.SUCCESS, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Logs an ERROR level message."""
        self.log(LogLevel.ERROR, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Logs a WARNING level message."""
        self.log(LogLevel.WARNING, message, **kwargs)


class FileLogger(Logger):
    def __init__(self, filename: str, levels: Optional[List[LogLevel]] = None):
        """
        Logger that writes logs to a file.
        
        :param filename: The file to write logs to.
        :param levels: List of log levels to publish (default: all levels).
        """
        self.filename = filename
        os.makedirs(os.path.dirname(filename), exist_ok=True)  # Ensure directory exists
        super().__init__(publish_function=self.write_to_file, levels=levels)

    def write_to_file(self, message: str) -> None:
        """Writes the log message to the specified file."""
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(message + "\n")