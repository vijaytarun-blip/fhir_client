"""
FHIR Observation resource model and helper functions.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime


class Observation:
    """Helper class for creating and validating FHIR Observation resources."""
    
    @staticmethod
    def create(
        patient_reference: str,
        code: Dict[str, Any],
        value: Any,
        status: str = "final",
        effective_datetime: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a FHIR Observation resource.
        
        Args:
            patient_reference: Reference to patient (e.g., "Patient/123")
            code: Observation code with system and code
            value: Observation value (Quantity, string, etc.)
            status: Observation status (registered, preliminary, final, amended)
            effective_datetime: When observation was made (ISO 8601 format)
            **kwargs: Additional FHIR Observation fields
            
        Returns:
            Dictionary representing a FHIR Observation resource
        """
        observation = {
            "resourceType": "Observation",
            "status": status,
            "code": code,
            "subject": {
                "reference": patient_reference
            }
        }
        
        # Add value based on type
        if isinstance(value, dict) and "value" in value and "unit" in value:
            observation["valueQuantity"] = value
        elif isinstance(value, str):
            observation["valueString"] = value
        elif isinstance(value, bool):
            observation["valueBoolean"] = value
        else:
            observation["valueQuantity"] = value
        
        if effective_datetime:
            observation["effectiveDateTime"] = effective_datetime
        else:
            observation["effectiveDateTime"] = datetime.utcnow().isoformat() + "Z"
        
        # Add any additional fields
        observation.update(kwargs)
        
        return observation
    
    @staticmethod
    def create_vital_sign(
        patient_reference: str,
        vital_type: str,
        value: float,
        unit: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a vital sign observation (shorthand method).
        
        Args:
            patient_reference: Reference to patient
            vital_type: Type of vital sign (heart_rate, blood_pressure, temperature, etc.)
            value: Numeric value
            unit: Unit of measure
            **kwargs: Additional fields
            
        Returns:
            FHIR Observation resource
        """
        # Standard LOINC codes for common vital signs
        vital_codes = {
            "heart_rate": {"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"},
            "blood_pressure_systolic": {"system": "http://loinc.org", "code": "8480-6", "display": "Systolic blood pressure"},
            "blood_pressure_diastolic": {"system": "http://loinc.org", "code": "8462-4", "display": "Diastolic blood pressure"},
            "temperature": {"system": "http://loinc.org", "code": "8310-5", "display": "Body temperature"},
            "respiratory_rate": {"system": "http://loinc.org", "code": "9279-1", "display": "Respiratory rate"},
            "oxygen_saturation": {"system": "http://loinc.org", "code": "2708-6", "display": "Oxygen saturation"},
        }
        
        code_data = vital_codes.get(vital_type, {
            "system": "http://loinc.org",
            "code": "unknown",
            "display": vital_type
        })
        
        code = {
            "coding": [code_data],
            "text": code_data.get("display", vital_type)
        }
        
        value_quantity = {
            "value": value,
            "unit": unit,
            "system": "http://unitsofmeasure.org",
            "code": unit
        }
        
        return Observation.create(
            patient_reference=patient_reference,
            code=code,
            value=value_quantity,
            category=[{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "vital-signs",
                    "display": "Vital Signs"
                }]
            }],
            **kwargs
        )
    
    @staticmethod
    def validate(resource: Dict[str, Any]) -> bool:
        """
        Validate an Observation resource.
        
        Args:
            resource: Observation resource dictionary
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If validation fails
        """
        if resource.get("resourceType") != "Observation":
            raise ValueError("Resource must be of type Observation")
        
        if "status" not in resource:
            raise ValueError("Observation must have a status")
        
        if "code" not in resource:
            raise ValueError("Observation must have a code")
        
        return True
