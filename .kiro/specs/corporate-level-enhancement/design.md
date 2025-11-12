# Design Document: Corporate-Level Enhancement

## Overview

This design document outlines the architecture and implementation strategy for transforming the AI Supplier Selection & Risk Management Dashboard into an enterprise-grade, production-ready application. The enhancement introduces critical corporate features including authentication, authorization, comprehensive audit logging, data security, scalability improvements, monitoring, and compliance capabilities.

### Design Principles

1. **Security First**: All components prioritize security with defense-in-depth strategies
2. **Scalability**: Horizontal scaling support with stateless services and connection pooling
3. **Observability**: Comprehensive logging, monitoring, and alerting for operational excellence
4. **Compliance**: Built-in audit trails and data protection for regulatory requirements
5. **Backward Compatibility**: Maintain existing API functionality while adding enterprise features
6. **Performance**: Sub-500ms response times under load with caching and optimization

### Current Architecture Context

The existing application is built on:
- **Backend**: FastAPI (Python) with ML/NLP services
- **Frontend**: Streamlit dashboard
- **Database**: PostgreSQL (optional, currently minimal usage)
- **Deployment**: Render platform (separate backend/frontend services)

The current implementation has basic CORS security and health checks but lacks enterprise-grade features required for corporate deployment.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         API Gateway Layer                        │
│  (Rate Limiting, Request Validation, CORS, TLS Termination)     │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                    Authentication Middleware                     │
│         (JWT Validation, Session Management, MFA)               │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                   Authorization Middleware                       │
│              (RBAC, Permission Checks, Resource Access)          │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                      FastAPI Application                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Supplier   │  │     Risk     │  │    Fraud     │         │
│  │  Evaluation  │  │   Profiling  │  │  Detection   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │     NLP      │  │   Decision   │  │    Ethics    │         │
│  │   Contract   │  │   Support    │  │  Compliance  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                      Service Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │    Audit     │  │  Encryption  │  │    Cache     │         │
│  │   Service    │  │   Service    │  │   Service    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Monitoring  │  │    Backup    │  │   Webhook    │         │
│  │   Service    │  │   Service    │  │   Service    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                      Data Layer                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  PostgreSQL  │  │    Redis     │  │   S3/Blob    │         │
│  │   Database   │  │    Cache     │  │   Storage    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack Additions

**New Dependencies:**
- **Authentication**: PyJWT, passlib, python-jose
- **Database**: SQLAlchemy ORM (enhanced), alembic (migrations)
- **Caching**: redis-py, aioredis
- **Monitoring**: prometheus-client, opentelemetry
- **Logging**: structlog, python-json-logger
- **Security**: cryptography, python-multipart
- **Rate Limiting**: slowapi, limits
- **Validation**: pydantic (already present, enhanced usage)


## Components and Interfaces

### 1. Authentication Service

**Purpose**: Manage user authentication, session creation, and multi-factor authentication.

**Design Rationale**: JWT-based stateless authentication allows horizontal scaling while Redis provides session state for features like concurrent session limits and immediate token revocation.

**Components:**

```python
# backend/services/auth_service.py
class AuthenticationService:
    - authenticate_user(username: str, password: str) -> TokenResponse
    - create_session(user_id: str, metadata: dict) -> Session
    - validate_token(token: str) -> TokenPayload
    - refresh_token(refresh_token: str) -> TokenResponse
    - revoke_session(session_id: str) -> bool
    - verify_mfa(user_id: str, code: str) -> bool
    - generate_mfa_secret(user_id: str) -> str
```

**Token Structure:**
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "roles": ["analyst", "viewer"],
  "session_id": "uuid",
  "exp": 1234567890,
  "iat": 1234567890,
  "jti": "token_id"
}
```

**Session Storage (Redis):**
```json
{
  "session:{session_id}": {
    "user_id": "user_id",
    "created_at": "timestamp",
    "last_activity": "timestamp",
    "ip_address": "x.x.x.x",
    "user_agent": "browser_info",
    "mfa_verified": true
  }
}
```

**API Endpoints:**
- `POST /api/v1/auth/login` - User login with credentials
- `POST /api/v1/auth/logout` - Session termination
- `POST /api/v1/auth/refresh` - Token refresh
- `POST /api/v1/auth/mfa/setup` - MFA enrollment
- `POST /api/v1/auth/mfa/verify` - MFA verification
- `GET /api/v1/auth/sessions` - List active sessions
- `DELETE /api/v1/auth/sessions/{session_id}` - Terminate specific session


### 2. Authorization Service

**Purpose**: Implement role-based access control (RBAC) with granular permissions.

**Design Rationale**: Separate authorization from authentication allows flexible permission management. Role hierarchy enables inheritance and reduces configuration complexity.

**Role Hierarchy:**
```
Super Admin
  └─> Admin
       └─> Analyst
            └─> Viewer
```

**Permission Model:**
```python
# backend/models/authorization.py
class Permission(Enum):
    SUPPLIER_READ = "supplier:read"
    SUPPLIER_WRITE = "supplier:write"
    SUPPLIER_DELETE = "supplier:delete"
    RISK_READ = "risk:read"
    RISK_WRITE = "risk:write"
    FRAUD_READ = "fraud:read"
    FRAUD_WRITE = "fraud:write"
    CONTRACT_READ = "contract:read"
    CONTRACT_WRITE = "contract:write"
    AUDIT_READ = "audit:read"
    USER_MANAGE = "user:manage"
    SYSTEM_ADMIN = "system:admin"

class Role(BaseModel):
    name: str
    permissions: List[Permission]
    inherits_from: Optional[str]
```

**Default Roles:**
- **Viewer**: Read-only access to all modules
- **Analyst**: Read/write access to supplier, risk, fraud, contract modules
- **Admin**: All analyst permissions + user management + audit log access
- **Super Admin**: All permissions including system configuration

**Components:**
```python
# backend/services/authorization_service.py
class AuthorizationService:
    - check_permission(user_id: str, permission: Permission) -> bool
    - get_user_roles(user_id: str) -> List[Role]
    - assign_role(user_id: str, role: str) -> bool
    - remove_role(user_id: str, role: str) -> bool
    - create_custom_role(role: Role) -> bool
```

**Middleware Implementation:**
```python
# backend/middleware/authorization.py
@app.middleware("http")
async def authorization_middleware(request: Request, call_next):
    # Extract user from JWT token
    # Check required permission for endpoint
    # Allow/deny based on user roles
```

**Decorator for Route Protection:**
```python
@require_permission(Permission.SUPPLIER_WRITE)
async def create_supplier(supplier: SupplierCreate):
    pass
```


### 3. Audit Logging Service

**Purpose**: Provide immutable, comprehensive audit trails for all system activities.

**Design Rationale**: Separate audit database ensures tamper-proof logs. Asynchronous logging prevents performance impact. Structured format enables efficient querying and compliance reporting.

**Components:**
```python
# backend/services/audit_service.py
class AuditService:
    - log_event(event: AuditEvent) -> None
    - query_logs(filters: AuditQuery) -> List[AuditEvent]
    - generate_compliance_report(start_date: date, end_date: date) -> bytes
    - export_logs(filters: AuditQuery, format: str) -> bytes
```

**Audit Event Schema:**
```python
class AuditEvent(BaseModel):
    id: UUID
    timestamp: datetime
    user_id: str
    user_email: str
    action: str  # CREATE, READ, UPDATE, DELETE, LOGIN, LOGOUT
    resource_type: str  # supplier, risk_profile, contract, etc.
    resource_id: Optional[str]
    ip_address: str
    user_agent: str
    request_method: str
    request_path: str
    status_code: int
    changes: Optional[dict]  # before/after state for modifications
    metadata: dict
    correlation_id: str  # for request tracing
```

**Database Schema:**
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    ip_address INET NOT NULL,
    user_agent TEXT,
    request_method VARCHAR(10),
    request_path TEXT,
    status_code INTEGER,
    changes JSONB,
    metadata JSONB,
    correlation_id UUID NOT NULL,
    INDEX idx_timestamp (timestamp),
    INDEX idx_user_id (user_id),
    INDEX idx_resource (resource_type, resource_id),
    INDEX idx_correlation (correlation_id)
);

-- Partition by month for performance
CREATE TABLE audit_logs_y2024m11 PARTITION OF audit_logs
    FOR VALUES FROM ('2024-11-01') TO ('2024-12-01');
```

**Middleware for Automatic Logging:**
```python
@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    correlation_id = str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    
    # Capture request details
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Log asynchronously
    await audit_service.log_event(AuditEvent(...))
    
    return response
```

**Compliance Report Generation:**
- PDF format with executive summary
- Filterable by date range, user, action type, resource
- Includes statistics and anomaly detection
- Digital signature for authenticity


### 4. Encryption Service

**Purpose**: Provide encryption for data at rest and in transit with key management.

**Design Rationale**: Layered encryption approach with field-level encryption for sensitive data, TLS for transport, and external key management service for enterprise deployments.

**Components:**
```python
# backend/services/encryption_service.py
class EncryptionService:
    - encrypt_field(data: str, field_type: str) -> str
    - decrypt_field(encrypted_data: str, field_type: str) -> str
    - encrypt_file(file_path: str) -> bytes
    - decrypt_file(encrypted_data: bytes, password: str) -> bytes
    - rotate_keys() -> bool
    - hash_password(password: str) -> str
    - verify_password(password: str, hashed: str) -> bool
```

**Encryption Strategy:**

1. **Data at Rest (Database)**:
   - Sensitive fields: AES-256-GCM encryption
   - Fields to encrypt: API keys, credentials, PII, financial data
   - Key storage: Environment variables (dev) / AWS KMS or Azure Key Vault (prod)

2. **Data in Transit**:
   - TLS 1.3 with strong cipher suites
   - Certificate management via Let's Encrypt or corporate CA
   - HSTS headers enforced

3. **Password Storage**:
   - Argon2id hashing (preferred) or bcrypt
   - Salt per password
   - Configurable work factor

**Database Model with Encryption:**
```python
class EncryptedField(TypeDecorator):
    impl = Text
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return encryption_service.encrypt_field(value, "general")
        return value
    
    def process_result_value(self, value, dialect):
        if value is not None:
            return encryption_service.decrypt_field(value, "general")
        return value

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    api_key = Column(EncryptedField, nullable=True)  # Encrypted
```

**Key Rotation Strategy:**
- Automated rotation every 90 days
- Dual-key approach: new key encrypts new data, old key decrypts existing
- Background job re-encrypts data with new key
- Zero-downtime rotation

**File Export Encryption:**
```python
# Password-protected ZIP with AES-256
def export_data_encrypted(data: pd.DataFrame, password: str) -> bytes:
    # Convert to Excel/CSV
    # Encrypt with password
    # Return encrypted bytes
```


### 5. Rate Limiting Service

**Purpose**: Protect API from abuse and ensure fair resource distribution.

**Design Rationale**: Sliding window algorithm provides accurate rate limiting. Redis-based implementation supports distributed deployments. Tiered limits allow premium users higher quotas.

