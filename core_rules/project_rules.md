# Project Development Rules v2.0

> Global development guidelines template. Customize for your specific project needs.

## 🎯 Core Development Philosophy

### 1. Async-First Architecture
- **Principle**: All I/O operations must be non-blocking
- **Implementation**:
  - Use `async/await` for file, network, and database operations
  - Prefer `asyncio` for concurrent task management
  - Use `aiofiles` instead of synchronous `open()`
  - Use `httpx` instead of `requests` for HTTP calls
  
**Rationale**: Non-blocking I/O improves scalability and resource utilization.

### 2. Strong Typing & Data Validation
- **Principle**: Explicit types everywhere, runtime validation at boundaries
- **Implementation**:
  - All function signatures must have type hints
  - Use Pydantic models for data structures and API contracts
  - Avoid `Any` type unless dealing with truly dynamic data
  - Enable strict mypy checking in CI/CD
  
**Rationale**: Catch errors at compile-time, not runtime. Self-documenting code.

### 3. Modular Design & Dependency Injection
- **Principle**: Loose coupling, high cohesion
- **Implementation**:
  - Layered architecture: API → Services → Data Access
  - No circular dependencies between modules
  - Use dependency injection for testability
  - Interfaces (Protocols) for abstraction

**Rationale**: Easier testing, maintenance, and future refactoring.

---

## 📐 Code Quality Standards

### Naming Conventions
- **Functions**: `snake_case`, verb-first (`get_user`, `validate_token`)
- **Classes**: `PascalCase`, noun-based (`User`, `TokenValidator`)
- **Constants**: `UPPER_SNAKE_CASE` (`MAX_RETRY_COUNT`)
- **Private members**: Leading underscore (`_internal_method`)

### Function Guidelines
- **Maximum length**: 50 lines per function
- **Maximum parameters**: 5 parameters
- **Single responsibility**: One clear purpose per function
- **Docstrings**: Required for all public functions

**Example**:
```python
async def authenticate_user(
    username: str,
    password: str,
    session: AsyncSession
) -> AuthToken:
    """
    Authenticate user and return JWT token.
    
    Args:
        username: User's login username
        password: Plain text password (will be hashed)
        session: Database session for user lookup
    
    Returns:
        AuthToken containing JWT and refresh token
    
    Raises:
        AuthenticationError: If credentials are invalid
    """
    # Implementation...
```

### File Organization
- **Maximum file length**: 500 lines
- **One class per file** (except tiny helper classes)
- **Imports order**: stdlib → third-party → local
- **Group related functions** with blank line separators

---

## 🧪 Testing Requirements

### Coverage
- **Minimum**: 80% code coverage
- **Critical paths**: 100% coverage (auth, payments, data validation)
- **Use**: `pytest-cov` for measurement

### Test Structure
```python
# tests/test_authentication.py
import pytest
from unittest.mock import AsyncMock

class TestAuthenticationService:
    @pytest.mark.asyncio
    async def test_successful_login(self):
        # Given
        mock_session = AsyncMock()
        service = AuthenticationService(mock_session)
        
        # When
        token = await service.authenticate("user@example.com", "password123")
        
        # Then
        assert token.access_token is not None
        assert token.expires_in == 3600
```

### Mocking
- **External services**: Always mock (APIs, databases)
- **Time-dependent code**: Use `freezegun` or similar
- **File system**: Use `pytest.tmp_path` fixture

---

## 🔒 Security Standards

### Input Validation
- **Never trust user input**: Validate everything at API boundary
- **Use Pydantic**: For automatic validation and sanitization
- **SQL injection**: Always use parameterized queries or ORM

### Secrets Management
- **Never commit**: API keys, passwords, tokens
- **Use environment variables**: For configuration
- **Use secret managers**: For production (AWS Secrets Manager, Vault)

### Authentication & Authorization
- **Use established libraries**: Don't roll your own crypto
- **JWT best practices**: Short expiration, refresh tokens
- **Rate limiting**: On all public endpoints

---

## ⚡ Performance Guidelines

### Database
- **Indexes**: On frequently queried fields
- **N+1 queries**: Use eager loading or batch queries
- **Connection pooling**: Always configure properly
- **Caching**: Redis for frequently accessed data

