"""
Example: Working with Observations

This script demonstrates creating and managing Observation resources,
including vital signs.
"""
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.client import FHIRClient, FHIRClientError
from src.models import Patient, Observation
from src.utils.logger import setup_logging
from datetime import datetime


def main():
    # Setup logging
    setup_logging(level="INFO")
    
    # Initialize client
    client = FHIRClient(base_url="https://hapi.fhir.org/baseR4")
    
    print("=" * 60)
    print("FHIR Client - Observations Example")
    print("=" * 60)
    
    try:
        # First, create a patient
        print("\n1. Creating a patient...")
        patient = Patient.create(
            family_name="Johnson",
            given_names=["Sarah"],
            gender="female",
            birth_date="1985-03-20"
        )
        created_patient = client.create_resource(patient)
        patient_id = created_patient["id"]
        patient_reference = f"Patient/{patient_id}"
        print(f"   ✓ Patient created: {Patient.get_full_name(created_patient)} (ID: {patient_id})")
        
        # Create vital sign observations
        print("\n2. Creating vital sign observations...")
        
        # Heart rate
        heart_rate = Observation.create_vital_sign(
            patient_reference=patient_reference,
            vital_type="heart_rate",
            value=72,
            unit="beats/min"
        )
        created_hr = client.create_resource(heart_rate)
        print(f"   ✓ Heart Rate: {created_hr['valueQuantity']['value']} {created_hr['valueQuantity']['unit']}")
        
        # Blood pressure (systolic)
        bp_systolic = Observation.create_vital_sign(
            patient_reference=patient_reference,
            vital_type="blood_pressure_systolic",
            value=120,
            unit="mmHg"
        )
        created_bp_sys = client.create_resource(bp_systolic)
        print(f"   ✓ Blood Pressure (Systolic): {created_bp_sys['valueQuantity']['value']} {created_bp_sys['valueQuantity']['unit']}")
        
        # Temperature
        temperature = Observation.create_vital_sign(
            patient_reference=patient_reference,
            vital_type="temperature",
            value=36.8,
            unit="Cel"
        )
        created_temp = client.create_resource(temperature)
        print(f"   ✓ Body Temperature: {created_temp['valueQuantity']['value']} °C")
        
        # Oxygen saturation
        oxygen_sat = Observation.create_vital_sign(
            patient_reference=patient_reference,
            vital_type="oxygen_saturation",
            value=98,
            unit="%"
        )
        created_o2 = client.create_resource(oxygen_sat)
        print(f"   ✓ Oxygen Saturation: {created_o2['valueQuantity']['value']}{created_o2['valueQuantity']['unit']}")
        
        # Create a custom observation
        print("\n3. Creating a custom observation (Glucose level)...")
        glucose_obs = Observation.create(
            patient_reference=patient_reference,
            code={
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "15074-8",
                    "display": "Glucose [Moles/volume] in Blood"
                }],
                "text": "Glucose"
            },
            value={"value": 95, "unit": "mg/dL", "system": "http://unitsofmeasure.org", "code": "mg/dL"},
            status="final"
        )
        created_glucose = client.create_resource(glucose_obs)
        print(f"   ✓ Glucose Level: {created_glucose['valueQuantity']['value']} {created_glucose['valueQuantity']['unit']}")
        
        # Search for patient's observations
        print(f"\n4. Searching for all observations for Patient/{patient_id}...")
        search_results = client.search("Observation", {
            "patient": patient_id,
            "_sort": "-date"
        })
        
        total = search_results.get("total", 0)
        print(f"   ✓ Found {total} observations")
        
        if search_results.get("entry"):
            print("\n   Observations Summary:")
            for entry in search_results["entry"]:
                obs = entry.get("resource", {})
                code_text = obs.get("code", {}).get("text", "Unknown")
                value_qty = obs.get("valueQuantity", {})
                if value_qty:
                    value = value_qty.get("value", "N/A")
                    unit = value_qty.get("unit", "")
                    print(f"     • {code_text}: {value} {unit}")
        
        print("\n" + "=" * 60)
        print("Observations example completed successfully!")
        print("=" * 60)
        
    except FHIRClientError as e:
        print(f"\n❌ Error: {e}")
    
    finally:
        client.close()


if __name__ == "__main__":
    main()
