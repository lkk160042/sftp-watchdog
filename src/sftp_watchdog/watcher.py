from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, time as clock_time
from pathlib import Path
import time
import traceback

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from sftp_watchdog.config import WatchdogConfig
from sftp_watchdog.loader import ProcessFunc
from sftp_watchdog.processor import handle_new_file, scan_existing_files
from sftp_watchdog.process import process as default_process

ShutdownTime = clock_time | str
NowFunc = Callable[[], datetime]
SleepFunc = Callable[[float], None]


class IncomingFileHandler(FileSystemEventHandler):
    def __init__(self, config: WatchdogConfig, process: ProcessFunc = default_process) -> None:
        self.config = config
        self.process = process

    def on_created(self, event) -> None:  # noqa: ANN001
        if event.is_directory:
            return
        self._handle_event_path(Path(event.src_path))

    def on_moved(self, event) -> None:  # noqa: ANN001
        if event.is_directory:
            return
        self._handle_event_path(Path(event.dest_path))

    def _handle_event_path(self, file_path: Path) -> None:
        try:
            handle_new_file(file_path, self.config, process=self.process)
        except Exception:
            print(f"[ERROR] failed to process event file: {file_path}")
            print(traceback.format_exc())


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

    def run_daily(
        self,
        *,
        shutdown_start: ShutdownTime | None = None,
        shutdown_end: ShutdownTime | None = None,
        poll_interval: float = 1.0,
        now_func: NowFunc = datetime.now,
        sleep_func: SleepFunc = time.sleep,
    ) -> None:
        if shutdown_start is None and shutdown_end is None:
            self.run_forever()
            return
        if shutdown_start is None or shutdown_end is None:
            raise ValueError("Both shutdown_start and shutdown_end are required.")

        start_time = parse_shutdown_time(shutdown_start)
        end_time = parse_shutdown_time(shutdown_end)

        print(
            f"[START] watching until shutdown window: "
            f"{start_time.strftime('%H:%M')}~{end_time.strftime('%H:%M')}"
        )
        self.start()

        try:
            while not is_in_shutdown_window(now_func().time(), start_time, end_time):
                sleep_func(poll_interval)
        except KeyboardInterrupt:
            print("[STOP] watcher interrupted")
        finally:
            print("[STOP] shutdown window reached")
            self.stop()
            self.join()


def run(config: WatchdogConfig, *, process: ProcessFunc = default_process) -> None:
    SFTPWatchdog(config, process=process).run_forever()


def parse_shutdown_time(value: ShutdownTime) -> clock_time:
    if isinstance(value, clock_time):
        return value

    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError as exc:
        raise ValueError("Shutdown time must use HH:MM format.") from exc


def is_in_shutdown_window(
    current_time: clock_time,
    shutdown_start: clock_time,
    shutdown_end: clock_time,
) -> bool:
    if shutdown_start <= shutdown_end:
        return shutdown_start <= current_time < shutdown_end
    return current_time >= shutdown_start or current_time < shutdown_end
