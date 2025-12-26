"""
FHIR Client Module
Provides a robust client for interacting with FHIR servers.
"""

import requests
import logging
from typing import Dict, Optional, Any, List
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FHIRClientError(Exception):
    """Base exception for FHIR Client errors"""

    pass


class FHIRClient:
    """
    A client for interacting with FHIR servers.

    Supports CRUD operations and search functionality with proper error handling,
    authentication, and connection pooling.
    """

    def __init__(
        self,
        base_url: str,
        auth: Optional[tuple] = None,
        timeout: int = 30,
        verify_ssl: bool = True,
    ):
        """
        Initialize FHIR Client.

        Args:
            base_url: Base URL of the FHIR server (e.g., "https://hapi.fhir.org/baseR4")
            auth: Optional tuple of (username, password) for basic authentication
            timeout: Request timeout in seconds (default: 30)
            verify_ssl: Whether to verify SSL certificates (default: True)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        # Create session with retry strategy
        self.session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set authentication if provided
        if auth:
            self.session.auth = auth

        # Set default headers
        self.session.headers.update(
            {"Accept": "application/fhir+json", "Content-Type": "application/fhir+json"}
        )

        logger.info(f"FHIR Client initialized with base URL: {self.base_url}")

    def create_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new resource on the FHIR server.

        Args:
            resource: Dictionary representing the FHIR resource

        Returns:
            Created resource with server-assigned ID

        Raises:
            FHIRClientError: If creation fails
        """
        if "resourceType" not in resource:
            raise FHIRClientError("Resource must have 'resourceType' field")

        resource_type = resource["resourceType"]
        url = f"{self.base_url}/{resource_type}"

        try:
            logger.info(f"Creating {resource_type} resource")
            response = self.session.post(
                url, json=resource, timeout=self.timeout, verify=self.verify_ssl
            )
            response.raise_for_status()
            created = response.json()
            logger.info(
                f"Successfully created {resource_type} with ID: {created.get('id')}"
            )
            return created
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create resource: {str(e)}")
            raise FHIRClientError(f"Failed to create resource: {str(e)}")

    def read_resource(self, resource_type: str, resource_id: str) -> Dict[str, Any]:
        """
        Read a resource from the FHIR server.

        Args:
            resource_type: Type of FHIR resource (e.g., "Patient", "Observation")
            resource_id: ID of the resource to read

        Returns:
            The requested resource

        Raises:
            FHIRClientError: If read fails
        """
        url = f"{self.base_url}/{resource_type}/{resource_id}"

        try:
            logger.info(f"Reading {resource_type}/{resource_id}")
            response = self.session.get(
                url, timeout=self.timeout, verify=self.verify_ssl
            )
            response.raise_for_status()
            resource = response.json()
            logger.info(f"Successfully read {resource_type}/{resource_id}")
            return resource
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to read resource: {str(e)}")
            raise FHIRClientError(f"Failed to read resource: {str(e)}")

    def update_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing resource on the FHIR server.

        Args:
            resource: Dictionary representing the FHIR resource with 'id' field

        Returns:
            Updated resource

        Raises:
            FHIRClientError: If update fails
        """
        if "resourceType" not in resource:
            raise FHIRClientError("Resource must have 'resourceType' field")
        if "id" not in resource:
            raise FHIRClientError("Resource must have 'id' field for update")

        resource_type = resource["resourceType"]
        resource_id = resource["id"]
        url = f"{self.base_url}/{resource_type}/{resource_id}"

        try:
            logger.info(f"Updating {resource_type}/{resource_id}")
            response = self.session.put(
                url, json=resource, timeout=self.timeout, verify=self.verify_ssl
            )
            response.raise_for_status()
            updated = response.json()
            logger.info(f"Successfully updated {resource_type}/{resource_id}")
            return updated
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update resource: {str(e)}")
            raise FHIRClientError(f"Failed to update resource: {str(e)}")

    def delete_resource(self, resource_type: str, resource_id: str) -> bool:
        """
        Delete a resource from the FHIR server.

        Args:
            resource_type: Type of FHIR resource (e.g., "Patient", "Observation")
            resource_id: ID of the resource to delete

        Returns:
            True if deletion was successful

        Raises:
            FHIRClientError: If deletion fails
        """
        url = f"{self.base_url}/{resource_type}/{resource_id}"

        try:
            logger.info(f"Deleting {resource_type}/{resource_id}")
            response = self.session.delete(
                url, timeout=self.timeout, verify=self.verify_ssl
            )
            response.raise_for_status()
            logger.info(f"Successfully deleted {resource_type}/{resource_id}")
            return response.status_code in [200, 204]
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to delete resource: {str(e)}")
            raise FHIRClientError(f"Failed to delete resource: {str(e)}")

    def search(
        self, resource_type: str, search_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for resources on the FHIR server.

        Args:
            resource_type: Type of FHIR resource to search for
            search_params: Dictionary of search parameters

        Returns:
            Bundle of matching resources

        Raises:
            FHIRClientError: If search fails
        """
        url = f"{self.base_url}/{resource_type}"

        try:
            logger.info(f"Searching {resource_type} with params: {search_params}")
            response = self.session.get(
                url, params=search_params, timeout=self.timeout, verify=self.verify_ssl
            )
            response.raise_for_status()
            bundle = response.json()
            total = bundle.get("total", 0)
            logger.info(f"Search returned {total} results")
            return bundle
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to search resources: {str(e)}")
            raise FHIRClientError(f"Failed to search resources: {str(e)}")

    def get_capability_statement(self) -> Dict[str, Any]:
        """
        Retrieve the capability statement from the FHIR server.

        Returns:
            CapabilityStatement resource

        Raises:
            FHIRClientError: If retrieval fails
        """
        url = f"{self.base_url}/metadata"

        try:
            logger.info("Retrieving capability statement")
            response = self.session.get(
                url, timeout=self.timeout, verify=self.verify_ssl
            )
            response.raise_for_status()
            capability = response.json()
            logger.info("Successfully retrieved capability statement")
            return capability
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to retrieve capability statement: {str(e)}")
            raise FHIRClientError(f"Failed to retrieve capability statement: {str(e)}")

    def close(self):
        """Close the session and clean up resources."""
        self.session.close()
        logger.info("FHIR Client session closed")
