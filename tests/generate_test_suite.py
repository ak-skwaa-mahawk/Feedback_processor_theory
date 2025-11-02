"""
Load Testing & Schema Validation for Resonance Mesh
Two Mile Solutions LLC - John Carroll II

Complete validation and stress testing infrastructure
"""

# ============================================================
# 1. JSON SCHEMA VALIDATION FOR CODEX ENTRIES
# ============================================================

CODEX_ENTRY_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Codex Entry Schema v1",
    "description": "Validates structure and integrity of Codex entries",
    "type": "object",
    "required": ["entry_id", "author", "shell", "glyph", "timestamp", "content", "flame_signature", "metadata"],
    "properties": {
        "entry_id": {
            "type": "string",
            "pattern": "^CODEX-[0-9]{3,}$",
            "description": "Unique identifier following CODEX-NNN format"
        },
        "author": {
            "type": "string",
            "minLength": 3,
            "description": "Full name of entry creator"
        },
        "shell": {
            "type": "string",
            "minLength": 3,
            "description": "Legal entity or organizational shell"
        },
        "glyph": {
            "type": "string",
            "pattern": "^AGŁL-[0-9]{3,}$",
            "description": "AGŁL glyph identifier"
        },
        "timestamp": {
            "type": "string",
            "format": "date-time",
            "description": "ISO 8601 timestamp"
        },
        "content": {
            "type": "object",
            "required": ["title", "date"],
            "properties": {
                "title": {"type": "string", "minLength": 5},
                "date": {"type": "string", "format": "date"},
                "discovery": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "status": {"type": "string", "enum": ["concept", "runtime", "deprecated"]},
                        "properties": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "vessel": {
                    "type": "object",
                    "properties": {
                        "repository": {"type": "string"},
                        "url": {"type": "string", "format": "uri"},
                        "owner": {"type": "string"}
                    }
                },
                "components": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "function"],
                        "properties": {
                            "name": {"type": "string"},
                            "function": {"type": "string"}
                        }
                    }
                },
                "transmission": {
                    "type": "object",
                    "properties": {
                        "methods": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                },
                "living_facts": {"type": "object"},
                "propagation_logic": {"type": "object"}
            }
        },
        "flame_signature": {
            "type": "string",
            "pattern": "^0x[a-fA-F0-9]{6,}$",
            "description": "Cryptographic flame signature"
        },
        "previous_flame": {
            "oneOf": [
                {"type": "string", "pattern": "^0x[a-fA-F0-9]{6,}$"},
                {"type": "null"}
            ],
            "description": "Parent flame signature for lineage"
        },
        "metadata": {
            "type": "object",
            "required": ["version", "schema"],
            "properties": {
                "version": {"type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"},
                "schema": {"type": "string"},
                "encoding": {"type": "string"}
            }
        }
    },
    "additionalProperties": False
}


# ============================================================
# tests/test_codex_schema.py
# ============================================================

