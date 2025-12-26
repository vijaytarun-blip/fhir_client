"""
Error handling and custom exceptions for FHIR Client.
"""


class FHIRClientError(Exception):
    """Base exception for FHIR Client errors."""
    pass


class FHIRConnectionError(FHIRClientError):
    """Raised when connection to FHIR server fails."""
    pass


class FHIRAuthenticationError(FHIRClientError):
    """Raised when authentication fails."""
    pass


class FHIRResourceNotFoundError(FHIRClientError):
    """Raised when a requested resource is not found."""
    pass


class FHIRValidationError(FHIRClientError):
    """Raised when resource validation fails."""
    pass


class FHIROperationError(FHIRClientError):
    """Raised when a FHIR operation fails."""
    pass


def handle_response_error(response):
    """
    Handle HTTP response errors and raise appropriate exceptions.
    
    Args:
        response: requests.Response object
        
    Raises:
        FHIRAuthenticationError: For 401/403 status codes
        FHIRResourceNotFoundError: For 404 status code
        FHIROperationError: For other error status codes
    """
    status_code = response.status_code
    
    if status_code == 401 or status_code == 403:
        raise FHIRAuthenticationError(
            f"Authentication failed: {response.status_code} - {response.text}"
        )
    elif status_code == 404:
        raise FHIRResourceNotFoundError(
            f"Resource not found: {response.url}"
        )
    elif status_code >= 400:
        raise FHIROperationError(
            f"Operation failed: {response.status_code} - {response.text}"
        )
