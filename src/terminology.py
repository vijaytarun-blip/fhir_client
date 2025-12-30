"""
Terminology Server Client Module

Provides functionality for interacting with FHIR Terminology Servers.
Supports operations like code validation, lookup, value set expansion, and code translation.

Common Terminology Servers:
- https://tx.fhir.org (HL7 Official)
- https://snowstorm.ihtsdotools.org/fhir (SNOMED CT)
"""

import logging
from typing import Dict, Optional, Any, List, Union
from .client import FHIRClient, FHIRClientError

logger = logging.getLogger(__name__)


class TerminologyService:
    """
    A service for interacting with FHIR Terminology Servers.

    Provides operations for:
    - Code validation ($validate-code)
    - Code lookup ($lookup)
    - Value set expansion ($expand)
    - Code translation ($translate)
    - Subsumption testing ($subsumes)

    Example:
        >>> client = FHIRClient("https://tx.fhir.org/r4")
        >>> terminology = TerminologyService(client)
        >>> result = terminology.lookup_code("http://loinc.org", "29463-7")
        >>> print(result.get("display"))  # "Body weight"
    """

    # Common code systems
    CODE_SYSTEMS = {
        "snomed": "http://snomed.info/sct",
        "loinc": "http://loinc.org",
        "icd10": "http://hl7.org/fhir/sid/icd-10",
        "icd10cm": "http://hl7.org/fhir/sid/icd-10-cm",
        "rxnorm": "http://www.nlm.nih.gov/research/umls/rxnorm",
        "cpt": "http://www.ama-assn.org/go/cpt",
        "ucum": "http://unitsofmeasure.org",
        "ndc": "http://hl7.org/fhir/sid/ndc",
    }

    def __init__(self, client: FHIRClient):
        """
        Initialize Terminology Service.

        Args:
            client: A FHIRClient instance configured to connect to a terminology server
        """
        self.client = client
        logger.info("TerminologyService initialized")

    @classmethod
    def create_default(
        cls, terminology_server_url: str = "https://tx.fhir.org/r4"
    ) -> "TerminologyService":
        """
        Create a TerminologyService with default HL7 terminology server.

        Args:
            terminology_server_url: URL of the terminology server

        Returns:
            Configured TerminologyService instance
        """
        client = FHIRClient(terminology_server_url)
        return cls(client)

    def get_code_system_url(self, code_system: str) -> str:
        """
        Get the full URL for a code system alias.

        Args:
            code_system: Either a full URL or alias (e.g., "snomed", "loinc")

        Returns:
            Full code system URL
        """
        return self.CODE_SYSTEMS.get(code_system.lower(), code_system)

    # ==================== $validate-code ====================

    def validate_code(
        self,
        code: str,
        system: str,
        display: Optional[str] = None,
        value_set_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Validate that a code exists in a code system or value set.

        This operation checks if a given code is valid within its code system
        and optionally within a specific value set.

        Args:
            code: The code to validate (e.g., "29463-7")
            system: The code system URL or alias (e.g., "loinc" or "http://loinc.org")
            display: Optional display name to validate
            value_set_url: Optional value set to validate against

        Returns:
            Validation result with 'result' (bool) and optional 'message'

        Example:
            >>> result = terminology.validate_code("29463-7", "loinc")
            >>> if result.get("parameter"):
            ...     for param in result["parameter"]:
            ...         if param["name"] == "result":
            ...             print(f"Valid: {param['valueBoolean']}")
        """
        system_url = self.get_code_system_url(system)

        params = {
            "code": code,
            "system": system_url,
        }

        if display:
            params["display"] = display
        if value_set_url:
            params["url"] = value_set_url

        endpoint = (
            "CodeSystem/$validate-code"
            if not value_set_url
            else "ValueSet/$validate-code"
        )

        try:
            result = self.client._make_request("GET", endpoint, params=params)
            logger.info(f"Validated code {code} in system {system_url}")
            return result
        except FHIRClientError as e:
            logger.error(f"Code validation failed: {e}")
            raise

    def is_valid_code(self, code: str, system: str) -> bool:
        """
        Simple check if a code is valid in a code system.

        Args:
            code: The code to validate
            system: The code system URL or alias

        Returns:
            True if code is valid, False otherwise
        """
        try:
            result = self.validate_code(code, system)
            for param in result.get("parameter", []):
                if param.get("name") == "result":
                    return param.get("valueBoolean", False)
            return False
        except Exception:
            return False

    # ==================== $lookup ====================

    def lookup_code(
        self,
        system: str,
        code: str,
        properties: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Look up information about a code.

        Returns detailed information about a code including its display name,
        definition, and other properties.

        Args:
            system: The code system URL or alias (e.g., "snomed", "loinc")
            code: The code to look up
            properties: Optional list of specific properties to retrieve

        Returns:
            Parameters resource with code details (name, display, definition, etc.)

        Example:
            >>> result = terminology.lookup_code("loinc", "29463-7")
            >>> # Extract display name
            >>> for param in result.get("parameter", []):
            ...     if param["name"] == "display":
            ...         print(f"Display: {param['valueString']}")
        """
        system_url = self.get_code_system_url(system)

        params: Dict[str, Any] = {
            "system": system_url,
            "code": code,
        }

        if properties:
            params["property"] = properties

        try:
            result = self.client._make_request(
                "GET", "CodeSystem/$lookup", params=params
            )
            logger.info(f"Looked up code {code} in system {system_url}")
            return result
        except FHIRClientError as e:
            logger.error(f"Code lookup failed: {e}")
            raise

    def get_display_name(self, system: str, code: str) -> Optional[str]:
        """
        Get the display name for a code.

        Args:
            system: The code system URL or alias
            code: The code to look up

        Returns:
            Display name string or None if not found
        """
        try:
            result = self.lookup_code(system, code)
            for param in result.get("parameter", []):
                if param.get("name") == "display":
                    return param.get("valueString")
            return None
        except Exception:
            return None

    # ==================== $expand ====================

    def expand_value_set(
        self,
        value_set_url: Optional[str] = None,
        value_set_id: Optional[str] = None,
        filter_text: Optional[str] = None,
        offset: int = 0,
        count: int = 100,
    ) -> Dict[str, Any]:
        """
        Expand a value set to get all its codes.

        This operation takes a value set and returns its expansion - the list
        of codes that are in the value set.

        Args:
            value_set_url: The canonical URL of the value set
            value_set_id: The resource ID of the value set (alternative to URL)
            filter_text: Optional text filter to search within the expansion
            offset: Starting index for pagination (default: 0)
            count: Maximum number of codes to return (default: 100)

        Returns:
            ValueSet resource with expansion containing codes

        Example:
            >>> # Expand a value set
            >>> result = terminology.expand_value_set(
            ...     value_set_url="http://hl7.org/fhir/ValueSet/observation-codes"
            ... )
            >>> for code in result.get("expansion", {}).get("contains", []):
            ...     print(f"{code['code']}: {code['display']}")
        """
        params: Dict[str, Any] = {}

        if value_set_url:
            params["url"] = value_set_url
        if filter_text:
            params["filter"] = filter_text
        if offset > 0:
            params["offset"] = offset
        if count != 100:
            params["count"] = count

        endpoint = (
            f"ValueSet/{value_set_id}/$expand" if value_set_id else "ValueSet/$expand"
        )

        try:
            result = self.client._make_request("GET", endpoint, params=params)
            logger.info(f"Expanded value set: {value_set_url or value_set_id}")
            return result
        except FHIRClientError as e:
            logger.error(f"Value set expansion failed: {e}")
            raise

    def search_value_set(
        self,
        value_set_url: str,
        search_text: str,
        max_results: int = 20,
    ) -> List[Dict[str, str]]:
        """
        Search for codes within a value set.

        Args:
            value_set_url: The value set to search in
            search_text: Text to search for
            max_results: Maximum number of results

        Returns:
            List of matching codes with their details
        """
        try:
            result = self.expand_value_set(
                value_set_url=value_set_url, filter_text=search_text, count=max_results
            )
            return result.get("expansion", {}).get("contains", [])
        except Exception:
            return []

    # ==================== $translate ====================

    def translate_code(
        self,
        code: str,
        source_system: str,
        target_system: str,
        concept_map_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Translate a code from one code system to another.

        Uses concept maps to translate between code systems (e.g., ICD-10 to SNOMED CT).

        Args:
            code: The code to translate
            source_system: Source code system URL or alias
            target_system: Target code system URL or alias
            concept_map_url: Optional URL of a specific concept map to use

        Returns:
            Parameters resource with translation results

        Example:
            >>> # Translate from ICD-10 to SNOMED
            >>> result = terminology.translate_code(
            ...     code="I10",
            ...     source_system="icd10",
            ...     target_system="snomed"
            ... )
        """
        source_url = self.get_code_system_url(source_system)
        target_url = self.get_code_system_url(target_system)

        params = {
            "code": code,
            "system": source_url,
            "targetSystem": target_url,
        }

        if concept_map_url:
            params["url"] = concept_map_url

        try:
            result = self.client._make_request(
                "GET", "ConceptMap/$translate", params=params
            )
            logger.info(
                f"Translated code {code} from {source_system} to {target_system}"
            )
            return result
        except FHIRClientError as e:
            logger.error(f"Code translation failed: {e}")
            raise

    # ==================== $subsumes ====================

    def check_subsumption(
        self,
        code_a: str,
        code_b: str,
        system: str,
    ) -> Dict[str, Any]:
        """
        Check if one code subsumes another (hierarchical relationship).

        Determines if code_a is a parent/ancestor of code_b in the code system hierarchy.

        Args:
            code_a: The first code (potential parent)
            code_b: The second code (potential child)
            system: The code system URL or alias

        Returns:
            Parameters resource with 'outcome' parameter:
            - "equivalent": codes are the same
            - "subsumes": code_a subsumes code_b (code_a is parent)
            - "subsumed-by": code_a is subsumed by code_b (code_b is parent)
            - "not-subsumed": no subsumption relationship

        Example:
            >>> # Check if "Heart disease" subsumes "Acute myocardial infarction"
            >>> result = terminology.check_subsumption(
            ...     code_a="56265001",  # Heart disease
            ...     code_b="22298006",  # Acute MI
            ...     system="snomed"
            ... )
        """
        system_url = self.get_code_system_url(system)

        params = {
            "codeA": code_a,
            "codeB": code_b,
            "system": system_url,
        }

        try:
            result = self.client._make_request(
                "GET", "CodeSystem/$subsumes", params=params
            )
            logger.info(f"Checked subsumption between {code_a} and {code_b}")
            return result
        except FHIRClientError as e:
            logger.error(f"Subsumption check failed: {e}")
            raise

    # ==================== Utility Methods ====================

    def get_value_set(self, value_set_id: str) -> Dict[str, Any]:
        """
        Retrieve a value set resource by ID.

        Args:
            value_set_id: The ID of the value set

        Returns:
            ValueSet resource
        """
        return self.client.read_resource("ValueSet", value_set_id)

    def get_code_system(self, code_system_id: str) -> Dict[str, Any]:
        """
        Retrieve a code system resource by ID.

        Args:
            code_system_id: The ID of the code system

        Returns:
            CodeSystem resource
        """
        return self.client.read_resource("CodeSystem", code_system_id)

    def search_code_systems(
        self,
        name: Optional[str] = None,
        title: Optional[str] = None,
        url: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for code systems.

        Args:
            name: Search by name
            title: Search by title
            url: Search by canonical URL

        Returns:
            List of matching CodeSystem resources
        """
        params = {}
        if name:
            params["name"] = name
        if title:
            params["title"] = title
        if url:
            params["url"] = url

        result = self.client.search("CodeSystem", params)
        return result.get("entry", [])

    def search_value_sets(
        self,
        name: Optional[str] = None,
        title: Optional[str] = None,
        url: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for value sets.

        Args:
            name: Search by name
            title: Search by title
            url: Search by canonical URL

        Returns:
            List of matching ValueSet resources
        """
        params = {}
        if name:
            params["name"] = name
        if title:
            params["title"] = title
        if url:
            params["url"] = url

        result = self.client.search("ValueSet", params)
        return result.get("entry", [])
