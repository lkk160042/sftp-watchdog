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


class SFTPWatchdog:
    def __init__(self, config: WatchdogConfig, *, process: ProcessFunc = default_process) -> None:
        self.config = config
        self.process = process
        self._observer: Observer | None = None

    def scan_existing(self) -> int:
        self.config.ensure_dirs()
        return scan_existing_files(self.config, process=self.process)

    def start(self, *, scan_existing: bool = True) -> None:
        self.config.ensure_dirs()
        if scan_existing:
            self.scan_existing()

        observer = Observer()
        observer.schedule(
            IncomingFileHandler(self.config, process=self.process),
            str(self.config.watch_dir),
            recursive=False,
        )
        observer.start()
        self._observer = observer

    def stop(self) -> None:
        if self._observer is not None:
            self._observer.stop()

    def join(self) -> None:
        if self._observer is not None:
            self._observer.join()

    def run_forever(self) -> None:
        print(f"[START] watching: {self.config.watch_dir}")
        self.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("[STOP] watcher interrupted")
            self.stop()

        self.join()


def run(config: WatchdogConfig, *, process: ProcessFunc = default_process) -> None:
    SFTPWatchdog(config, process=process).run_forever()
