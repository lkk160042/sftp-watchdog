from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class WatchdogConfig:
    watch_dir: Path
    processing_dir: Path
    done_dir: Path
    failed_dir: Path
    extensions: set[str] | None = None
    stability_checks: int = 3
    stability_interval: float = 1.0

    def __post_init__(self) -> None:
        normalized_extensions = None
        if self.extensions is not None:
            normalized_extensions = {
                extension if extension.startswith(".") else f".{extension}"
                for extension in self.extensions
            }
            normalized_extensions = {
                extension.lower() for extension in normalized_extensions
            }

        object.__setattr__(self, "watch_dir", Path(self.watch_dir))
        object.__setattr__(self, "processing_dir", Path(self.processing_dir))
        object.__setattr__(self, "done_dir", Path(self.done_dir))
        object.__setattr__(self, "failed_dir", Path(self.failed_dir))
        object.__setattr__(self, "extensions", normalized_extensions)

    @classmethod
    def default(cls) -> "WatchdogConfig":
        return cls(
            watch_dir=Path("/data/incoming"),
            processing_dir=Path("/data/processing"),
            done_dir=Path("/data/done"),
            failed_dir=Path("/data/failed"),
        )

    def ensure_dirs(self) -> None:
        for directory in self.required_dirs:
            directory.mkdir(parents=True, exist_ok=True)

    @property
    def required_dirs(self) -> list[Path]:
        return [
            self.watch_dir,
            self.processing_dir,
            self.done_dir,
            self.failed_dir,
        ]
