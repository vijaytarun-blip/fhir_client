"""
Read operation for FHIR resources.
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def read_resource(fhir_client, resource_type: str, resource_id: str) -> Dict[str, Any]:
    """
    Read a resource from the FHIR server.

    This is a wrapper function that delegates to the FHIRClient's read_resource method.
    
    Parameters:
        fhir_client: An instance of the FHIRClient class to handle the connection.
        resource_type: The type of FHIR resource (e.g., "Patient", "Observation").
        resource_id: The ID of the resource to read.

    Returns:
        The requested FHIR resource as a dictionary.
        
    Raises:
        FHIRClientError: If the read operation fails.
    """
    logger.info(f"Reading resource {resource_type}/{resource_id}")
    return fhir_client.read_resource(resource_type, resource_id)