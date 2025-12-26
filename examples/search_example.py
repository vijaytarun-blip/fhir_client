"""
Example: Search and Filter Resources

This script demonstrates various search and filtering capabilities.
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
    
    # Initialize client
    client = FHIRClient(base_url="https://hapi.fhir.org/baseR4")
    
    print("=" * 60)
    print("FHIR Client - Search and Filter Example")
    print("=" * 60)
    
    try:
        # 1. Simple search by name
        print("\n1. Searching for patients named 'Smith'...")
        results = client.search("Patient", {"family": "Smith", "_count": "5"})
        print(f"   ✓ Found {results.get('total', 0)} patients")
        
        # 2. Search with multiple parameters
        print("\n2. Searching for male patients born after 1990...")
        results = client.search("Patient", {
            "gender": "male",
            "birthdate": "gt1990-01-01",
            "_count": "5"
        })
        print(f"   ✓ Found {results.get('total', 0)} matching patients")
        
        # 3. Search with sorting
        print("\n3. Getting recently updated patients...")
        results = client.search("Patient", {
            "_sort": "-_lastUpdated",
            "_count": "5"
        })
        
        if results.get("entry"):
            print(f"   ✓ Retrieved {len(results['entry'])} patients")
            print("   Most recently updated:")
            for i, entry in enumerate(results["entry"][:3], 1):
                resource = entry.get("resource", {})
                name = Patient.get_full_name(resource)
                last_updated = resource.get("meta", {}).get("lastUpdated", "Unknown")
                print(f"     {i}. {name} - Last updated: {last_updated[:19]}")
        
        # 4. Search for specific resource types
        print("\n4. Searching for observations...")
        obs_results = client.search("Observation", {
            "code": "http://loinc.org|8867-4",  # Heart rate
            "_count": "3"
        })
        print(f"   ✓ Found {obs_results.get('total', 0)} heart rate observations")
        
        # 5. Search with text filter
        print("\n5. Searching with text filter...")
        text_results = client.search("Patient", {
            "_text": "John",
            "_count": "5"
        })
        print(f"   ✓ Found {text_results.get('total', 0)} patients matching 'John'")
        
        # 6. Count-only search (no results returned)
        print("\n6. Getting total patient count...")
        count_results = client.search("Patient", {"_summary": "count"})
        print(f"   ✓ Total patients on server: {count_results.get('total', 'Unknown')}")
        
        print("\n" + "=" * 60)
        print("Search example completed successfully!")
        print("=" * 60)
        
    except FHIRClientError as e:
        print(f"\n❌ Error: {e}")
    
    finally:
        client.close()


if __name__ == "__main__":
    main()