**Components:**
```python
# backend/services/rate_limiter.py
class RateLimiter:
    - check_limit(user_id: str, endpoint: str) -> RateLimitResult
    - get_remaining(user_id: str, endpoint: str) -> int
    - reset_limit(user_id: str, endpoint: str) -> bool
    - get_user_tier(user_id: str) -> str
```

**Rate Limit Tiers:**
```python
RATE_LIMITS = {
    "free": {
        "requests_per_minute": 100,
        "requests_per_hour": 1000,
        "requests_per_day": 10000
    },
    "premium": {
        "requests_per_minute": 500,
        "requests_per_hour": 10000,
        "requests_per_day": 100000
    },
    "enterprise": {
        "requests_per_minute": 2000,
        "requests_per_hour": 50000,
        "requests_per_day": 1000000
    }
}
```

**Implementation:**
```python
# Middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    user_id = request.state.user.id if hasattr(request.state, 'user') else request.client.host
    
    result = await rate_limiter.check_limit(user_id, request.url.path)
    
    if not result.allowed:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "retry_after": result.retry_after
            },
            headers={
                "Retry-After": str(result.retry_after),
                "X-RateLimit-Limit": str(result.limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(result.reset_time)
            }
        )
    
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(result.limit)
    response.headers["X-RateLimit-Remaining"] = str(result.remaining)
    response.headers["X-RateLimit-Reset"] = str(result.reset_time)
    
    return response
```

**Redis Storage:**
```
rate_limit:{user_id}:{endpoint}:{window} -> count
TTL: window duration
```

**IP-Based Blocking:**
- Unauthenticated requests: 1000 requests per 5 minutes per IP
- Automatic 1-hour block after threshold
- Whitelist for known corporate IPs


### 6. Monitoring and Alerting Service

**Purpose**: Provide real-time visibility into system health, performance, and errors.

**Design Rationale**: Prometheus for metrics collection enables industry-standard monitoring. Structured logging with correlation IDs facilitates debugging. Multi-channel alerting ensures rapid incident response.

**Components:**
```python
# backend/services/monitoring_service.py
class MonitoringService:
    - record_metric(name: str, value: float, labels: dict) -> None
    - increment_counter(name: str, labels: dict) -> None
    - record_histogram(name: str, value: float, labels: dict) -> None
    - check_health() -> HealthStatus
    - send_alert(alert: Alert) -> None
```

**Metrics to Collect:**

1. **Application Metrics**:
   - Request count (by endpoint, method, status code)
   - Request duration (p50, p95, p99)
   - Error rate (by type, endpoint)
   - Active sessions count
   - Cache hit/miss ratio

2. **System Metrics**:
   - CPU usage (%)
   - Memory usage (MB)
   - Disk I/O (ops/sec)
   - Network I/O (bytes/sec)

3. **Database Metrics**:
   - Connection pool size (active, idle, waiting)
   - Query duration (by query type)
   - Transaction count
   - Deadlock count

4. **Business Metrics**:
   - Supplier evaluations per hour
   - Risk assessments per hour
   - ML model prediction latency
   - User activity by role

**Prometheus Metrics Export:**
```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Define metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

active_sessions = Gauge(
    'active_sessions',
    'Number of active user sessions'
)

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

**Health Check Endpoint:**
```python
@app.get("/health")
async def health_check():
    checks = {
        "database": await check_database_connection(),
        "redis": await check_redis_connection(),
        "disk_space": check_disk_space(),
        "memory": check_memory_usage()
    }
    
    status = "healthy" if all(checks.values()) else "unhealthy"
    status_code = 200 if status == "healthy" else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks,
            "version": settings.API_VERSION
        }
    )
```

**Alerting Rules:**
```yaml
alerts:
  - name: HighErrorRate
    condition: error_rate > 0.05 for 5 minutes
    severity: critical
    channels: [email, sms, slack]
    
  - name: HighResponseTime
    condition: p95_response_time > 1000ms for 5 minutes
    severity: warning
    channels: [email, slack]
    
  - name: DatabaseConnectionPoolExhausted
    condition: db_pool_usage > 0.9
    severity: critical
    channels: [email, sms, pagerduty]
    
  - name: HighMemoryUsage
    condition: memory_usage > 0.85
    severity: warning
    channels: [email, slack]
```

**Alert Notification Service:**
```python
class AlertService:
    async def send_email(alert: Alert) -> None
    async def send_sms(alert: Alert) -> None
    async def send_slack(alert: Alert) -> None
    async def send_pagerduty(alert: Alert) -> None
```


### 7. Backup and Disaster Recovery Service

**Purpose**: Ensure data durability and rapid recovery from failures.

**Design Rationale**: Automated backups with multiple retention policies balance storage costs with recovery needs. Point-in-time recovery enables precise restoration. Geographic separation protects against regional failures.

**Components:**
```python
# backend/services/backup_service.py
class BackupService:
    - create_full_backup() -> BackupResult
    - create_incremental_backup() -> BackupResult
    - restore_backup(backup_id: str, target_time: datetime) -> RestoreResult
    - verify_backup(backup_id: str) -> VerificationResult
    - list_backups(filters: BackupQuery) -> List[Backup]
    - delete_old_backups() -> int
```

**Backup Strategy:**

1. **Full Backups**:
   - Schedule: Daily at 02:00 UTC
   - Retention: 30 days
   - Storage: S3/Azure Blob (separate region)
   - Compression: gzip
   - Encryption: AES-256

2. **Incremental Backups**:
   - Schedule: Every 6 hours (08:00, 14:00, 20:00 UTC)
   - Retention: 7 days
   - Storage: S3/Azure Blob
   - Based on: Write-Ahead Log (WAL) for PostgreSQL

3. **Transaction Logs**:
   - Continuous archival
   - Retention: 7 days
   - Enables point-in-time recovery

**Backup Metadata:**
```python
class Backup(BaseModel):
    id: UUID
    type: str  # full, incremental
    timestamp: datetime
    size_bytes: int
    duration_seconds: float
    status: str  # completed, failed, in_progress
    storage_location: str
    checksum: str
    encryption_key_id: str
```

**PostgreSQL Backup Implementation:**
```bash
# Full backup
pg_dump -Fc -Z9 $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).dump

# Incremental (WAL archiving)
archive_command = 'cp %p /backup/wal_archive/%f'
```

**Restore Process:**
```python
async def restore_backup(backup_id: str, target_time: datetime):
    # 1. Stop application (maintenance mode)
    # 2. Download backup from storage
    # 3. Verify backup integrity (checksum)
    # 4. Restore database
    # 5. Apply WAL logs up to target_time
    # 6. Verify data integrity
    # 7. Restart application
    # 8. Run smoke tests
```

**Automated Verification:**
```python
# Weekly backup verification
async def verify_backup_weekly():
    latest_backup = await get_latest_backup()
    
    # Restore to temporary database
    temp_db = await create_temp_database()
    await restore_backup_to(latest_backup, temp_db)
    
    # Run integrity checks
    checks = [
        check_table_counts(temp_db),
        check_data_consistency(temp_db),
        check_foreign_keys(temp_db)
    ]
    
    # Log results
    await audit_service.log_event({
        "action": "BACKUP_VERIFICATION",
        "backup_id": latest_backup.id,
        "results": checks,
        "success": all(checks)
    })
    
    # Cleanup
    await drop_temp_database(temp_db)
```

**Disaster Recovery Plan:**
- RTO (Recovery Time Objective): 4 hours
- RPO (Recovery Point Objective): 6 hours (incremental backup interval)
- Documented runbook for recovery procedures
- Quarterly DR drills


### 8. Caching Service

**Purpose**: Improve performance and reduce database/ML model load through intelligent caching.

**Design Rationale**: Redis provides fast, distributed caching. Multi-level caching strategy balances performance with data freshness. Cache invalidation ensures data consistency.

**Components:**
```python
# backend/services/cache_service.py
class CacheService:
    - get(key: str) -> Optional[Any]
    - set(key: str, value: Any, ttl: int) -> bool
    - delete(key: str) -> bool
    - invalidate_pattern(pattern: str) -> int
    - get_stats() -> CacheStats
```

**Caching Strategy:**

1. **ML Model Predictions** (1 hour TTL):
   - Key: `ml:prediction:{model_name}:{input_hash}`
   - Reduces expensive model inference
   - Invalidate on model retraining

2. **Database Queries** (5 minutes TTL):
   - Key: `db:query:{query_hash}:{params_hash}`
   - Cache frequently accessed data
   - Invalidate on data modification

3. **API Responses** (1 minute TTL):
   - Key: `api:response:{endpoint}:{params_hash}`
   - Cache GET requests only
   - Respect user permissions

4. **Session Data** (8 hours TTL):
   - Key: `session:{session_id}`
   - Fast session validation
   - Invalidate on logout

**Cache Decorator:**
```python
def cached(ttl: int = 300, key_prefix: str = ""):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash_args(args, kwargs)}"
            
            # Try cache
            cached_value = await cache_service.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache_service.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Usage
@cached(ttl=3600, key_prefix="ml:supplier_score")
async def predict_supplier_score(supplier_data: dict):
    return model.predict(supplier_data)
```

**Cache Invalidation:**
```python
# Invalidate on data modification
@app.post("/api/v1/suppliers")
async def create_supplier(supplier: SupplierCreate):
    result = await supplier_service.create(supplier)
    
    # Invalidate related caches
    await cache_service.invalidate_pattern("db:query:suppliers:*")
    await cache_service.invalidate_pattern("api:response:/api/v1/suppliers*")
    
    return result
```

**Cache Warming:**
```python
# Pre-populate cache with frequently accessed data
async def warm_cache():
    # Load top suppliers
    suppliers = await get_top_suppliers(limit=100)
    for supplier in suppliers:
        await cache_service.set(
            f"supplier:{supplier.id}",
            supplier,
            ttl=3600
        )
```


### 9. Input Validation and Sanitization Service

**Purpose**: Protect against injection attacks and ensure data integrity.

**Design Rationale**: Pydantic models provide type-safe validation. Additional sanitization layer prevents XSS and SQL injection. File upload validation prevents malware.

**Components:**
```python
# backend/services/validation_service.py
class ValidationService:
    - validate_input(data: dict, schema: Type[BaseModel]) -> ValidationResult
    - sanitize_string(text: str) -> str
    - validate_file(file: UploadFile) -> FileValidationResult
    - check_sql_injection(text: str) -> bool
    - check_xss(text: str) -> bool
```

**Pydantic Models with Validation:**
```python
from pydantic import BaseModel, Field, validator, constr
from typing import Optional

class SupplierCreate(BaseModel):
    name: constr(min_length=1, max_length=200, strip_whitespace=True)
    email: EmailStr
    phone: Optional[constr(regex=r'^\+?[1-9]\d{1,14}$')]
    revenue: confloat(ge=0, le=1e12)
    risk_score: confloat(ge=0, le=100)
    
    @validator('name')
    def sanitize_name(cls, v):
        # Remove potentially dangerous characters
        return validation_service.sanitize_string(v)
    
    @validator('revenue')
    def validate_revenue(cls, v):
        if v < 0:
            raise ValueError('Revenue cannot be negative')
        return v
    
    class Config:
        str_strip_whitespace = True
        anystr_lower = False
