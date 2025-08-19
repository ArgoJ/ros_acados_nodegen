import json
import logging
from pathlib import Path
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def get_diagonal(matrix: list) -> list[float]:
    """Extracts the diagonal from a list of lists."""
    if not isinstance(matrix, list) or not all(isinstance(row, list) for row in matrix):
        return []
    
    if not matrix or not matrix[0]:
        return []

    return [matrix[i][i] for i in range(len(matrix))]


class ValueContext(BaseModel):
    name: str = "acados_name"
    log_label: str = "This Value"
    value: list[float] = Field(default=list)

class AcadosModelContext(BaseModel):
    name: str = "my_model"
    
class AcadosSolverOptionsContext(BaseModel):
    nlp_solver_type: str = "SQP_RTI"
    warmstart_first: bool = True
    warmstart: bool = False

class AcadosConstraintsContext(BaseModel):
    # States Bounds
    lbx: ValueContext = Field(default=ValueContext(name="lbx", log_label="Lower Bound X"))
    ubx: ValueContext = Field(default=ValueContext(name="ubx", log_label="Upper Bound X"))
    lbx_e: ValueContext = Field(default=ValueContext(name="lbx_e", log_label="Lower Bound X Terminal"))
    ubx_e: ValueContext = Field(default=ValueContext(name="ubx_e", log_label="Upper Bound X Terminal"))

    # State Slack Bounds
    lsbx: ValueContext = Field(default=ValueContext(name="lsbx", log_label="Lower Slack Bound X"))
    usbx: ValueContext = Field(default=ValueContext(name="usbx", log_label="Upper Slack Bound X"))
    lsbx_e: ValueContext = Field(default=ValueContext(name="lsbx_e", log_label="Lower Slack Bound X Terminal"))
    usbx_e: ValueContext = Field(default=ValueContext(name="usbx_e", log_label="Upper Slack Bound X Terminal"))

    # Input Bounds
    lbu: ValueContext = Field(default=ValueContext(name="lbu", log_label="Lower Bound U"))
    ubu: ValueContext = Field(default=ValueContext(name="ubu", log_label="Upper Bound U"))

    # Input Slack Bounds
    lsbu: ValueContext = Field(default=ValueContext(name="lsbu", log_label="Lower Slack Bound U"))
    usbu: ValueContext = Field(default=ValueContext(name="usbu", log_label="Upper Slack Bound U"))

    # Nonlinear Bounds
    lh: ValueContext = Field(default=ValueContext(name="lh", log_label="Lower Bound H"))
    uh: ValueContext = Field(default=ValueContext(name="uh", log_label="Upper Bound H"))
    lh_0: ValueContext = Field(default=ValueContext(name="lh_0", log_label="Lower Bound H Initial"))
    uh_0: ValueContext = Field(default=ValueContext(name="uh_0", log_label="Upper Bound H Initial"))
    lh_e: ValueContext = Field(default=ValueContext(name="lh_e", log_label="Lower Bound H Terminal"))
    uh_e: ValueContext = Field(default=ValueContext(name="uh_e", log_label="Upper Bound H Terminal"))

    # Nonlinear Slack Bounds
    lsh: ValueContext = Field(default=ValueContext(name="lsh", log_label="Lower Bound H"))
    ush: ValueContext = Field(default=ValueContext(name="ush", log_label="Upper Bound H"))
    lsh_0: ValueContext = Field(default=ValueContext(name="lsh_0", log_label="Lower Bound H Initial"))
    ush_0: ValueContext = Field(default=ValueContext(name="ush_0", log_label="Upper Bound H Initial"))
    lsh_e: ValueContext = Field(default=ValueContext(name="lsh_e", log_label="Lower Bound H Terminal"))
    ush_e: ValueContext = Field(default=ValueContext(name="ush_e", log_label="Upper Bound H Terminal"))

    # Nonlinear Phase Bounds
    lphi: ValueContext = Field(default=ValueContext(name="lphi", log_label="Lower Bound Phi"))
    uphi: ValueContext = Field(default=ValueContext(name="uphi", log_label="Upper Bound Phi"))
    lphi_0: ValueContext = Field(default=ValueContext(name="lphi_0", log_label="Lower Bound Phi Initial"))
    uphi_0: ValueContext = Field(default=ValueContext(name="uphi_0", log_label="Upper Bound Phi Initial"))
    lphi_e: ValueContext = Field(default=ValueContext(name="lphi_e", log_label="Lower Bound Phi Terminal"))
    uphi_e: ValueContext = Field(default=ValueContext(name="uphi_e", log_label="Upper Bound Phi Terminal"))

    # Nonlinear Phase Slack Bounds
    lsphi: ValueContext = Field(default=ValueContext(name="lsphi", log_label="Lower Bound Phi Slack"))
    usphi: ValueContext = Field(default=ValueContext(name="usphi", log_label="Upper Bound Phi Slack"))
    lsphi_0: ValueContext = Field(default=ValueContext(name="lsphi_0", log_label="Lower Bound Phi Initial Slack"))
    usphi_0: ValueContext = Field(default=ValueContext(name="usphi_0", log_label="Upper Bound Phi Initial Slack"))
    lsphi_e: ValueContext = Field(default=ValueContext(name="lsphi_e", log_label="Lower Bound Phi Terminal Slack"))
    usphi_e: ValueContext = Field(default=ValueContext(name="usphi_e", log_label="Upper Bound Phi Terminal Slack"))

    # General Polytopic Inequalities Bounds
    lg: ValueContext = Field(default=ValueContext(name="lg", log_label="Lower Bound G"))
    ug: ValueContext = Field(default=ValueContext(name="ug", log_label="Upper Bound G"))
    lg_e: ValueContext = Field(default=ValueContext(name="lg_e", log_label="Lower Bound G Terminal"))
    ug_e: ValueContext = Field(default=ValueContext(name="ug_e", log_label="Upper Bound G Terminal"))

    # General Polytopic Inequalities Slack Bounds
    lsg: ValueContext = Field(default=ValueContext(name="lsg", log_label="Lower Bound G Slack"))
    usg: ValueContext = Field(default=ValueContext(name="usg", log_label="Upper Bound G Slack"))
    lsg_e: ValueContext = Field(default=ValueContext(name="lsg_e", log_label="Lower Bound G Terminal Slack"))
    usg_e: ValueContext = Field(default=ValueContext(name="usg_e", log_label="Upper Bound G Terminal Slack"))

    @classmethod
    def values_only(cls, **kwargs) -> 'AcadosConstraintsContext':
        processed_data = {}
        for field_name, field_value in kwargs.items():
            if field_name in cls.model_fields and isinstance(field_value, list):
                default_field: ValueContext = cls.model_fields[field_name].default
                processed_data[field_name] = default_field.model_copy(update={'value': field_value})
                
        return cls.model_validate(processed_data)


