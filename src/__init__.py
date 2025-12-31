"""
FHIR Client Package

A comprehensive Python client for interacting with FHIR servers.
"""

from .client import FHIRClient, FHIRClientError
from .models import Patient, Observation
from .terminology import TerminologyService
from .integrated_client import IntegratedFHIRClient, ValidationError

__version__ = "1.0.0"
__all__ = [
    "FHIRClient",
    "FHIRClientError",
    "Patient",
    "Observation",
    "TerminologyService",
    "IntegratedFHIRClient",
    "ValidationError",
]
