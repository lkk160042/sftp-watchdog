"""SFTP incoming-folder watchdog."""

from sftp_watchdog.config import WatchdogConfig
from sftp_watchdog.loader import load_processor
from sftp_watchdog.processor import handle_new_file
from sftp_watchdog.watcher import SFTPWatchdog

__all__ = ["SFTPWatchdog", "WatchdogConfig", "handle_new_file", "load_processor"]
