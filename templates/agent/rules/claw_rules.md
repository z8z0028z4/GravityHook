# Repository Rules for OpenClaw

> This file defines the development principles and constraints that OpenClaw should follow for this specific repository.

## Development Philosophy

### 1. Async-First Approach
- All I/O operations (file, network, database) MUST use async/await
- Use `asyncio` for concurrent operations
- Prefer `aiofiles` for file operations over synchronous `open()`

### 2. Strong Typing
- All functions must have type hints for parameters and return values
- Use Pydantic models for data validation and serialization
- Avoid `Any` type unless absolutely necessary

### 3. Code Quality Standards
- Maximum function length: 50 lines
- Maximum file length: 500 lines
- Use descriptive variable names (no single-letter variables except in comprehensions)
- All public functions must have docstrings

### 4. Testing Requirements
- Every new feature must have corresponding unit tests
- Minimum 80% code coverage
- Use `pytest` for all testing
- Mock external dependencies in tests

### 5. Error Handling
- Never use bare `except:` clauses
- Always log errors with context
- Use custom exception classes for domain-specific errors
- Fail fast and fail loud - don't suppress errors

## Project-Specific Rules

### Architecture Constraints
- Follow layered architecture: API → Services → Data Access
- No circular dependencies between modules
- Database models should not leak into API layer (use DTOs)

### Performance Guidelines
- Response time for API endpoints should be < 200ms
- Use database indexes for frequently queried fields
- Implement caching for expensive operations

### Security Requirements
- Never commit secrets or API keys
- Use environment variables for configuration
- Sanitize all user inputs
- Implement rate limiting on public endpoints

## Documentation Standards
- Update README.md when adding new features
- Maintain API documentation using OpenAPI/Swagger
- Document breaking changes in CHANGELOG.md

---

## 🔧 Customization Notes

This template can be customized per repository. OpenClaw should:
1. Read this file at the start of every session
2. Alert if proposed changes violate these rules
3. Reference specific rules when explaining design decisions

For questions about these rules, consult the human engineer.
