import logging
from .utils.logger import setup_logging
setup_logging(logging.DEBUG)

from .generator import generate_ros_package

__all__ = [
    'generate_ros_package'
]

__annotations__ = {
    'generate_ros_package': 'function'
}