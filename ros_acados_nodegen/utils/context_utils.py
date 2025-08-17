import logging
import json
from typing import Any

logger = logging.getLogger(__name__)


def _coerce_value(val: str):
    """Versuche JSON -> bool -> int -> float -> str."""
    if val is None:
        return None
    s = str(val).strip()
    # JSON structures (listen/objekte)
    if s.startswith(("{", "[")):
        try:
            return json.loads(s)
        except Exception:
            pass
    low = s.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s
        

def parse_dot_key_value(pairs: dict) -> dict:
    """Parse list of {'a.b.c': val} into nested dicts {'a': {'b': {'c': val}}}"""
    out: dict = {}
    for key, val in pairs.items():
        parts = key.split(".")
        cur = out
        for part in parts[:-1]:
            cur = cur.setdefault(part, {})
        cur[parts[-1]] = val
    return out


def parse_args_values(pairs: list[str]) -> dict:
    """Parse list of "a.b.c=val" into nested dicts {'a.b.c': val}"""
    if not pairs:
        return {}
    
    out: dict = {}
    for p in pairs:
        if "=" not in p:
            continue
        key, val = p.split("=", 1)
        out[key] = _coerce_value(val)
    return out


def deep_update(dst: dict, src: dict) -> None:
    """Rekursively updates the destination dictionary with values from the source dictionary."""
    for k, v in src.items():
        if k not in dst:
            logger.warning(f"Key '{k}' not found in destination dict.")
            continue
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            deep_update(dst[k], v)
        else:
            dst[k] = v