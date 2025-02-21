import importlib
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict

# TODO: make blackbox tests more ergonomic
@dataclass
class BlackboxTestConfig:
    description: str
    input: str
    expected_output: List[str]
    cmdline_args: Optional[List[str]] = None
    custom_error_message: Optional[str] = None
    additional_files_mapping: Optional[Dict[Path, Path]] = None

    @staticmethod
    def load_exercise_mapping_from_python_dir(test_configs_dir: str) -> Dict[str, List["BlackboxTestConfig"]]:
        mappings: Dict[str, List[BlackboxTestConfig]] = {}

        PYTHON_EXTENSION: str = '.py'
        for root, dirs, files in os.walk(test_configs_dir):
            for filename in files:
                if not filename.endswith(PYTHON_EXTENSION):
                    continue

                module_path: str = os.path.join(root, filename).removesuffix(PYTHON_EXTENSION).replace(os.path.sep, ".")
                module = importlib.import_module(module_path)
                if hasattr(module, "CONFIG"):
                    logging.debug("Detected module automatically: %s", module_path)
                    mappings[module_path] = [BlackboxTestConfig(**config) for config in module.CONFIG]

        return mappings
    
    @staticmethod
    def load_config_from_file(test_config_path: Path) -> List["BlackboxTestConfig"]:
        module_path: str = str(test_config_path.parent / test_config_path.stem).replace(os.path.sep, ".")
        module = importlib.import_module(module_path)
        if hasattr(module, "CONFIG"):
            return [BlackboxTestConfig(**config) for config in module.CONFIG]
        
        raise Exception("Module have no config for blackbox tests")
