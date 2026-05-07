from pathlib import Path

from sftp_watchdog.config import WatchdogConfig
from sftp_watchdog.watcher import IncomingFileHandler


class Event:
    is_directory = False

    def __init__(self, src_path: Path) -> None:
        self.src_path = str(src_path)


def make_config(tmp_path: Path) -> WatchdogConfig:
    return WatchdogConfig(
        watch_dir=tmp_path / "incoming",
        processing_dir=tmp_path / "processing",
        done_dir=tmp_path / "done",
        failed_dir=tmp_path / "failed",
        stability_checks=1,
        stability_interval=0,
    )


def test_event_handler_continues_after_processor_attribute_error(tmp_path: Path) -> None:
    config = make_config(tmp_path)
    config.ensure_dirs()
    bad_file = config.watch_dir / "bad.csv"
    good_file = config.watch_dir / "good.csv"
    bad_file.write_text("bad", encoding="utf-8")
    good_file.write_text("good", encoding="utf-8")
    calls: list[Path] = []

    def process(file_path: Path) -> None:
        calls.append(file_path)
        if file_path.name == "bad.csv":
            raise AttributeError("missing column")

    handler = IncomingFileHandler(config, process=process)

    handler.on_created(Event(bad_file))
    handler.on_created(Event(good_file))

    assert calls == [config.processing_dir / "bad.csv", config.processing_dir / "good.csv"]
    assert (config.failed_dir / "bad.csv").read_text(encoding="utf-8") == "bad"
    assert (config.done_dir / "good.csv").read_text(encoding="utf-8") == "good"
