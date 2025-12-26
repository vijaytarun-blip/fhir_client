"""
Example: Basic FHIR Client Usage

This script demonstrates basic CRUD operations with the FHIR client.
"""
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.client import FHIRClient, FHIRClientError
from src.models import Patient
from src.utils.logger import setup_logging


def main():
    # Setup logging
    setup_logging(level="INFO")
    
    # Initialize client with a public FHIR server
    client = FHIRClient(base_url="https://hapi.fhir.org/baseR4")
    
    print("=" * 60)
    print("FHIR Client - Basic Example")
    print("=" * 60)
    
    try:
        # 1. Create a Patient resource
        print("\n1. Creating a new Patient resource...")
        patient = Patient.create(
            family_name="Smith",
            given_names=["John", "Jacob"],
            gender="male",
            birth_date="1990-05-15"
        )
        
        created_patient = client.create_resource(patient)
        patient_id = created_patient["id"]
        print(f"   ✓ Patient created with ID: {patient_id}")
        print(f"   Name: {Patient.get_full_name(created_patient)}")
        
        # 2. Read the Patient resource
        print(f"\n2. Reading Patient/{patient_id}...")
        read_patient = client.read_resource("Patient", patient_id)
        print(f"   ✓ Patient retrieved")
        print(f"   Name: {Patient.get_full_name(read_patient)}")
        print(f"   Birth Date: {read_patient.get('birthDate', 'N/A')}")
        
        # 3. Update the Patient resource
        print(f"\n3. Updating Patient/{patient_id}...")
        read_patient["name"][0]["given"] = ["Jane", "Marie"]
        updated_patient = client.update_resource(read_patient)
        print(f"   ✓ Patient updated")
        print(f"   New Name: {Patient.get_full_name(updated_patient)}")
        
        # 4. Search for Patients
        print("\n4. Searching for patients with family name 'Smith'...")
        search_results = client.search("Patient", {"family": "Smith", "_count": "5"})
        total = search_results.get("total", 0)
        print(f"   ✓ Found {total} matching patients")
        
        if search_results.get("entry"):
            print("   First 3 results:")
            for i, entry in enumerate(search_results["entry"][:3], 1):
                resource = entry.get("resource", {})
                name = Patient.get_full_name(resource)
                res_id = resource.get("id", "N/A")
                print(f"     {i}. {name} (ID: {res_id})")
        
        # 5. Get server capability statement
        print("\n5. Retrieving server capabilities...")
        capability = client.get_capability_statement()
        print(f"   ✓ Server: {capability.get('software', {}).get('name', 'Unknown')}")
        print(f"   FHIR Version: {capability.get('fhirVersion', 'Unknown')}")
        
        # 6. Delete the Patient resource (optional - uncomment to test)
        # print(f"\n6. Deleting Patient/{patient_id}...")
        # delete_result = client.delete_resource("Patient", patient_id)
        # if delete_result:
        #     print(f"   ✓ Patient deleted successfully")
        
        print("\n" + "=" * 60)
        print("Example completed successfully!")
        print("=" * 60)
        
    except FHIRClientError as e:
        print(f"\n❌ Error: {e}")
    
    finally:
        # Clean up
        client.close()


if __name__ == "__main__":
    main()
