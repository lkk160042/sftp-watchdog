from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from sftp_watchdog.config import WatchdogConfig
from sftp_watchdog.loader import ProcessFunc, load_processor
from sftp_watchdog.watcher import run


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Watch an SFTP incoming directory and process new files.")
    parser.add_argument("--watch-dir", type=Path, default=Path("/data/incoming"))
    parser.add_argument("--processing-dir", type=Path, default=Path("/data/processing"))
    parser.add_argument("--done-dir", type=Path, default=Path("/data/done"))
    parser.add_argument("--failed-dir", type=Path, default=Path("/data/failed"))
    parser.add_argument(
        "--extension",
        action="append",
        dest="extensions",
        help="Only process this extension. May be passed multiple times, e.g. --extension csv.",
    )
    parser.add_argument("--stability-checks", type=int, default=3)
    parser.add_argument("--stability-interval", type=float, default=1.0)
    parser.add_argument(
        "--processor",
        required=True,
        help="Callable to run for each uploaded file: module:function or /path/to/file.py:function.",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> tuple[WatchdogConfig, ProcessFunc]:
    args = build_parser().parse_args(argv)
    config = WatchdogConfig(
        watch_dir=args.watch_dir,
        processing_dir=args.processing_dir,
        done_dir=args.done_dir,
        failed_dir=args.failed_dir,
        extensions=set(args.extensions) if args.extensions else None,
        stability_checks=args.stability_checks,
        stability_interval=args.stability_interval,
    )
    return config, load_processor(args.processor)


def main() -> None:
    config, processor = parse_args()
    run(config, process=processor)


if __name__ == "__main__":
    main()