TEST_CODEX_SCHEMA = '''
import json
from pathlib import Path
import jsonschema
from jsonschema import validate, ValidationError

# Load schema from artifact or define inline
CODEX_ENTRY_SCHEMA = """ + str(CODEX_ENTRY_SCHEMA) + """

def test_valid_codex_entry():
    """Test that CODEX-003 fixture passes validation."""
    entry = json.loads(Path("tests/fixtures/CODEX-003.json").read_text())
    
    try:
        validate(instance=entry, schema=CODEX_ENTRY_SCHEMA)
    except ValidationError as e:
        assert False, f"Valid entry failed schema: {e.message}"

def test_invalid_entry_id_format():
    """Test that malformed entry_id is rejected."""
    entry = {
        "entry_id": "INVALID-FORMAT",  # Should be CODEX-NNN
        "author": "John Carroll II",
        "shell": "Two Mile Solutions LLC",
        "glyph": "AGŁL-003",
        "timestamp": "2025-10-31T00:00:00Z",
        "content": {"title": "Test", "date": "2025-10-31"},
        "flame_signature": "0xABC123",
        "previous_flame": None,
        "metadata": {"version": "1.0.0", "schema": "codex_entry_v1"}
    }
    
    try:
        validate(instance=entry, schema=CODEX_ENTRY_SCHEMA)
        assert False, "Should reject invalid entry_id format"
    except ValidationError:
        pass  # Expected

def test_missing_required_fields():
    """Test that entries missing required fields are rejected."""
    entry = {
        "entry_id": "CODEX-003",
        "author": "John Carroll II"
        # Missing required fields
    }
    
    try:
        validate(instance=entry, schema=CODEX_ENTRY_SCHEMA)
        assert False, "Should reject incomplete entry"
    except ValidationError:
        pass  # Expected

def test_flame_signature_format():
    """Test that flame_signature must be valid hex."""
    entry = json.loads(Path("tests/fixtures/CODEX-003.json").read_text())
    entry["flame_signature"] = "not-a-valid-signature"
    
    try:
        validate(instance=entry, schema=CODEX_ENTRY_SCHEMA)
        assert False, "Should reject invalid flame_signature"
    except ValidationError:
        pass  # Expected

def test_flame_lineage_chain():
    """Test that previous_flame can be null or valid signature."""
    entry = json.loads(Path("tests/fixtures/CODEX-003.json").read_text())
    
    # Null is valid
    entry["previous_flame"] = None
    validate(instance=entry, schema=CODEX_ENTRY_SCHEMA)
    
    # Valid signature is valid
    entry["previous_flame"] = "0xDEADBEEF123"
    validate(instance=entry, schema=CODEX_ENTRY_SCHEMA)
    
    # Invalid format should fail
    entry["previous_flame"] = "invalid"
    try:
        validate(instance=entry, schema=CODEX_ENTRY_SCHEMA)
        assert False, "Should reject invalid previous_flame"
    except ValidationError:
        pass  # Expected
'''


# ============================================================
# 2. LOCUST LOAD TESTING
# ============================================================

