import os
import numpy as np
import scipy.linalg as spl
import casadi as ca

from acados_template import AcadosOcp, AcadosOcpSolver, builders, AcadosSim, AcadosSimSolver
from .skid_steer_model import get_skid_steer_model



def create_solver(
        N_horizon: int,
        dt: float, 
        max_num_obs: int, 
        R_ref: np.ndarray = None,
        R_delta: np.ndarray = None,
        gen_code_path: str = ""
):
    """
    Erstellt und konfiguriert den AcadosOcpSolver.
    """
    ocp = AcadosOcp()
    ocp.model = get_skid_steer_model(dt)

    # --- Dimensions  ---
    ocp.dims.nx = ocp.model.x.size1()
    ocp.dims.nu = ocp.model.u.size1()

    # Gewichtungsmatrizen
    v_scale = 1e1
    omega_scale = 1e-1

    if R_ref is None:
        R_ref = np.diag([1.5 * v_scale, 1. * omega_scale])
    if R_delta is None:
        R_delta = np.diag([1. * v_scale, 3. * omega_scale])

    u_delta = ocp.model.u - ocp.model.x[3:5]

    ocp.cost.cost_type_0 = "NONLINEAR_LS"
    ocp.cost.W_0 = spl.block_diag(R_ref, R_delta)
    ocp.model.cost_y_expr_0 = ca.vertcat(ocp.model.u, u_delta)
    ocp.cost.yref_0 = np.zeros(ocp.dims.nu * 2)

    ocp.cost.cost_type = "NONLINEAR_LS"
    ocp.cost.W = R_delta
    ocp.model.cost_y_expr = u_delta
    ocp.cost.yref = np.zeros(ocp.dims.nu)

    # --- Constraints ---
    # Box-Constraints für Steuerungen
    v_max = 1.0
    omega_max = 1.5
    ocp.constraints.lbu = np.array([-v_max, -omega_max])
    ocp.constraints.ubu = np.array([v_max, omega_max])
    ocp.constraints.idxbu = np.array([0, 1])

    # Box-Constraints für Zustände (Geschwindigkeit)
    ocp.constraints.lbx = np.array([-v_max, -omega_max])
    ocp.constraints.ubx = np.array([v_max, omega_max])
    ocp.constraints.idxbx = np.array([3, 4])

    # Nichtlineare Beschränkungen für Hindernisse
    ocp.dims.np = max_num_obs*3 + 1
    ocp.dims.nh = max_num_obs

    p = ca.MX.sym('p', ocp.dims.np) # [r_unsafe_sqare,x0,y0,switch0,x01,y1,switch1]
    ocp.model.p = p
    robot_pos = ocp.model.x[:2] # [x, y]
    
    eps = 1e-6
    ocp.model.con_h_expr = ca.vertcat(*[
        p[3*i+3] * ((robot_pos[0] - p[3*i+1])**2 + (robot_pos[1] - p[3*i+2])**2 - p[0] + eps)
        for i in range(max_num_obs)
    ])

    # Untere Schranke (Sicherheitsabstand), obere Schranke unendlich
    ocp.constraints.lh = np.zeros(max_num_obs)
    ocp.constraints.uh = np.full(max_num_obs, 1e4)

    # --- Parameter ---
    # Anfangszustand
    ocp.constraints.x0 = np.zeros(ocp.dims.nx)
    ocp.parameter_values = np.zeros(ocp.dims.np) 

    # --- Solver-Options ---
    ocp.solver_options.qp_solver = 'PARTIAL_CONDENSING_HPIPM'
    ocp.solver_options.hessian_approx = 'GAUSS_NEWTON'
    ocp.solver_options.integrator_type = 'ERK'
    ocp.solver_options.nlp_solver_type = 'SQP_RTI' # Real-Time Iteration
    ocp.solver_options.nlp_solver_tol_ineq = 1e-4
    ocp.solver_options.nlp_solver_max_iter = 5
    ocp.solver_options.N_horizon = N_horizon
    ocp.solver_options.tf = dt * N_horizon

    # --- Solver creation ---
    if gen_code_path:
        ocp.code_export_directory = gen_code_path

    cm_builder = builders.ocp_get_default_cmake_builder()
    cm_builder.options_on = ['BUILD_ACADOS_OCP_SOLVER_LIB']

    json_file = os.path.join(os.path.dirname(__file__) if not gen_code_path else gen_code_path, 'safety_filter_ocp.json')
    if os.path.exists(json_file):
        os.remove(json_file)

    solver = AcadosOcpSolver(ocp, json_file=json_file, cmake_builder=cm_builder)

    return solver


def create_sim(
        dt: float,
        gen_code_path: str = ""
):
    sim = AcadosSim()
    sim.model = get_skid_steer_model(dt)
    sim.solver_options.T = dt
    sim.solver_options.integrator_type = 'ERK'
    sim.solver_options.num_stages = 4
    sim.solver_options.num_steps = 1
    
    if gen_code_path:
        sim.code_export_directory = gen_code_path

    json_file = os.path.join(os.path.dirname(__file__) if not gen_code_path else gen_code_path, 'skid_steer_sim.json')
    if os.path.exists(json_file):
        os.remove(json_file)

    acados_simulator = AcadosSimSolver(sim, json_file=json_file)
    return acados_simulator