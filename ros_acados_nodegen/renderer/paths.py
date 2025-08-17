from importlib.resources import files
from pathlib import Path

try:
    PACKAGE_DIR = files("ros_acados_nodegen")
except ModuleNotFoundError:
    PACKAGE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES_DIR = PACKAGE_DIR / "templates"

DEFAULT_CONFIG_PATH = PACKAGE_DIR / "config" / "default_config.yaml"