"""
Create operation for FHIR resources.
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def create_resource(fhir_client, resource: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new resource on the FHIR server.

    This is a wrapper function that delegates to the FHIRClient's create_resource method.
    
    Parameters:
        fhir_client: An instance of the FHIRClient class to handle the connection.
        resource: A dictionary representing the FHIR resource to be created.

    Returns:
        The response from the FHIR server after attempting to create the resource.
        
    Raises:
        FHIRClientError: If the creation fails.
    """
    logger.info(f"Creating resource of type {resource.get('resourceType')}")
    return fhir_client.create_resource(resource)