"""
Utility modules for FHIR Client.
"""
from .config import FHIRConfig, config
from .errors import (
    FHIRClientError,
    FHIRConnectionError,
    FHIRAuthenticationError,
    FHIRResourceNotFoundError,
    FHIRValidationError,
    FHIROperationError
)
from .logger import setup_logging, get_logger

__all__ = [
    'FHIRConfig',
    'config',
    'FHIRClientError',
    'FHIRConnectionError',
    'FHIRAuthenticationError',
    'FHIRResourceNotFoundError',
    'FHIRValidationError',
    'FHIROperationError',
    'setup_logging',
    'get_logger'
]