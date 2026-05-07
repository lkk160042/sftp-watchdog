from pathlib import Path
from datetime import datetime

from sftp_watchdog import SFTPWatchdog, WatchdogConfig


def test_importable_watchdog_scans_existing_files_with_custom_processor(tmp_path: Path) -> None:
    config = WatchdogConfig(
        watch_dir=tmp_path / "incoming",
        processing_dir=tmp_path / "processing",
        done_dir=tmp_path / "done",
        failed_dir=tmp_path / "failed",
        stability_checks=1,
        stability_interval=0,
    )
    config.ensure_dirs()
    incoming_file = config.watch_dir / "upload.csv"
    incoming_file.write_text("id,name\n1,Ada\n", encoding="utf-8")
    processed_paths: list[Path] = []

    watchdog = SFTPWatchdog(config, process=lambda path: processed_paths.append(path))

    assert watchdog.scan_existing() == 1
    assert processed_paths == [config.processing_dir / "upload.csv"]
    assert (config.done_dir / "upload.csv").read_text(encoding="utf-8") == "id,name\n1,Ada\n"


def test_run_daily_stops_when_shutdown_window_is_reached(tmp_path: Path) -> None:
    config = WatchdogConfig(
        watch_dir=tmp_path / "incoming",
        processing_dir=tmp_path / "processing",
        done_dir=tmp_path / "done",
        failed_dir=tmp_path / "failed",
        stability_checks=1,
        stability_interval=0,
    )
    watchdog = SFTPWatchdog(config, process=lambda _: None)
    calls: list[str] = []
    times = iter(
        [
            datetime(2026, 5, 7, 4, 59),
            datetime(2026, 5, 7, 5, 0),
        ]
    )

    watchdog.start = lambda: calls.append("start")  # type: ignore[method-assign]
    watchdog.stop = lambda: calls.append("stop")  # type: ignore[method-assign]
    watchdog.join = lambda: calls.append("join")  # type: ignore[method-assign]

    watchdog.run_daily(
        shutdown_start="05:00",
        shutdown_end="05:30",
        poll_interval=0,
        now_func=lambda: next(times),
        sleep_func=lambda _: None,
    )

    assert calls == ["start", "stop", "join"]


def test_run_daily_without_shutdown_window_delegates_to_run_forever(tmp_path: Path) -> None:
    config = WatchdogConfig(
        watch_dir=tmp_path / "incoming",
        processing_dir=tmp_path / "processing",
        done_dir=tmp_path / "done",
        failed_dir=tmp_path / "failed",
    )
    watchdog = SFTPWatchdog(config, process=lambda _: None)
    calls: list[str] = []
    watchdog.run_forever = lambda: calls.append("run_forever")  # type: ignore[method-assign]

    watchdog.run_daily()

    assert calls == ["run_forever"]
