import logging
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

class PackageContext(BaseModel):
    name: str          = "my_package"
    version: str       = "0.0.1"
    description: str   = "A package for my project"
    author_email: str  = "your.name@email.com"
    author_name: str   = "Your Name"
    license: str       = "MY LICENSE"
    with_markers: bool = Field(default=False)
    dependencies: set[str] = Field(default_factory=set)
    
    @field_validator("dependencies", mode="before")
    @classmethod
    def _coerce_deps(cls, v):
        if v is None:
            return set()
        if isinstance(v, str):
            return {v}
        try:
            return set(v)
        except Exception:
            logger.warning("Failed to coerce dependencies to set, using empty set instead.")
            return set()