```

**SQL Injection Prevention:**
```python
# Always use parameterized queries
async def get_supplier_by_name(name: str):
    # GOOD: Parameterized query
    query = "SELECT * FROM suppliers WHERE name = :name"
    result = await database.fetch_one(query, {"name": name})
    
    # BAD: String concatenation (never do this)
    # query = f"SELECT * FROM suppliers WHERE name = '{name}'"
```

**XSS Prevention:**
```python
import bleach

def sanitize_html(text: str) -> str:
    """Remove potentially dangerous HTML/JavaScript"""
    allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li']
    allowed_attributes = {}
    
    return bleach.clean(
        text,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )
```

**File Upload Validation:**
```python
ALLOWED_EXTENSIONS = {'.pdf', '.xlsx', '.csv', '.txt', '.docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

async def validate_file_upload(file: UploadFile) -> FileValidationResult:
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type {file_ext} not allowed")
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset
    
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"File size {file_size} exceeds limit")
    
    # Check MIME type
    mime_type = magic.from_buffer(await file.read(1024), mime=True)
    await file.seek(0)
    
    if not is_mime_type_allowed(mime_type):
        raise ValueError(f"MIME type {mime_type} not allowed")
    
    # Virus scan (if available)
    if settings.ENABLE_VIRUS_SCAN:
        scan_result = await virus_scanner.scan(file)
        if not scan_result.clean:
            raise ValueError("File failed virus scan")
    
    return FileValidationResult(valid=True)
```

**Request Validation Middleware:**
```python
@app.middleware("http")
async def validation_middleware(request: Request, call_next):
    # Validate content type
    if request.method in ["POST", "PUT", "PATCH"]:
        content_type = request.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            return JSONResponse(
                status_code=415,
                content={"error": "Unsupported media type"}
            )
    
    # Validate JSON payload size
    if request.method in ["POST", "PUT", "PATCH"]:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 1024 * 1024:  # 1 MB
            return JSONResponse(
                status_code=413,
                content={"error": "Payload too large"}
            )
    
    response = await call_next(request)
    return response
```


### 10. Configuration Management Service

**Purpose**: Centralize configuration with environment-specific settings and validation.

**Design Rationale**: Environment variables provide secure, deployment-agnostic configuration. Validation at startup prevents runtime errors. Separate profiles enable consistent multi-environment deployments.

**Components:**
```python
# backend/config/settings.py (Enhanced)
from pydantic_settings import BaseSettings
from typing import Optional, List
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False
    
    # API Configuration
    API_TITLE: str = "AI Supplier Selection API"
    API_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str  # Required, no default
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 480  # 8 hours
    JWT_REFRESH_EXPIRATION_DAYS: int = 30
    PASSWORD_MIN_LENGTH: int = 12
    MFA_ENABLED: bool = False
    
    # Database
    DATABASE_URL: str  # Required
    DB_POOL_SIZE: int = 50
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    LOG_LEVEL: str = "INFO"
    STRUCTURED_LOGGING: bool = True
    
    # Backup
    BACKUP_ENABLED: bool = True
    BACKUP_STORAGE_URL: str = ""  # S3/Azure Blob URL
    BACKUP_RETENTION_DAYS: int = 30
    
    # Encryption
    ENCRYPTION_KEY: str  # Required for production
    KEY_ROTATION_DAYS: int = 90
    
    # External Services
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SLACK_WEBHOOK_URL: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:8501"]
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".xlsx", ".csv"]
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v, values):
        if values.get("ENVIRONMENT") == Environment.PRODUCTION and len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters in production")
        return v
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        if not v.startswith(("postgresql://", "postgres://")):
            raise ValueError("DATABASE_URL must be a PostgreSQL connection string")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Singleton instance
settings = Settings()
```

**Environment-Specific Configuration Files:**

```bash
# .env.development
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql://localhost:5432/supplier_dev
SECRET_KEY=dev-secret-key-not-for-production
LOG_LEVEL=DEBUG

# .env.staging
ENVIRONMENT=staging
DEBUG=false
DATABASE_URL=postgresql://staging-db:5432/supplier_staging
SECRET_KEY=${STAGING_SECRET_KEY}
LOG_LEVEL=INFO

# .env.production
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=${PRODUCTION_DATABASE_URL}
SECRET_KEY=${PRODUCTION_SECRET_KEY}
ENCRYPTION_KEY=${PRODUCTION_ENCRYPTION_KEY}
LOG_LEVEL=WARNING
MFA_ENABLED=true
```

**Configuration Validation at Startup:**
```python
@app.on_event("startup")
async def validate_configuration():
    """Validate all required configuration on startup"""
    required_settings = [
        "SECRET_KEY",
        "DATABASE_URL",
        "ENCRYPTION_KEY"
    ]
    
    missing = []
    for setting in required_settings:
        if not getattr(settings, setting, None):
            missing.append(setting)
    
    if missing:
        raise RuntimeError(f"Missing required configuration: {', '.join(missing)}")
    
    # Test database connection
    try:
        await database.connect()
        logger.info("Database connection successful")
    except Exception as e:
        raise RuntimeError(f"Database connection failed: {e}")
    
    # Test Redis connection
    try:
        await redis.ping()
        logger.info("Redis connection successful")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
```

**Dynamic Configuration Reload:**
```python
# For non-critical settings that can be reloaded
@app.post("/api/v1/admin/config/reload")
@require_permission(Permission.SYSTEM_ADMIN)
async def reload_configuration():
    """Reload configuration without restart"""
    # Reload rate limits, feature flags, etc.
    await config_service.reload()
    return {"status": "Configuration reloaded"}
```


### 11. Webhook Service

**Purpose**: Enable real-time integration with external systems through event notifications.

**Design Rationale**: Asynchronous webhook delivery prevents blocking. Retry logic with exponential backoff ensures reliable delivery. HMAC signatures provide authentication and integrity verification.

**Components:**
```python
# backend/services/webhook_service.py
class WebhookService:
    - register_webhook(webhook: WebhookConfig) -> Webhook
    - send_webhook(event: WebhookEvent) -> WebhookDelivery
    - retry_failed_webhook(delivery_id: str) -> WebhookDelivery
    - list_webhooks(filters: WebhookQuery) -> List[Webhook]
    - delete_webhook(webhook_id: str) -> bool
    - test_webhook(webhook_id: str) -> WebhookDelivery
```

**Webhook Configuration:**
```python
class WebhookConfig(BaseModel):
    url: HttpUrl
    events: List[str]  # supplier.created, risk.updated, etc.
    secret: str  # For HMAC signature
    active: bool = True
    retry_policy: RetryPolicy = RetryPolicy()
    headers: Optional[dict] = None

class RetryPolicy(BaseModel):
    max_retries: int = 3
    initial_delay_seconds: int = 60
    max_delay_seconds: int = 3600
    backoff_multiplier: float = 2.0
```

**Supported Events:**
```python
WEBHOOK_EVENTS = [
    "supplier.created",
    "supplier.updated",
    "supplier.deleted",
    "risk_profile.created",
    "risk_profile.updated",
    "fraud_alert.triggered",
    "contract.analyzed",
    "decision.completed",
    "user.login",
    "user.logout",
    "system.alert"
]
```

**Webhook Payload:**
```python
class WebhookPayload(BaseModel):
    event: str
    timestamp: datetime
    data: dict
    metadata: dict

# Example payload
{
    "event": "supplier.created",
    "timestamp": "2024-11-11T10:30:00Z",
    "data": {
        "id": "supplier_123",
        "name": "Acme Corp",
        "risk_score": 75.5
    },
    "metadata": {
        "user_id": "user_456",
        "correlation_id": "req_789"
    }
}
```

**HMAC Signature Generation:**
```python
import hmac
import hashlib

def generate_signature(payload: str, secret: str) -> str:
    """Generate HMAC-SHA256 signature for webhook payload"""
    return hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

# Include in headers
headers = {
    "X-Webhook-Signature": signature,
    "X-Webhook-Event": event_type,
    "X-Webhook-Delivery": delivery_id,
    "Content-Type": "application/json"
}
```

**Webhook Delivery with Retry:**
```python
async def deliver_webhook(webhook: Webhook, event: WebhookEvent):
    """Deliver webhook with retry logic"""
    payload = event.to_json()
    signature = generate_signature(payload, webhook.secret)
    
    delivery = WebhookDelivery(
        id=str(uuid.uuid4()),
        webhook_id=webhook.id,
        event=event.type,
        payload=payload,
        status="pending"
    )
    
    for attempt in range(webhook.retry_policy.max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    webhook.url,
                    json=event.dict(),
                    headers={
                        "X-Webhook-Signature": signature,
                        "X-Webhook-Event": event.type,
                        "X-Webhook-Delivery": delivery.id
                    }
                )
                
                delivery.status_code = response.status_code
                delivery.response_body = response.text
                
                if response.status_code < 300:
                    delivery.status = "delivered"
                    await save_delivery(delivery)
                    return delivery
                
        except Exception as e:
            delivery.error = str(e)
            logger.error(f"Webhook delivery failed: {e}")
        
        # Calculate backoff delay
        if attempt < webhook.retry_policy.max_retries:
            delay = min(
                webhook.retry_policy.initial_delay_seconds * (
                    webhook.retry_policy.backoff_multiplier ** attempt
                ),
                webhook.retry_policy.max_delay_seconds
            )
            await asyncio.sleep(delay)
    
    delivery.status = "failed"
    await save_delivery(delivery)
    return delivery
```

**Webhook Management API:**
```python
@app.post("/api/v1/webhooks")
@require_permission(Permission.SYSTEM_ADMIN)
async def create_webhook(webhook: WebhookConfig):
    return await webhook_service.register_webhook(webhook)

@app.get("/api/v1/webhooks")
@require_permission(Permission.SYSTEM_ADMIN)
async def list_webhooks():
    return await webhook_service.list_webhooks()

@app.post("/api/v1/webhooks/{webhook_id}/test")
@require_permission(Permission.SYSTEM_ADMIN)
async def test_webhook(webhook_id: str):
    return await webhook_service.test_webhook(webhook_id)

@app.get("/api/v1/webhooks/deliveries")
@require_permission(Permission.SYSTEM_ADMIN)
async def list_deliveries(webhook_id: Optional[str] = None):
    return await webhook_service.list_deliveries(webhook_id)
```

**Event Emission:**
```python
# Emit webhook events after operations
@app.post("/api/v1/suppliers")
async def create_supplier(supplier: SupplierCreate):
    result = await supplier_service.create(supplier)
    
    # Emit webhook event
    await webhook_service.emit_event(WebhookEvent(
        type="supplier.created",
        data=result.dict(),
        metadata={"user_id": current_user.id}
    ))
    
    return result
```


### 12. Export and Reporting Service

**Purpose**: Generate data exports and reports in multiple formats with proper access control.

**Design Rationale**: Asynchronous export generation prevents request timeouts. Pagination handles large datasets efficiently. Format flexibility supports various business needs.

**Components:**
```python
# backend/services/export_service.py
class ExportService:
    - export_data(query: ExportQuery, format: str) -> ExportResult
    - generate_report(report_type: str, params: dict) -> bytes
    - schedule_report(schedule: ReportSchedule) -> ScheduledReport
    - get_export_status(export_id: str) -> ExportStatus
