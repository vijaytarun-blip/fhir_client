# FHIR Terminology Server - Technical Documentation

## Table of Contents

1. [Overview](#overview)
2. [What is a Terminology Server?](#what-is-a-terminology-server)
3. [Architecture](#architecture)
4. [FHIR Terminology Resources](#fhir-terminology-resources)
5. [Operations Reference](#operations-reference)
6. [Business Use Cases](#business-use-cases)
7. [Integration Guide](#integration-guide)
8. [Code Examples](#code-examples)
9. [Best Practices](#best-practices)
10. [Public Terminology Servers](#public-terminology-servers)

---

## Overview

The `TerminologyService` module provides a comprehensive interface for interacting with FHIR Terminology Servers. It enables healthcare applications to validate, lookup, translate, and expand clinical codes from standard terminologies like SNOMED CT, LOINC, ICD-10, and RxNorm.

### Key Capabilities

| Capability | FHIR Operation | Description |
|------------|----------------|-------------|
| Code Validation | `$validate-code` | Verify if a code exists in a code system |
| Code Lookup | `$lookup` | Retrieve detailed information about a code |
| Value Set Expansion | `$expand` | List all codes in a value set |
| Code Translation | `$translate` | Map codes between different code systems |
| Subsumption Testing | `$subsumes` | Check hierarchical relationships |

---

## What is a Terminology Server?

A **Terminology Server** is a specialized FHIR server that manages and distributes clinical vocabularies, code systems, and value sets. It serves as the authoritative source for terminology operations in healthcare systems.

### Why Terminology Matters in Healthcare

Clinical terminologies enable:

1. **Semantic Interoperability**: Systems exchange data with shared meaning
2. **Clinical Decision Support**: Rules based on standardized codes trigger alerts
3. **Analytics & Reporting**: Aggregate data using consistent coding
4. **Regulatory Compliance**: Meet requirements like USCDI, HIPAA, Meaningful Use

### Core Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TERMINOLOGY SERVER                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │
│  │ CodeSystem  │  │  ValueSet   │  │ ConceptMap  │                  │
│  │             │  │             │  │             │                  │
│  │ • SNOMED CT │  │ • Includes  │  │ • Source    │                  │
│  │ • LOINC     │  │ • Excludes  │  │ • Target    │                  │
│  │ • ICD-10    │  │ • Filters   │  │ • Mappings  │                  │
│  │ • RxNorm    │  │             │  │             │                  │
│  └─────────────┘  └─────────────┘  └─────────────┘                  │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    FHIR REST Operations                         │ │
│  │  $lookup  |  $validate-code  |  $expand  |  $translate         │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Architecture

### Data Flow

```
┌──────────────────┐     HTTP/FHIR      ┌──────────────────┐
│  Your Application │ ◄───────────────► │ Terminology      │
│                   │                    │ Server           │
│  ┌──────────────┐ │                    │                  │
│  │ Terminology  │ │  GET /$lookup      │ ┌──────────────┐ │
│  │ Service      │─┼──────────────────►│ │ CodeSystem   │ │
│  │              │ │                    │ │ Database     │ │
│  │ • validate() │ │  Parameters JSON   │ └──────────────┘ │
│  │ • lookup()   │◄┼──────────────────┤ │                  │
│  │ • expand()   │ │                    │ ┌──────────────┐ │
│  │ • translate()│ │                    │ │ Hierarchy    │ │
│  └──────────────┘ │                    │ │ Graph        │ │
│                   │                    │ └──────────────┘ │
└──────────────────┘                    └──────────────────┘
```

### Module Structure

```
src/
├── client.py              # FHIRClient - HTTP transport layer
├── terminology.py         # TerminologyService - Terminology operations
└── utils/
    └── config.py          # Configuration including terminology servers
```

---

## FHIR Terminology Resources

### CodeSystem

A **CodeSystem** defines a set of codes and their meanings. It contains:

- **concept**: List of codes with display names and definitions
- **property**: Additional properties for each code (e.g., status, parent)
- **hierarchy**: Parent-child relationships between codes

**Common Code Systems:**

| Code System | URL | Description | Size |
|-------------|-----|-------------|------|
| SNOMED CT | `http://snomed.info/sct` | Clinical terminology | 350,000+ concepts |
| LOINC | `http://loinc.org` | Lab & clinical observations | 98,000+ codes |
| ICD-10-CM | `http://hl7.org/fhir/sid/icd-10-cm` | Diagnosis codes (US) | 72,000+ codes |
| ICD-10 | `http://hl7.org/fhir/sid/icd-10` | Diagnosis codes (WHO) | 14,000+ codes |
| RxNorm | `http://www.nlm.nih.gov/research/umls/rxnorm` | Medications | 115,000+ concepts |
| CPT | `http://www.ama-assn.org/go/cpt` | Procedure codes | 10,000+ codes |
| UCUM | `http://unitsofmeasure.org` | Units of measure | 300+ units |
| NDC | `http://hl7.org/fhir/sid/ndc` | Drug identifiers | 200,000+ codes |

### ValueSet

A **ValueSet** defines a selection of codes from one or more code systems. It can:

- **Include** specific codes or entire code systems
- **Exclude** certain codes
- **Filter** codes based on properties (e.g., all active SNOMED concepts)

**Example Use Cases:**

| Value Set | Purpose |
|-----------|---------|
| Administrative Gender | Constrain gender field to: male, female, other, unknown |
| Vital Signs Codes | LOINC codes for heart rate, BP, temperature, etc. |
| Condition Severity | mild, moderate, severe |
| Allergy Substances | Common allergens for clinical documentation |

### ConceptMap

A **ConceptMap** defines mappings between codes in different systems. Used for:

- Translating ICD-10 diagnoses to SNOMED CT
- Mapping local codes to standard terminologies
- Supporting data exchange between systems

---

## Operations Reference

### 1. Code Validation (`$validate-code`)

Validates that a code exists in a code system or value set.

**HTTP Request:**
```
GET [base]/CodeSystem/$validate-code?system={system}&code={code}
GET [base]/ValueSet/$validate-code?url={valueSetUrl}&code={code}&system={system}
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `code` | string | The code to validate |
| `system` | uri | The code system URL |
| `display` | string | Optional display name to validate |
| `url` | uri | Value set URL (for value set validation) |

**Response:**
```json
{
  "resourceType": "Parameters",
  "parameter": [
    {"name": "result", "valueBoolean": true},
    {"name": "display", "valueString": "Body weight"}
  ]
}
```

### 2. Code Lookup (`$lookup`)

Retrieves detailed information about a code.

**HTTP Request:**
```
GET [base]/CodeSystem/$lookup?system={system}&code={code}
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `code` | string | The code to look up |
| `system` | uri | The code system URL |
| `property` | string | Specific properties to retrieve (repeatable) |

**Response:**
```json
{
  "resourceType": "Parameters",
  "parameter": [
    {"name": "name", "valueString": "LOINC"},
    {"name": "display", "valueString": "Body weight"},
    {"name": "definition", "valueString": "Patient body weight measured"},
    {"name": "property", "part": [
      {"name": "code", "valueCode": "COMPONENT"},
      {"name": "value", "valueString": "Body weight"}
    ]}
  ]
}
```

### 3. Value Set Expansion (`$expand`)

Returns all codes that are members of a value set.

**HTTP Request:**
```
GET [base]/ValueSet/$expand?url={valueSetUrl}&filter={searchText}&count={limit}
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | uri | Canonical URL of the value set |
| `filter` | string | Text filter to search within expansion |
| `offset` | integer | Starting index for pagination |
| `count` | integer | Maximum codes to return |

**Response:**
```json
{
  "resourceType": "ValueSet",
  "expansion": {
    "total": 4,
    "contains": [
      {"system": "http://hl7.org/fhir/administrative-gender", "code": "male", "display": "Male"},
      {"system": "http://hl7.org/fhir/administrative-gender", "code": "female", "display": "Female"},
      {"system": "http://hl7.org/fhir/administrative-gender", "code": "other", "display": "Other"},
      {"system": "http://hl7.org/fhir/administrative-gender", "code": "unknown", "display": "Unknown"}
    ]
  }
}
```

### 4. Code Translation (`$translate`)

Maps a code from one system to another using ConceptMaps.

**HTTP Request:**
```
GET [base]/ConceptMap/$translate?system={sourceSystem}&code={code}&targetSystem={targetSystem}
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `code` | string | The code to translate |
| `system` | uri | Source code system |
| `targetSystem` | uri | Target code system |
| `url` | uri | Optional specific ConceptMap to use |

**Response:**
```json
{
  "resourceType": "Parameters",
  "parameter": [
    {"name": "result", "valueBoolean": true},
    {
      "name": "match",
      "part": [
        {"name": "equivalence", "valueCode": "equivalent"},
        {"name": "concept", "valueCoding": {
          "system": "http://snomed.info/sct",
          "code": "38341003",
          "display": "Hypertensive disorder"
        }}
      ]
    }
  ]
}
```

### 5. Subsumption Testing (`$subsumes`)

Tests whether one code is a parent/ancestor of another in the hierarchy.

**HTTP Request:**
```
GET [base]/CodeSystem/$subsumes?system={system}&codeA={parent}&codeB={child}
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `codeA` | string | First code (potential parent) |
| `codeB` | string | Second code (potential child) |
| `system` | uri | The code system |

**Response Values:**

| Outcome | Meaning |
|---------|---------|
| `equivalent` | Codes are the same |
| `subsumes` | codeA is a parent of codeB |
| `subsumed-by` | codeB is a parent of codeA |
| `not-subsumed` | No hierarchical relationship |

---

## Business Use Cases

### 1. Electronic Health Record (EHR) Data Entry

**Scenario:** Clinical staff enter diagnosis codes during patient encounters.

**Implementation:**
```python
def validate_diagnosis_on_entry(icd_code: str) -> dict:
    """Validate ICD-10 code before saving to patient record."""
    terminology = TerminologyService.create_default()
    
    # Check if code exists
    if not terminology.is_valid_code(icd_code, "icd10cm"):
        return {"valid": False, "error": "Invalid ICD-10-CM code"}
    
    # Get display name for confirmation
    display = terminology.get_display_name("icd10cm", icd_code)
    
    return {
        "valid": True,
        "code": icd_code,
        "display": display,
        "message": f"Confirm diagnosis: {display}"
    }
```

**Business Value:**
- ✅ Prevents invalid codes in medical records
- ✅ Reduces claim rejections from payers
- ✅ Improves data quality for analytics

---

### 2. Clinical Decision Support (CDS)

**Scenario:** Alert clinicians when a patient with cardiovascular disease is prescribed contraindicated medications.

**Implementation:**
```python
def check_cardiovascular_risk(patient_diagnoses: list) -> bool:
    """Check if any diagnosis is a cardiovascular condition."""
    terminology = TerminologyService.create_default()
    
    CARDIOVASCULAR_ROOT = "49601007"  # SNOMED: Disorder of cardiovascular system
    
    for diagnosis in patient_diagnoses:
        if diagnosis["system"] == "http://snomed.info/sct":
            result = terminology.check_subsumption(
                code_a=CARDIOVASCULAR_ROOT,
                code_b=diagnosis["code"],
                system="snomed"
            )
            # Extract outcome
            for param in result.get("parameter", []):
                if param.get("name") == "outcome":
                    if param.get("valueCode") == "subsumes":
                        return True  # This diagnosis IS a cardiovascular condition
    
    return False
```

**Business Value:**
- ✅ Reduces adverse drug events
- ✅ Improves patient safety
- ✅ Supports evidence-based medicine

---

### 3. Healthcare Data Exchange (Interoperability)

**Scenario:** Hospital A uses ICD-10 for diagnoses, but the receiving HIE requires SNOMED CT.

**Implementation:**
```python
def prepare_for_health_information_exchange(encounter: dict) -> dict:
    """Translate diagnosis codes for HIE submission."""
    terminology = TerminologyService.create_default()
    
    translated_conditions = []
    
    for condition in encounter.get("conditions", []):
        if condition["system"] == "http://hl7.org/fhir/sid/icd-10":
            # Translate ICD-10 to SNOMED CT
            result = terminology.translate_code(
                code=condition["code"],
                source_system="icd10",
                target_system="snomed"
            )
            
            # Extract translated code
            for param in result.get("parameter", []):
                if param.get("name") == "match":
                    for part in param.get("part", []):
                        if part.get("name") == "concept":
                            translated_conditions.append(part["valueCoding"])
                            break
        else:
            translated_conditions.append(condition)
    
    encounter["conditions"] = translated_conditions
    return encounter
```

**Business Value:**
- ✅ Enables data sharing across disparate systems
- ✅ Supports care coordination
- ✅ Meets regulatory interoperability requirements (ONC, CMS)

---

### 4. Dynamic Form Building

**Scenario:** Build a patient intake form with dropdowns populated from standard value sets.

**Implementation:**
```python
def get_form_options(field_name: str) -> list:
    """Get dropdown options from FHIR value sets."""
    terminology = TerminologyService.create_default()
    
    VALUE_SET_MAP = {
        "gender": "http://hl7.org/fhir/ValueSet/administrative-gender",
        "marital_status": "http://hl7.org/fhir/ValueSet/marital-status",
        "language": "http://hl7.org/fhir/ValueSet/languages",
        "ethnicity": "http://hl7.org/fhir/us/core/ValueSet/omb-ethnicity-category",
    }
    
    value_set_url = VALUE_SET_MAP.get(field_name)
    if not value_set_url:
        return []
    
    result = terminology.expand_value_set(value_set_url=value_set_url)
    
    return [
        {"value": code["code"], "label": code["display"]}
        for code in result.get("expansion", {}).get("contains", [])
    ]

# Usage in web application
@app.route("/api/form-options/<field>")
def form_options(field):
    return jsonify(get_form_options(field))
```

**Business Value:**
- ✅ Ensures standardized data collection
- ✅ Reduces maintenance (options auto-update)
- ✅ Supports multiple languages via terminology server

---

### 5. Quality Measure Reporting

**Scenario:** Calculate quality measures that require specific diagnosis or procedure codes.

**Implementation:**
```python
def find_diabetic_patients(patient_records: list) -> list:
    """Identify patients with diabetes for quality reporting (HEDIS)."""
    terminology = TerminologyService.create_default()
    
    # Expand the diabetes value set used in quality measures
    diabetes_codes = terminology.expand_value_set(
        value_set_url="http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.103.12.1001"
    )
    
    # Build a set of valid codes for fast lookup
    valid_codes = {
        (code["system"], code["code"])
        for code in diabetes_codes.get("expansion", {}).get("contains", [])
    }
    
    # Filter patients
    diabetic_patients = []
    for patient in patient_records:
        for condition in patient.get("conditions", []):
            if (condition["system"], condition["code"]) in valid_codes:
                diabetic_patients.append(patient)
                break
    
    return diabetic_patients
```

**Business Value:**
- ✅ Accurate quality measure calculation
- ✅ Value set updates automatically reflected
- ✅ Audit trail for measure methodology

---

### 6. Lab Result Interpretation

**Scenario:** Display human-readable names for LOINC codes in lab results.

**Implementation:**
```python
def enrich_lab_results(lab_results: list) -> list:
    """Add display names to lab result codes."""
    terminology = TerminologyService.create_default()
    
    for result in lab_results:
        if result.get("code", {}).get("system") == "http://loinc.org":
            loinc_code = result["code"]["coding"][0]["code"]
            
            # Look up the display name
            display = terminology.get_display_name("loinc", loinc_code)
            
            if display:
                result["code"]["coding"][0]["display"] = display
                result["code"]["text"] = display
    
    return lab_results
```

**Business Value:**
- ✅ Improves clinician efficiency
- ✅ Enhances patient portal readability
- ✅ Supports internationalization

---

### 7. Medication Reconciliation

**Scenario:** Match patient-reported medications to standard RxNorm codes.

**Implementation:**
```python
def search_medications(search_text: str) -> list:
    """Search for medications by name."""
    terminology = TerminologyService.create_default()
    
    # Search within RxNorm medication value set
    results = terminology.search_value_set(
        value_set_url="http://hl7.org/fhir/ValueSet/medication-codes",
        search_text=search_text,
        max_results=10
    )
    
    return [
        {
            "rxnorm_code": code["code"],
            "name": code["display"],
            "system": code["system"]
        }
        for code in results
    ]
```

**Business Value:**
- ✅ Standardizes medication documentation
- ✅ Enables drug-drug interaction checking
- ✅ Improves medication safety

---

## Integration Guide

### Installation

The `TerminologyService` is included in the FHIR Client package:

```python
from src import FHIRClient, TerminologyService
```

### Configuration

#### Option 1: Use Default HL7 Server

```python
# Connects to https://tx.fhir.org/r4
terminology = TerminologyService.create_default()
```

#### Option 2: Custom Terminology Server

```python
# Use your organization's terminology server
client = FHIRClient("https://terminology.yourorg.com/fhir")
terminology = TerminologyService(client)
```

#### Option 3: Environment-Based Configuration

```python
import os
from src.utils.config import FHIRConfig

# Set environment variable
os.environ["TERMINOLOGY_SERVER_URL"] = "https://your-server.com/fhir"

# Use from config
config = FHIRConfig()
server_url = config.TERMINOLOGY_SERVERS.get("hl7-tx")
```

### Code System Aliases

The `TerminologyService` supports convenient aliases:

```python
# Instead of full URLs
terminology.lookup_code("http://loinc.org", "29463-7")

# Use aliases
terminology.lookup_code("loinc", "29463-7")
terminology.lookup_code("snomed", "38341003")
terminology.lookup_code("icd10", "I10")
```

**Available Aliases:**

| Alias | Full URL |
|-------|----------|
| `snomed` | `http://snomed.info/sct` |
| `loinc` | `http://loinc.org` |
| `icd10` | `http://hl7.org/fhir/sid/icd-10` |
| `icd10cm` | `http://hl7.org/fhir/sid/icd-10-cm` |
| `rxnorm` | `http://www.nlm.nih.gov/research/umls/rxnorm` |
| `cpt` | `http://www.ama-assn.org/go/cpt` |
| `ucum` | `http://unitsofmeasure.org` |
| `ndc` | `http://hl7.org/fhir/sid/ndc` |

---

## Code Examples

### Complete Example: Patient Intake Validation

```python
from src import TerminologyService

def validate_patient_intake(data: dict) -> dict:
    """Validate all coded fields in patient intake form."""
    terminology = TerminologyService.create_default()
    errors = []
    
    # Validate gender
    if not terminology.is_valid_code(data["gender"], 
            "http://hl7.org/fhir/administrative-gender"):
        errors.append(f"Invalid gender code: {data['gender']}")
    
    # Validate primary diagnosis (ICD-10)
    if data.get("primary_diagnosis"):
        if not terminology.is_valid_code(data["primary_diagnosis"], "icd10cm"):
            errors.append(f"Invalid ICD-10-CM code: {data['primary_diagnosis']}")
        else:
            # Get display for confirmation
            display = terminology.get_display_name("icd10cm", data["primary_diagnosis"])
            data["primary_diagnosis_display"] = display
    
    # Validate allergies (SNOMED)
    for i, allergy in enumerate(data.get("allergies", [])):
        if not terminology.is_valid_code(allergy["code"], "snomed"):
            errors.append(f"Invalid allergy code at index {i}: {allergy['code']}")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "data": data
    }
```

---

## Best Practices

### 1. Cache Frequently Used Lookups

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_code_display(system: str, code: str) -> str:
    """Cache terminology lookups for performance."""
    return terminology.get_display_name(system, code)
```

### 2. Handle Network Errors Gracefully

```python
def safe_validate(code: str, system: str) -> bool:
    """Validate with fallback on network error."""
    try:
        return terminology.is_valid_code(code, system)
    except Exception as e:
        logger.warning(f"Terminology server unavailable: {e}")
        return True  # Fail open for availability
```

### 3. Batch Operations When Possible

```python
def validate_codes_batch(codes: list) -> dict:
    """Validate multiple codes efficiently."""
    # Expand value set once, then check locally
    value_set = terminology.expand_value_set(
        value_set_url="http://hl7.org/fhir/ValueSet/observation-codes"
    )
    valid_codes = {c["code"] for c in value_set.get("expansion", {}).get("contains", [])}
    
    return {code: code in valid_codes for code in codes}
```

### 4. Log All Terminology Operations

```python
import logging
logging.getLogger("src.terminology").setLevel(logging.DEBUG)
```

---

## Public Terminology Servers

| Server | URL | Description | Rate Limits |
|--------|-----|-------------|-------------|
| **HL7 Official** | `https://tx.fhir.org/r4` | General purpose, all major code systems | Fair use |
| **SNOMED Snowstorm** | `https://snowstorm.ihtsdotools.org/fhir` | SNOMED CT specific | Requires API key for production |
| **NLM VSAC** | `https://cts.nlm.nih.gov/fhir` | US value sets (requires UMLS account) | Authentication required |
| **HAPI FHIR** | `https://hapi.fhir.org/baseR4` | Test server with basic terminology | For development only |

### Production Recommendations

1. **Self-Host**: Deploy your own terminology server (HAPI FHIR, Ontoserver) for reliability
2. **License Compliance**: Ensure proper licenses for SNOMED CT, CPT, etc.
3. **Caching Layer**: Add Redis/Memcached for high-volume applications
4. **Monitoring**: Track terminology server latency and availability

---

## Appendix: FHIR Specification References

- [FHIR Terminology Module](https://hl7.org/fhir/terminology-module.html)
- [CodeSystem Resource](https://hl7.org/fhir/codesystem.html)
- [ValueSet Resource](https://hl7.org/fhir/valueset.html)
- [ConceptMap Resource](https://hl7.org/fhir/conceptmap.html)
- [Terminology Operations](https://hl7.org/fhir/terminology-service.html)
