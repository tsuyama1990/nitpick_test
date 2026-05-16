"""Proxy module to expose configuration from the new domain_models structure.
This file ensures backwards compatibility with SPEC.md expectations while respecting the
domain_models architectural pattern.
"""

from src.domain_models.config import Settings, get_settings

__all__ = ["Settings", "get_settings"]
