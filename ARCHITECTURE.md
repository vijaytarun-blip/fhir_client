# FHIR Client - Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FHIR Client Library                          │
│                          (Version 1.0.0)                             │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                          User Application                            │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────────────┐   │
│  │   Basic CRUD  │  │  Search/Query │  │  Resource Management │   │
│  └───────────────┘  └───────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FHIRClient (Main Class)                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ • create_resource()      • search()                          │  │
│  │ • read_resource()        • get_capability_statement()        │  │
│  │ • update_resource()      • Session Management                │  │
│  │ • delete_resource()      • Retry Logic                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  Resource Models │  │    Operations    │  │    Utilities     │
│ ┌──────────────┐ │  │ ┌──────────────┐ │  │ ┌──────────────┐ │
│ │   Patient    │ │  │ │   create.py  │ │  │ │   config.py  │ │
│ │ • create()   │ │  │ │   read.py    │ │  │ │   errors.py  │ │
│ │ • validate() │ │  │ │   update.py  │ │  │ │   logger.py  │ │
│ │ • get_name() │ │  │ │   delete.py  │ │  │ └──────────────┘ │
│ └──────────────┘ │  │ └──────────────┘ │  └──────────────────┘
│ ┌──────────────┐ │  └──────────────────┘
│ │ Observation  │ │
│ │ • create()   │ │
│ │ • vital()    │ │
│ │ • validate() │ │
│ └──────────────┘ │
└──────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        HTTP Layer (Requests)                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ • Connection Pooling     • Timeout Management                │  │
│  │ • Retry with Backoff     • SSL Verification                  │  │
│  │ • Authentication         • Error Handling                    │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         FHIR Server                                  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ HAPI FHIR (https://hapi.fhir.org/baseR4)                     │  │
│  │ • RESTful API                                                │  │
│  │ • FHIR R4 Compliant                                          │  │
│  │ • CapabilityStatement                                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌──────────────┐
│     User     │
└──────┬───────┘
       │ 1. Call method
       ▼
┌──────────────────────────┐
│     FHIRClient           │
│  - Validate input        │
│  - Prepare request       │
└──────┬───────────────────┘
       │ 2. HTTP Request
       ▼
┌──────────────────────────┐
│   Requests Session       │
│  - Add headers           │
│  - Handle auth           │
│  - Apply retry logic     │
└──────┬───────────────────┘
       │ 3. Send to server
       ▼
┌──────────────────────────┐
│     FHIR Server          │
│  - Process request       │
│  - Return response       │
└──────┬───────────────────┘
       │ 4. Response
       ▼
┌──────────────────────────┐
│   Error Handling         │
│  - Check status          │
│  - Parse response        │
│  - Raise exceptions      │
└──────┬───────────────────┘
       │ 5. Return data
       ▼
┌──────────────────────────┐
│     User                 │
│  - Receive resource      │
└──────────────────────────┘
```

## Component Responsibilities

### FHIRClient
- Main interface for all FHIR operations
- Session and connection management
- Request/response handling
- Retry logic implementation
- Authentication management

### Resource Models
- Simplify resource creation
- Provide validation
- Helper methods for common operations
- Type-safe interfaces

### Operations Module
- Wrapper functions for CRUD
- Additional business logic
- Operation-specific logging

### Utilities
- **config.py**: Environment and configuration
- **errors.py**: Exception hierarchy
- **logger.py**: Logging setup and management

### Tests
- Unit tests with mocks
- Integration test examples
- Coverage reporting

### Examples
- Real-world usage patterns
- Best practices demonstration
- Quick start templates

## Error Handling Flow

```
┌─────────────────────┐
│   Request Failed    │
└─────────┬───────────┘
          │
          ├─── 401/403 ──→ FHIRAuthenticationError
          │
          ├─── 404 ──────→ FHIRResourceNotFoundError
          │
          ├─── 400-499 ──→ FHIRValidationError
          │
          ├─── 500+ ─────→ FHIROperationError
          │
          └─── Network ──→ FHIRConnectionError
```

## Configuration Hierarchy

```
1. Code Parameters (Highest Priority)
   client = FHIRClient(base_url="...", auth=...)
   
2. Environment Variables
   FHIR_SERVER_URL=...
   FHIR_USERNAME=...
   
3. Default Configuration
   FHIRConfig.DEFAULT_SERVERS['hapi-r4']
```

## Testing Strategy

```
┌─────────────────────────────────────┐
│          Unit Tests                 │
│  • Mock all external calls          │
│  • Test individual methods          │
│  • Verify error handling            │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│       Integration Tests             │
│  • Test with real FHIR server       │
│  • End-to-end workflows             │
│  • Example scripts validation       │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│         CI/CD Pipeline              │
│  • Automated on push                │
│  • Multi-Python version testing     │
│  • Code quality checks              │
└─────────────────────────────────────┘
```

## Key Design Decisions

1. **Session Reuse**: Single session with connection pooling for performance
2. **Retry Logic**: Exponential backoff for resilience
3. **Type Hints**: Throughout for better IDE support and type checking
4. **Model Classes**: Static methods for easy resource creation
5. **Modular Design**: Separation of concerns for maintainability
6. **Comprehensive Logging**: Configurable logging for debugging
7. **Error Hierarchy**: Specific exceptions for different error types
8. **Environment Config**: Flexible configuration via env vars

## Performance Optimizations

- Connection pooling (HTTPAdapter)
- Session reuse
- Configurable timeouts
- Retry with exponential backoff
- Efficient error handling

## Security Considerations

- SSL verification (configurable)
- Basic authentication support
- Credential handling via environment variables
- No hardcoded secrets
- Secure default configuration

---

This architecture provides a solid foundation for FHIR client operations
while maintaining flexibility, testability, and production-readiness.
