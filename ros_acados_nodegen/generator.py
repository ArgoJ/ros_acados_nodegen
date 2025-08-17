from pathlib import Path

from .renderer.package_generator import *
from .context import RosPackageContext, AcadosContext
from .utils.context_utils import parse_dot_key_value, parse_args_values, deep_update

from pprint import pprint


def generate_ros_package(solver_path, install_path=None, config_path=None, **kwargs):
    """
    Generiert ein ROS-Package mit einer mehrschichtigen Konfiguration.
    """
    
    if config_path:
        context = RosPackageContext.from_yaml(config_path)
    else:
        context = RosPackageContext()
    context.acados = AcadosContext.from_solver_json(solver_path)
    context.script_path = Path(__file__).parent.parent / "examples" / "scripts" / "safety_filter_mpc.py"

    if kwargs:
        kwargs = parse_dot_key_value(kwargs)
        data = context.model_dump(mode="python")
        deep_update(data, kwargs)
        context = RosPackageContext.model_validate(data)

    if install_path is None:
        install_path = Path.cwd()

    # pprint(context.model_dump(mode="python"))
    generator = RosPackageGenerator(context, install_path)
    generator.generate_all()
    

if __name__ == "__main__":
    import argparse
    from pathlib import Path
    
    parser = argparse.ArgumentParser(description="Generate a ROS package from an Acados solver.")
    parser.add_argument("solver_json_path", type=Path, help="Path to the Acados solver JSON file.")
    parser.add_argument("config_path", type=Path, help="Path to the ROS package configuration YAML file.")
    parser.add_argument("--set", action="append", default=[], help="Override context values, e.g. --set package.name=mpc --set ros.node_name=mpc_node")
    args = parser.parse_args()

    kwargs = parse_args_values(args.set)
    generate_ros_package(args.solver_json_path, config_path=args.config_path, **kwargs)