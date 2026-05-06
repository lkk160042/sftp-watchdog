from pathlib import Path

from sftp_watchdog.cli import parse_args


def test_parse_args_loads_custom_processor_from_import_path(tmp_path: Path) -> None:
    module_path = tmp_path / "custom_processor.py"
    module_path.write_text(
        "from pathlib import Path\n"
        "\n"
        "def handle_upload(file_path: Path) -> None:\n"
        "    file_path.with_suffix('.ok').write_text(file_path.name, encoding='utf-8')\n",
        encoding="utf-8",
    )

    config, processor = parse_args(
        [
            "--watch-dir",
            str(tmp_path / "incoming"),
            "--processing-dir",
            str(tmp_path / "processing"),
            "--done-dir",
            str(tmp_path / "done"),
            "--failed-dir",
            str(tmp_path / "failed"),
            "--processor",
            f"{module_path}:handle_upload",
        ]
    )
    uploaded_file = config.processing_dir / "upload.csv"
    config.processing_dir.mkdir()
    uploaded_file.write_text("content", encoding="utf-8")

    processor(uploaded_file)

    assert uploaded_file.with_suffix(".ok").read_text(encoding="utf-8") == "upload.csv"
