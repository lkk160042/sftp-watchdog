"""SFTP incoming-folder watchdog."""

from sftp_watchdog.config import WatchdogConfig
from sftp_watchdog.processor import handle_new_file

__all__ = ["WatchdogConfig", "handle_new_file"]
