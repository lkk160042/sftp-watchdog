from __future__ import annotations

from pathlib import Path
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from sftp_watchdog.config import WatchdogConfig
from sftp_watchdog.loader import ProcessFunc
from sftp_watchdog.processor import handle_new_file, scan_existing_files
from sftp_watchdog.process import process as default_process


class IncomingFileHandler(FileSystemEventHandler):
    def __init__(self, config: WatchdogConfig, process: ProcessFunc = default_process) -> None:
        self.config = config
        self.process = process

    def on_created(self, event) -> None:  # noqa: ANN001
        if event.is_directory:
            return
        handle_new_file(Path(event.src_path), self.config, process=self.process)

    def on_moved(self, event) -> None:  # noqa: ANN001
        if event.is_directory:
            return
        handle_new_file(Path(event.dest_path), self.config, process=self.process)


def run(config: WatchdogConfig, *, process: ProcessFunc = default_process) -> None:
    config.ensure_dirs()
    print(f"[START] watching: {config.watch_dir}")

    scan_existing_files(config, process=process)

    observer = Observer()
    observer.schedule(
        IncomingFileHandler(config, process=process),
        str(config.watch_dir),
        recursive=False,
    )
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[STOP] watcher interrupted")
        observer.stop()

    observer.join()
