import jinja2
import stat
import shutil
import logging
from typing import Any
from pathlib import Path

from .paths import TEMPLATES_DIR
from ..context import RosPackageContext
from ..utils.jinja_utils import *

logger = logging.getLogger(__name__)

INCLUDE_DIR = 'include'
SRC_DIR = 'src'
SCRIPTS_DIR = 'scripts'
CONFIG_DIR = 'config'
LAUNCH_DIR = 'launch'

JINJA_SUFFIX = '.j2'
NODE_H_TEMP_NAME = 'node.h' + JINJA_SUFFIX
CONFIG_HPP_TEMP_NAME = 'config.hpp' + JINJA_SUFFIX
MARKER_PUBLISHER_HPP_TEMP_NAME = 'marker_publisher.hpp' + JINJA_SUFFIX
UTILS_HPP_TEMP_NAME = 'utils.hpp' + JINJA_SUFFIX
NODE_CPP_TEMP_NAME = 'node.cpp' + JINJA_SUFFIX
CMAKELISTS_TEMP_NAME = 'CMakeLists.txt' + JINJA_SUFFIX
PACKAGE_XML_TEMP_NAME = 'package.xml' + JINJA_SUFFIX
GENERATE_SOLVER_TEMP_NAME = 'generate_solver.sh' + JINJA_SUFFIX
README_MD_TEMP_NAME = 'README.md' + JINJA_SUFFIX


class RosPackageGenerator:
    """Generate the structure and files for a ROS-Package."""
    def __init__(self, context: RosPackageContext, install_path: Path):
        """
        Initialises the generator with the context and package path.
        
        Parameters
        ----------
        context: RosPackageContext
            The context containing package and node information.
        package_path: Path
            The path where the package will be created.
        """
        self.context = context
        self.package_path = Path(install_path) / context.package.name

        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self._setup_jinja_filters()

    def _setup_jinja_filters(self):
        self.jinja_env.filters['basename'] = jinja_basename_filter
        self.jinja_env.filters['snake'] = snake_case
        self.jinja_env.filters['cpp_type'] = cpp_type
        self.jinja_env.filters['include_path'] = include_path
        self.jinja_env.filters['pkg_from_type'] = extract_pkg_from_type
        self.jinja_env.filters['basename'] = jinja_basename_filter
        self.jinja_env.filters['diagonal'] = get_diagonal

        self.jinja_env.globals['snake'] = snake_case
        self.jinja_env.globals['cpp_type'] = cpp_type
        self.jinja_env.globals['include_path'] = include_path
        self.jinja_env.globals['pkg_from_type'] = extract_pkg_from_type
        self.jinja_env.globals['basename'] = jinja_basename_filter
        self.jinja_env.globals['diagonal'] = get_diagonal

    def copy_scripts_folder(self):
        """Kopiert den gesamten Scripts-Ordner in das Zielpaket."""
        source_scripts_dir = Path(self.context.script_path).parent
        if not source_scripts_dir.exists() and not source_scripts_dir.is_absolute():
            source_scripts_dir = (Path.cwd() / source_scripts_dir).resolve()

        dest_scripts_dir = self.package_path / SCRIPTS_DIR

        ignore_patterns = ['__pycache__']
        if source_scripts_dir.exists():
            logger.debug(f"Copying scripts from '{source_scripts_dir}' to '{dest_scripts_dir}'...")
            shutil.copytree(
                source_scripts_dir, 
                dest_scripts_dir, 
                ignore=shutil.ignore_patterns(*ignore_patterns),
                dirs_exist_ok=True
            )
        else:
            logger.warning(f"Source scripts directory not found at '{source_scripts_dir}'")

    def _create_file_from_template(
            self, template_name: str, 
            relative_dest_path: Path, 
            executable: bool = False
    ):
        """Helperfunction to generate a file based on templates and context."""
        template = self.jinja_env.get_template(template_name)
        rendered_content = template.render(**self.context.model_dump())
        file_path = self.package_path / relative_dest_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.write(rendered_content)
            
        if executable:
            file_path.chmod(file_path.stat().st_mode | stat.S_IEXEC)

    def create_node_h(self):
        dest = Path(INCLUDE_DIR) / self.package_path.name / f'{self.context.ros.node_name}.h'
        self._create_file_from_template(NODE_H_TEMP_NAME, dest)
        
    def create_config_hpp(self):
        dest = Path(INCLUDE_DIR) / self.package_path.name / CONFIG_HPP_TEMP_NAME.strip(JINJA_SUFFIX)
        self._create_file_from_template(CONFIG_HPP_TEMP_NAME, dest)

    def create_marker_publisher_hpp(self):
        dest = Path(INCLUDE_DIR) / self.package_path.name / MARKER_PUBLISHER_HPP_TEMP_NAME.strip(JINJA_SUFFIX)
        self._create_file_from_template(MARKER_PUBLISHER_HPP_TEMP_NAME, dest)
        
    def create_utils_hpp(self):
        dest = Path(INCLUDE_DIR) / self.package_path.name / UTILS_HPP_TEMP_NAME.strip(JINJA_SUFFIX)
        self._create_file_from_template(UTILS_HPP_TEMP_NAME, dest)

    def create_node_cpp(self):
        dest = Path(SRC_DIR) / f'{self.context.ros.node_name}.cpp'
        self._create_file_from_template(NODE_CPP_TEMP_NAME, dest)

    def create_cmakelists_txt(self):
        dest = Path(CMAKELISTS_TEMP_NAME.strip(JINJA_SUFFIX))
        self._create_file_from_template(CMAKELISTS_TEMP_NAME, dest)

    def create_package_xml(self):
        dest = Path(PACKAGE_XML_TEMP_NAME.strip(JINJA_SUFFIX))
        self._create_file_from_template(PACKAGE_XML_TEMP_NAME, dest)

    def create_generator_sh(self):
        dest = Path(SCRIPTS_DIR) / GENERATE_SOLVER_TEMP_NAME.strip(JINJA_SUFFIX)
        self._create_file_from_template(GENERATE_SOLVER_TEMP_NAME, dest, executable=True)

    def create_readme_md(self):
        dest = Path(README_MD_TEMP_NAME.strip(JINJA_SUFFIX))
        self._create_file_from_template(README_MD_TEMP_NAME, dest)

    def generate_all(self):
        logger.info(f"Generating ROS package '{self.package_path.name}'...")
        self.copy_scripts_folder()
        self.create_node_h()
        self.create_config_hpp()
        self.create_marker_publisher_hpp()
        self.create_utils_hpp()
        self.create_node_cpp()
        self.create_cmakelists_txt()
        self.create_package_xml()
        self.create_generator_sh()
        self.create_readme_md()