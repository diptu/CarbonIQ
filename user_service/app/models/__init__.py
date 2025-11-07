import glob
import importlib
import os

# Import all .py files in the current directory except __init__.py
modules = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
for module in modules:
    module_name = os.path.basename(module)[:-3]  # strip .py
    if module_name != "__init__":
        importlib.import_module(f"{__package__}.{module_name}")
