# FHIR Client

A comprehensive Python client for interacting with FHIR (Fast Healthcare Interoperability Resources) servers. This library provides an easy-to-use interface for performing CRUD operations, searching resources, and working with FHIR data.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

✨ **Core Functionality**
- 🔄 **Full CRUD Operations**: Create, Read, Update, and Delete FHIR resources
- 🔍 **Advanced Search**: Support for complex search queries with multiple parameters
- 📦 **Resource Models**: Helper classes for Patient and Observation resources
- 🔐 **Authentication**: Support for basic authentication
- 🛡️ **Error Handling**: Comprehensive error handling with custom exceptions
- 📊 **Logging**: Configurable logging for debugging and monitoring
- 🔄 **Retry Logic**: Automatic retries with exponential backoff
- 🌐 **Public Server Support**: Works with public FHIR test servers out-of-the-box

🏥 **Terminology Services**
- 📖 **Code Lookup**: Retrieve details about clinical codes (SNOMED, LOINC, ICD-10)
- ✅ **Code Validation**: Validate codes exist in code systems or value sets
- 📋 **Value Set Expansion**: List all codes in a value set
- 🔄 **Code Translation**: Map codes between different terminologies
- 🌳 **Subsumption Testing**: Check hierarchical relationships between codes

## Installation

### From Source

```bash
git clone https://github.com/vijaytarun-blip/fhir_client.git
cd fhir_client
pip install -e .
```

### Using pip

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from src.client import FHIRClient
from src.models import Patient

# Initialize the client
client = FHIRClient(base_url="https://hapi.fhir.org/baseR4")

# Create a patient
patient = Patient.create(
    family_name="Doe",
    given_names=["John"],
    gender="male",
    birth_date="1980-01-01"
)

# Create on server
created_patient = client.create_resource(patient)
print(f"Created patient with ID: {created_patient['id']}")

# Read the patient
patient = client.read_resource("Patient", created_patient['id'])
print(f"Patient name: {Patient.get_full_name(patient)}")

# Search for patients
results = client.search("Patient", {"family": "Doe"})
print(f"Found {results['total']} patients")

# Clean up
client.close()
```

### Working with Observations

```python
from src.models import Observation

# Create a vital sign observation
heart_rate = Observation.create_vital_sign(
    patient_reference="Patient/123",
    vital_type="heart_rate",
    value=72,
    unit="beats/min"
)

created_obs = client.create_resource(heart_rate)
```

### Working with Terminology Services

```python
from src import TerminologyService

# Connect to HL7's public terminology server
terminology = TerminologyService.create_default()

# Look up a LOINC code
display = terminology.get_display_name("loinc", "29463-7")
print(f"Code display: {display}")  # "Body weight"

# Validate a code exists
is_valid = terminology.is_valid_code("29463-7", "loinc")
print(f"Valid: {is_valid}")  # True

# Expand a value set
result = terminology.expand_value_set(
    value_set_url="http://hl7.org/fhir/ValueSet/administrative-gender"
)
for code in result["expansion"]["contains"]:
    print(f"  {code['code']}: {code['display']}")

# Translate codes between systems (e.g., ICD-10 to SNOMED)
translation = terminology.translate_code(
    code="I10",
    source_system="icd10",
    target_system="snomed"
)
```

For detailed terminology documentation, see [TERMINOLOGY_SERVER.md](TERMINOLOGY_SERVER.md).

## Configuration

### Environment Variables

Configure the client using environment variables:

```bash
export FHIR_SERVER_URL="https://hapi.fhir.org/baseR4"
export FHIR_USERNAME="your_username"
export FHIR_PASSWORD="your_password"
export FHIR_TIMEOUT="30"
export FHIR_VERIFY_SSL="true"
export FHIR_LOG_LEVEL="INFO"
```

### Programmatic Configuration

```python
from src.client import FHIRClient

client = FHIRClient(
    base_url="https://hapi.fhir.org/baseR4",
    auth=("username", "password"),
    timeout=60,
    verify_ssl=True
)
```

## Project Structure

```
fhir-client/
├── src/
│   ├── __init__.py
│   ├── client.py              # Main FHIRClient class
│   ├── terminology.py         # TerminologyService for code operations
│   ├── models/
│   │   ├── __init__.py
│   │   ├── patient.py         # Patient resource helpers
│   │   └── observation.py     # Observation resource helpers
│   ├── operations/
│   │   ├── __init__.py
│   │   ├── create.py          # Create operations
│   │   ├── read.py            # Read operations
│   │   ├── update.py          # Update operations
│   │   └── delete.py          # Delete operations
│   └── utils/
│       ├── __init__.py
│       ├── config.py          # Configuration management
│       ├── errors.py          # Custom exceptions
│       └── logger.py          # Logging setup
├── tests/
│   ├── __init__.py
│   ├── test_client.py         # Client tests
│   └── test_operations.py     # Operations tests
├── examples/
│   ├── basic_usage.py         # Basic CRUD examples
│   ├── observations_example.py # Observation examples
│   ├── search_example.py      # Search examples
│   └── terminology_example.py # Terminology server examples
├── requirements.txt           # Dependencies
├── setup.py                   # Package setup
├── TERMINOLOGY_SERVER.md      # Terminology documentation
├── LICENSE                    # MIT License
└── README.md                  # This file
```

## Running Tests

### Run all tests

```bash
python -m pytest tests/
```

### Run with coverage

```bash
python -m pytest tests/ --cov=src --cov-report=html
```

### Run specific test file

```bash
python -m pytest tests/test_client.py -v
```

## Examples

See the [examples/](examples/) directory for complete working examples:

- **basic_usage.py**: Basic CRUD operations
- **observations_example.py**: Working with observations and vital signs
- **search_example.py**: Advanced search and filtering

Run examples:

```bash
python examples/basic_usage.py
```

python examples/basic_usage.py
```

## Error Handling

The library provides custom exceptions for different error scenarios:

```python
from src.client import FHIRClient, FHIRClientError
from src.utils.errors import (
    FHIRConnectionError,
    FHIRAuthenticationError,
    FHIRResourceNotFoundError,
    FHIRValidationError
)

try:
    client = FHIRClient(base_url="https://hapi.fhir.org/baseR4")
    patient = client.read_resource("Patient", "nonexistent-id")
except FHIRResourceNotFoundError:
    print("Patient not found")
except FHIRAuthenticationError:
    print("Authentication failed")
except FHIRClientError as e:
    print(f"FHIR error: {e}")
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Resources

- [FHIR Specification](https://www.hl7.org/fhir/)
- [FHIR Terminology Services](https://hl7.org/fhir/terminology-service.html)
- [HAPI FHIR Documentation](https://hapifhir.io/)
- [FHIR Resource List](https://www.hl7.org/fhir/resourcelist.html)
- [HL7 Terminology Server](https://tx.fhir.org)

---

**Note**: This is a client library for development and testing. For production use, ensure proper security measures, authentication, and compliance with healthcare data regulations (HIPAA, GDPR, etc.).