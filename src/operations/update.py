"""
Update operation for FHIR resources.
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def update_resource(fhir_client, resource: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing FHIR resource on the server.

    This is a wrapper function that delegates to the FHIRClient's update_resource method.
    
    Parameters:
        fhir_client: An instance of the FHIRClient to handle the request.
        resource: The updated resource data as a dictionary (must include 'id' field).

    Returns:
        The updated resource from the FHIR server.
        
    Raises:
        FHIRClientError: If the update operation fails.
    """
    logger.info(f"Updating resource {resource.get('resourceType')}/{resource.get('id')}")
    return fhir_client.update_resource(resource)