```

**Supported Export Formats:**
```python
class ExportFormat(str, Enum):
    CSV = "csv"
    EXCEL = "xlsx"
    JSON = "json"
    PDF = "pdf"
```

**Export Query Model:**
```python
class ExportQuery(BaseModel):
    resource_type: str  # suppliers, risks, contracts
    filters: dict
    fields: Optional[List[str]]  # Specific fields to export
    sort_by: Optional[str]
    limit: int = 10000
    offset: int = 0
```

**Asynchronous Export for Large Datasets:**
```python
@app.post("/api/v1/exports")
@require_permission(Permission.SUPPLIER_READ)
async def create_export(query: ExportQuery, format: ExportFormat):
    """Create async export job for large datasets"""
    
    # Create export job
    export_job = ExportJob(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        query=query,
        format=format,
        status="pending",
        created_at=datetime.utcnow()
    )
    
    await save_export_job(export_job)
    
    # Queue background task
    background_tasks.add_task(
        process_export,
        export_job.id
    )
    
    return {
        "export_id": export_job.id,
        "status": "pending",
        "status_url": f"/api/v1/exports/{export_job.id}"
    }

@app.get("/api/v1/exports/{export_id}")
async def get_export_status(export_id: str):
    """Check export status and download when ready"""
    export_job = await get_export_job(export_id)
    
    if export_job.status == "completed":
        return {
            "status": "completed",
            "download_url": f"/api/v1/exports/{export_id}/download",
            "expires_at": export_job.expires_at
        }
    
    return {
        "status": export_job.status,
        "progress": export_job.progress
    }

@app.get("/api/v1/exports/{export_id}/download")
async def download_export(export_id: str):
    """Download completed export"""
    export_job = await get_export_job(export_id)
    
    if export_job.status != "completed":
        raise HTTPException(status_code=400, detail="Export not ready")
    
    # Apply user permissions to filter data
    data = await apply_user_permissions(export_job.data, current_user)
    
    return FileResponse(
        export_job.file_path,
        media_type=get_media_type(export_job.format),
        filename=f"export_{export_id}.{export_job.format}"
    )
```

**Export Generation:**
```python
async def process_export(export_id: str):
    """Background task to generate export"""
    export_job = await get_export_job(export_id)
    
    try:
        export_job.status = "processing"
        await save_export_job(export_job)
        
        # Fetch data with pagination
        data = []
        offset = 0
        batch_size = 1000
        
        while True:
            batch = await fetch_data(
                export_job.query,
                limit=batch_size,
                offset=offset
            )
            
            if not batch:
                break
            
            data.extend(batch)
            offset += batch_size
            
            # Update progress
            export_job.progress = min(offset / export_job.query.limit, 1.0)
            await save_export_job(export_job)
        
        # Generate file
        file_path = await generate_export_file(
            data,
            export_job.format,
            export_job.id
        )
        
        export_job.status = "completed"
        export_job.file_path = file_path
        export_job.expires_at = datetime.utcnow() + timedelta(hours=24)
        await save_export_job(export_job)
        
    except Exception as e:
        export_job.status = "failed"
        export_job.error = str(e)
        await save_export_job(export_job)
```

**Format-Specific Generators:**
```python
async def generate_csv(data: List[dict], file_path: str):
    """Generate CSV export"""
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)

async def generate_excel(data: List[dict], file_path: str):
    """Generate Excel export with formatting"""
    df = pd.DataFrame(data)
    
    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Data', index=False)
        
        # Add metadata sheet
        metadata = pd.DataFrame({
            'Export Date': [datetime.utcnow()],
            'Record Count': [len(data)],
            'Generated By': [current_user.email]
        })
        metadata.to_excel(writer, sheet_name='Metadata', index=False)

async def generate_json(data: List[dict], file_path: str):
    """Generate JSON export"""
    with open(file_path, 'w') as f:
        json.dump({
            'data': data,
            'metadata': {
                'export_date': datetime.utcnow().isoformat(),
                'record_count': len(data)
            }
        }, f, indent=2)
```

**Scheduled Reports:**
```python
class ReportSchedule(BaseModel):
    report_type: str
    schedule: str  # cron expression
    recipients: List[EmailStr]
    format: ExportFormat
    filters: dict

@app.post("/api/v1/reports/schedule")
@require_permission(Permission.SYSTEM_ADMIN)
async def schedule_report(schedule: ReportSchedule):
    """Schedule recurring report generation"""
    scheduled_report = await report_service.schedule_report(schedule)
    return scheduled_report

# Background job to process scheduled reports
async def process_scheduled_reports():
    """Run scheduled reports and email to recipients"""
    due_reports = await get_due_reports()
    
    for report in due_reports:
        # Generate report
        data = await fetch_report_data(report.report_type, report.filters)
        file_path = await generate_export_file(data, report.format, report.id)
        
        # Email to recipients
        await email_service.send_report(
            recipients=report.recipients,
            subject=f"Scheduled Report: {report.report_type}",
            attachment=file_path
        )
        
        # Update next run time
        report.last_run = datetime.utcnow()
        report.next_run = calculate_next_run(report.schedule)
        await save_scheduled_report(report)
```


## Data Models

### User and Authentication Models

```python
# backend/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from core.database import Base
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    roles = relationship("UserRole", back_populates="user")
    sessions = relationship("Session", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    permissions = Column(JSON, nullable=False)  # List of permission strings
    inherits_from = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    users = relationship("UserRole", back_populates="role")

class UserRole(Base):
    __tablename__ = "user_roles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    role_id = Column(String, ForeignKey("roles.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    assigned_by = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    token_jti = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=False)
    user_agent = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
```

### Audit Log Models

```python
# backend/models/audit.py
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    user_email = Column(String, nullable=False)
    action = Column(String, nullable=False, index=True)
    resource_type = Column(String, nullable=True, index=True)
    resource_id = Column(String, nullable=True, index=True)
    ip_address = Column(String, nullable=False)
    user_agent = Column(String, nullable=True)
    request_method = Column(String, nullable=True)
    request_path = Column(String, nullable=True)
    status_code = Column(Integer, nullable=True)
    changes = Column(JSON, nullable=True)  # Before/after state
    metadata = Column(JSON, nullable=True)
    correlation_id = Column(String, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
```

### Webhook Models

```python
# backend/models/webhook.py
class Webhook(Base):
    __tablename__ = "webhooks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    url = Column(String, nullable=False)
    events = Column(JSON, nullable=False)  # List of event types
    secret = Column(String, nullable=False)  # Encrypted
    active = Column(Boolean, default=True)
    retry_max_attempts = Column(Integer, default=3)
    retry_initial_delay = Column(Integer, default=60)
    retry_max_delay = Column(Integer, default=3600)
    retry_backoff_multiplier = Column(Float, default=2.0)
    headers = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, ForeignKey("users.id"))
    
    # Relationships
    deliveries = relationship("WebhookDelivery", back_populates="webhook")

class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    webhook_id = Column(String, ForeignKey("webhooks.id"), nullable=False)
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(String, nullable=False)  # pending, delivered, failed
    status_code = Column(Integer, nullable=True)
    response_body = Column(String, nullable=True)
    error = Column(String, nullable=True)
    attempts = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)
    
    # Relationships
    webhook = relationship("Webhook", back_populates="deliveries")
```

### Export and Report Models

```python
# backend/models/export.py
class ExportJob(Base):
    __tablename__ = "export_jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    resource_type = Column(String, nullable=False)
    format = Column(String, nullable=False)
    query = Column(JSON, nullable=False)
    status = Column(String, nullable=False)  # pending, processing, completed, failed
    progress = Column(Float, default=0.0)
    file_path = Column(String, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    record_count = Column(Integer, nullable=True)
    error = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

class ScheduledReport(Base):
    __tablename__ = "scheduled_reports"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    report_type = Column(String, nullable=False)
    schedule = Column(String, nullable=False)  # Cron expression
    recipients = Column(JSON, nullable=False)  # List of emails
    format = Column(String, nullable=False)
    filters = Column(JSON, nullable=True)
    active = Column(Boolean, default=True)
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=False)
```


## Error Handling

### Error Response Structure

**Design Rationale**: Consistent error format aids client integration. Correlation IDs enable request tracing. Environment-aware detail level prevents information leakage in production.

```python
# backend/models/error.py
class ErrorResponse(BaseModel):
    error: str
    message: str
    status_code: int
    correlation_id: str
    timestamp: datetime
    path: str
    details: Optional[dict] = None  # Only in development

# Example error response
{
    "error": "ValidationError",
    "message": "Invalid supplier data provided",
    "status_code": 422,
    "correlation_id": "req_abc123",
    "timestamp": "2024-11-11T10:30:00Z",
    "path": "/api/v1/suppliers",
    "details": {  # Only in development
        "field": "revenue",
        "issue": "Value must be non-negative"
    }
}
```

### Global Exception Handler

```python
# backend/middleware/error_handler.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import traceback
import structlog

logger = structlog.get_logger()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    # Log error with full context
    logger.error(
        "unhandled_exception",
        correlation_id=correlation_id,
        path=str(request.url),
        method=request.method,
        error_type=type(exc).__name__,
        error_message=str(exc),
        traceback=traceback.format_exc() if settings.DEBUG else None
    )
    
    # Audit log for security-related errors
    if isinstance(exc, (AuthenticationError, AuthorizationError)):
        await audit_service.log_event(AuditEvent(
            action="SECURITY_ERROR",
            user_id=getattr(request.state, 'user_id', 'anonymous'),
            error=str(exc),
            correlation_id=correlation_id
        ))
    
    # Return appropriate response
    if settings.DEBUG:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": type(exc).__name__,
                "message": str(exc),
                "status_code": 500,
                "correlation_id": correlation_id,
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url),
                "traceback": traceback.format_exc()
            }
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred. Please contact support.",
                "status_code": 500,
                "correlation_id": correlation_id,
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url)
            }
        )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Request validation failed",
            "status_code": 422,
            "correlation_id": correlation_id,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url),
            "details": exc.errors() if settings.DEBUG else None
        }
    )

@app.exception_handler(AuthenticationError)
async def authentication_exception_handler(request: Request, exc: AuthenticationError):
    """Handle authentication errors"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": "AuthenticationError",
            "message": str(exc),
            "status_code": 401,
            "correlation_id": getattr(request.state, 'correlation_id', 'unknown'),
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        },
        headers={"WWW-Authenticate": "Bearer"}
    )

@app.exception_handler(AuthorizationError)
async def authorization_exception_handler(request: Request, exc: AuthorizationError):
    """Handle authorization errors"""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "error": "AuthorizationError",
            "message": "You do not have permission to access this resource",
            "status_code": 403,
            "correlation_id": getattr(request.state, 'correlation_id', 'unknown'),
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )
```

### Custom Exception Classes

```python
# backend/exceptions.py
class BaseAPIException(Exception):
    """Base exception for all API errors"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AuthenticationError(BaseAPIException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)

class AuthorizationError(BaseAPIException):
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, status_code=403)

class ResourceNotFoundError(BaseAPIException):
    def __init__(self, resource: str, resource_id: str):
        message = f"{resource} with id {resource_id} not found"
        super().__init__(message, status_code=404)