### API Response Times
- **Target**: < 200ms for simple queries
- **Target**: < 1s for complex operations
- **Monitoring**: Use APM tools (New Relic, DataDog)

### Optimization
- **Profile before optimizing**: Don't guess
- **Async for I/O**: Threads for CPU-bound tasks
- **Batch operations**: Where possible

---

## 📝 Documentation Standards

### Code Comments
- **Why, not what**: Explain reasoning, not obvious code
- **TODOs**: Include ticket number (`# TODO(PROJ-123): Refactor this`)
- **Warnings**: Mark dangerous code (`# WARNING: Thread-unsafe`)

### API Documentation
- **OpenAPI/Swagger**: Auto-generated from code
- **Examples**: Include request/response samples
- **Errors**: Document all possible error codes

### Project Documentation
- **README.md**: Setup, usage, architecture overview
- **CHANGELOG.md**: All breaking changes and major features
- **ARCHITECTURE.md**: System design and component relationships

---

## 🚀 Deployment & CI/CD

### Pre-commit Checks
- Linting (`ruff` or `pylint`)
- Type checking (`mypy`)
- Unit tests (`pytest`)
- Code formatting (`black`)

### CI Pipeline
1. Install dependencies
2. Run linters
3. Run type checker
4. Run unit tests
5. Run integration tests
6. Build Docker image
7. Deploy to staging (auto)
8. Deploy to production (manual approval)

---

## 🛠️ Error Handling

### Exception Strategy
- **Custom exceptions**: For domain-specific errors
- **Never silence**: Always log or propagate
- **Fail fast**: Don't continue with invalid state

**Example**:
```python
class AuthenticationError(Exception):
    """Raised when user authentication fails."""
    pass

async def login(username: str, password: str) -> User:
    user = await get_user(username)
    
    if not user or not verify_password(password, user.password_hash):
        raise AuthenticationError(f"Invalid credentials for {username}")
    
    return user
```

### Logging
- **Structured logging**: Use JSON format for production
- **Log levels**: ERROR for problems, INFO for major events, DEBUG for details
- **Context**: Include request ID, user ID where relevant

---

## 🔄 Version Control

### Commit Messages
Format: `<type>(<scope>): <subject>`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Build/tooling changes

Example: `feat(auth): add JWT refresh token support`

### Branching Strategy
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `hotfix/*`: Emergency production fixes

---

## 📊 Monitoring & Observability

### Metrics to Track
- Request latency (p50, p95, p99)
- Error rate (4xx, 5xx)
- Database query time
- External API call success rate

### Alerts
- Error rate > 1%
- Latency p95 > 500ms
- Database connection pool exhausted
- Disk usage > 80%

---

## 🤝 Code Review Checklist

Before requesting review:
- [ ] Code follows project style guide
- [ ] All tests pass locally
- [ ] No commented-out code
- [ ] No hardcoded values
- [ ] Docstrings updated
- [ ] CHANGELOG.md updated (if user-facing change)
- [ ] Security implications considered

During review:
- [ ] Logic is sound and handles edge cases
- [ ] Error handling is appropriate
- [ ] No performance anti-patterns
- [ ] Code is maintainable and readable

---

## 📦 Dependency Management

### Adding Dependencies
1. Evaluate necessity (don't add for trivial functionality)
2. Check license compatibility
3. Review security advisories
4. Add to `requirements.txt` or `pyproject.toml`
5. Document why it was added

### Updating Dependencies
- Security patches: Immediately
- Minor versions: Monthly
- Major versions: Quarterly (with testing)

---

## ✨ Best Practices Summary

1. **Write tests first** (TDD when practical)
2. **Keep functions small** (single responsibility)
3. **Use type hints everywhere**
4. **Validate at boundaries** (API entry points)
5. **Log meaningful events** (with context)
6. **Document "why"** (not "what")
7. **Profile before optimizing**
8. **Review your own code** (before requesting review)
9. **Automate everything** (testing, deployment, checks)
10. **Think about maintainability** (code is read more than written)

---

**Remember**: These rules exist to make development faster and safer in the long run. If a rule doesn't make sense for a specific situation, discuss with the team rather than silently breaking it.

**Last Updated**: 2026-02-05  
**Version**: 2.0  
**Maintained by**: Project Lead