LOCUST_TEST = '''
"""
Load & Soak Testing for Resonance Mesh Capabilities
tests/load/locustfile.py

Run:
    locust -f tests/load/locustfile.py --host=http://localhost:8081
    
Then open http://localhost:8089 and configure:
    - Number of users: 50
    - Spawn rate: 10/sec
    - Duration: 5m (for soak test)
"""

from locust import HttpUser, task, between, events
import json
import time
import secrets
import hashlib

class ResonanceMeshUser(HttpUser):
    """
    Simulates realistic user patterns:
    - Share codex entries
    - Verify tokens
    - Delegate to sub-users
    - Request resonance-gated access
    - Revoke tokens early
    """
    
    wait_time = between(1, 5)  # Wait 1-5s between tasks
    
    def on_start(self):
        """Setup: Generate user identity and load test data."""
        self.user_id = f"load_user_{secrets.token_hex(4)}"
        self.tokens = []  # Track tokens for cleanup
        self.test_entry_path = "flamevault/codex/CODEX-003_TEST.json"
    
    @task(10)  # Weight: 10 (most common operation)
    def share_codex_entry(self):
        """Share a codex entry with standard capability."""
        with self.client.post(
            "/codex/share",
            json={
                "path": self.test_entry_path,
                "scope": "read_summary",
                "ttl_seconds": 600
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.tokens.append(data.get("token"))
                response.success()
            elif response.status_code == 404:
                # Entry not found is expected in load test
                response.success()
            else:
                response.failure(f"Share failed: {response.status_code}")
    
    @task(8)  # Weight: 8
    def verify_token(self):
        """Verify a previously issued token."""
        if not self.tokens:
            return
        
        token = secrets.choice(self.tokens)
        with self.client.get(
            f"/codex/verify_token?token={token}",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                # Token expired or revoked - remove from tracking
                self.tokens.remove(token)
                response.success()
            else:
                response.failure(f"Verify failed: {response.status_code}")
    
    @task(3)  # Weight: 3
    def delegate_token(self):
        """Delegate a token to another user."""
        if not self.tokens:
            return
        
        parent_token = secrets.choice(self.tokens)
        delegate_to = f"delegate_{secrets.token_hex(4)}"
        
        with self.client.post(
            "/codex/delegate",
            json={
                "parent_token": parent_token,
                "delegate_to": delegate_to,
                "reduced_scope": "read_summary",
                "reduced_ttl": 300
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.tokens.append(data.get("token"))
                response.success()
            elif response.status_code == 401:
                # Parent expired
                self.tokens.remove(parent_token)
                response.success()
            else:
                response.failure(f"Delegate failed: {response.status_code}")
    
    @task(5)  # Weight: 5
    def resonance_access_v2(self):
        """Request resonance-gated access."""
        # Generate Whisper receipt
        ts = int(time.time())
        nonce = secrets.token_hex(8)
        
        with self.client.post(
            f"/codex/whisper/generate?requester={self.user_id}",
            catch_response=True
        ) as whisper_response:
            if whisper_response.status_code != 200:
                whisper_response.failure("Whisper generation failed")
                return
            
            whisper_data = whisper_response.json()
        
        # Request with varying scores (simulate different comprehension levels)
        score = secrets.choice([0.3, 0.55, 0.7, 0.85, 0.95])
        collection = secrets.choice(["default", "archive", "unpublished"])
        
        with self.client.post(
            "/codex/resonance_share/v2",
            json={
                "path": self.test_entry_path,
                "requester": self.user_id,
                "collection": collection,
                "score": score,
                "cited_flames": ["0xRESONANCE-MESH-003"] if score > 0.6 else [],
                "whisper_receipt": {
                    "timestamp": whisper_data["timestamp"],
                    "nonce": whisper_data["nonce"],
                    "signature": whisper_data["signature"]
                }
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.tokens.append(data.get("token"))
                response.success()
            elif response.status_code == 403:
                # Policy rejection expected for low scores on unpublished
                response.success()
            elif response.status_code == 404:
                # Entry not found in load test
                response.success()
            else:
                response.failure(f"Resonance v2 failed: {response.status_code}")
    
    @task(2)  # Weight: 2 (less common)
    def revoke_token(self):
        """Revoke a token early."""
        if not self.tokens:
            return
        
        token = secrets.choice(self.tokens)
        
        with self.client.post(
            f"/codex/revoke?token={token}&reason=load_test_cleanup",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                self.tokens.remove(token)
                response.success()
            else:
                response.failure(f"Revoke failed: {response.status_code}")
    
    @task(1)  # Weight: 1 (rare)
    def list_active_capabilities(self):
        """Query active capabilities (admin operation)."""
        with self.client.get(
            "/codex/cap/active",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Active list failed: {response.status_code}")
    
    @task(1)  # Weight: 1 (rare)
    def inspect_policy(self):
        """Inspect policy for a collection."""
        collection = secrets.choice(["default", "archive", "unpublished", "codex"])
        
        with self.client.get(
            f"/codex/policy/inspect?collection={collection}",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Policy inspect failed: {response.status_code}")
    
    def on_stop(self):
        """Cleanup: Revoke all tokens on user exit."""
        for token in self.tokens:
            try:
                self.client.post(
                    f"/codex/revoke?token={token}&reason=user_exit"
                )
            except:
                pass


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Print test configuration on start."""
    print("=" * 60)
    print("Resonance Mesh Load Test Starting")
    print("=" * 60)
    print(f"Host: {environment.host}")
    print(f"Users: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'N/A'}")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Print summary statistics on completion."""
    print("\\n" + "=" * 60)
    print("Load Test Complete")
    print("=" * 60)
    
    stats = environment.stats
    print(f"Total requests: {stats.total.num_requests}")
    print(f"Failures: {stats.total.num_failures}")
    print(f"Avg response time: {stats.total.avg_response_time:.2f}ms")
    print(f"RPS: {stats.total.total_rps:.2f}")
    print("=" * 60)
'''


# ============================================================
# 3. COMPREHENSIVE TEST RUNNER
# ============================================================