class RateLimitExceededError(BaseAPIException):
    def __init__(self, retry_after: int):
        message = f"Rate limit exceeded. Retry after {retry_after} seconds"
        super().__init__(message, status_code=429)
        self.retry_after = retry_after

class ValidationError(BaseAPIException):
    def __init__(self, message: str, field: str = None):
        super().__init__(message, status_code=422)
        self.field = field
```

### Structured Logging

```python
# backend/core/logging.py
import structlog
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configure structured logging"""
    
    if settings.STRUCTURED_LOGGING:
        # JSON logging for production
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        # Human-readable logging for development
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.dev.ConsoleRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

# Usage
logger = structlog.get_logger()

logger.info(
    "user_login",
    user_id="user_123",
    ip_address="192.168.1.1",
    correlation_id="req_abc"
)

logger.error(
    "database_error",
    error=str(exc),
    query=query,
    correlation_id="req_abc"
)
```


## Testing Strategy

### Testing Pyramid

**Design Rationale**: Comprehensive testing at multiple levels ensures reliability. Focus on unit tests for speed, integration tests for component interaction, and end-to-end tests for critical flows.

```
        /\
       /  \      E2E Tests (10%)
      /    \     - Critical user flows
     /------\    - Authentication flow
    /        \   - Data export flow
   /          \  
  /------------\ Integration Tests (30%)
 /              \ - API endpoints
/                \ - Database operations
/------------------\ - Service interactions
/                    \
/----------------------\ Unit Tests (60%)
         - Business logic
         - Validation
         - Utilities
```

### Unit Tests

**Focus**: Individual functions and methods in isolation.

```python
# tests/unit/test_auth_service.py
import pytest
from services.auth_service import AuthenticationService
from exceptions import AuthenticationError

@pytest.fixture
def auth_service():
    return AuthenticationService()

@pytest.fixture
def mock_user():
    return {
        "id": "user_123",
        "email": "test@example.com",
        "password_hash": "$2b$12$..."
    }

def test_create_token_success(auth_service, mock_user):
    """Test JWT token creation"""
    token = auth_service.create_token(mock_user)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0

def test_validate_token_success(auth_service, mock_user):
    """Test token validation with valid token"""
    token = auth_service.create_token(mock_user)
    payload = auth_service.validate_token(token)
    
    assert payload["sub"] == mock_user["id"]
    assert payload["email"] == mock_user["email"]

def test_validate_token_expired(auth_service):
    """Test token validation with expired token"""
    expired_token = "eyJ..."  # Expired token
    
    with pytest.raises(AuthenticationError, match="Token expired"):
        auth_service.validate_token(expired_token)

def test_hash_password(auth_service):
    """Test password hashing"""
    password = "SecurePassword123!"
    hashed = auth_service.hash_password(password)
    
    assert hashed != password
    assert auth_service.verify_password(password, hashed)

def test_verify_password_invalid(auth_service):
    """Test password verification with wrong password"""
    password = "SecurePassword123!"
    hashed = auth_service.hash_password(password)
    
    assert not auth_service.verify_password("WrongPassword", hashed)
```

### Integration Tests

**Focus**: Component interactions, database operations, API endpoints.

```python
# tests/integration/test_auth_api.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def test_user(client):
    """Create a test user"""
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test User"
    })
    return response.json()

@pytest.mark.asyncio
async def test_login_success(client, test_user):
    """Test successful login"""
    response = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "SecurePassword123!"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "WrongPassword"
    })
    
    assert response.status_code == 401
    assert "error" in response.json()

@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without token"""
    response = await client.get("/api/v1/suppliers")
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_protected_endpoint_with_token(client, test_user):
    """Test accessing protected endpoint with valid token"""
    # Login
    login_response = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "SecurePassword123!"
    })
    token = login_response.json()["access_token"]
    
    # Access protected endpoint
    response = await client.get(
        "/api/v1/suppliers",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_rate_limiting(client, test_user):
    """Test rate limiting enforcement"""
    # Login
    login_response = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "SecurePassword123!"
    })
    token = login_response.json()["access_token"]
    
    # Make requests until rate limit
    for i in range(101):
        response = await client.get(
            "/api/v1/suppliers",
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # Next request should be rate limited
    response = await client.get(
        "/api/v1/suppliers",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 429
    assert "retry_after" in response.headers
```

### End-to-End Tests

**Focus**: Complete user workflows from start to finish.

```python
# tests/e2e/test_supplier_workflow.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_complete_supplier_evaluation_workflow(client):
    """Test complete workflow: register, login, create supplier, evaluate"""
    
    # 1. Register user
    register_response = await client.post("/api/v1/auth/register", json={
        "email": "analyst@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test Analyst"
    })
    assert register_response.status_code == 201
    
    # 2. Login
    login_response = await client.post("/api/v1/auth/login", json={
        "email": "analyst@example.com",
        "password": "SecurePassword123!"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Create supplier
    supplier_data = {
        "name": "Acme Corp",
        "email": "contact@acme.com",
        "revenue": 1000000,
        "employees": 50
    }
    create_response = await client.post(
        "/api/v1/suppliers",
        json=supplier_data,
        headers=headers
    )
    assert create_response.status_code == 201
    supplier_id = create_response.json()["id"]
    
    # 4. Evaluate supplier
    eval_response = await client.post(
        f"/api/v1/suppliers/{supplier_id}/evaluate",
        headers=headers
    )
    assert eval_response.status_code == 200
    evaluation = eval_response.json()
    assert "risk_score" in evaluation
    assert 0 <= evaluation["risk_score"] <= 100
    
    # 5. Export results
    export_response = await client.post(
        "/api/v1/exports",
        json={
            "resource_type": "suppliers",
            "format": "csv",
            "filters": {"id": supplier_id}
        },
        headers=headers
    )
    assert export_response.status_code == 200
    export_id = export_response.json()["export_id"]
    
    # 6. Check audit log
    audit_response = await client.get(
        "/api/v1/audit/logs",
        params={"resource_id": supplier_id},
        headers=headers
    )
    assert audit_response.status_code == 200
    logs = audit_response.json()
    assert len(logs) > 0
    assert any(log["action"] == "CREATE" for log in logs)
```

### Performance Tests

**Focus**: Load testing, stress testing, scalability validation.

```python
# tests/performance/test_load.py
import pytest
import asyncio
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_concurrent_requests():
    """Test system under concurrent load"""
    async with AsyncClient(base_url="http://test") as client:
        # Simulate 1000 concurrent requests
        tasks = []
        for i in range(1000):
            task = client.get("/api/v1/suppliers")
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        # Check success rate
        success_count = sum(1 for r in responses if r.status_code == 200)
        success_rate = success_count / len(responses)
        
        assert success_rate >= 0.95  # 95% success rate
        
        # Check response times
        response_times = [r.elapsed.total_seconds() for r in responses]
        p95 = sorted(response_times)[int(len(response_times) * 0.95)]
        
        assert p95 < 0.5  # P95 under 500ms
```

### Security Tests

**Focus**: Authentication, authorization, injection attacks, encryption.

```python
# tests/security/test_security.py
import pytest

@pytest.mark.asyncio
async def test_sql_injection_prevention(client):
    """Test SQL injection prevention"""
    malicious_input = "'; DROP TABLE users; --"
    
    response = await client.get(
        f"/api/v1/suppliers",
        params={"name": malicious_input}
    )
    
    # Should not cause error, should sanitize input
    assert response.status_code in [200, 400]

@pytest.mark.asyncio
async def test_xss_prevention(client, auth_headers):
    """Test XSS prevention"""
    xss_payload = "<script>alert('XSS')</script>"
    
    response = await client.post(
        "/api/v1/suppliers",
        json={"name": xss_payload, "email": "test@example.com"},
        headers=auth_headers
    )
    
    # Should sanitize or reject
    if response.status_code == 201:
        supplier = response.json()
        assert "<script>" not in supplier["name"]

@pytest.mark.asyncio
async def test_unauthorized_access(client):
    """Test unauthorized access to protected resources"""
    response = await client.delete("/api/v1/suppliers/123")
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_insufficient_permissions(client, viewer_token):
    """Test access with insufficient permissions"""
    headers = {"Authorization": f"Bearer {viewer_token}"}
    
    response = await client.delete(
        "/api/v1/suppliers/123",
        headers=headers
    )
    
    assert response.status_code == 403
```


## Deployment Architecture

### Infrastructure Components

**Design Rationale**: Cloud-native architecture enables scalability and reliability. Managed services reduce operational overhead. Multi-region deployment provides disaster recovery.

```
┌─────────────────────────────────────────────────────────────────┐
│                         Load Balancer                            │
│                    (AWS ALB / Azure LB)                          │
│                  - TLS Termination                               │
│                  - Health Checks                                 │
│                  - Request Routing                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
┌───────▼────────┐                       ┌───────▼────────┐
│   Backend      │                       │   Backend      │
│   Instance 1   │                       │   Instance 2   │
│   (Container)  │                       │   (Container)  │
└───────┬────────┘                       └───────┬────────┘
        │                                         │
        └────────────────────┬────────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌───────▼────────┐  ┌───────▼────────┐
│   PostgreSQL   │  │     Redis      │  │   S3/Blob      │
│   (Primary)    │  │    (Cache)     │  │   (Storage)    │
└───────┬────────┘  └────────────────┘  └────────────────┘
        │
┌───────▼────────┐
│   PostgreSQL   │
│   (Replica)    │
└────────────────┘
```

### Container Configuration

**Dockerfile (Enhanced):**
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Environment Variables

```bash
# Production environment variables
# Security
SECRET_KEY=${SECRET_KEY}
ENCRYPTION_KEY=${ENCRYPTION_KEY}
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=480
MFA_ENABLED=true

# Database
DATABASE_URL=${DATABASE_URL}
DB_POOL_SIZE=50
DB_MAX_OVERFLOW=10

# Redis
REDIS_URL=${REDIS_URL}
REDIS_MAX_CONNECTIONS=50

# Monitoring
PROMETHEUS_ENABLED=true
LOG_LEVEL=INFO
STRUCTURED_LOGGING=true

# Backup
BACKUP_ENABLED=true
BACKUP_STORAGE_URL=${BACKUP_STORAGE_URL}

# Email
SMTP_HOST=${SMTP_HOST}
SMTP_PORT=587
SMTP_USERNAME=${SMTP_USERNAME}
SMTP_PASSWORD=${SMTP_PASSWORD}

# Alerting
SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
PAGERDUTY_API_KEY=${PAGERDUTY_API_KEY}

# Application
ENVIRONMENT=production
DEBUG=false
```

### Database Migration Strategy

**Alembic Configuration:**
```python
# alembic/env.py
from alembic import context
from sqlalchemy import engine_from_config, pool
from backend.core.database import Base
from backend.models import *  # Import all models

def run_migrations_online():
    """Run migrations in 'online' mode"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=Base.metadata,
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()
```

**Migration Commands:**
```bash
# Create new migration
alembic revision --autogenerate -m "Add user authentication tables"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check current version
alembic current
```

### Scaling Strategy

**Horizontal Scaling:**
- Stateless application design enables multiple instances
- Load balancer distributes traffic across instances
- Auto-scaling based on CPU/memory metrics
- Minimum 2 instances for high availability

**Database Scaling:**
- Read replicas for read-heavy operations
- Connection pooling to manage connections efficiently
- Query optimization and indexing
- Partitioning for large tables (audit logs)

**Caching Strategy:**
- Redis cluster for distributed caching
- Cache warming on deployment
- Intelligent cache invalidation
- Cache hit rate monitoring

### Monitoring and Observability

**Prometheus Metrics:**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'supplier-api'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
```

**Grafana Dashboards:**
- API Performance (request rate, latency, errors)
- System Resources (CPU, memory, disk)
- Database Metrics (connections, query time)
- Business Metrics (evaluations, users, exports)

**Log Aggregation:**
- Centralized logging with ELK Stack or CloudWatch
- Structured JSON logs for parsing
- Log retention: 90 days
- Real-time log streaming for debugging

### Security Hardening

**Network Security:**
- VPC with private subnets for database
- Security groups restricting access
- TLS 1.3 for all communications
- WAF for DDoS protection

**Application Security:**
- Secrets management (AWS Secrets Manager / Azure Key Vault)
- Regular security scanning (Snyk, Trivy)
- Dependency updates and vulnerability patching
- Security headers (HSTS, CSP, X-Frame-Options)

**Access Control:**
- IAM roles for service-to-service communication
- Principle of least privilege
- MFA for administrative access
- Regular access audits

### Disaster Recovery

**Backup Strategy:**
- Automated daily database backups
- Cross-region backup replication
- 30-day retention policy
- Weekly backup verification

**Recovery Procedures:**
1. Detect failure (monitoring alerts)
2. Assess impact and determine recovery strategy
3. Restore from backup or failover to replica
4. Verify data integrity
5. Resume normal operations
6. Post-incident review

**RTO/RPO Targets:**
- RTO: 4 hours (time to restore service)
- RPO: 6 hours (maximum data loss)


## API Documentation and Versioning

### OpenAPI Specification

**Design Rationale**: OpenAPI 3.0 provides standardized, interactive documentation. Versioning in URL path enables backward compatibility. Comprehensive examples aid integration.

**FastAPI Configuration:**
```python
# backend/main.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="AI Supplier Selection & Risk Management API",
    description="""
    Enterprise-grade API for supplier evaluation, risk assessment, and procurement decision-making.
    
    ## Features
    - **Authentication**: JWT-based authentication with MFA support
    - **Authorization**: Role-based access control (RBAC)
    - **Audit Logging**: Comprehensive audit trails for compliance
    - **Rate Limiting**: Tiered rate limits to prevent abuse
    - **Data Export**: Multiple format support (CSV, Excel, JSON, PDF)
    - **Webhooks**: Real-time event notifications
    
    ## Authentication
    All endpoints (except /auth/login and /auth/register) require authentication.
    Include the JWT token in the Authorization header:
    ```
    Authorization: Bearer <your_token>
    ```
    """,
    version="1.0.0",
    terms_of_service="https://example.com/terms",
    contact={
        "name": "API Support",
        "email": "api-support@example.com",
        "url": "https://example.com/support"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

def custom_openapi():
    """Customize OpenAPI schema"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token"
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    # Add response examples
    openapi_schema["components"]["examples"] = {
        "SupplierExample": {
            "value": {
                "id": "supplier_123",
                "name": "Acme Corp",
                "email": "contact@acme.com",
                "revenue": 1000000,
                "risk_score": 75.5
            }
        },
        "ErrorExample": {
            "value": {
                "error": "ValidationError",
                "message": "Invalid input data",
                "status_code": 422,
                "correlation_id": "req_abc123",
                "timestamp": "2024-11-11T10:30:00Z"
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

### API Versioning Strategy

**URL Path Versioning:**
```python
# Version 1 routes
app.include_router(
    supplier_router,
    prefix="/api/v1/suppliers",
    tags=["Suppliers v1"]
)

# Version 2 routes (when needed)
app.include_router(
    supplier_router_v2,
    prefix="/api/v2/suppliers",
    tags=["Suppliers v2"]
)
```

**Version Deprecation Policy:**
- New version released: Previous version supported for 12 months
- 6 months before deprecation: Deprecation warnings in responses
- 3 months before deprecation: Email notifications to API consumers
- Deprecation date: Version removed, returns 410 Gone

**Deprecation Header:**
```python
@app.middleware("http")
async def deprecation_middleware(request: Request, call_next):
    response = await call_next(request)
    
    if "/api/v1/" in request.url.path:
        response.headers["Deprecation"] = "true"
        response.headers["Sunset"] = "2025-12-31T23:59:59Z"
        response.headers["Link"] = '</api/v2/>; rel="successor-version"'
    
    return response
```

### API Response Standards

**Success Response:**
```json
{
    "data": { ... },
    "metadata": {
        "timestamp": "2024-11-11T10:30:00Z",
        "version": "1.0.0"
    }
}
```

**Paginated Response:**
```json
{
    "data": [ ... ],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total_pages": 5,
        "total_items": 100
    },
    "metadata": {
        "timestamp": "2024-11-11T10:30:00Z"
    }
}
```

**Error Response:**
```json
{
    "error": "ValidationError",
    "message": "Invalid supplier data",
    "status_code": 422,
    "correlation_id": "req_abc123",
    "timestamp": "2024-11-11T10:30:00Z",
    "path": "/api/v1/suppliers"
}
```

### Code Examples in Documentation

**Python Example:**
```python
import requests

# Authentication
response = requests.post(
    "https://api.example.com/api/v1/auth/login",
    json={
        "email": "user@example.com",
        "password": "password"
    }
)
token = response.json()["access_token"]

# Create supplier
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    "https://api.example.com/api/v1/suppliers",
    json={
        "name": "Acme Corp",
        "email": "contact@acme.com",
        "revenue": 1000000
    },
    headers=headers
)
supplier = response.json()
```

**JavaScript Example:**
```javascript
// Authentication
const loginResponse = await fetch('https://api.example.com/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        email: 'user@example.com',
        password: 'password'
    })
});
const { access_token } = await loginResponse.json();

// Create supplier
const response = await fetch('https://api.example.com/api/v1/suppliers', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${access_token}`
    },
    body: JSON.stringify({
        name: 'Acme Corp',
        email: 'contact@acme.com',
        revenue: 1000000
    })
});
const supplier = await response.json();
```

**cURL Example:**
```bash
# Authentication
TOKEN=$(curl -X POST https://api.example.com/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"user@example.com","password":"password"}' \
    | jq -r '.access_token')

# Create supplier
curl -X POST https://api.example.com/api/v1/suppliers \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{
        "name": "Acme Corp",
        "email": "contact@acme.com",
        "revenue": 1000000
    }'
```


## Performance Optimization

### Database Optimization

**Connection Pooling:**
```python
# backend/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=50,              # Minimum connections
    max_overflow=10,           # Additional connections when needed
    pool_timeout=30,           # Wait time for connection
    pool_recycle=3600,         # Recycle connections after 1 hour
    pool_pre_ping=True,        # Verify connections before use
    echo=False                 # Disable SQL logging in production
)
```

**Query Optimization:**
```python
# Use indexes for frequently queried fields
class Supplier(Base):
    __tablename__ = "suppliers"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, index=True)
    risk_score = Column(Float, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

# Use eager loading to prevent N+1 queries
from sqlalchemy.orm import joinedload

suppliers = await db.query(Supplier)\
    .options(joinedload(Supplier.risk_profiles))\
    .all()

# Use pagination for large result sets
def paginate_query(query, page: int, page_size: int):
    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size)
```

**Database Indexes:**
```sql
-- Composite indexes for common queries
CREATE INDEX idx_supplier_risk_created ON suppliers(risk_score, created_at);
CREATE INDEX idx_audit_user_timestamp ON audit_logs(user_id, timestamp);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);

