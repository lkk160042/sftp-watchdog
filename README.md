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
  --failed-dir /data/failed
```

To process only CSV files:

```bash
.venv/bin/sftp-watchdog --extension csv
```

## Processing Hook

Replace the pseudo-code in `src/sftp_watchdog/process.py` with real business
logic:

```python
def process(file_path: Path) -> None:
    data = read_csv(file_path)
    validate(data)
    save_to_db(data)
    make_result(data)
```

## Flow

1. SFTP uploads a file into `incoming`.
2. The watcher handles both create and rename/move events.
3. The processor waits until file size is stable.
4. The file is moved into `processing`.
5. `process()` runs.
6. Successful files move to `done`; failed files move to `failed`.

## Test

```bash
.venv/bin/python -m pytest -q
```

## Project Layout

- `src/sftp_watchdog/config.py`: directory and filtering configuration
- `src/sftp_watchdog/processor.py`: stable-file wait, moves, scan, and error flow
- `src/sftp_watchdog/process.py`: replaceable business processing hook
- `src/sftp_watchdog/watcher.py`: watchdog event adapter
- `src/sftp_watchdog/cli.py`: command-line entry point
- `tests/`: focused behavior tests
