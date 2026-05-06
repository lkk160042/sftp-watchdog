from pathlib import Path


def process(file_path: Path) -> None:
    """Fallback processor for direct library usage."""
    raise NotImplementedError(
        "Pass a processor callable or run the CLI with --processor module:function."
    )
