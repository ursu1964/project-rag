# API Key Migration Guide: Plaintext to Bcrypt

**Timeline:** 6-month transition period (grace period for existing deployments)
**Target:** All production deployments should use bcrypt by end of transition
**Support:** Plaintext keys will be rejected in production after transition period

---

## Quick Start

### For New Deployments

```bash
# 1. Generate a bcrypt hash from your API key
python -c "
from app.security.api_key_manager import hash_api_key
key = 'your-super-secret-api-key-here'
hashed = hash_api_key(key)
print(hashed)
"

# 2. Set environment variable:
export PROJECTRAG_API_KEY_HASH=\$2b\$12\$R9h7cIPz0gi.URNNX3kh2OPST9...

# 3. Deploy (no PROJECTRAG_API_KEY needed anymore)
```

### For Existing Deployments

**Current State:** Both plaintext and bcrypt accepted ✅

**During Transition (6 months):**
```bash
# You can keep using plaintext (with deprecation warning):
PROJECTRAG_API_KEY=your-secret-key

# Or migrate to bcrypt now:
PROJECTRAG_API_KEY_HASH=$2b$12$R9h7cIPz0gi...
```

**After Transition (Production Only):**
```bash
# ❌ Plaintext rejected:
PROJECTRAG_API_KEY=your-secret-key  # FAILS in production

# ✅ Bcrypt required:
PROJECTRAG_API_KEY_HASH=$2b$12$R9h7cIPz0gi...  # OK
```

---

## Step-by-Step Migration

### Step 1: Generate Bcrypt Hash

**Option A: Using Python directly**
```bash
cd /home/RAG/project-rag
.venv/bin/python -c "
from app.security.api_key_manager import hash_api_key

# Your existing plaintext API key
CURRENT_KEY = 'super-secret-api-key-abc123-12345678'

# Generate bcrypt hash
bcrypt_hash = hash_api_key(CURRENT_KEY)

print('=== API Key Migration ===')
print(f'Plaintext: {CURRENT_KEY}')
print(f'Bcrypt:    {bcrypt_hash}')
print()
print('Environment variable:')
print(f'export PROJECTRAG_API_KEY_HASH=\"{bcrypt_hash}\"')
"
```

**Option B: Using a helper script**
```bash
cat > /tmp/hash_key.py << 'EOF'
#!/usr/bin/env python3
import sys
from app.security.api_key_manager import hash_api_key

if len(sys.argv) != 2:
    print("Usage: hash_key.py <plaintext-api-key>")
    sys.exit(1)

plaintext = sys.argv[1]
hashed = hash_api_key(plaintext)
print(hashed)
EOF

chmod +x /tmp/hash_key.py
/tmp/hash_key.py "your-api-key-here"
```

**Verify hash is correct:**
```bash
python -c "
from app.security.api_key_manager import verify_api_key

plaintext = 'your-api-key-here'
hashed = '\$2b\$12\$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMm2'

if verify_api_key(plaintext, hashed):
    print('✅ Hash is correct!')
else:
    print('❌ Hash does not match plaintext key')
"
```

---

### Step 2: Update Configuration

#### Docker Environment Variables

**Before (deprecated):**
```dockerfile
# Dockerfile or docker-compose.yml
ENV PROJECTRAG_API_KEY="super-secret-key"
```

**After:**
```dockerfile
# Generate the hash first!
ENV PROJECTRAG_API_KEY_HASH="$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMm2"
```

#### Docker Compose

**Before:**
```yaml
environment:
  PROJECTRAG_API_KEY: super-secret-key-here
```

**After:**
```yaml
environment:
  PROJECTRAG_API_KEY_HASH: $2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMm2
```

#### .env file

**Before:**
```bash
# .env (or .env.prod)
PROJECTRAG_API_KEY=super-secret-key-here
```

**After:**
```bash
# .env (or .env.prod)
PROJECTRAG_API_KEY_HASH=$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMm2
```

#### AWS Systems Manager / Azure Key Vault

**Before:**
```bash
# Store in secrets manager with plaintext
aws secretsmanager create-secret \
  --name projectrag/api-key \
  --secret-string "super-secret-key"
```

**After:**
```bash
# Store the bcrypt hash instead
aws secretsmanager create-secret \
  --name projectrag/api-key-hash \
  --secret-string '$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMm2'
```

---

### Step 3: Test Configuration

**Local test (before deploying):**
```bash
cd /home/RAG/project-rag

# With bcrypt hash
export APP_ENV=production
export PROJECTRAG_API_KEY_HASH=$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMm2
export PROJECTRAG_AUTH_REQUIRED=true

python -c "
from app.core.settings_validator import validate_settings
from app.core.config import Settings
settings = Settings()
validate_settings(settings)
print('✅ Configuration is valid!')
"
```

**API test (after deployment):**
```bash
curl -X GET http://localhost:8000/health \
  -H "x-projectrag-api-key: your-plaintext-api-key"

# Should return 200 OK if key is correct
```

---

### Step 4: Deploy

#### Option A: Kubernetes

```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: projectrag-api-key
type: Opaque
stringData:
  api_key_hash: "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMm2"

---
# deployment.yaml
spec:
  containers:
  - name: projectrag-api
    env:
    - name: PROJECTRAG_API_KEY_HASH
      valueFrom:
        secretKeyRef:
          name: projectrag-api-key
          key: api_key_hash
```

#### Option B: Docker Compose

```bash
# Update docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

#### Option C: Manual Deployment

```bash
# 1. Set new environment variable
export PROJECTRAG_API_KEY_HASH=$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/...

