import logging
import sys

class PackageNameFilter(logging.Filter):
    """
    Fügt packagename/filename in Uppercase hinzu (falls noch nicht gesetzt).
    """
    def filter(self, record):
        if not getattr(record, 'packagename', None):
            record.packagename = record.name.split('.')[0].upper()
        if not getattr(record, 'filename', None):
            filename = getattr(record, 'filename', '')
            record.filename = filename.split('/')[-1].split('.')[0].upper() if filename else ''
        return True

class SafeFormatter(logging.Formatter):
    """
    Formatter, der fehlende erwartete Felder vor dem Formatieren setzt,
    damit fehlende Attribute nicht zu Exceptions führen.
    """
    def format(self, record):
        pkg_name = getattr(record, 'packagename', '')
        if not pkg_name:
            record.packagename = record.name.split('.')[0].upper()

        if record.filename:
            record.filename = record.filename.split('/')[-1].split('.')[0].upper() if record.filename else ''
        return super().format(record)

def setup_logging(level=logging.INFO, package_name='ros_acados_nodegen'):
    """
    Robustes, idempotentes Setup: hängt einen StreamHandler am root-logger
    mit SafeFormatter und PackageNameFilter. Dadurch treten keine Exceptions
    auf, auch wenn schon früh Logs produziert werden.
    """
    pkg_logger = logging.getLogger(package_name)
    pkg_logger.setLevel(level)

    # remove previous handlers for idempotence
    if pkg_logger.hasHandlers():
        pkg_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    log_format = "[%(packagename)s] [%(filename)s] [%(levelname)s] %(message)s"
    formatter = SafeFormatter(log_format)
    handler.setFormatter(formatter)
    handler.addFilter(PackageNameFilter())

    pkg_logger.addHandler(handler)
    pkg_logger.propagate = False
    pkg_logger.info("Logging initialized")