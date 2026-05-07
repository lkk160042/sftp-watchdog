from pathlib import Path

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
