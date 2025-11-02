import time
import statistics
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
from synara_core.modules.capability_token import mint_capability, verify_capability
from synara_core.modules.resonance_policy import mint_resonance_capability_v2, ResonancePolicy

class PerformanceBenchmark:
    """Benchmark capability operations under load."""
    
    def __init__(self):
        self.results = {}
        self.policy = ResonancePolicy("tests/fixtures/policy.yaml")
    
    def benchmark_mint(self, iterations=1000):
        """Benchmark token minting throughput."""
        print(f"\n🔨 Minting {iterations} tokens...")
        
        start = time.time()
        tokens = []
        
        for i in range(iterations):
            token = mint_capability(
                sub=f"user_{i}",
                scope="read_summary",
                digest=f"0x{i:064x}",
                ttl_s=600,
                extra={"kind": "codex"}
            )
            tokens.append(token)
        
        duration = time.time() - start
        ops_per_sec = iterations / duration
        
        self.results['mint'] = {
            'iterations': iterations,
            'duration': duration,
            'ops_per_sec': ops_per_sec,
            'avg_latency_ms': (duration / iterations) * 1000
        }
        
        print(f"   ✓ {ops_per_sec:.0f} ops/sec")
        print(f"   ✓ {self.results['mint']['avg_latency_ms']:.2f}ms avg latency")
        
        return tokens
    
    def benchmark_verify(self, tokens, iterations=1000):
        """Benchmark token verification throughput."""
        print(f"\n🔍 Verifying {iterations} tokens...")
        
        start = time.time()
        
        for i in range(iterations):
            token = tokens[i % len(tokens)]
            verify_capability(token)
        
        duration = time.time() - start
        ops_per_sec = iterations / duration
        
        self.results['verify'] = {
            'iterations': iterations,
            'duration': duration,
            'ops_per_sec': ops_per_sec,
            'avg_latency_ms': (duration / iterations) * 1000
        }
        
        print(f"   ✓ {ops_per_sec:.0f} ops/sec")
        print(f"   ✓ {self.results['verify']['avg_latency_ms']:.2f}ms avg latency")
    
    def benchmark_resonance(self, iterations=100):
        """Benchmark resonance-gated minting."""
        print(f"\n🎵 Resonance-gated minting {iterations} tokens...")
        
        scores = [0.3, 0.55, 0.7, 0.85, 0.95] * (iterations // 5)
        latencies = []
        
        for score in scores[:iterations]:
            start = time.time()
            
            mint_resonance_capability_v2(
                requester="bench_user",
                digest="0xBENCHMARK",
                collection="default",
                score=score,
                policy=self.policy
            )
            
            latencies.append((time.time() - start) * 1000)
        
        self.results['resonance'] = {
            'iterations': iterations,
            'avg_latency_ms': statistics.mean(latencies),
            'median_latency_ms': statistics.median(latencies),
            'p95_latency_ms': statistics.quantiles(latencies, n=20)[18],
            'p99_latency_ms': statistics.quantiles(latencies, n=100)[98]
        }
        
        print(f"   ✓ {self.results['resonance']['avg_latency_ms']:.2f}ms avg latency")
        print(f"   ✓ {self.results['resonance']['p95_latency_ms']:.2f}ms P95")
        print(f"   ✓ {self.results['resonance']['p99_latency_ms']:.2f}ms P99")
    
    def benchmark_concurrent(self, workers=10, ops_per_worker=100):
        """Benchmark concurrent operations."""
        print(f"\n⚡ Concurrent test: {workers} workers × {ops_per_worker} ops...")
        
        def worker_task(worker_id):
            latencies = []
            for i in range(ops_per_worker):
                start = time.time()
                
                token = mint_capability(
                    sub=f"worker_{worker_id}_op_{i}",
                    scope="read_summary",
                    digest=f"0x{i:064x}",
                    ttl_s=600,
                    extra={"worker": worker_id}
                )
                verify_capability(token)
                
                latencies.append((time.time() - start) * 1000)
            return latencies
        
        start = time.time()
        all_latencies = []
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(worker_task, i) for i in range(workers)]
            for future in as_completed(futures):
                all_latencies.extend(future.result())
        
        duration = time.time() - start
        total_ops = workers * ops_per_worker
        
        self.results['concurrent'] = {
            'workers': workers,
            'total_ops': total_ops,
            'duration': duration,
            'ops_per_sec': total_ops / duration,
            'avg_latency_ms': statistics.mean(all_latencies),
            'p95_latency_ms': statistics.quantiles(all_latencies, n=20)[18]
        }
        
        print(f"   ✓ {self.results['concurrent']['ops_per_sec']:.0f} ops/sec")
        print(f"   ✓ {self.results['concurrent']['avg_latency_ms']:.2f}ms avg latency")
        print(f"   ✓ {self.results['concurrent']['p95_latency_ms']:.2f}ms P95")
    
    def print_summary(self):
        """Print benchmark summary."""
        print("\n" + "=" * 60)
        print("PERFORMANCE SUMMARY")
        print("=" * 60)
        
        for operation, metrics in self.results.items():
            print(f"\n{operation.upper()}:")
            for key, value in metrics.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: {value}")


