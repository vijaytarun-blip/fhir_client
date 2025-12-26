"""
FHIR Client Package

A comprehensive Python client for interacting with FHIR servers.
"""
from .client import FHIRClient, FHIRClientError
from .models import Patient, Observation

__version__ = '1.0.0'
__all__ = ['FHIRClient', 'FHIRClientError', 'Patient', 'Observation']