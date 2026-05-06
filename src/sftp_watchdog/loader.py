from __future__ import annotations

from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Callable

ProcessFunc = Callable[[Path], None]


def load_processor(import_path: str) -> ProcessFunc:
    if ":" not in import_path:
        raise ValueError("Processor must use 'module:function' or '/path/to/file.py:function'.")

    module_ref, function_name = import_path.rsplit(":", 1)
    if not module_ref or not function_name:
        raise ValueError("Processor must include both module and function names.")

    module_path = Path(module_ref)
    if module_path.suffix == ".py" or module_path.exists():
        module = _load_module_from_file(module_path)
    else:
        module = import_module(module_ref)

    processor = getattr(module, function_name, None)
    if not callable(processor):
        raise TypeError(f"Processor is not callable: {import_path}")

    return processor


def _load_module_from_file(module_path: Path):
    module_path = module_path.expanduser().resolve()
    spec = spec_from_file_location(module_path.stem, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load processor module: {module_path}")

    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
