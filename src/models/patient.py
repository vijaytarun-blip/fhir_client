"""
FHIR Patient resource model and helper functions.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime


class Patient:
    """Helper class for creating and validating FHIR Patient resources."""
    
    @staticmethod
    def create(
        family_name: str,
        given_names: List[str],
        gender: Optional[str] = None,
        birth_date: Optional[str] = None,
        identifier: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a FHIR Patient resource.
        
        Args:
            family_name: Family name (surname)
            given_names: List of given names
            gender: Gender (male, female, other, unknown)
            birth_date: Birth date in YYYY-MM-DD format
            identifier: Patient identifier (system, value)
            **kwargs: Additional FHIR Patient fields
            
        Returns:
            Dictionary representing a FHIR Patient resource
        """
        patient = {
            "resourceType": "Patient",
            "name": [{
                "use": "official",
                "family": family_name,
                "given": given_names
            }]
        }
        
        if gender:
            patient["gender"] = gender
        
        if birth_date:
            patient["birthDate"] = birth_date
        
        if identifier:
            patient["identifier"] = [identifier]
        
        # Add any additional fields
        patient.update(kwargs)
        
        return patient
    
    @staticmethod
    def validate(resource: Dict[str, Any]) -> bool:
        """
        Validate a Patient resource has required fields.
        
        Args:
            resource: Patient resource dictionary
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If validation fails
        """
        if resource.get("resourceType") != "Patient":
            raise ValueError("Resource must be of type Patient")
        
        if "name" not in resource or not resource["name"]:
            raise ValueError("Patient must have at least one name")
        
        return True
    
    @staticmethod
    def get_full_name(patient: Dict[str, Any]) -> str:
        """
        Extract full name from Patient resource.
        
        Args:
            patient: Patient resource dictionary
            
        Returns:
            Full name as string
        """
        if not patient.get("name"):
            return "Unknown"
        
        name = patient["name"][0]
        given = " ".join(name.get("given", []))
        family = name.get("family", "")
        
        return f"{given} {family}".strip()
