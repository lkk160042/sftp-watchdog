from pathlib import Path

import pytest

from sftp_watchdog.config import WatchdogConfig
from sftp_watchdog.processor import handle_new_file, unique_path


def make_config(tmp_path: Path, *, extensions: set[str] | None = None) -> WatchdogConfig:
    return WatchdogConfig(
        watch_dir=tmp_path / "incoming",
        processing_dir=tmp_path / "processing",
        done_dir=tmp_path / "done",
        failed_dir=tmp_path / "failed",
        extensions=extensions,
        stability_checks=1,
        stability_interval=0,
    )


def test_unique_path_adds_numeric_suffix_without_overwriting(tmp_path: Path) -> None:
    (tmp_path / "data.csv").write_text("existing", encoding="utf-8")

    candidate = unique_path(tmp_path, "data.csv")

    assert candidate == tmp_path / "data_1.csv"


def test_handle_new_file_moves_processed_file_to_done(tmp_path: Path) -> None:
    config = make_config(tmp_path)
    config.ensure_dirs()
    incoming_file = config.watch_dir / "data.csv"
    incoming_file.write_text("id,name\n1,Ada\n", encoding="utf-8")
    processed_paths: list[Path] = []

    handle_new_file(incoming_file, config, process=lambda path: processed_paths.append(path))

    done_file = config.done_dir / "data.csv"
    assert done_file.read_text(encoding="utf-8") == "id,name\n1,Ada\n"
    assert processed_paths == [config.processing_dir / "data.csv"]
    assert not incoming_file.exists()
    assert not (config.processing_dir / "data.csv").exists()


def test_handle_new_file_moves_failed_processing_file_to_failed(tmp_path: Path) -> None:
    config = make_config(tmp_path)
    config.ensure_dirs()
    incoming_file = config.watch_dir / "broken.csv"
    incoming_file.write_text("bad", encoding="utf-8")

    def fail(_: Path) -> None:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        handle_new_file(incoming_file, config, process=fail)

    failed_file = config.failed_dir / "broken.csv"
    assert failed_file.read_text(encoding="utf-8") == "bad"
    assert not incoming_file.exists()
    assert not (config.processing_dir / "broken.csv").exists()


def test_handle_new_file_ignores_hidden_files_and_unmatched_extensions(tmp_path: Path) -> None:
    config = make_config(tmp_path, extensions={".csv"})
    config.ensure_dirs()
    hidden_file = config.watch_dir / ".upload.tmp"
    text_file = config.watch_dir / "note.txt"
    hidden_file.write_text("temp", encoding="utf-8")
    text_file.write_text("ignore", encoding="utf-8")
    calls: list[Path] = []

    handle_new_file(hidden_file, config, process=lambda path: calls.append(path))
    handle_new_file(text_file, config, process=lambda path: calls.append(path))

    assert calls == []
    assert hidden_file.exists()
    assert text_file.exists()
