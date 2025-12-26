"""
FHIR Resource Models

This module provides helper classes for creating and validating FHIR resources.
"""

from .patient import Patient
from .observation import Observation

__all__ = ["Patient", "Observation"]