-- Partial indexes for filtered queries
CREATE INDEX idx_active_suppliers ON suppliers(id) WHERE is_active = true;

-- Full-text search indexes
CREATE INDEX idx_supplier_name_fts ON suppliers USING gin(to_tsvector('english', name));
```

### Caching Strategy

**Multi-Level Caching:**
```python
# 1. Application-level cache (in-memory)
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_user_permissions(user_id: str) -> List[str]:
    """Cache user permissions in memory"""
    return fetch_permissions_from_db(user_id)

# 2. Distributed cache (Redis)
@cached(ttl=3600, key_prefix="ml:prediction")
async def predict_supplier_risk(supplier_data: dict) -> float:
    """Cache ML predictions in Redis"""
    return model.predict(supplier_data)

# 3. HTTP cache headers
@app.get("/api/v1/suppliers/{supplier_id}")
async def get_supplier(supplier_id: str, response: Response):
    supplier = await get_supplier_by_id(supplier_id)
    
    # Set cache headers
    response.headers["Cache-Control"] = "private, max-age=300"
    response.headers["ETag"] = generate_etag(supplier)
    
    return supplier
```

**Cache Warming:**
```python
@app.on_event("startup")
async def warm_cache():
    """Pre-populate cache with frequently accessed data"""
    # Cache top suppliers
    top_suppliers = await get_top_suppliers(limit=100)
    for supplier in top_suppliers:
        await cache_service.set(
            f"supplier:{supplier.id}",
            supplier,
            ttl=3600
        )
    
    # Cache user permissions
    active_users = await get_active_users()
    for user in active_users:
        permissions = await get_user_permissions(user.id)
        await cache_service.set(
            f"permissions:{user.id}",
            permissions,
            ttl=3600
        )
```

### Asynchronous Processing

**Background Tasks:**
```python
from fastapi import BackgroundTasks

@app.post("/api/v1/suppliers/{supplier_id}/evaluate")
async def evaluate_supplier(
    supplier_id: str,
    background_tasks: BackgroundTasks
):
    """Trigger evaluation and return immediately"""
    
    # Queue background task
    background_tasks.add_task(
        perform_evaluation,
        supplier_id
    )
    
    return {
        "status": "evaluation_queued",
        "supplier_id": supplier_id
    }

async def perform_evaluation(supplier_id: str):
    """Perform expensive evaluation in background"""
    supplier = await get_supplier(supplier_id)
    
    # Run ML models
    risk_score = await predict_risk(supplier)
    fraud_score = await predict_fraud(supplier)
    
    # Update supplier
    await update_supplier_scores(supplier_id, risk_score, fraud_score)
    
    # Send notification
    await notify_user(supplier.owner_id, "Evaluation complete")
```

**Task Queue (Celery):**
```python
# For more complex background processing
from celery import Celery

celery_app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

@celery_app.task
def generate_large_report(report_id: str):
    """Generate report asynchronously"""
    report = fetch_report_config(report_id)
    data = fetch_report_data(report.filters)
    file_path = generate_report_file(data, report.format)
    
    # Update report status
    update_report_status(report_id, "completed", file_path)
    
    # Send email notification
    send_email(report.recipients, file_path)
```

### Response Compression

```python
from fastapi.middleware.gzip import GZipMiddleware

# Enable gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### Request Batching

