"""
Configuration management for FHIR Client.

This module provides configuration settings and environment variable management
for the FHIR client.
"""

import os
from typing import Optional


class FHIRConfig:
    """Configuration class for FHIR Client settings."""

    # Default FHIR server URLs (public test servers)
    DEFAULT_SERVERS = {
        "hapi-r4": "https://hapi.fhir.org/baseR4",
        "hapi-r5": "https://hapi.fhir.org/baseR5",
        "test-server": "http://test.fhir.org/r4",
    }

    # Default Terminology Server URLs
    TERMINOLOGY_SERVERS = {
        "hl7-tx": "https://tx.fhir.org/r4",  # HL7 Official
        "snomed": "https://snowstorm.ihtsdotools.org/fhir",  # SNOMED CT
    }

    def __init__(self):
        """Initialize configuration from environment variables or defaults."""
        # Primary configuration from environment variables
        self.base_url = os.getenv("FHIR_SERVER_URL", self.DEFAULT_SERVERS["hapi-r4"])
        self.username = os.getenv("FHIR_USERNAME")
        self.password = os.getenv("FHIR_PASSWORD")
        self.timeout = int(os.getenv("FHIR_TIMEOUT", "30"))
        self.verify_ssl = os.getenv("FHIR_VERIFY_SSL", "true").lower() == "true"
        self.max_retries = int(os.getenv("FHIR_MAX_RETRIES", "3"))
        self.log_level = os.getenv("FHIR_LOG_LEVEL", "INFO")

    @property
    def auth(self) -> Optional[tuple]:
        """
        Get authentication tuple if credentials are configured.

        Returns:
            Tuple of (username, password) or None
        """
        if self.username and self.password:
            return (self.username, self.password)
        return None

    def get_server_url(self, server_key: str) -> str:
        """
        Get a predefined server URL by key.

        Args:
            server_key: Key for the server (e.g., 'hapi-r4', 'hapi-r5')

        Returns:
            Server URL

        Raises:
            KeyError: If server_key is not found
        """
        return self.DEFAULT_SERVERS[server_key]

    def __repr__(self):
        """String representation of config (excluding sensitive data)."""
        return (
            f"FHIRConfig(base_url='{self.base_url}', "
            f"timeout={self.timeout}, verify_ssl={self.verify_ssl})"
        )


# Global configuration instance
config = FHIRConfig()

# Legacy compatibility - keep old variable names
FHIR_SERVER_BASE_URL = config.base_url
base_url = config.base_url
auth = {"username": config.username, "password": config.password}
