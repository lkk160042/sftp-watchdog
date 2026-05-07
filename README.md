# sftp-watchdog

Watch an SFTP upload directory on Linux, wait until new files are stable, then run
a processing hook and move files through `processing`, `done`, and `failed`
directories.

## Install

```bash
python -m venv .venv
.venv/bin/python -m pip install -e .
```

## Run

```bash
.venv/bin/sftp-watchdog \
  --watch-dir /data/incoming \
  --processing-dir /data/processing \
  --done-dir /data/done \
  --failed-dir /data/failed \
  --processor /opt/my_app/process_upload.py:handle_upload
```

To process only CSV files:

```bash
.venv/bin/sftp-watchdog \
  --processor /opt/my_app/process_upload.py:handle_upload \
  --extension csv
```

## Custom Processor

Provide your own callable with `--processor`. The callable receives the uploaded
file after it has been moved into the processing directory.

```python
from pathlib import Path


def handle_upload(file_path: Path) -> None:
    print(f"Process uploaded file: {file_path}")
```

The processor value can be either a Python file path or an importable module:

- `/opt/my_app/process_upload.py:handle_upload`
- `my_app.process_upload:handle_upload`

## Library Usage

You can also embed the watcher in your own Python application:

```python
from pathlib import Path

from sftp_watchdog import SFTPWatchdog, WatchdogConfig


def handle_upload(file_path: Path) -> None:
    print(f"Process uploaded file: {file_path}")


config = WatchdogConfig(
    watch_dir=Path("/data/incoming"),
    processing_dir=Path("/data/processing"),
    done_dir=Path("/data/done"),
    failed_dir=Path("/data/failed"),
    extensions={".csv"},
)

watchdog = SFTPWatchdog(config, process=handle_upload)
watchdog.run_forever()
```

For applications that manage their own lifecycle, call `start()`, `stop()`, and
`join()` directly. To process only files already present in `watch_dir`, call
`scan_existing()`.

## Flow

1. SFTP uploads a file into `incoming`.
2. The watcher handles both create and rename/move events.
3. The processor waits until file size is stable.
4. The file is moved into `processing`.
5. The callable passed with `--processor` runs.
6. Successful files move to `done`; failed files move to `failed`.

## Test

```bash
.venv/bin/python -m pytest -q
```

## Project Layout

- `src/sftp_watchdog/config.py`: directory and filtering configuration
- `src/sftp_watchdog/loader.py`: user processor import-path loader
- `src/sftp_watchdog/processor.py`: stable-file wait, moves, scan, and error flow
- `src/sftp_watchdog/process.py`: fallback processor for direct library misuse
- `src/sftp_watchdog/watcher.py`: importable watcher class and watchdog event adapter
- `src/sftp_watchdog/cli.py`: command-line entry point
- `tests/`: focused behavior tests
