"""
Quick test script for Terminology Service
"""
import sys
import os

# Add the parent directory to allow package imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import from the src package
from src import FHIRClient, TerminologyService

print("=" * 60)
print("Testing Terminology Service with FHIR Client")
print("=" * 60)

# Initialize terminology service with HL7's public server
print("\n1. Initializing TerminologyService...")
terminology = TerminologyService.create_default("https://tx.fhir.org/r4")
print("   Connected to tx.fhir.org")

# Test 1: Code Lookup
print("\n2. Testing $lookup operation (LOINC 29463-7 - Body weight)...")
try:
    result = terminology.lookup_code("loinc", "29463-7")
    print("   Lookup successful!")
    for param in result.get("parameter", []):
        name = param.get("name")
        if name == "display":
            print(f"   Display: {param.get('valueString')}")
        elif name == "name":
            print(f"   Name: {param.get('valueString')}")
except Exception as e:
    print(f"   Lookup failed: {e}")

# Test 2: Quick display name helper
print("\n3. Testing get_display_name() helper...")
try:
    display = terminology.get_display_name("loinc", "8867-4")
    print(f"   LOINC 8867-4 display: {display}")
except Exception as e:
    print(f"   Failed: {e}")

# Test 3: Code Validation
print("\n4. Testing $validate-code operation...")
try:
    is_valid = terminology.is_valid_code("29463-7", "loinc")
    print(f"   LOINC 29463-7 is valid: {is_valid}")
    
    is_invalid = terminology.is_valid_code("FAKE123", "loinc")
    print(f"   LOINC FAKE123 is valid: {is_invalid}")
except Exception as e:
    print(f"   Validation failed: {e}")

# Test 4: Value Set Expansion
print("\n5. Testing $expand operation (Administrative Gender)...")
try:
    result = terminology.expand_value_set(
        value_set_url="http://hl7.org/fhir/ValueSet/administrative-gender",
        count=10
    )
    codes = result.get("expansion", {}).get("contains", [])
    print(f"   Found {len(codes)} codes:")
    for code in codes[:5]:
        print(f"      - {code.get('code')}: {code.get('display')}")
except Exception as e:
    print(f"   Expansion failed: {e}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
