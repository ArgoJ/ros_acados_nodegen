from ros_acados_nodegen import generate_ros_package
from pathlib import Path


def main():
    generate_ros_package(
        solver_path=Path(__file__).parent / "scripts" / "c_generated_code" / "safety_filter_ocp.json",
        install_path=Path(__file__).parent,
        config_path=Path(__file__).parent / "safety_filter_node_config.yaml",
        script_path=Path(__file__).parent / "scripts" / "safety_filter_mpc.py",
    )

if __name__ == "__main__":
    main()