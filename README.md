# Ros Acados Nodegen
A Codegenerator for ROS2 Nodes, that use a generated acados solver. 
The `generate_ros_package` function creates a ROS2 package based on some `ocp_solver.json` file, created by acados. 
One can also add a [`config.yaml`](ros_acados_nodegen/config/all_configs.yaml) to directly specify 
package information, publisher and subscriber as well as node parameters.   
The generated `CMakeLists.txt` is build so that the acados C code files are generated during each build.

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
Create a python script that creates an ocp solver with acados. Use the corresponding `ocp_solver.json` file. 
Furthermore, copy the `all_configs.yaml` to keep and change youre desired parameters. 
Run an extra script with the `generate_ros_package`, as shown in this [example script](examples/generate_safety_fiter_node.py). 