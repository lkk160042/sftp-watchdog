from __future__ import annotations

from pathlib import Path
from typing import Callable
import shutil
import time

from sftp_watchdog.config import WatchdogConfig
from sftp_watchdog.process import process as default_process

ProcessFunc = Callable[[Path], None]


def wait_until_file_is_stable(
    file_path: Path,
    *,
    checks: int = 3,
    interval: float = 1.0,
) -> None:
    last_size = -1
    stable_count = 0

    while stable_count < checks:
        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")

        current_size = file_path.stat().st_size
        if current_size == last_size:
            stable_count += 1
        else:
            stable_count = 0
            last_size = current_size

        if stable_count < checks:
            time.sleep(interval)


def unique_path(directory: Path, filename: str) -> Path:
    target = directory / filename
    if not target.exists():
        return target

    index = 1
    while True:
        candidate = directory / f"{target.stem}_{index}{target.suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def should_process(file_path: Path, config: WatchdogConfig) -> bool:
    if not file_path.is_file():
        return False
    if file_path.name.startswith("."):
        return False
    if config.extensions is None:
        return True
    return file_path.suffix.lower() in config.extensions


def handle_new_file(
    file_path: Path,
    config: WatchdogConfig,
    *,
    process: ProcessFunc = default_process,
) -> bool:
    file_path = Path(file_path)
    if not should_process(file_path, config):
        return False

    print(f"[DETECTED] new file: {file_path}")
    processing_path = unique_path(config.processing_dir, file_path.name)

    try:
        wait_until_file_is_stable(
            file_path,
            checks=config.stability_checks,
            interval=config.stability_interval,
        )

        shutil.move(str(file_path), str(processing_path))
        print(f"[MOVE] to processing: {processing_path}")

        process(processing_path)

        done_path = unique_path(config.done_dir, file_path.name)
        shutil.move(str(processing_path), str(done_path))
        print(f"[DONE] moved processed file: {done_path}")
        return True
    except Exception:
        failed_path = unique_path(config.failed_dir, file_path.name)
        if processing_path.exists():
            shutil.move(str(processing_path), str(failed_path))
        elif file_path.exists():
            shutil.move(str(file_path), str(failed_path))
        print(f"[FAILED] moved failed file: {failed_path}")
        raise


def scan_existing_files(
    config: WatchdogConfig,
    *,
    process: ProcessFunc = default_process,
) -> int:
    processed_count = 0
    for file_path in sorted(config.watch_dir.iterdir()):
        if handle_new_file(file_path, config, process=process):
            processed_count += 1
    return processed_count