```python
@app.post("/api/v1/suppliers/batch")
async def batch_create_suppliers(suppliers: List[SupplierCreate]):
    """Create multiple suppliers in one request"""
    
    # Validate all suppliers first
    for supplier in suppliers:
        validate_supplier(supplier)
    
    # Bulk insert
    results = await db.bulk_insert(suppliers)
    
    return {
        "created": len(results),
        "suppliers": results
    }
```

### Database Query Batching

```python
# Use DataLoader pattern to batch database queries
from aiodataloader import DataLoader

class SupplierLoader(DataLoader):
    async def batch_load_fn(self, supplier_ids):
        """Load multiple suppliers in one query"""
        suppliers = await db.query(Supplier)\
            .filter(Supplier.id.in_(supplier_ids))\
            .all()
        
        # Return in same order as requested
        supplier_map = {s.id: s for s in suppliers}
        return [supplier_map.get(id) for id in supplier_ids]

# Usage
supplier_loader = SupplierLoader()
suppliers = await asyncio.gather(
    supplier_loader.load("id1"),
    supplier_loader.load("id2"),
    supplier_loader.load("id3")
)
# Results in single database query instead of 3
```

### CDN for Static Assets

```python
# Serve static files from CDN
STATIC_URL = "https://cdn.example.com/static/"

@app.get("/api/v1/reports/{report_id}/download")
async def download_report(report_id: str):
    """Redirect to CDN for file download"""
    report = await get_report(report_id)
    
    # Generate signed URL for CDN
    cdn_url = generate_signed_url(
        f"{STATIC_URL}/reports/{report.file_path}",
        expires_in=3600
    )
    
    return RedirectResponse(url=cdn_url)
```

### Performance Monitoring

```python
# Track endpoint performance
from prometheus_client import Histogram

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint', 'status']
)

@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).observe(duration)
    
    # Add performance headers
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    
    return response
```


## Security Considerations

### Authentication Security

**Password Requirements:**
```python
# backend/services/password_service.py
import re
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class PasswordPolicy:
    MIN_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    
    @staticmethod
    def validate(password: str) -> tuple[bool, str]:
        """Validate password against policy"""
        if len(password) < PasswordPolicy.MIN_LENGTH:
            return False, f"Password must be at least {PasswordPolicy.MIN_LENGTH} characters"
        
        if PasswordPolicy.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            return False, "Password must contain uppercase letter"
        
        if PasswordPolicy.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            return False, "Password must contain lowercase letter"
        
        if PasswordPolicy.REQUIRE_DIGIT and not re.search(r'\d', password):
            return False, "Password must contain digit"
        
        if PasswordPolicy.REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain special character"
        
        return True, "Password is valid"
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using Argon2"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
```

**Multi-Factor Authentication:**
```python
# backend/services/mfa_service.py
import pyotp
import qrcode
from io import BytesIO

class MFAService:
    @staticmethod
    def generate_secret() -> str:
        """Generate MFA secret"""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_qr_code(user_email: str, secret: str) -> bytes:
        """Generate QR code for MFA setup"""
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(
            name=user_email,
            issuer_name="Supplier Management"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
    
    @staticmethod
    def verify_code(secret: str, code: str) -> bool:
        """Verify MFA code"""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)
```

### Token Security

**JWT Configuration:**
```python
# backend/services/token_service.py
from jose import jwt, JWTError
from datetime import datetime, timedelta

class TokenService:
    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: timedelta = None
    ) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.JWT_EXPIRATION_MINUTES
            )
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": str(uuid.uuid4())  # Unique token ID
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # Check if token is revoked
            jti = payload.get("jti")
            if await is_token_revoked(jti):
                raise AuthenticationError("Token has been revoked")
            
            return payload
            
        except JWTError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")
```

**Token Revocation:**
```python
# Store revoked tokens in Redis with expiration
async def revoke_token(jti: str, expires_at: datetime):
    """Add token to revocation list"""
    ttl = int((expires_at - datetime.utcnow()).total_seconds())
    await redis.setex(f"revoked_token:{jti}", ttl, "1")

async def is_token_revoked(jti: str) -> bool:
    """Check if token is revoked"""
    return await redis.exists(f"revoked_token:{jti}")
```

### SQL Injection Prevention

```python
# ALWAYS use parameterized queries
# GOOD: Parameterized query
async def get_supplier_by_name(name: str):
    query = "SELECT * FROM suppliers WHERE name = :name"
    result = await database.fetch_one(query, {"name": name})
    return result

# BAD: String concatenation (NEVER DO THIS)
# query = f"SELECT * FROM suppliers WHERE name = '{name}'"

# Use SQLAlchemy ORM for automatic parameterization
async def get_suppliers_by_risk(min_risk: float, max_risk: float):
    suppliers = await db.query(Supplier)\
        .filter(Supplier.risk_score >= min_risk)\
        .filter(Supplier.risk_score <= max_risk)\
        .all()
    return suppliers
```

### XSS Prevention

```python
# Sanitize HTML input
import bleach

def sanitize_html(text: str) -> str:
    """Remove dangerous HTML/JavaScript"""
    allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a']
    allowed_attributes = {'a': ['href', 'title']}
    
    return bleach.clean(
        text,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )

# Set security headers
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response
```

### CSRF Protection

```python
# For state-changing operations, require CSRF token
from fastapi_csrf_protect import CsrfProtect

@app.post("/api/v1/suppliers")
async def create_supplier(
    supplier: SupplierCreate,
    csrf_protect: CsrfProtect = Depends()
):
    """Create supplier with CSRF protection"""
    await csrf_protect.validate_csrf(request)
    
    result = await supplier_service.create(supplier)
    return result
```

### Secrets Management

```python
# backend/core/secrets.py
import boto3
from typing import Optional

class SecretsManager:
    def __init__(self):
        if settings.ENVIRONMENT == "production":
            self.client = boto3.client('secretsmanager')
        else:
            self.client = None
    
    def get_secret(self, secret_name: str) -> Optional[str]:
        """Retrieve secret from AWS Secrets Manager"""
        if self.client is None:
            # Development: use environment variables
            return os.getenv(secret_name)
        
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            return response['SecretString']
        except Exception as e:
            logger.error(f"Failed to retrieve secret {secret_name}: {e}")
            return None

# Usage
secrets_manager = SecretsManager()
database_password = secrets_manager.get_secret("database_password")
encryption_key = secrets_manager.get_secret("encryption_key")
```

### Audit Trail for Security Events

```python
# Log all security-related events
async def log_security_event(
    event_type: str,
    user_id: str,
    details: dict,
    severity: str = "INFO"
):
    """Log security event to audit log"""
    await audit_service.log_event(AuditEvent(
        action=f"SECURITY_{event_type}",
        user_id=user_id,
        metadata={
            "severity": severity,
            "details": details
        }
    ))

# Examples
await log_security_event("LOGIN_FAILED", user_id, {"reason": "invalid_password"}, "WARNING")
await log_security_event("MFA_ENABLED", user_id, {}, "INFO")
await log_security_event("PERMISSION_DENIED", user_id, {"resource": resource_id}, "WARNING")
await log_security_event("TOKEN_REVOKED", user_id, {"reason": "logout"}, "INFO")
```

### Regular Security Scanning

```bash
# Dependency vulnerability scanning
pip install safety
safety check --json

# Container scanning
docker scan backend:latest

# Static code analysis
pip install bandit
bandit -r backend/ -f json -o security-report.json

# Secret scanning
pip install detect-secrets
detect-secrets scan --baseline .secrets.baseline
```


## Migration Strategy

### Phased Rollout Approach

**Design Rationale**: Incremental migration reduces risk and allows validation at each phase. Feature flags enable gradual rollout and quick rollback if issues arise.

**Phase 1: Foundation (Weeks 1-2)**
- Database schema updates and migrations
- Configuration management enhancement
- Structured logging implementation
- Basic monitoring setup

**Phase 2: Security Core (Weeks 3-4)**
- Authentication service implementation
- Authorization and RBAC
- Password policies and MFA
- Token management

**Phase 3: Audit and Compliance (Weeks 5-6)**
- Audit logging service
- Compliance reporting
- Data encryption at rest
- Backup automation

**Phase 4: Performance and Scalability (Weeks 7-8)**
- Redis caching implementation
- Connection pooling optimization
- Rate limiting
- Database query optimization

**Phase 5: Advanced Features (Weeks 9-10)**
- Webhook service
- Export and reporting
- Monitoring and alerting
- API documentation enhancement

**Phase 6: Testing and Hardening (Weeks 11-12)**
- Comprehensive testing
- Security hardening
- Performance tuning
- Documentation finalization

### Feature Flags

```python
# backend/core/feature_flags.py
from enum import Enum

class FeatureFlag(str, Enum):
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    AUDIT_LOGGING = "audit_logging"
    RATE_LIMITING = "rate_limiting"
    CACHING = "caching"
    WEBHOOKS = "webhooks"
    MFA = "mfa"
    ENCRYPTION = "encryption"

class FeatureFlagService:
    def __init__(self):
        self.flags = {
            FeatureFlag.AUTHENTICATION: True,
            FeatureFlag.AUTHORIZATION: True,
            FeatureFlag.AUDIT_LOGGING: True,
            FeatureFlag.RATE_LIMITING: False,  # Gradually enable
            FeatureFlag.CACHING: False,
            FeatureFlag.WEBHOOKS: False,
            FeatureFlag.MFA: False,
            FeatureFlag.ENCRYPTION: True
        }
    
    def is_enabled(self, flag: FeatureFlag) -> bool:
        """Check if feature is enabled"""
        return self.flags.get(flag, False)
    
    def enable(self, flag: FeatureFlag):
        """Enable feature flag"""
        self.flags[flag] = True
    
    def disable(self, flag: FeatureFlag):
        """Disable feature flag"""
        self.flags[flag] = False

feature_flags = FeatureFlagService()

# Usage in code
if feature_flags.is_enabled(FeatureFlag.RATE_LIMITING):
    await rate_limiter.check_limit(user_id, endpoint)
```

### Database Migration Plan

**Step 1: Create Migration Scripts**
```bash
# Create initial migration
alembic revision --autogenerate -m "Add authentication tables"

# Create audit logging migration
alembic revision --autogenerate -m "Add audit logging tables"

# Create webhook migration
alembic revision --autogenerate -m "Add webhook tables"
```

**Step 2: Test Migrations**
```bash
# Test on development database
alembic upgrade head

# Verify schema
psql $DATABASE_URL -c "\dt"

# Test rollback
alembic downgrade -1
alembic upgrade head
```

**Step 3: Production Migration**
```bash
# Backup database before migration
pg_dump $DATABASE_URL > backup_pre_migration.sql

# Run migrations
alembic upgrade head

# Verify migration
alembic current
```

### Data Migration

**Migrate Existing Users:**
```python
# scripts/migrate_users.py
async def migrate_existing_users():
    """Migrate existing users to new authentication system"""
    
    # Get all existing users (if any)
    old_users = await get_legacy_users()
    
    for old_user in old_users:
        # Create new user with hashed password
        new_user = User(
            id=old_user.id,
            email=old_user.email,
            password_hash=hash_password(generate_temp_password()),
            full_name=old_user.name,
            is_active=True,
            is_verified=False  # Require email verification
        )
        
        await db.add(new_user)
        
        # Assign default role
        await assign_role(new_user.id, "viewer")
        
        # Send password reset email
        await send_password_reset_email(new_user.email)
    
    await db.commit()
    logger.info(f"Migrated {len(old_users)} users")
```

