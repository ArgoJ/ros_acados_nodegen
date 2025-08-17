from typing import Any
from pydantic import BaseModel, Field, ValidationError

class PackageContext(BaseModel):
    name: str          = "my_package"
    version: str       = "0.0.1"
    description: str   = "A package for my project"
    author_email: str  = "your.name@email.com"
    author_name: str   = "Your Name"
    license: str       = "MY LICENSE"
    with_markers: bool = Field(default=False)
    dependencies: set[str] = Field(default_factory=set)