if __name__ == "__main__":
    import os
    os.environ['CAP_TOKEN_SECRET'] = 'benchmark-secret'
    os.environ['WHISPER_SECRET'] = 'benchmark-whisper'
    
    bench = PerformanceBenchmark()
    
    print("=" * 60)
    print("RESONANCE MESH PERFORMANCE BENCHMARK")
    print("=" * 60)
    
    # Run benchmarks
    tokens = bench.benchmark_mint(iterations=1000)
    bench.benchmark_verify(tokens, iterations=1000)
    bench.benchmark_resonance(iterations=100)
    bench.benchmark_concurrent(workers=10, ops_per_worker=100)
    
    # Summary
    bench.print_summary()
# tests/monitor/continuous_validation.py
"""
Continuous Validation Monitor
Runs validation checks against live system
"""

import time
import requests
import json
from datetime import datetime
from pathlib import Path

class ContinuousValidator:
    """Monitor system health and correctness."""
    
    def __init__(self, base_url="http://localhost:8081"):
        self.base_url = base_url
        self.checks = []
        self.log_file = Path("tests/monitor/validation.log")
        self.log_file.parent.mkdir(exist_ok=True)
    
    def log(self, message, level="INFO"):
        """Log validation results."""
        timestamp = datetime.now().isoformat()
        line = f"[{timestamp}] [{level}] {message}\n"
        print(line.strip())
        
        with open(self.log_file, "a") as f:
            f.write(line)
    
    def check_health(self):
        """Verify system is responsive."""
        try:
            r = requests.get(f"{self.base_url}/health", timeout=5)
            if r.status_code == 200:
                self.log("✓ Health check passed")
                return True
            else:
                self.log(f"✗ Health check failed: {r.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"✗ Health check error: {e}", "ERROR")
            return False
    
    def check_capability_lifecycle(self):
        """Verify full capability lifecycle works."""
        try:
            # Mint
            r = requests.post(
                f"{self.base_url}/codex/share",
                json={"path": "test.json", "scope": "read_summary", "ttl_seconds": 10}
            )
            if r.status_code != 200:
                self.log(f"✗ Mint failed: {r.status_code}", "ERROR")
                return False
            
            token = r.json().get("token")
            
            # Verify
            r = requests.get(f"{self.base_url}/codex/verify_token?token={token}")
            if r.status_code != 200:
                self.log(f"✗ Verify failed: {r.status_code}", "ERROR")
                return False
            
            # Revoke
            r = requests.post(f"{self.base_url}/codex/revoke?token={token}&reason=test")
            if r.status_code != 200:
                self.log(f"✗ Revoke failed: {r.status_code}", "ERROR")
                return False
            
            # Verify revoked
            r = requests.get(f"{self.base_url}/codex/verify_token?token={token}")
            if r.status_code == 200:
                self.log("✗ Token still valid after revocation", "ERROR")
                return False
            
            self.log("✓ Capability lifecycle check passed")
            return True
            
        except Exception as e:
            self.log(f"✗ Lifecycle check error: {e}", "ERROR")
            return False
    
    def check_policy_enforcement(self):
        """Verify policy is enforced correctly."""
        try:
            # Should fail without whisper for unpublished
            r = requests.post(
                f"{self.base_url}/codex/resonance_share/v2",
                json={
                    "path": "test.json",
                    "requester": "test_user",
                    "collection": "unpublished",
                    "score": 0.9
                }
            )
            if r.status_code == 200:
                self.log("✗ Policy bypass detected", "ERROR")
                return False
            
            self.log("✓ Policy enforcement check passed")
            return True
            
        except Exception as e:
            self.log(f"✗ Policy check error: {e}", "ERROR")
            return False
    
    def run_continuous(self, interval_seconds=60):
        """Run validation checks continuously."""
        self.log("Starting continuous validation monitor")
        
        while True:
            try:
                results = {
                    'health': self.check_health(),
                    'lifecycle': self.check_capability_lifecycle(),
                    'policy': self.check_policy_enforcement()
                }
                
                if all(results.values()):
                    self.log("✅ All checks passed")
                else:
                    failed = [k for k, v in results.items() if not v]
                    self.log(f"❌ Failed checks: {', '.join(failed)}", "WARN")
                
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                self.log("Monitor stopped by user")
                break
            except Exception as e:
                self.log(f"Monitor error: {e}", "ERROR")
                time.sleep(interval_seconds)


if __name__ == "__main__":
    monitor = ContinuousValidator()
    monitor.run_continuous(interval_seconds
