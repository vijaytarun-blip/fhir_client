"""
Integrated FHIR Client Example

This example demonstrates how the FHIRClient and TerminologyService
work together to provide validated, enriched healthcare data operations.

Key Integration Points:
1. Code validation before resource creation
2. Automatic enrichment with display names
3. Semantic search using terminology hierarchies
4. Code translation for interoperability
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.integrated_client import IntegratedFHIRClient, ValidationError


def main():
    """Demonstrate the integrated client capabilities."""

    print("=" * 70)
    print("INTEGRATED FHIR CLIENT DEMONSTRATION")
    print("Showing how FHIRClient + TerminologyService work together")
    print("=" * 70)

    # Initialize the integrated client
    client = IntegratedFHIRClient(
        fhir_server="https://hapi.fhir.org/baseR4",
        terminology_server="https://tx.fhir.org/r4",
        validate_codes=True,  # Validate codes before creating resources
        enrich_display=True,  # Add display names to retrieved resources
    )

    # =========================================================================
    # 1. CODE VALIDATION ON CREATE
    # =========================================================================
    print("\n" + "=" * 70)
    print("1. AUTOMATIC CODE VALIDATION")
    print("=" * 70)

    print("\nScenario: Create observation with VALID code (LOINC 29463-7)")
    print("-" * 50)

    # This will succeed - valid LOINC code
    try:
        # Note: In a real scenario, you'd have a real patient ID
        # For demo, we show the validation logic
        print("  Validating code '29463-7' in LOINC...")
        is_valid = client.terminology.is_valid_code("29463-7", "loinc")
        print(f"  ✓ Code is valid: {is_valid}")

        display = client.terminology.get_display_name("loinc", "29463-7")
        print(f"  ✓ Display name: {display}")
        print("  → Resource would be created with proper display name")

    except Exception as e:
        print(f"  ✗ Error: {e}")

    print("\nScenario: Create observation with INVALID code")
    print("-" * 50)

    # This will fail validation - invalid code
    try:
        print("  Validating code 'INVALID123' in LOINC...")
        is_valid = client.terminology.is_valid_code("INVALID123", "loinc")
        print(f"  Code is valid: {is_valid}")
        if not is_valid:
            raise ValidationError(
                "Invalid code 'INVALID123' in system 'loinc'. "
                "Code does not exist in the terminology server."
            )
    except ValidationError as e:
        print(f"  ✗ ValidationError: {e}")
        print("  → Resource creation BLOCKED - invalid code rejected")

    # =========================================================================
    # 2. RESOURCE ENRICHMENT
    # =========================================================================
    print("\n" + "=" * 70)
    print("2. AUTOMATIC DISPLAY NAME ENRICHMENT")
    print("=" * 70)

    print("\nScenario: Resource retrieved with only codes (no display names)")
    print("-" * 50)

    # Simulate a resource with codes but no display names
    raw_observation = {
        "resourceType": "Observation",
        "id": "example",
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "29463-7",
                    # No display name!
                }
            ]
        },
        "valueQuantity": {"value": 70, "unit": "kg"},
    }

    print("  Before enrichment:")
    print(f"    code.coding[0].display = {raw_observation['code']['coding'][0].get('display', 'MISSING')}")

    # Enrich with terminology service
    enriched = client._enrich_codings(raw_observation.copy())

    print("\n  After enrichment:")
    print(f"    code.coding[0].display = {enriched['code']['coding'][0].get('display', 'MISSING')}")
    print(f"    code.text = {enriched['code'].get('text', 'MISSING')}")

    # =========================================================================
    # 3. VALUE SET FOR UI DROPDOWNS
    # =========================================================================
    print("\n" + "=" * 70)
    print("3. VALUE SETS FOR UI DROPDOWNS")
    print("=" * 70)

    print("\nScenario: Populate a 'Gender' dropdown from standard value set")
    print("-" * 50)

    options = client.get_value_set_options(
        "http://hl7.org/fhir/ValueSet/administrative-gender"
    )

    print("  Dropdown options retrieved from terminology server:")
    for opt in options:
        print(f"    <option value='{opt['value']}'>{opt['label']}</option>")

    # =========================================================================
    # 4. CODE TRANSLATION FOR INTEROPERABILITY
    # =========================================================================
    print("\n" + "=" * 70)
    print("4. CODE TRANSLATION (ICD-10 → SNOMED)")
    print("=" * 70)

    print("\nScenario: Hospital A uses ICD-10, Hospital B requires SNOMED")
    print("-" * 50)

    # Simulate translating a diagnosis code
    print("  ICD-10 code: I10 (Essential hypertension)")

    try:
        result = client.terminology.translate_code(
            code="I10",
            source_system="icd10",
            target_system="snomed",
        )

        # Check if translation was successful
        for param in result.get("parameter", []):
            if param.get("name") == "result":
                success = param.get("valueBoolean", False)
                print(f"  Translation available: {success}")
            if param.get("name") == "match":
                for part in param.get("part", []):
                    if part.get("name") == "concept":
                        translated = part.get("valueCoding", {})
                        print(f"  → SNOMED code: {translated.get('code')}")
                        print(f"  → Display: {translated.get('display')}")

    except Exception as e:
        print(f"  Translation service unavailable: {e}")
        print("  (This is common - not all mappings exist)")

    # =========================================================================
    # 5. SEMANTIC SEARCH CONCEPT
    # =========================================================================
    print("\n" + "=" * 70)
    print("5. SEMANTIC SEARCH WITH TERMINOLOGY HIERARCHY")
    print("=" * 70)

    print("\nScenario: Find all cardiovascular conditions using SNOMED hierarchy")
    print("-" * 50)

    print("  Parent concept: 49601007 (Disorder of cardiovascular system)")
    print("  Child concepts that would be found:")
    print("    - 22298006 (Myocardial infarction)")
    print("    - 38341003 (Hypertension)")
    print("    - 84114007 (Heart failure)")
    print("    - ... and all other cardiovascular conditions")

    # Demonstrate subsumption check
    print("\n  Checking if 'Hypertension' is a cardiovascular condition...")
    try:
        result = client.terminology.check_subsumption(
            code_a="49601007",  # Cardiovascular disease
            code_b="38341003",  # Hypertension
            system="snomed",
        )
        for param in result.get("parameter", []):
            if param.get("name") == "outcome":
                outcome = param.get("valueCode")
                print(f"  Subsumption result: {outcome}")
                if outcome == "subsumes":
                    print("  ✓ Yes, hypertension IS a cardiovascular condition")

    except Exception as e:
        print(f"  Subsumption check failed: {e}")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 70)
    print("INTEGRATION SUMMARY")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────────┐
│                    HOW THEY WORK TOGETHER                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  User Action          FHIRClient              TerminologyService    │
│  ───────────          ──────────              ──────────────────    │
│                                                                     │
│  Create Observation   ──────────────────────► validate_code()       │
│                       ◄────── if valid ────── get_display_name()    │
│                       create_resource()                             │
│                                                                     │
│  Read Observation     read_resource()                               │
│                       ──────────────────────► lookup_code()         │
│                       ◄────── enrich ─────── (add display names)    │
│                                                                     │
│  Search Conditions    ──────────────────────► expand_value_set()    │
│                       ◄── expanded codes ─── check_subsumption()    │
│                       search() with all                             │
│                       related codes                                 │
│                                                                     │
│  Exchange Data        ──────────────────────► translate_code()      │
│                       ◄── mapped codes ─────                        │
│                       (ICD-10 → SNOMED)                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

BUSINESS VALUE:
  ✓ Data Quality: Invalid codes rejected at point of entry
  ✓ Usability: Human-readable names always displayed
  ✓ Interoperability: Codes translated for data exchange
  ✓ Clinical Intelligence: Semantic search finds related concepts
  ✓ Compliance: Standard terminologies enforced
""")

    client.close()


if __name__ == "__main__":
    main()