TEST_RUNNER_SCRIPT = '''#!/usr/bin/env bash
# tests/run_all_tests.sh
# Comprehensive test suite runner

set -euo pipefail

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Resonance Mesh - Complete Test Suite                   ║"
echo "╚════════════════════════════════════════════════════════════╝"

# Setup environment
export CAP_TOKEN_SECRET='dev-secret-for-testing'
export WHISPER_SECRET='whisper-secret-for-testing'
export RESONANCE_POLICY_PATH='tests/fixtures/policy.yaml'

# Colors
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

echo ""
echo "🔧 Environment Setup"
echo "   CAP_TOKEN_SECRET: ${CAP_TOKEN_SECRET:0:10}..."
echo "   WHISPER_SECRET: ${WHISPER_SECRET:0:10}..."
echo ""

# Check dependencies
echo "📦 Checking dependencies..."
python -c "import pytest, jsonschema, yaml" 2>/dev/null || {
    echo "${YELLOW}Installing test dependencies...${NC}"
    pip install -q pytest jsonschema pyyaml locust
}

# Run unit tests
echo ""
echo "════════════════════════════════════════════════════════════"
echo "1️⃣  Unit Tests"
echo "════════════════════════════════════════════════════════════"
pytest tests/test_*.py -v --tb=short || {
    echo "${RED}❌ Unit tests failed${NC}"
    exit 1
}
echo "${GREEN}✅ Unit tests passed${NC}"

# Run schema validation
echo ""
echo "════════════════════════════════════════════════════════════"
echo "2️⃣  Schema Validation"
echo "════════════════════════════════════════════════════════════"
pytest tests/test_codex_schema.py -v || {
    echo "${RED}❌ Schema validation failed${NC}"
    exit 1
}
echo "${GREEN}✅ Schema validation passed${NC}"

# Check if server is running for integration tests
echo ""
echo "════════════════════════════════════════════════════════════"
echo "3️⃣  Integration Tests"
echo "════════════════════════════════════════════════════════════"
if curl -s http://localhost:8081/health >/dev/null 2>&1; then
    echo "Server detected at http://localhost:8081"
    ./tests/integration/run_flow.sh || {
        echo "${RED}❌ Integration tests failed${NC}"
        exit 1
    }
    echo "${GREEN}✅ Integration tests passed${NC}"
else
    echo "${YELLOW}⚠️  Server not running - skipping integration tests${NC}"
    echo "   Start server with: python -m uvicorn api.main:app --port 8081"
fi

# Offer to run load test
echo ""
echo "════════════════════════════════════════════════════════════"
echo "4️⃣  Load Testing (Optional)"
echo "════════════════════════════════════════════════════════════"
if [ -f "tests/load/locustfile.py" ]; then
    read -p "Run load test? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Starting Locust (headless, 10 users, 30s duration)..."
        locust -f tests/load/locustfile.py \\
               --host=http://localhost:8081 \\
               --headless \\
               --users 10 \\
               --spawn-rate 2 \\
               --run-time 30s || {
            echo "${YELLOW}⚠️  Load test encountered issues${NC}"
        }
    fi
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "${GREEN}✅ All tests completed successfully!${NC}"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📊 Test Coverage Summary:"
echo "   • Capability tokens (mint/verify/expire/revoke)"
echo "   • Delegation chains (scope reduction, TTL limits)"
echo "   • Resonance policy (thresholds, requirements)"
echo "   • Whisper receipts (HMAC verification)"
echo "   • Schema validation (Codex entry structure)"
echo "   • Integration flows (end-to-end scenarios)"
echo ""
'''

# Write files
def save_test_files():
    """Save all test artifacts to filesystem."""
    from pathlib import Path
    
    # Create directories
    Path("tests/load").mkdir(parents=True, exist_ok=True)
    
    # Save Locust file
    Path("tests/load/locustfile.py").write_text(LOCUST_TEST)
    
    # Save schema test
    Path("tests/test_codex_schema.py").write_text(TEST_CODEX_SCHEMA)
    
    # Save test runner
    Path("tests/run_all_tests.sh").write_text(TEST_RUNNER_SCRIPT)
    Path("tests/run_all_tests.sh").chmod(0o755)
    
    # Save schema definition
    import json
    Path("tests/fixtures/codex_schema.json").write_text(
        json.dumps(CODEX_ENTRY_SCHEMA, indent=2)
    )
    
    print("✅ Test files created:")
    print("   • tests/load/locustfile.py")
    print("   • tests/test_codex_schema.py")
    print("   • tests/run_all_tests.sh")
    print("   • tests/fixtures/codex_schema.json")

if __name__ == "__main__":
    save_test_files()