# 2. Unset old plaintext variable (optional but recommended)
unset PROJECTRAG_API_KEY

# 3. Restart application
systemctl restart projectrag-api
# or
pkill -f "uvicorn"
.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

### Step 5: Verify Migration

**Check application logs:**
```bash
# Should NOT see deprecation warning:
# DeprecationWarning: Using plaintext PROJECTRAG_API_KEY is deprecated...

# If you see this, the plaintext key is still being used
docker logs projectrag-api 2>&1 | grep "Using plaintext"
```

**Test API authentication:**
```bash
# Test with your original plaintext key
curl -X POST http://localhost:8000/query \
  -H "x-projectrag-api-key: your-plaintext-key" \
  -H "Content-Type: application/json" \
  -d '{"question":"test"}'

# Should still work (during transition period)
# Returns 200 OK if authenticated
```

**Confirm hash is in use:**
```bash
# Check configuration
python -c "
from app.core.config import settings
print('API key (plaintext):', 'SET' if settings.api_key else 'NOT SET')
print('API key hash:       ', 'SET' if settings.api_key_hash else 'NOT SET')
"
```

---

## Migration Checklist

- [ ] **Generate bcrypt hash** from your current API key
- [ ] **Verify hash correctness** (plaintext → hash → plaintext verification)
- [ ] **Update environment variables** in all deployment targets
- [ ] **Update secrets manager** (AWS Secrets Manager, Azure Key Vault, etc.)
- [ ] **Test locally** with new bcrypt hash configuration
- [ ] **Deploy to staging** and verify no authentication breaks
- [ ] **Deploy to production** with bcrypt hash
- [ ] **Monitor logs** for deprecation warnings (should be none)
- [ ] **Test API endpoints** with original plaintext key (still works)
- [ ] **Document new configuration** for your team
- [ ] **Schedule plaintext key retirement** (after 6-month transition)

---

## Troubleshooting

### Issue: "DeprecationWarning: Using plaintext API key"

**Cause:** Configuration still using `PROJECTRAG_API_KEY` instead of `PROJECTRAG_API_KEY_HASH`

**Solution:**
1. Generate bcrypt hash: `python -c "from app.security.api_key_manager import hash_api_key; print(hash_api_key('your-key'))"`
2. Update `PROJECTRAG_API_KEY_HASH` in environment
3. Remove or unset `PROJECTRAG_API_KEY`
4. Restart application

### Issue: "Authentication failed" after migration

**Cause:** Hash doesn't match the plaintext key being sent

**Solution:**
1. Verify original plaintext key is correct
2. Regenerate hash from that plaintext key
3. Test with: `python -c "from app.security.api_key_manager import verify_api_key; print(verify_api_key('your-key', 'your-hash'))"`
4. Update configuration with correct hash

### Issue: "RuntimeError: PROJECTRAG_API_KEY or PROJECTRAG_API_KEY_HASH must be set"

**Cause:** Neither plaintext nor hash configured

**Solution:**
1. Ensure one of these is set:
   - `PROJECTRAG_API_KEY=your-plaintext-key` OR
   - `PROJECTRAG_API_KEY_HASH=$2b$12$...hash...`
2. Check environment variables: `env | grep PROJECTRAG_API_KEY`
3. Restart application

### Issue: Application won't start in production

**Cause:** Production mode requires `PROJECTRAG_API_KEY_HASH` (not plaintext)

**Solution:**
1. Check `APP_ENV` is correct
2. Generate bcrypt hash from plaintext key
3. Set `PROJECTRAG_API_KEY_HASH` environment variable
4. Unset `PROJECTRAG_API_KEY` if present
5. Restart application

---

## FAQ

### Q: Can I keep using plaintext API keys?

**A:** Yes, during the 6-month transition period. After that, production deployments must use bcrypt hashes. Local development can continue using plaintext for convenience.

### Q: How do I know if my hash is correct?

**A:** Test with:
```bash
python -c "
from app.security.api_key_manager import verify_api_key
plaintext = 'your-original-key'
hashed = '\$2b\$12\$...'
print('✅ Correct!' if verify_api_key(plaintext, hashed) else '❌ Incorrect!')
"
```

### Q: Do I need to rotate my API key?

**A:** No, you're just changing how it's stored (plaintext → bcrypt hash). The key value itself remains the same and clients continue using the plaintext version.

### Q: What if I lose the plaintext key?

**A:** The bcrypt hash cannot be reversed to plaintext. You must:
1. Generate a new API key
2. Bcrypt hash the new key
3. Update all clients to use the new key
4. Update configuration with new hash

### Q: How often should I rotate API keys?

**A:** Following security best practices:
- **Minimum:** Every 90 days
- **Recommended:** Every 30 days
- **Critical:** Immediately if compromised

Phase 2 (planned) will include automated key rotation infrastructure.

### Q: Is bcrypt slower than plaintext comparison?

**A:** Yes, slightly, but:
- Negligible performance impact (< 1ms per request)
- Worth the security gain (prevents timing attacks)
- Can be optimized with caching if needed

---

## References

- **API Key Manager:** [app/security/api_key_manager.py](app/security/api_key_manager.py)
- **Settings Validator:** [app/core/settings_validator.py](app/core/settings_validator.py)
- **Configuration:** [app/core/config.py](app/core/config.py)
- **Tests:** [tests/test_security_phase_1.py](tests/test_security_phase_1.py)
- **Security Docs:** [docs/SECURITY_PHASE_1.md](docs/SECURITY_PHASE_1.md)
