"""
================================================================================
REAL USE CASE: Clinical Data Validation with Terminology Services
================================================================================

SCENARIO: Emergency Department - Data Quality at Point of Entry

This example demonstrates ACTUAL working functionality:
- Gender code validation against FHIR value sets
- LOINC code validation for vital signs observations
- ICD-10 diagnosis code validation
- Automatic display name enrichment
- SNOMED CT subsumption checking
- Code translation attempts (with realistic failure handling)

What this does NOT include:
- Clinical Decision Support (requires rule engine integration)
- Quality measure evaluation (requires value set implementation)
- Database operations (uses in-memory storage for demo)

================================================================================
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.integrated_client import IntegratedFHIRClient, ValidationError
from src.client import FHIRClientError


# ==============================================================================
# IN-MEMORY STORAGE (Replace with real database in production)
# ==============================================================================

class DataStore:
    """Simple in-memory storage for demonstration."""
    
    def __init__(self):
        self.patients = {}
        self.observations = {}
        self.conditions = {}
    
    def save_patient(self, patient: Dict) -> str:
        patient_id = f"PT-{len(self.patients) + 1001}"
        patient["id"] = patient_id
        self.patients[patient_id] = patient
        print(f"    ✓ Saved to data store: {patient_id}")
        return patient_id
    
    def save_observation(self, obs: Dict, patient_id: str) -> str:
        obs_id = f"OBS-{len(self.observations) + 5001}"
        obs["id"] = obs_id
        obs["patient_id"] = patient_id
        self.observations[obs_id] = obs
        return obs_id
    
    def save_condition(self, condition: Dict, patient_id: str) -> str:
        cond_id = f"DX-{len(self.conditions) + 3001}"
        condition["id"] = cond_id
        condition["patient_id"] = patient_id
        self.conditions[cond_id] = condition
        return cond_id
    
    def get_patient_conditions(self, patient_id: str) -> List[Dict]:
        return [
            c for c in self.conditions.values()
            if c.get("patient_id") == patient_id
        ]


# ==============================================================================
# TERMINOLOGY VALIDATION SYSTEM
# ==============================================================================

class TerminologyValidationSystem:
    """
    Clinical system with real-time terminology validation.
    
    All clinical codes are validated against standard terminology servers
    before being accepted into the system.
    """
    
    def __init__(self):
        print("\n" + "=" * 70)
        print("INITIALIZING TERMINOLOGY VALIDATION SYSTEM")
        print("=" * 70)
        
        self.client = IntegratedFHIRClient(
            fhir_server="https://hapi.fhir.org/baseR4",
            terminology_server="https://tx.fhir.org/r4",
            validate_codes=True,
            enrich_display=True,
        )
        
        self.store = DataStore()
        
        print("✓ System initialized")
        print("  - FHIR Server: hapi.fhir.org")
        print("  - Terminology Server: tx.fhir.org (HL7 Official)")
        print("  - Real-time Validation: ENABLED")
        print("  - Display Enrichment: ENABLED")
    
    # ==========================================================================
    # PATIENT REGISTRATION WITH GENDER VALIDATION
    # ==========================================================================
    
    def register_patient(
        self,
        first_name: str,
        last_name: str,
        birth_date: str,
        gender: str,
        mrn: str,
    ) -> Optional[str]:
        """
        Register patient with validated gender code.
        
        REAL VALIDATION: Gender code is validated against FHIR administrative-gender
        value set via $expand operation to tx.fhir.org.
        """
        print("\n" + "-" * 70)
        print("USE CASE 1: PATIENT REGISTRATION")
        print("-" * 70)
        print(f"  Registering: {first_name} {last_name}")
        print(f"  Gender code to validate: '{gender}'")
        
        print(f"\n  [Real API Call] Expanding administrative-gender value set...")
        
        try:
            valid_genders = self.client.get_value_set_options(
                "http://hl7.org/fhir/ValueSet/administrative-gender"
            )
            valid_codes = [opt["value"] for opt in valid_genders]
            
            print(f"    Valid options from server: {valid_codes}")
            
            if gender not in valid_codes:
                print(f"  ✗ VALIDATION FAILED: '{gender}' not in value set")
                print(f"    Data rejected - cannot proceed with registration")
                return None
            
            gender_display = next(
                (opt["label"] for opt in valid_genders if opt["value"] == gender),
                gender
            )
            print(f"  ✓ VALIDATION PASSED: {gender} = {gender_display}")
            
        except Exception as e:
            print(f"  ✗ Validation error: {e}")
            return None
        
        patient = {
            "resourceType": "Patient",
            "identifier": [{"system": "http://hospital.org/mrn", "value": mrn}],
            "name": [{"family": last_name, "given": [first_name]}],
            "birthDate": birth_date,
            "gender": gender,
            "_gender_display": gender_display,
        }
        
        patient_id = self.store.save_patient(patient)
        print(f"\n  ✓ Patient registered successfully")
        
        return patient_id
    
    # ==========================================================================
    # VITAL SIGNS WITH LOINC VALIDATION
    # ==========================================================================
    
    def record_vital_sign(
        self,
        patient_id: str,
        loinc_code: str,
        value: float,
        unit: str,
        expected_name: str,
    ) -> Optional[str]:
        """
        Record a single vital sign with LOINC code validation.
        
        REAL VALIDATION: Each LOINC code is validated via $validate-code
        operation to tx.fhir.org. Display names are fetched via $lookup.
        """
        print(f"\n  Recording: {expected_name}")
        print(f"    LOINC code: {loinc_code}")
        print(f"    Value: {value} {unit}")
        
        print(f"\n    [Real API Call] Validating LOINC code via $validate-code...")
        
        try:
            # Real validation
            if not self.client.terminology.is_valid_code(loinc_code, "loinc"):
                print(f"    ✗ VALIDATION FAILED: Invalid LOINC code")
                print(f"    Data rejected - observation not recorded")
                return None
            
            print(f"    ✓ Code validated successfully")
            
            # Real display name lookup
            print(f"    [Real API Call] Fetching display name via $lookup...")
            display = self.client.terminology.get_display_name("loinc", loinc_code)
            print(f"    Official name: {display}")
            
        except Exception as e:
            print(f"    ✗ Validation error: {e}")
            return None
        
        obs = {
            "resourceType": "Observation",
            "status": "final",
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": loinc_code,
                    "display": display,
                }],
                "text": display,
            },
            "valueQuantity": {
                "value": value,
                "unit": unit,
                "system": "http://unitsofmeasure.org",
            },
            "effectiveDateTime": datetime.now().isoformat(),
        }
        
        obs_id = self.store.save_observation(obs, patient_id)
        print(f"    ✓ Observation saved: {obs_id}")
        
        return obs_id
    
    def record_vital_signs(self, patient_id: str) -> List[str]:
        """Record multiple vital signs with validation."""
        print("\n" + "-" * 70)
        print("USE CASE 2: VITAL SIGNS WITH LOINC VALIDATION")
        print("-" * 70)
        print(f"  Patient: {patient_id}")
        
        vitals = [
            ("8867-4", 102, "/min", "Heart Rate"),
            ("8480-6", 168, "mm[Hg]", "Systolic Blood Pressure"),
            ("8462-4", 95, "mm[Hg]", "Diastolic Blood Pressure"),
            ("8310-5", 37.2, "Cel", "Body Temperature"),
            ("9279-1", 20, "/min", "Respiratory Rate"),
        ]
        
        recorded_ids = []
        
        for code, value, unit, name in vitals:
            obs_id = self.record_vital_sign(patient_id, code, value, unit, name)
            if obs_id:
                recorded_ids.append(obs_id)
        
        print(f"\n  ✓ {len(recorded_ids)}/{len(vitals)} vital signs recorded")
        return recorded_ids
    
    # ==========================================================================
    # DIAGNOSIS WITH ICD-10 VALIDATION
    # ==========================================================================
    
    def record_diagnosis(
        self,
        patient_id: str,
        icd10_code: str,
        description: str = "",
    ) -> Optional[str]:
        """
        Record diagnosis with ICD-10 code validation.
        
        REAL VALIDATION: ICD-10 code validated via $validate-code operation.
        Invalid codes are REJECTED at point of entry.
        """
        print(f"\n  Attempting to record diagnosis: {icd10_code}")
        if description:
            print(f"    Expected: {description}")
        
        print(f"\n    [Real API Call] Validating ICD-10 code via $validate-code...")
        
        try:
            if not self.client.terminology.is_valid_code(icd10_code, "icd10"):
                print(f"    ✗ VALIDATION FAILED: Code does not exist in ICD-10")
                print(f"    Data rejected - diagnosis not recorded")
                return None
            
            print(f"    ✓ Code validated successfully")
            
            print(f"    [Real API Call] Fetching display name via $lookup...")
            display = self.client.terminology.get_display_name("icd10", icd10_code)
            print(f"    Official name: {display}")
            
        except Exception as e:
            print(f"    ✗ Validation error: {e}")
            return None
        
        condition = {
            "resourceType": "Condition",
            "clinicalStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": "active",
                }]
            },
            "code": {
                "coding": [{
                    "system": "http://hl7.org/fhir/sid/icd-10",
                    "code": icd10_code,
                    "display": display,
                }],
                "text": display,
            },
            "recordedDate": datetime.now().isoformat(),
        }
        
        cond_id = self.store.save_condition(condition, patient_id)
        print(f"    ✓ Diagnosis saved: {cond_id}")
        
        return cond_id
    
    def record_diagnoses(self, patient_id: str):
        """Record multiple diagnoses including invalid ones."""
        print("\n" + "-" * 70)
        print("USE CASE 3: DIAGNOSIS VALIDATION")
        print("-" * 70)
        print(f"  Patient: {patient_id}")
        
        # Valid diagnosis
        self.record_diagnosis(patient_id, "I10", "Essential hypertension")
        
        # Another valid diagnosis
        self.record_diagnosis(patient_id, "R07.9", "Chest pain, unspecified")
        
        # Invalid diagnosis - will be rejected
        print("\n  --- Testing with invalid code ---")
        self.record_diagnosis(patient_id, "INVALID99", "Fake diagnosis code")
        
        conditions = self.store.get_patient_conditions(patient_id)
        print(f"\n  ✓ Total diagnoses accepted: {len(conditions)}")
    
    # ==========================================================================
    # SNOMED SUBSUMPTION CHECKING
    # ==========================================================================
    
    def demonstrate_snomed_hierarchy(self):
        """
        Demonstrate SNOMED CT subsumption checking.
        
        REAL OPERATION: Uses $subsumes operation to check if one SNOMED concept
        is a subtype of another in the terminology hierarchy.
        """
        print("\n" + "-" * 70)
        print("USE CASE 4: SNOMED CT HIERARCHY CHECKING")
        print("-" * 70)
        print("  Checking if 'Hypertensive disorder' is a type of 'Cardiovascular disease'")
        
        parent_code = "49601007"  # Disorder of cardiovascular system
        child_code = "38341003"   # Hypertensive disorder
        
        print(f"\n  Parent concept: {parent_code} (Cardiovascular disease)")
        print(f"  Child concept: {child_code} (Hypertensive disorder)")
        
        print(f"\n  [Real API Call] Checking subsumption via $subsumes operation...")
        
        try:
            result = self.client.terminology.check_subsumption(
                code_a=parent_code,
                code_b=child_code,
                system="snomed"
            )
            
            for param in result.get("parameter", []):
                if param.get("name") == "outcome":
                    outcome = param.get("valueCode")
                    print(f"\n  Result: {outcome}")
                    
                    if outcome == "subsumes":
                        print(f"  ✓ Confirmed: Hypertension IS a cardiovascular condition")
                        print(f"    This is determined by the SNOMED CT ontology")
                    elif outcome == "subsumed-by":
                        print(f"  ✓ Parent/child relationship reversed")
                    else:
                        print(f"  ✗ No hierarchical relationship found")
                        
        except Exception as e:
            print(f"  ✗ Subsumption check failed: {e}")
    
    # ==========================================================================
    # CODE TRANSLATION (WITH REALISTIC FAILURE HANDLING)
    # ==========================================================================
    
    def demonstrate_code_translation(self, patient_id: str):
        """
        Demonstrate code translation between systems.
        
        REAL OPERATION: Uses $translate operation, but with realistic
        expectation that mappings often don't exist.
        """
        print("\n" + "-" * 70)
        print("USE CASE 5: CODE TRANSLATION (ICD-10 → SNOMED CT)")
        print("-" * 70)
        print(f"  Patient: {patient_id}")
        print("  Attempting to translate diagnosis codes for interoperability")
        
        conditions = self.store.get_patient_conditions(patient_id)
        
        for condition in conditions:
            icd_code = condition.get("code", {}).get("coding", [{}])[0].get("code", "")
            icd_display = condition.get("code", {}).get("text", "")
            
            print(f"\n  Source: ICD-10 {icd_code} ({icd_display})")
            print(f"  [Real API Call] Attempting translation via $translate...")
            
            try:
                result = self.client.terminology.translate_code(
                    code=icd_code,
                    source_system="icd10",
                    target_system="snomed"
                )
                
                # Look for matches
                found_match = False
                for param in result.get("parameter", []):
                    if param.get("name") == "match":
                        for part in param.get("part", []):
                            if part.get("name") == "concept":
                                snomed = part.get("valueCoding", {})
                                print(f"  ✓ Translated to SNOMED CT:")
                                print(f"    Code: {snomed.get('code')}")
                                print(f"    Display: {snomed.get('display')}")
                                found_match = True
                                break
                
                if not found_match:
                    print(f"  ⚠️  No mapping found in ConceptMap")
                    print(f"     This is common - not all codes have translations")
                    
            except FHIRClientError as e:
                if "422" in str(e):
                    print(f"  ⚠️  Translation not available (HTTP 422)")
                    print(f"     ConceptMap may not exist for this code system pair")
                else:
                    print(f"  ✗ Translation failed: {e}")
    
    def close(self):
        """Clean up resources."""
        self.client.close()


# ==============================================================================
# MAIN DEMONSTRATION
# ==============================================================================

def main():
    """
    Demonstrate real terminology validation functionality.
    
    This shows ONLY what actually works via API calls to terminology servers.
    All validation is performed in real-time against tx.fhir.org.
    """
    
    print("=" * 70)
    print("  CLINICAL DATA VALIDATION WITH TERMINOLOGY SERVICES")
    print("  Demonstrating Real Working Functionality")
    print("=" * 70)
    print("""
    WHAT THIS DEMONSTRATES (All Real API Calls):
    
    ✓ Gender code validation via $expand operation
    ✓ LOINC code validation via $validate-code
    ✓ Display name enrichment via $lookup
    ✓ ICD-10 diagnosis validation via $validate-code
    ✓ SNOMED CT subsumption checking via $subsumes
    ✓ Code translation attempts via $translate
    
    WHAT THIS DOES NOT INCLUDE:
    
    ✗ Clinical Decision Support (requires rule engine)
    ✗ Quality Measure evaluation (requires value set implementation)
    ✗ Real database operations (uses in-memory storage)
    ✗ Clinical algorithms or business logic
    
    All validation calls go to: https://tx.fhir.org/r4
    """)
    
    system = TerminologyValidationSystem()
    
    try:
        # ==================================================================
        # USE CASE 1: Patient Registration
        # ==================================================================
        patient_id = system.register_patient(
            first_name="John",
            last_name="Smith",
            birth_date="1967-03-15",
            gender="male",
            mrn="MRN-2024-001234",
        )
        
        if not patient_id:
            print("\n❌ Cannot proceed - registration failed")
            return
        
        # ==================================================================
        # USE CASE 2: Vital Signs Recording
        # ==================================================================
        system.record_vital_signs(patient_id)
        
        # ==================================================================
        # USE CASE 3: Diagnosis Recording
        # ==================================================================
        system.record_diagnoses(patient_id)
        
        # ==================================================================
        # USE CASE 4: SNOMED Hierarchy Checking
        # ==================================================================
        system.demonstrate_snomed_hierarchy()
        
        # ==================================================================
        # USE CASE 5: Code Translation
        # ==================================================================
        system.demonstrate_code_translation(patient_id)
        
        # ==================================================================
        # SUMMARY
        # ==================================================================
        print("\n" + "=" * 70)
        print("DEMONSTRATION COMPLETE")
        print("=" * 70)
        
        print(f"""
    ✓ All operations used REAL API calls to terminology server
    ✓ Validations: {len(system.store.patients)} patients, 
                   {len(system.store.observations)} observations,
                   {len(system.store.conditions)} conditions
    
    KEY BENEFITS DEMONSTRATED:
    
    1. DATA QUALITY
       - Invalid codes rejected automatically at point of entry
       - No manual code lookup required
    
    2. STANDARDIZATION  
       - All codes validated against authoritative terminology servers
       - Display names enriched automatically
    
    3. SEMANTIC CAPABILITIES
       - SNOMED CT hierarchy enables intelligent classification
       - Subsumption checking supports clinical reasoning
    
    4. INTEROPERABILITY
       - Code translation attempted (when mappings exist)
       - Standards-based approach ensures compatibility
    
    PRODUCTION READINESS:
    - FHIRClient: Production-ready ✓
    - TerminologyService: Production-ready ✓  
    - IntegratedFHIRClient: Production-ready ✓
    - Clinical logic/CDS: Requires implementation
        """)
        
    finally:
        system.close()


if __name__ == "__main__":
    main()
