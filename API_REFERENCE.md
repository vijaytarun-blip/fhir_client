# FHIR Client API Reference

## Table of Contents
1. [FHIRClient](#fhirclient)
2. [TerminologyService](#terminologyservice)
3. [Resource Models](#resource-models)
4. [Operations](#operations)
5. [Utilities](#utilities)
6. [Exceptions](#exceptions)

---

## FHIRClient

### Class: `FHIRClient`

Main client for interacting with FHIR servers.

#### Constructor

```python
FHIRClient(
    base_url: str,
    auth: Optional[tuple] = None,
    timeout: int = 30,
    verify_ssl: bool = True
)
```

**Parameters:**
- `base_url` (str): Base URL of the FHIR server (e.g., "https://hapi.fhir.org/baseR4")
- `auth` (tuple, optional): Tuple of (username, password) for basic authentication
- `timeout` (int): Request timeout in seconds (default: 30)
- `verify_ssl` (bool): Whether to verify SSL certificates (default: True)

**Example:**
```python
client = FHIRClient(
    base_url="https://hapi.fhir.org/baseR4",
    auth=("username", "password"),
    timeout=60
)
```

#### Methods

##### `create_resource(resource: Dict[str, Any]) -> Dict[str, Any]`

Create a new FHIR resource.

**Parameters:**
- `resource` (dict): Dictionary representing the FHIR resource (must include `resourceType`)

**Returns:**
- Dict: Created resource with server-assigned ID

**Raises:**
- `FHIRClientError`: If creation fails or resource is invalid

**Example:**
```python
patient = {
    "resourceType": "Patient",
    "name": [{"family": "Doe", "given": ["John"]}]
}
created = client.create_resource(patient)
print(f"Created with ID: {created['id']}")
```

##### `read_resource(resource_type: str, resource_id: str) -> Dict[str, Any]`

Read a resource by type and ID.

**Parameters:**
- `resource_type` (str): Type of resource (e.g., "Patient", "Observation")
- `resource_id` (str): ID of the resource

**Returns:**
- Dict: The requested resource

**Raises:**
- `FHIRResourceNotFoundError`: If resource doesn't exist
- `FHIRClientError`: For other errors

**Example:**
```python
patient = client.read_resource("Patient", "123")
```

##### `update_resource(resource: Dict[str, Any]) -> Dict[str, Any]`

Update an existing resource.

**Parameters:**
- `resource` (dict): Resource dictionary (must include `id` and `resourceType`)

**Returns:**
- Dict: Updated resource

**Raises:**
- `FHIRClientError`: If update fails or resource is invalid

**Example:**
```python
patient["name"][0]["given"] = ["Jane"]
updated = client.update_resource(patient)
```

##### `delete_resource(resource_type: str, resource_id: str) -> bool`

Delete a resource.

**Parameters:**
- `resource_type` (str): Type of resource
- `resource_id` (str): ID of the resource

**Returns:**
- bool: True if deletion was successful

**Raises:**
- `FHIRClientError`: If deletion fails

**Example:**
```python
success = client.delete_resource("Patient", "123")
```

##### `search(resource_type: str, search_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`

Search for resources.

**Parameters:**
- `resource_type` (str): Type of resource to search
- `search_params` (dict, optional): Search parameters

**Returns:**
- Dict: Bundle of matching resources

**Example:**
```python
results = client.search("Patient", {
    "family": "Smith",
    "gender": "male",
    "_count": "10"
})
print(f"Found {results['total']} patients")
```

##### `get_capability_statement() -> Dict[str, Any]`

Get the server's capability statement.

**Returns:**
- Dict: CapabilityStatement resource

**Example:**
```python
capability = client.get_capability_statement()
print(f"Server: {capability['software']['name']}")
```

##### `close()`

Close the session and clean up resources.

**Example:**
```python
client.close()
```

---

## TerminologyService

### Class: `TerminologyService`

Service for interacting with FHIR Terminology Servers. Provides operations for code validation, lookup, value set expansion, translation, and subsumption testing.

#### Constructor

```python
TerminologyService(client: FHIRClient)
```

**Parameters:**
- `client` (FHIRClient): A FHIRClient instance configured to connect to a terminology server

**Example:**
```python
from src import FHIRClient, TerminologyService

client = FHIRClient("https://tx.fhir.org/r4")
terminology = TerminologyService(client)
```

#### Class Method: `create_default`

```python
@classmethod
create_default(terminology_server_url: str = "https://tx.fhir.org/r4") -> TerminologyService
```

Create a TerminologyService with the default HL7 terminology server.

**Parameters:**
- `terminology_server_url` (str): URL of the terminology server (default: HL7's public server)

**Returns:**
- TerminologyService: Configured instance

**Example:**
```python
# Use default HL7 server
terminology = TerminologyService.create_default()

# Use custom server
terminology = TerminologyService.create_default("https://your-server.com/fhir")
```

#### Methods

##### `validate_code(code: str, system: str, display: Optional[str] = None, value_set_url: Optional[str] = None) -> Dict[str, Any]`

Validate that a code exists in a code system or value set.

**Parameters:**
- `code` (str): The code to validate
- `system` (str): Code system URL or alias (e.g., "loinc", "snomed")
- `display` (str, optional): Display name to validate
- `value_set_url` (str, optional): Value set URL to validate against

**Returns:**
- Dict: Parameters resource with validation result

**Example:**
```python
result = terminology.validate_code("29463-7", "loinc")
for param in result.get("parameter", []):
    if param["name"] == "result":
        print(f"Valid: {param['valueBoolean']}")
```

##### `is_valid_code(code: str, system: str) -> bool`

Simple check if a code is valid.

**Parameters:**
- `code` (str): The code to validate
- `system` (str): Code system URL or alias

**Returns:**
- bool: True if code is valid

**Example:**
```python
if terminology.is_valid_code("29463-7", "loinc"):
    print("Code is valid")
```

##### `lookup_code(system: str, code: str, properties: Optional[List[str]] = None) -> Dict[str, Any]`

Look up detailed information about a code.

**Parameters:**
- `system` (str): Code system URL or alias
- `code` (str): The code to look up
- `properties` (list, optional): Specific properties to retrieve

**Returns:**
- Dict: Parameters resource with code details

**Example:**
```python
result = terminology.lookup_code("loinc", "29463-7")
for param in result.get("parameter", []):
    if param["name"] == "display":
        print(f"Display: {param['valueString']}")
```

##### `get_display_name(system: str, code: str) -> Optional[str]`

Get the display name for a code.

**Parameters:**
- `system` (str): Code system URL or alias
- `code` (str): The code to look up

**Returns:**
- str or None: Display name

**Example:**
```python
display = terminology.get_display_name("loinc", "29463-7")
print(display)  # "Body weight"
```

##### `expand_value_set(value_set_url: Optional[str] = None, value_set_id: Optional[str] = None, filter_text: Optional[str] = None, offset: int = 0, count: int = 100) -> Dict[str, Any]`

Expand a value set to get all its codes.

**Parameters:**
- `value_set_url` (str, optional): Canonical URL of the value set
- `value_set_id` (str, optional): Resource ID of the value set
- `filter_text` (str, optional): Text filter for searching
- `offset` (int): Starting index for pagination
- `count` (int): Maximum codes to return

**Returns:**
- Dict: ValueSet resource with expansion

**Example:**
```python
result = terminology.expand_value_set(
    value_set_url="http://hl7.org/fhir/ValueSet/administrative-gender"
)
for code in result["expansion"]["contains"]:
    print(f"{code['code']}: {code['display']}")
```

##### `search_value_set(value_set_url: str, search_text: str, max_results: int = 20) -> List[Dict[str, str]]`

Search for codes within a value set.

**Parameters:**
- `value_set_url` (str): Value set to search in
- `search_text` (str): Text to search for
- `max_results` (int): Maximum results

**Returns:**
- List: Matching codes

**Example:**
```python
codes = terminology.search_value_set(
    "http://hl7.org/fhir/ValueSet/observation-codes",
    "blood pressure",
    max_results=5
)
```

##### `translate_code(code: str, source_system: str, target_system: str, concept_map_url: Optional[str] = None) -> Dict[str, Any]`

Translate a code from one code system to another.

**Parameters:**
- `code` (str): The code to translate
- `source_system` (str): Source code system URL or alias
- `target_system` (str): Target code system URL or alias
- `concept_map_url` (str, optional): Specific ConceptMap to use

**Returns:**
- Dict: Parameters resource with translation

**Example:**
```python
result = terminology.translate_code(
    code="I10",
    source_system="icd10",
    target_system="snomed"
)
```

##### `check_subsumption(code_a: str, code_b: str, system: str) -> Dict[str, Any]`

Check if one code subsumes another (hierarchical relationship).

**Parameters:**
- `code_a` (str): First code (potential parent)
- `code_b` (str): Second code (potential child)
- `system` (str): Code system URL or alias

**Returns:**
- Dict: Parameters with outcome (equivalent, subsumes, subsumed-by, not-subsumed)

**Example:**
```python
result = terminology.check_subsumption(
    code_a="49601007",  # Cardiovascular disease
    code_b="22298006",  # Myocardial infarction
    system="snomed"
)
# outcome: "subsumes" (cardiovascular disease includes MI)
```

#### Code System Aliases

The following aliases can be used instead of full URLs:

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

## Resource Models

### Class: `Patient`

Helper class for Patient resources.

#### Static Methods

##### `create(family_name, given_names, gender=None, birth_date=None, **kwargs)`

Create a Patient resource.

**Parameters:**
- `family_name` (str): Family name (surname)
- `given_names` (list): List of given names
- `gender` (str, optional): Gender (male, female, other, unknown)
- `birth_date` (str, optional): Birth date (YYYY-MM-DD)
- `**kwargs`: Additional FHIR fields

**Returns:**
- Dict: Patient resource

**Example:**
```python
from src.models import Patient

patient = Patient.create(
    family_name="Smith",
    given_names=["John", "Jacob"],
    gender="male",
    birth_date="1990-05-15"
)
```

##### `validate(resource: Dict[str, Any]) -> bool`

Validate a Patient resource.

**Parameters:**
- `resource` (dict): Patient resource to validate

**Returns:**
- bool: True if valid

**Raises:**
- `ValueError`: If validation fails

##### `get_full_name(patient: Dict[str, Any]) -> str`

Extract full name from Patient resource.

**Parameters:**
- `patient` (dict): Patient resource

**Returns:**
- str: Full name

### Class: `Observation`

Helper class for Observation resources.

#### Static Methods

##### `create(patient_reference, code, value, status="final", effective_datetime=None, **kwargs)`

Create an Observation resource.

**Parameters:**
- `patient_reference` (str): Reference to patient (e.g., "Patient/123")
- `code` (dict): Observation code
- `value` (any): Observation value
- `status` (str): Status (default: "final")
- `effective_datetime` (str, optional): ISO 8601 datetime
- `**kwargs`: Additional fields

**Returns:**
- Dict: Observation resource

**Example:**
```python
from src.models import Observation

obs = Observation.create(
    patient_reference="Patient/123",
    code={"coding": [{"system": "http://loinc.org", "code": "15074-8"}]},
    value={"value": 95, "unit": "mg/dL"}
)
```

##### `create_vital_sign(patient_reference, vital_type, value, unit, **kwargs)`

Create a vital sign observation (shorthand).

**Parameters:**
- `patient_reference` (str): Patient reference
- `vital_type` (str): Type of vital sign (heart_rate, blood_pressure_systolic, etc.)
- `value` (float): Numeric value
- `unit` (str): Unit of measure

**Returns:**
- Dict: Observation resource

**Example:**
```python
heart_rate = Observation.create_vital_sign(
    patient_reference="Patient/123",
    vital_type="heart_rate",
    value=72,
    unit="beats/min"
)
```

**Available vital types:**
- `heart_rate`
- `blood_pressure_systolic`
- `blood_pressure_diastolic`
- `temperature`
- `respiratory_rate`
- `oxygen_saturation`

---

## Operations

Wrapper functions for CRUD operations.

### `create_resource(fhir_client, resource)`
### `read_resource(fhir_client, resource_type, resource_id)`
### `update_resource(fhir_client, resource)`
### `delete_resource(fhir_client, resource_type, resource_id)`

These functions delegate to the FHIRClient methods.

---

## Utilities

### Configuration

#### Class: `FHIRConfig`

Configuration management.

**Attributes:**
- `base_url`: FHIR server URL
- `username`: Authentication username
- `password`: Authentication password
- `timeout`: Request timeout
- `verify_ssl`: SSL verification flag
- `log_level`: Logging level

**Environment Variables:**
- `FHIR_SERVER_URL`
- `FHIR_USERNAME`
- `FHIR_PASSWORD`
- `FHIR_TIMEOUT`
- `FHIR_VERIFY_SSL`
- `FHIR_LOG_LEVEL`

### Logging

#### `setup_logging(level="INFO", log_file=None)`

Configure logging.

**Parameters:**
- `level` (str): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `log_file` (str, optional): Path to log file

**Example:**
```python
from src.utils.logger import setup_logging

setup_logging(level="DEBUG", log_file="fhir_client.log")
```

#### `get_logger(name)`

Get a logger instance.

---

## Exceptions

### `FHIRClientError`
Base exception for all FHIR client errors.

### `FHIRConnectionError`
Raised when connection to server fails.

### `FHIRAuthenticationError`
Raised when authentication fails (401, 403).

### `FHIRResourceNotFoundError`
Raised when a resource is not found (404).

### `FHIRValidationError`
Raised when resource validation fails.

### `FHIROperationError`
Raised when a FHIR operation fails.

**Example:**
```python
from src.utils.errors import FHIRResourceNotFoundError

try:
    patient = client.read_resource("Patient", "nonexistent")
except FHIRResourceNotFoundError:
    print("Patient not found")
```

---

## Search Parameters

Common search parameters for all resources:
- `_id`: Resource ID
- `_lastUpdated`: Last update date
- `_count`: Number of results
- `_sort`: Sort order (prefix with `-` for descending)
- `_summary`: Summary mode (count, true, false)
- `_text`: Text search

Resource-specific parameters:
- **Patient**: `family`, `given`, `gender`, `birthdate`, `identifier`
- **Observation**: `code`, `patient`, `date`, `status`, `category`

**Example:**
```python
# Search with multiple parameters
results = client.search("Patient", {
    "family": "Smith",
    "gender": "male",
    "birthdate": "gt1990",
    "_count": "20",
    "_sort": "-_lastUpdated"
})
```

---

For more examples, see the [examples/](examples/) directory.
