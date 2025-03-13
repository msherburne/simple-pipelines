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
            self.publish_function(formatted_message.strip())

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


class RocketChatLogger(Logger):
    def __init__(self, url: str, userid: str, access_token: str, channel: str, levels: Optional[List[LogLevel]] = None):
        """
        Logger that sends logs to a Rocket.Chat channel.
        
        :param url: The URL of the Rocket.Chat server.
        :param userid: The user ID of the sender.
        :param access_token: The senders personal access token.
        :param channel: The room ID of the channel to send logs to (e.g. #general).
        :param levels: List of log levels to publish (default: all levels).
        """
        self.url = url
        self.userid = userid
        self.access_token = access_token
        self.channel = channel
        super().__init__(publish_function=self.send_to_rocket_chat, levels=levels)


    def send_to_rocket_chat(self, message: str) -> None:
        """Sends the log message to the specified Rocket.Chat channel."""
        import requests

        headers = {
            "X-Auth-Token": self.access_token,
            "X-User-Id": self.userid,
        }

        response = requests.post(
            f"{self.url}/api/v1/chat.postMessage",
            headers=headers,
            data={
                "roomId": self.channel,
                "text": message,
            }
        )

        if response.status_code != 200:
            raise RuntimeError(f"Failed to send log message to Rocket.Chat channel: {response.status_code}")
        
# class ChatSurferLogger(Logger):
#     def __init__(self, url: str, cert_path: str, password: str, room_name: str, domain_id: str, classifcation: str, levels: Optional[List[LogLevel]] = None):
#         """
#         Logger that sends logs to a ChatSurfer room.
        
#         :param url: The URL of the ChatSurfer server.
#         :param cert_path: The path to the NPE certificate.
#         :param password: The password for the certificate.
#         :param room_name: The name of the room to send logs to.
#         :param domain_id: The domain of the chatroom (ie: TS/SCI).
#         :param classifcation: The classification level of the logs.
#         :param levels: List of log levels to publish (default: all levels).
#         """
#         self.url = url
#         self.cert_path = cert_path
#         self.password = password
#         self.room_name = room_name
#         self.domain_id = domain_id
#         self.classifcation = classifcation
#         super().__init__(publish_function=self.send_to_chatsurfer, levels=levels)

#     def send_to_chatsurfer(self, message: str) -> None:
#         """Sends the log message to the specified ChatSurfer room."""
#         try:
#             import yapki
#         except:
#             raise ImportError("yapki is required to send logs to ChatSurfer. Please install it using the whl file.")
        
#         session = yapki.Session(cert=self.cert_path, password=self.password)


