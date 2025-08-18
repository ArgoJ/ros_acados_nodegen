# Ros Acados Nodegen
A Codegenerator for ROS2 Nodes, that use a generated acados solver. 
The `generate_ros_package` function creates a ROS2 package based on some `acados_solver.json` file. 
The generated `CMakeLists.txt` is build so that the acados C code files are generated during each build.

## Installation
The package can be installed easily with:
```bash
pip install .
```

### Acados Installation
If you want to install acados, you can use:
```bash
acados-install --qpoases --omp -e
```
This will install acados with qpoases and omp, while also exporting the relevant paths for acados. 
