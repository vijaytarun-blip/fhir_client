# FHIR Client API Reference

## Table of Contents
1. [FHIRClient](#fhirclient)
2. [Resource Models](#resource-models)
3. [Operations](#operations)
4. [Utilities](#utilities)
5. [Exceptions](#exceptions)

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
