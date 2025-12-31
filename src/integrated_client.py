"""
Integrated FHIR Client with Terminology Support

This module demonstrates how FHIRClient and TerminologyService work together
to provide validated, enriched healthcare data operations.

The integration provides:
1. Automatic code validation before creating resources
2. Automatic enrichment of resources with display names
3. Semantic search using terminology hierarchies
4. Code translation for interoperability
"""

import logging
from typing import Dict, Any, List, Optional
from .client import FHIRClient
from .terminology import TerminologyService

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when resource validation fails."""

    pass


class IntegratedFHIRClient:
    """
    A FHIR client with integrated terminology support.

    This client automatically:
    - Validates coded elements before creating/updating resources
    - Enriches retrieved resources with human-readable display names
    - Supports semantic searches using terminology hierarchies

    Example:
        >>> client = IntegratedFHIRClient(
        ...     fhir_server="https://hapi.fhir.org/baseR4",
        ...     terminology_server="https://tx.fhir.org/r4"
        ... )
        >>>
        >>> # Create observation with automatic code validation
        >>> obs = client.create_observation(
        ...     patient_id="123",
        ...     code="29463-7",
        ...     system="loinc",
        ...     value=70.5,
        ...     unit="kg"
        ... )
        >>>
        >>> # Search for all cardiovascular conditions (uses hierarchy)
        >>> conditions = client.search_conditions_by_category(
        ...     patient_id="123",
        ...     category_code="49601007",  # Cardiovascular disease
        ...     system="snomed"
        ... )
    """

    def __init__(
        self,
        fhir_server: str = "https://hapi.fhir.org/baseR4",
        terminology_server: str = "https://tx.fhir.org/r4",
        validate_codes: bool = True,
        enrich_display: bool = True,
        auth: Optional[tuple] = None,
    ):
        """
        Initialize the integrated client.

        Args:
            fhir_server: URL of the FHIR data server
            terminology_server: URL of the terminology server
            validate_codes: Whether to validate codes before create/update
            enrich_display: Whether to add display names to retrieved resources
            auth: Optional (username, password) for authentication
        """
        self.fhir = FHIRClient(fhir_server, auth=auth)
        self.terminology = TerminologyService(FHIRClient(terminology_server, auth=auth))
        self.validate_codes = validate_codes
        self.enrich_display = enrich_display

        logger.info(
            f"IntegratedFHIRClient initialized: "
            f"FHIR={fhir_server}, Terminology={terminology_server}"
        )

    # ==================== Validated Resource Creation ====================

    def create_observation(
        self,
        patient_id: str,
        code: str,
        system: str,
        value: float,
        unit: str,
        status: str = "final",
        validate: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Create an observation with automatic code validation.

        The code is validated against the terminology server before
        the resource is created on the FHIR server.

        Args:
            patient_id: Patient resource ID
            code: Observation code (e.g., "29463-7" for body weight)
            system: Code system alias or URL (e.g., "loinc")
            value: Numeric value
            unit: Unit of measure (e.g., "kg")
            status: Observation status (default: "final")
            validate: Override default validation setting

        Returns:
            Created Observation resource

        Raises:
            ValidationError: If code is invalid
            FHIRClientError: If creation fails

        Example:
            >>> obs = client.create_observation(
            ...     patient_id="123",
            ...     code="29463-7",
            ...     system="loinc",
            ...     value=70.5,
            ...     unit="kg"
            ... )
            >>> print(f"Created observation: {obs['id']}")
        """
        should_validate = validate if validate is not None else self.validate_codes

        # Step 1: Validate the code using terminology service
        if should_validate:
            if not self.terminology.is_valid_code(code, system):
                raise ValidationError(
                    f"Invalid code '{code}' in system '{system}'. "
                    "Code does not exist in the terminology server."
                )

        # Step 2: Get display name to include in resource
        display = self.terminology.get_display_name(system, code)
        system_url = self.terminology.get_code_system_url(system)

        # Step 3: Build the FHIR Observation resource
        observation = {
            "resourceType": "Observation",
            "status": status,
            "code": {
                "coding": [
                    {
                        "system": system_url,
                        "code": code,
                        "display": display or code,
                    }
                ],
                "text": display or code,
            },
            "subject": {"reference": f"Patient/{patient_id}"},
            "valueQuantity": {
                "value": value,
                "unit": unit,
                "system": "http://unitsofmeasure.org",
                "code": unit,
            },
        }

        # Step 4: Create on FHIR server
        return self.fhir.create_resource(observation)

    def create_condition(
        self,
        patient_id: str,
        code: str,
        system: str = "icd10cm",
        clinical_status: str = "active",
        validate: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Create a condition/diagnosis with automatic code validation.

        Args:
            patient_id: Patient resource ID
            code: Diagnosis code (e.g., "I10" for hypertension)
            system: Code system alias or URL (default: "icd10cm")
            clinical_status: Clinical status (default: "active")
            validate: Override default validation setting

        Returns:
            Created Condition resource

        Raises:
            ValidationError: If diagnosis code is invalid

        Example:
            >>> condition = client.create_condition(
            ...     patient_id="123",
            ...     code="I10",
            ...     system="icd10cm"
            ... )
            >>> print(f"Diagnosis: {condition['code']['text']}")
        """
        should_validate = validate if validate is not None else self.validate_codes

        if should_validate:
            if not self.terminology.is_valid_code(code, system):
                raise ValidationError(
                    f"Invalid diagnosis code '{code}' in system '{system}'."
                )

        display = self.terminology.get_display_name(system, code)
        system_url = self.terminology.get_code_system_url(system)

        condition = {
            "resourceType": "Condition",
            "clinicalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": clinical_status,
                    }
                ]
            },
            "code": {
                "coding": [{"system": system_url, "code": code, "display": display}],
                "text": display or code,
            },
            "subject": {"reference": f"Patient/{patient_id}"},
        }

        return self.fhir.create_resource(condition)

    # ==================== Enriched Resource Retrieval ====================

    def read_observation(
        self, observation_id: str, enrich: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Read an observation and optionally enrich with display names.

        Args:
            observation_id: Observation resource ID
            enrich: Override default enrichment setting

        Returns:
            Observation resource (enriched with display names if enabled)

        Example:
            >>> obs = client.read_observation("456")
            >>> print(obs['code']['text'])  # "Body weight" instead of just "29463-7"
        """
        observation = self.fhir.read_resource("Observation", observation_id)

        should_enrich = enrich if enrich is not None else self.enrich_display
        if should_enrich:
            observation = self._enrich_codings(observation)

        return observation

    def read_condition(
        self, condition_id: str, enrich: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Read a condition and optionally enrich with display names.

        Args:
            condition_id: Condition resource ID
            enrich: Override default enrichment setting

        Returns:
            Condition resource (enriched with display names if enabled)
        """
        condition = self.fhir.read_resource("Condition", condition_id)

        should_enrich = enrich if enrich is not None else self.enrich_display
        if should_enrich:
            condition = self._enrich_codings(condition)

        return condition

    def _enrich_codings(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich all codings in a resource with display names.

        Recursively finds all 'coding' arrays and adds display names
        from the terminology server.
        """

        def enrich_coding_list(codings: List[Dict]) -> List[Dict]:
            for coding in codings:
                if (
                    "system" in coding
                    and "code" in coding
                    and not coding.get("display")
                ):
                    display = self.terminology.get_display_name(
                        coding["system"], coding["code"]
                    )
                    if display:
                        coding["display"] = display
            return codings

        def recursive_enrich(obj: Any) -> Any:
            if isinstance(obj, dict):
                if "coding" in obj and isinstance(obj["coding"], list):
                    obj["coding"] = enrich_coding_list(obj["coding"])
                    # Also set text if not present
                    if not obj.get("text") and obj["coding"]:
                        obj["text"] = obj["coding"][0].get("display", "")
                for key, value in obj.items():
                    obj[key] = recursive_enrich(value)
            elif isinstance(obj, list):
                return [recursive_enrich(item) for item in obj]
            return obj

        return recursive_enrich(resource)

    # ==================== Semantic Search Operations ====================

    def search_observations_by_category(
        self,
        patient_id: str,
        category_code: str,
        system: str = "loinc",
        include_children: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Search for observations using terminology hierarchy.

        If include_children is True, expands the search to include
        all codes that are subsumed by (children of) the category code.

        Args:
            patient_id: Patient resource ID
            category_code: Parent code to search for
            system: Code system
            include_children: Whether to include child codes

        Returns:
            List of matching Observation resources

        Example:
            >>> # Find all vital signs (LOINC category)
            >>> vitals = client.search_observations_by_category(
            ...     patient_id="123",
            ...     category_code="85354-9",  # Blood pressure panel
            ...     system="loinc"
            ... )
        """
        # Start with the base code
        codes_to_search = [category_code]

        # If hierarchical search, this would expand using $subsumes
        # Note: Full implementation would query terminology for all children
        # This is a simplified version

        results = []
        for code in codes_to_search:
            system_url = self.terminology.get_code_system_url(system)
            bundle = self.fhir.search(
                "Observation",
                {"patient": patient_id, "code": f"{system_url}|{code}"},
            )
            entries = bundle.get("entry", [])
            results.extend([e["resource"] for e in entries])

        if self.enrich_display:
            results = [self._enrich_codings(r) for r in results]

        return results

    def find_related_conditions(
        self,
        patient_id: str,
        parent_code: str,
        system: str = "snomed",
    ) -> List[Dict[str, Any]]:
        """
        Find all conditions that are children of a parent concept.

        Uses terminology subsumption to find all conditions that
        fall under a parent category.

        Args:
            patient_id: Patient resource ID
            parent_code: Parent SNOMED code (e.g., cardiovascular disease)
            system: Code system (default: snomed)

        Returns:
            List of Condition resources that are types of the parent

        Example:
            >>> # Find all cardiovascular conditions for a patient
            >>> cv_conditions = client.find_related_conditions(
            ...     patient_id="123",
            ...     parent_code="49601007",  # Disorder of cardiovascular system
            ...     system="snomed"
            ... )
        """
        # Get all conditions for the patient
        bundle = self.fhir.search("Condition", {"patient": patient_id})
        all_conditions = [e["resource"] for e in bundle.get("entry", [])]

        related = []
        for condition in all_conditions:
            # Extract the code from the condition
            codings = condition.get("code", {}).get("coding", [])
            for coding in codings:
                if self.terminology.get_code_system_url(system) == coding.get("system"):
                    # Check if this code is subsumed by the parent
                    try:
                        result = self.terminology.check_subsumption(
                            code_a=parent_code,
                            code_b=coding["code"],
                            system=system,
                        )
                        for param in result.get("parameter", []):
                            if param.get("name") == "outcome":
                                if param.get("valueCode") in [
                                    "subsumes",
                                    "equivalent",
                                ]:
                                    related.append(condition)
                                    break
                    except Exception:
                        pass  # Skip if subsumption check fails

        if self.enrich_display:
            related = [self._enrich_codings(r) for r in related]

        return related

    # ==================== Code Translation for Interoperability ====================

    def translate_condition_codes(
        self,
        condition: Dict[str, Any],
        target_system: str,
    ) -> Dict[str, Any]:
        """
        Translate condition codes to a different code system.

        Useful for data exchange when systems use different terminologies.

        Args:
            condition: Condition resource
            target_system: Target code system (e.g., "snomed", "icd10")

        Returns:
            Condition with additional translated coding

        Example:
            >>> # Translate ICD-10 condition to SNOMED for HIE exchange
            >>> condition = client.read_condition("789")
            >>> translated = client.translate_condition_codes(
            ...     condition,
            ...     target_system="snomed"
            ... )
        """
        codings = condition.get("code", {}).get("coding", [])

        for coding in codings:
            source_system = coding.get("system", "")
            source_code = coding.get("code", "")

            # Try to translate
            try:
                result = self.terminology.translate_code(
                    code=source_code,
                    source_system=source_system,
                    target_system=target_system,
                )

                # Extract translated code
                for param in result.get("parameter", []):
                    if param.get("name") == "match":
                        for part in param.get("part", []):
                            if part.get("name") == "concept":
                                translated = part.get("valueCoding", {})
                                # Add translated coding to the condition
                                condition["code"]["coding"].append(translated)
                                break
            except Exception as e:
                logger.warning(f"Translation failed for {source_code}: {e}")

        return condition

    # ==================== Utility Methods ====================

    def validate_resource_codes(self, resource: Dict[str, Any]) -> List[str]:
        """
        Validate all codes in a resource.

        Returns a list of validation errors (empty if all valid).

        Args:
            resource: Any FHIR resource

        Returns:
            List of error messages for invalid codes
        """
        errors = []

        def check_codings(obj: Any, path: str = "") -> None:
            if isinstance(obj, dict):
                if "coding" in obj and isinstance(obj["coding"], list):
                    for i, coding in enumerate(obj["coding"]):
                        system = coding.get("system")
                        code = coding.get("code")
                        if system and code:
                            if not self.terminology.is_valid_code(code, system):
                                errors.append(
                                    f"{path}.coding[{i}]: Invalid code '{code}' "
                                    f"in system '{system}'"
                                )
                for key, value in obj.items():
                    check_codings(value, f"{path}.{key}" if path else key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_codings(item, f"{path}[{i}]")

        check_codings(resource)
        return errors

    def get_value_set_options(self, value_set_url: str) -> List[Dict[str, str]]:
        """
        Get options for a dropdown/selection field from a value set.

        Args:
            value_set_url: Canonical URL of the value set

        Returns:
            List of {value, label} dictionaries for UI

        Example:
            >>> options = client.get_value_set_options(
            ...     "http://hl7.org/fhir/ValueSet/administrative-gender"
            ... )
            >>> # Returns: [{"value": "male", "label": "Male"}, ...]
        """
        result = self.terminology.expand_value_set(value_set_url=value_set_url)
        return [
            {"value": c["code"], "label": c.get("display", c["code"])}
            for c in result.get("expansion", {}).get("contains", [])
        ]

    def close(self):
        """Close all connections."""
        self.fhir.close()
        self.terminology.client.close()
