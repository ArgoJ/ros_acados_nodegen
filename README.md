# Ros Acados Nodegen
A Codegenerator for ROS2 Nodes, that use a generated acados solver. 
The `generate_ros_package` function creates a ROS2 package based on some `ocp_solver.json` file, created by acados. 
One can also add a [`config.yaml`](ros_acados_nodegen/config/all_configs.yaml) to directly specify 
package information, publisher and subscriber as well as node parameters.   
The generated `CMakeLists.txt` is build such that the acados C code files are generated during each build.

## Installation
Acados don't need to be installed in the same environment, but recomendet.
The package can be installed easily with:
```bash
pip install .
```

### Acados Installation
If you want to install acados after this package installation, you can use:
```bash
acados-install --qpoases --omp -e
```
This will install acados with qpoases and omp, while also exporting the relevant paths for acados. 
You can also follow the official installation guide on [acados.org](https://docs.acados.org/installation).


## Usage
Create a python script that creates an ocp solver with acados. Use the corresponding `ocp_solver.json` file path, your script path where you create the ocp solver, and a copied [all_configs.yaml](/ros_acados_nodegen/config/all_configs.yaml) path.

```python
generate_ros_package(
    solver_path="path" / "to" / "your" / "acados_solver.json",
    install_path="path" / "to" / "desired" / "nodegen_code",
    config_path="path" / "to" / "your" / "config.yaml",
    script_path="path" / "to" / "your" / "script.py",
)
```

### ROS2 build
For the build, you need to specify the python `VENV_PATH` where acados is installed, otherwise the script will use the default path *~/.acados_env*.

```bash
colcon build --packages-select <your_package_name>
```

The acados build can be debugged a little bit during the ros build with the `event-handlers`, while the cmake argument `DCMAKE_EXPORT_COMPILE_COMMANDS` gives you analytics your IDE. 
```bash
colcon build --packages-select <your_package_name>  --event-handlers console_direct+ --cmake-args -DVENV_PYTHON_EXECUTABLE=~/.acados_env -DCMAKE_EXPORT_COMPILE_COMMANDS=1 
```

## Example
After proper installation, run the example script of the safety filter with:
```bash
source ~/.acados_env/bin/activate
python3 examples/safety_filter/scripts/safety_filter_mpc.py -p
```

Generate the ROS2 node code with.
```bash
python3 examples/safety_filter/generate_safety_filter_node.py 
```

Then source ROS2 Humble and build the node.
```bash
source /opt/ros/humble/setup.bash
colcon build --packages-select <your_package_name>  --event-handlers console_direct+ --cmake-args -DVENV_PYTHON_EXECUTABLE=~/.acados_env -DCMAKE_EXPORT_COMPILE_COMMANDS=1 
```

Start the ROS2 node.
```bash
ros2 run safety_filter safety_filter_node
```