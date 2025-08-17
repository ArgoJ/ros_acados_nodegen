---
mode: ask
---
# Project Context: MPC Safety Filter for ROS2

## I. High-Level Overview
This project is a real-time safety filter for a mobile robot using Model Predictive Control (MPC). The core of the filter is an optimization problem solved by 'acados'. The solver is generated as C code from a Python script and then integrated into a C++ ROS2 node. This C++ node is implemented as a **Nav2 Controller Plugin** which acts as a **Proxy Controller**.

## II. Core Components & Data Flow

1.  **PYTHON (scripts/safety_filter_mpc.py):**
    - Uses 'acados_template' to define the MPC problem (robot model, cost function, constraints).
    - Generates a high-performance C code solver which is then compiled into a shared library.

2.  **C++ (src/mpc_controller.cpp):**
    - Implements a Nav2 Controller Plugin inheriting from `nav2_core::Controller`.
    - This plugin internally loads a standard Nav2 controller (like DWB) using `pluginlib`.
    - The plugin calls the standard controller to get a desired `cmd_vel`. This desired command is used as the **reference (y_ref)** for the MPC.
    - The plugin extracts lethal obstacles from the Nav2 `Costmap2D` object.
    - It calls the generated Acados C-API to solve the MPC problem in real-time.
    - The result is the final, safe `cmd_vel` which is returned to the Nav2 `controller_server`.

## III. Key Technologies
- ROS2 Humble
- C++17
- acados
- Eigen3
- pluginlib
- colcon

## IV. Important Conventions
- **States $x$:** The state vector $x$ includes the robot's position $(x,y)$, the orientation $\theta$, velocity $v$, and angular velocity $\omega$.
- **Inputs $u$:** The input vector $u$ consists of the robot's linear and angular velocities $(v, \omega)$.
- **Acados Parameter Vector $p$:** This vector is crucial. It is organized as triplets: `[safety_radius, obstacle1_x, obstacle1_y, obstacle1_activation, obstacle2_x, ...]`. The activation is `1.0` for active obstacles and `0.0` for inactive slots.
- **Coordinate Frames:** The controller operates in ROS2 standard frames: `map` (global), `odom` (odometry), and `base_link` (robot).
- **Safety Radius:** The safety radius is a critical parameter that must be set correctly to ensure the robot avoids collisions with obstacles $res_{map} * \sqrt{2} + r_{car}$, where $r_{car}$ is the robot's footprint radius and $res_{map}$ is the map resolution.
- **MPC Safety Filter:** The formulation of the MPC safety filter is designed to ensure that the robot maintains a safe distance from obstacles while following a desired input. $L_f(u_unsafe,0) = |u_{safe,0} - u_{unsafe,0}|^2_{W_{ref}} + /sum^N_0 () $, where $u_{safe,0}$ is optimized.