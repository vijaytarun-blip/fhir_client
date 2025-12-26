# FHIR Client Examples

This directory contains example scripts demonstrating various features of the FHIR client.

## Available Examples

### 1. basic_usage.py
Demonstrates basic CRUD operations:
- Creating a Patient resource
- Reading a resource by ID
- Updating an existing resource
- Searching for resources
- Deleting a resource

**Run:**
```bash
python examples/basic_usage.py
```

### 2. observations_example.py
Shows how to work with Observation resources:
- Creating vital sign observations (heart rate, blood pressure, temperature, etc.)
- Creating custom observations
- Searching for patient observations
- Retrieving and displaying observation data

**Run:**
```bash
python examples/observations_example.py
```

### 3. search_example.py
Demonstrates advanced search capabilities:
- Simple name-based searches
- Multi-parameter searches
- Sorting results
- Text filtering
- Count-only queries

**Run:**
```bash
python examples/search_example.py
```

## Prerequisites

Before running the examples, ensure you have:

1. Installed the package:
```bash
pip install -e .
```

2. Or installed dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

By default, examples use the public HAPI FHIR test server:
- **URL:** https://hapi.fhir.org/baseR4
- **Version:** FHIR R4

To use a different server, modify the `base_url` parameter in the examples or set the `FHIR_SERVER_URL` environment variable:

```bash
export FHIR_SERVER_URL="https://your-fhir-server.com/fhir"
python examples/basic_usage.py
```

## Notes

- The public test server may have rate limits
- Resources created on the test server may be periodically cleaned up
- Some operations (like delete) are commented out to prevent accidental data loss
- All examples include proper error handling and logging
