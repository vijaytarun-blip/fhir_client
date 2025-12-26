"""
Delete operation for FHIR resources.
"""

import logging

logger = logging.getLogger(__name__)


def delete_resource(fhir_client, resource_type: str, resource_id: str) -> bool:
    """
    Delete a resource from the FHIR server.

    This is a wrapper function that delegates to the FHIRClient's delete_resource method.

    Parameters:
        fhir_client: An instance of the FHIRClient to handle the request.
        resource_type: The type of FHIR resource (e.g., "Patient", "Observation").
        resource_id: The ID of the resource to delete.

    Returns:
        True if the deletion was successful.

    Raises:
        FHIRClientError: If the deletion fails.
    """
    logger.info(f"Deleting resource {resource_type}/{resource_id}")
    return fhir_client.delete_resource(resource_type, resource_id)
