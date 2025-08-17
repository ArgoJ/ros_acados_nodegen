import os
import re
from typing import Optional

def extract_pkg_from_type(t: Optional[str]) -> str:
    """Extract package name from a message type string"""
    if not t:
        return ""
    if "::" in t:
        return t.split("::")[0].strip()
    if "/" in t:
        return t.split("/")[0].strip()
    return t.strip()

def snake_case(s: Optional[str]) -> str:
    """Convert CamelCase or spaced string to snake_case."""
    if not s:
        return ""
    s = s.strip()
    # CamelCase -> snake_case
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.replace(" ", "_").lower()

def cpp_type(t: Optional[str]) -> str:
    """Return C++ message type: pkg::msg::Type"""
    if not t:
        return ""
    if "::" in t:
        parts = [p.strip() for p in t.split("::", 1)]
        return f"{parts[0]}::msg::{parts[1]}"
    if "/" in t:
        parts = [p.strip() for p in t.split("/", 1)]
        # use last segment as type name
        type_name = parts[1].split("/")[-1]
        return f"{parts[0]}::msg::{type_name}"
    return t

def include_path(t: Optional[str]) -> str:
    """Return include path like 'pkg/msg/type.hpp' (type in snake_case)."""
    if not t:
        return ""
    if "::" in t:
        parts = [p.strip() for p in t.split("::", 1)]
        return f"{parts[0]}/msg/{snake_case(parts[1])}.hpp"
    if "/" in t:
        parts = [p.strip() for p in t.split("/", 1)]
        type_name = parts[1].split("/")[-1]
        return f"{parts[0]}/msg/{snake_case(type_name)}.hpp"
    return t

def jinja_basename_filter(path: Optional[str]) -> str:
    if path:
        return os.path.basename(path)
    return ''

def get_diagonal(matrix):
    """Extracts the diagonal from a list of lists."""
    if not isinstance(matrix, list) or not all(isinstance(row, list) for row in matrix):
        return []
    return [matrix[i][i] for i in range(len(matrix))]