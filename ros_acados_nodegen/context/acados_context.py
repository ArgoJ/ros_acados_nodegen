import json
import logging
from pathlib import Path
from pydantic import BaseModel, Field, model_validator

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
    
    @property
    def non_empty(self) -> bool:
        return bool(self.value)
    
class _BaseFlagged(BaseModel):
    has_init: bool = False
    has_stage: bool = False
    has_term: bool = False

    _exclude_flag_names = {"has_init", "has_stage", "has_term"}

    @staticmethod
    def _is_init(name: str) -> bool:
        return name.endswith("_0")

    @staticmethod
    def _is_term(name: str) -> bool:
        return name.endswith("_e")

    @model_validator(mode="after")
    def _compute_flags(self):
        cls = type(self)
        init_fields, term_fields, stage_fields = [], [], []
        for fname in cls.model_fields:
            if fname in self._exclude_flag_names:
                continue
            if cls._is_init(fname):
                init_fields.append(fname)
            elif cls._is_term(fname):
                term_fields.append(fname)
            else:
                stage_fields.append(fname)
        self.has_init = any(getattr(self, f).non_empty for f in init_fields)
        self.has_term = any(getattr(self, f).non_empty for f in term_fields)
        self.has_stage = any(getattr(self, f).non_empty for f in stage_fields)
        return self

class AcadosModelContext(BaseModel):
    name: str = "my_model"
    
class AcadosSolverOptionsContext(BaseModel):
    nlp_solver_type: str = "SQP_RTI"
    warmstart_first: bool = True
    warmstart: bool = False
    Tsim: float = 0.1

class AcadosConstraintsContext(_BaseFlagged):
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


class AcadosWeightsContext(_BaseFlagged):
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
    
    
class AcadosSlackContext(_BaseFlagged):
    Zl: ValueContext = Field(default=ValueContext(name="Zl", log_label="Lower Slack Hessian Stage"))
    Zl_0: ValueContext = Field(default=ValueContext(name="Zl_0", log_label="Lower Slack Hessian Initial"))
    Zl_e: ValueContext = Field(default=ValueContext(name="Zl_e", log_label="Lower Slack Hessian Terminal"))
    Zu: ValueContext = Field(default=ValueContext(name="Zu", log_label="Upper Slack Hessian Stage"))
    Zu_0: ValueContext = Field(default=ValueContext(name="Zu_0", log_label="Upper Slack Hessian Initial"))
    Zu_e: ValueContext = Field(default=ValueContext(name="Zu_e", log_label="Upper Slack Hessian Terminal"))

    zl: ValueContext = Field(default=ValueContext(name="zl", log_label="Lower Slack Gradient Stage"))
    zl_0: ValueContext = Field(default=ValueContext(name="zl_0", log_label="Lower Slack Gradient Initial"))
    zl_e: ValueContext = Field(default=ValueContext(name="zl_e", log_label="Lower Slack Gradient Terminal"))
    zu: ValueContext = Field(default=ValueContext(name="zu", log_label="Upper Slack Gradient Stage"))
    zu_0: ValueContext = Field(default=ValueContext(name="zu_0", log_label="Upper Slack Gradient Initial"))
    zu_e: ValueContext = Field(default=ValueContext(name="zu_e", log_label="Upper Slack Gradient Terminal"))

    @classmethod
    def values_only(cls, **kwargs) -> 'AcadosSlackContext':
        processed_data = {}
        for field_name, field_value in kwargs.items():
            if field_name in cls.model_fields and isinstance(field_value, list):
                default_field: ValueContext = cls.model_fields[field_name].default
                processed_data[field_name] = default_field.model_copy(update={'value': field_value})
        return cls.model_validate(processed_data)
    

class AcadosReferencesContext(_BaseFlagged):
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
    slacks: AcadosSlackContext = Field(default=AcadosSlackContext)
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
            "W_e": get_diagonal(cost_options.get("W_e", [])),
        }
        
        processed_slacks = {
            "Zl": get_diagonal(cost_options.get("Zl", [])),
            "Zl_0": get_diagonal(cost_options.get("Zl_0", [])),
            "Zl_e": get_diagonal(cost_options.get("Zl_e", [])),
            "Zu": get_diagonal(cost_options.get("Zu", [])),
            "Zu_0": get_diagonal(cost_options.get("Zu_0", [])),
            "Zu_e": get_diagonal(cost_options.get("Zu_e", [])),
            "zl": cost_options.get("zl", []),
            "zl_0": cost_options.get("zl_0", []),
            "zl_e": cost_options.get("zl_e", []),
            "zu": cost_options.get("zu", []),
            "zu_0": cost_options.get("zu_0", []),
            "zu_e": cost_options.get("zu_e", []),
        }

        return cls(
            model=AcadosModelContext(**model_options), 
            solver=AcadosSolverOptionsContext(**solver_options), 
            constraints=AcadosConstraintsContext.values_only(**constraints_options), 
            weights=AcadosWeightsContext.values_only(**processed_weights), 
            slacks=AcadosSlackContext.values_only(**processed_slacks), 
            references=AcadosReferencesContext.values_only(**cost_options), 
            parameter_values=ValueContext(value=data.get("parameter_values", [])),
            x0=ValueContext(value=constraints_options.get("lbx_0", [])),
        )