### Backward Compatibility

**Maintain Existing Endpoints:**
```python
# Keep old endpoints working during transition
@app.get("/api/suppliers")  # Old endpoint
async def get_suppliers_legacy():
    """Legacy endpoint for backward compatibility"""
    logger.warning("Legacy endpoint used: /api/suppliers")
    return await get_suppliers_v1()

@app.get("/api/v1/suppliers")  # New endpoint
@require_authentication
async def get_suppliers_v1():
    """New authenticated endpoint"""
    return await supplier_service.get_all()
```

**Gradual Authentication Enforcement:**
```python
# Make authentication optional initially
@app.get("/api/v1/suppliers")
async def get_suppliers(
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Endpoint with optional authentication"""
    
    if current_user:
        # Authenticated: return full data
        return await supplier_service.get_all()
    else:
        # Unauthenticated: return limited data
        logger.warning("Unauthenticated access to suppliers endpoint")
        return await supplier_service.get_public_data()
```

### Rollback Plan

**Database Rollback:**
```bash
# Rollback to previous migration
alembic downgrade -1

# Restore from backup if needed
psql $DATABASE_URL < backup_pre_migration.sql
```

**Application Rollback:**
```bash
# Revert to previous version
docker pull backend:previous-version
docker stop backend-current
docker run -d --name backend backend:previous-version

# Or use feature flags to disable new features
curl -X POST http://localhost:8000/api/v1/admin/feature-flags/disable \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -d '{"flag": "authentication"}'
```

### Monitoring During Migration

```python
# Track migration progress
migration_metrics = {
    "users_migrated": 0,
    "errors": 0,
    "start_time": None,
    "end_time": None
}

@app.get("/api/v1/admin/migration/status")
@require_permission(Permission.SYSTEM_ADMIN)
async def get_migration_status():
    """Get migration progress"""
    return {
        "status": "in_progress" if migration_metrics["end_time"] is None else "completed",
        "users_migrated": migration_metrics["users_migrated"],
        "errors": migration_metrics["errors"],
        "duration_seconds": (
            datetime.utcnow() - migration_metrics["start_time"]
        ).total_seconds() if migration_metrics["start_time"] else 0
    }
```

### Communication Plan

**Internal Communication:**
- Week before migration: Notify all stakeholders
- Day before migration: Final reminder and maintenance window
- During migration: Real-time status updates
- After migration: Summary and next steps

**User Communication:**
- Email notification about new authentication requirements
- Documentation updates with migration guide
- Support channels for migration issues
- FAQ document for common questions

**Documentation Updates:**
- Update API documentation with authentication requirements
- Create migration guide for API consumers
- Update deployment documentation
- Create troubleshooting guide


## Compliance and Regulatory Considerations

### GDPR Compliance

**Data Subject Rights:**
```python
# backend/services/gdpr_service.py
class GDPRService:
    async def export_user_data(self, user_id: str) -> dict:
        """Export all user data (Right to Data Portability)"""
        user = await get_user(user_id)
        suppliers = await get_user_suppliers(user_id)
        audit_logs = await get_user_audit_logs(user_id)
        
        return {
            "user": user.dict(),
            "suppliers": [s.dict() for s in suppliers],
            "audit_logs": [log.dict() for log in audit_logs],
            "export_date": datetime.utcnow().isoformat()
        }
    
    async def delete_user_data(self, user_id: str) -> bool:
        """Delete all user data (Right to Erasure)"""
        # Anonymize audit logs (keep for compliance)
        await anonymize_audit_logs(user_id)
        
        # Delete user-created data
        await delete_user_suppliers(user_id)
        await delete_user_exports(user_id)
        
        # Delete user account
        await delete_user(user_id)
        
        # Log deletion
        await audit_service.log_event(AuditEvent(
            action="USER_DATA_DELETED",
            user_id=user_id,
            metadata={"reason": "gdpr_request"}
        ))
        
        return True
    
    async def restrict_processing(self, user_id: str) -> bool:
        """Restrict data processing (Right to Restriction)"""
        user = await get_user(user_id)
        user.processing_restricted = True
        await db.commit()
        
        return True

# API endpoints for GDPR
@app.get("/api/v1/gdpr/export")
@require_authentication
async def export_my_data(current_user: User):
    """Export user's personal data"""
    data = await gdpr_service.export_user_data(current_user.id)
    
    # Create encrypted export
    encrypted_data = encrypt_data(json.dumps(data))
    
    return Response(
        content=encrypted_data,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename=user_data_{current_user.id}.enc"
        }
    )

@app.delete("/api/v1/gdpr/delete")
@require_authentication
async def delete_my_data(current_user: User):
    """Request account deletion"""
    await gdpr_service.delete_user_data(current_user.id)
    return {"message": "Your data has been deleted"}
```

**Data Retention Policies:**
```python
# Automated data retention enforcement
class DataRetentionService:
    RETENTION_POLICIES = {
        "audit_logs": 2555,  # 7 years in days
        "user_sessions": 90,
        "export_files": 30,
        "webhook_deliveries": 90
    }
    
    async def enforce_retention_policies(self):
        """Delete data older than retention period"""
        for data_type, retention_days in self.RETENTION_POLICIES.items():
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            if data_type == "audit_logs":
                # Archive instead of delete
                await archive_old_audit_logs(cutoff_date)
            else:
                await delete_old_data(data_type, cutoff_date)
            
            logger.info(f"Enforced retention policy for {data_type}")

# Run daily
@app.on_event("startup")
async def schedule_retention_enforcement():
    scheduler.add_job(
        data_retention_service.enforce_retention_policies,
        'cron',
        hour=3,
        minute=0
    )
```

### SOC 2 Compliance

**Access Control Requirements:**
- Role-based access control (RBAC) ✓
- Principle of least privilege ✓
- Regular access reviews ✓
- MFA for privileged accounts ✓

**Audit Logging Requirements:**
- Comprehensive audit trails ✓
- Immutable logs ✓
- Log retention (7 years) ✓
- Log monitoring and alerting ✓

**Data Security Requirements:**
- Encryption at rest (AES-256) ✓
- Encryption in transit (TLS 1.3) ✓
- Key rotation ✓
- Secure key management ✓

**Availability Requirements:**
- Backup and recovery procedures ✓
- Disaster recovery plan ✓
- Monitoring and alerting ✓
- Incident response plan ✓

### ISO 27001 Compliance

**Information Security Controls:**
```python
# Security control implementation tracking
SECURITY_CONTROLS = {
    "A.9.2.1": {
        "name": "User registration and de-registration",
        "implemented": True,
        "evidence": "User management API with audit logging"
    },
    "A.9.2.2": {
        "name": "User access provisioning",
        "implemented": True,
        "evidence": "RBAC system with role assignment"
    },
    "A.9.2.3": {
        "name": "Management of privileged access rights",
        "implemented": True,
        "evidence": "Admin role with MFA requirement"
    },
    "A.9.4.1": {
        "name": "Information access restriction",
        "implemented": True,
        "evidence": "Authorization middleware on all endpoints"
    },
    "A.12.4.1": {
        "name": "Event logging",
        "implemented": True,
        "evidence": "Comprehensive audit logging service"
    }
}
```

### HIPAA Compliance (if handling health data)

**Technical Safeguards:**
- Access control (unique user IDs, automatic logoff) ✓
- Audit controls (audit logs, monitoring) ✓
- Integrity controls (data validation, checksums) ✓
- Transmission security (encryption, integrity controls) ✓

**Administrative Safeguards:**
- Security management process
- Workforce security (authorization, supervision)
- Information access management
- Security awareness and training

### Compliance Reporting

```python
# backend/services/compliance_service.py
class ComplianceService:
    async def generate_compliance_report(
        self,
        report_type: str,
        start_date: date,
        end_date: date
    ) -> bytes:
        """Generate compliance report"""
        
        if report_type == "gdpr":
            return await self._generate_gdpr_report(start_date, end_date)
        elif report_type == "soc2":
            return await self._generate_soc2_report(start_date, end_date)
        elif report_type == "iso27001":
            return await self._generate_iso27001_report(start_date, end_date)
        else:
            raise ValueError(f"Unknown report type: {report_type}")
    
    async def _generate_gdpr_report(
        self,
        start_date: date,
        end_date: date
    ) -> bytes:
        """Generate GDPR compliance report"""
        
        # Collect metrics
        metrics = {
            "data_subject_requests": await count_gdpr_requests(start_date, end_date),
            "data_breaches": await count_data_breaches(start_date, end_date),
            "consent_records": await count_consent_records(start_date, end_date),
            "data_retention_compliance": await check_retention_compliance()
        }
        
        # Generate PDF report
        pdf = generate_pdf_report("GDPR Compliance Report", metrics)
        return pdf

@app.get("/api/v1/compliance/report")
@require_permission(Permission.SYSTEM_ADMIN)
async def get_compliance_report(
    report_type: str,
    start_date: date,
    end_date: date
):
    """Generate compliance report"""
    report = await compliance_service.generate_compliance_report(
        report_type,
        start_date,
        end_date
    )
    
    return Response(
        content=report,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={report_type}_report.pdf"
        }
    )
```

## Summary

This design document provides a comprehensive blueprint for transforming the AI Supplier Selection & Risk Management Dashboard into an enterprise-grade application. The design addresses all 15 requirements from the requirements document with:

**Key Design Decisions:**

1. **JWT-based Authentication with Redis Sessions**: Balances stateless scalability with session management needs
2. **RBAC with Role Hierarchy**: Simplifies permission management while maintaining flexibility
3. **Asynchronous Audit Logging**: Prevents performance impact while ensuring comprehensive trails
4. **Multi-Level Caching Strategy**: Optimizes performance at application, distributed, and HTTP levels
5. **Sliding Window Rate Limiting**: Provides accurate rate limiting for distributed deployments
6. **Prometheus + Grafana Monitoring**: Industry-standard observability stack
7. **Automated Backup with Point-in-Time Recovery**: Ensures data durability and precise restoration
8. **Webhook Service with Retry Logic**: Enables reliable external integrations
9. **Phased Migration with Feature Flags**: Reduces risk and enables gradual rollout

**Technology Stack Additions:**
- Authentication: PyJWT, passlib, pyotp
- Caching: redis-py, aioredis
- Monitoring: prometheus-client, structlog
- Security: cryptography, bleach
- Rate Limiting: slowapi
- Database: SQLAlchemy with Alembic migrations

**Performance Targets:**
- API response time: <500ms (P95) under 1000 concurrent requests
- Database connection pool: 50 connections with 10 overflow
- Cache hit rate: >80% for frequently accessed data
- Backup RTO: 4 hours, RPO: 6 hours

**Security Measures:**
- AES-256 encryption at rest
- TLS 1.3 for data in transit
- Argon2 password hashing
- MFA support for privileged accounts
- Comprehensive input validation and sanitization
- Regular security scanning and updates

The design maintains backward compatibility with existing functionality while adding enterprise features incrementally through a phased rollout approach.

