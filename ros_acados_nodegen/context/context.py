import yaml
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field

from .pkg_context import PackageContext
from .ros_context import RosContext, PublisherContext, SubscriberContext
from .acados_context import AcadosContext
from ..utils.jinja_utils import extract_pkg_from_type

class RosPackageContext(BaseModel):
    script_path: str | Path = Field(default_factory=str)
    package: PackageContext = Field(default_factory=lambda: PackageContext(validate_assignment=True))
    ros: RosContext         = Field(default_factory=lambda: RosContext(validate_assignment=True))
    acados: AcadosContext   = Field(default_factory=lambda: AcadosContext(validate_assignment=True))

    def model_post_init(self, __context: Any | None = None) -> None:
        self.add_msg_dependencies(self.ros.publishers + self.ros.subscribers)

    @classmethod
    def from_json(cls, config_path: str | Path) -> 'RosPackageContext':
        with open(config_path, 'r') as f:
            return cls.model_validate_json(f.read())
    
    @classmethod
    def from_yaml(cls, config_path: str | Path) -> 'RosPackageContext':
        with open(config_path, 'r') as f:
            config_data: dict[str, Any] = yaml.safe_load(f)
        return cls.model_validate(config_data)

    def add_msg_dependencies(self, pub_sub: list[PublisherContext | SubscriberContext]):
        for item in pub_sub:
            pkg = extract_pkg_from_type(item.msg_type)
            if pkg:
                self.package.dependencies.add(pkg)