class AcadosWeightsContext(BaseModel):
    W_0: ValueContext = Field(default=ValueContext(name="W_0", log_label="Initial Weight"))
    W: ValueContext = Field(default=ValueContext(name="W", log_label="Stage Weight"))
    W_e: ValueContext = Field(default=ValueContext(name="W_e", log_label="Terminal Weight"))
    
    @classmethod
    def values_only(cls, **kwargs) -> 'AcadosWeightsContext':
        processed_data = {}
        for field_name, field_value in kwargs.items():
            if field_name in cls.model_fields and isinstance(field_value, list):
                default_field: ValueContext = cls.model_fields[field_name].default
                processed_data[field_name] = default_field.model_copy(update={'value': field_value})
                
        return cls.model_validate(processed_data)
    

class AcadosReferencesContext(BaseModel):
    yref_0: ValueContext = Field(default=ValueContext(name="yref_0", log_label="Initial Reference"))
    yref: ValueContext = Field(default=ValueContext(name="yref", log_label="Stage Reference"))
    yref_e: ValueContext = Field(default=ValueContext(name="yref_e", log_label="Terminal Reference"))

    @classmethod
    def values_only(cls, **kwargs) -> 'AcadosReferencesContext':
        processed_data = {}
        for field_name, field_value in kwargs.items():
            if field_name in cls.model_fields and isinstance(field_value, list):
                default_field: ValueContext = cls.model_fields[field_name].default
                processed_data[field_name] = default_field.model_copy(update={'value': field_value})
                
        return cls.model_validate(processed_data)


class AcadosContext(BaseModel):
    model: AcadosModelContext = Field(default=AcadosModelContext)
    solver: AcadosSolverOptionsContext = Field(default=AcadosSolverOptionsContext)
    constraints: AcadosConstraintsContext = Field(default=AcadosConstraintsContext)
    weights: AcadosWeightsContext = Field(default=AcadosWeightsContext)
    references: AcadosReferencesContext = Field(default=AcadosReferencesContext)
    parameter_values: ValueContext = Field(default=ValueContext(name="parameter_values", log_label="Parameter Values"))
    x0: ValueContext = Field(default=ValueContext(name="x0", log_label="Initial State"))

    @classmethod
    def from_solver_json(cls, solver_path: str) -> 'AcadosContext':
        """
        Read an acados JSON (exported solver config) and return a minimal context
        dict that can seed the Jinja templates with model name and dimensions.
        """
        logger.debug(f"Loading solver JSON from: {solver_path}")
        if not solver_path:
            return {}

        p = Path(solver_path)
        if p.is_dir():
            json_files = list(p.glob("*.json"))
            if not json_files:
                return {}
            p = json_files[0]

        try:
            with open(p, "r") as f:
                data: dict = json.load(f)
        except Exception:
            return {}


        solver_options = data.get("solver", {})
        model_options = data.get("model", {})
        constraints_options = data.get("constraints", {})
        cost_options = data.get("cost", {})
        
        processed_weights = {
            "W_0": get_diagonal(cost_options.get("W_0", [])),
            "W": get_diagonal(cost_options.get("W", [])),
            "W_e": get_diagonal(cost_options.get("W_e", []))
        }

        return cls(
            model=AcadosModelContext(**model_options), 
            solver=AcadosSolverOptionsContext(**solver_options), 
            constraints=AcadosConstraintsContext.values_only(**constraints_options), 
            weights=AcadosWeightsContext.values_only(**processed_weights), 
            references=AcadosReferencesContext.values_only(**cost_options), 
            parameter_values=ValueContext(value=data.get("parameter_values", [])),
            x0=ValueContext(value=constraints_options.get("lbx_0", [])),
        )