"""
CommuneOS Load Test — 100 concurrent requests
Targets: /agents/personalize (pipeline, cache warm) and /community/metrics
"""
import asyncio
import time
import httpx

BASE = "http://localhost:8000/api/v1"

async def hit(client, url, method="GET", json=None):
    start = time.perf_counter()
    try:
        if method == "POST":
            r = await client.post(url, json=json)
        else:
            r = await client.get(url)
        ms = (time.perf_counter() - start) * 1000
        return r.status_code, ms
    except Exception as e:
        ms = (time.perf_counter() - start) * 1000
        return 0, ms

async def run_batch(label, coro_factory, n=100):
    async with httpx.AsyncClient(timeout=30) as client:
        tasks = [coro_factory(client) for _ in range(n)]
        t0 = time.perf_counter()
        results = await asyncio.gather(*tasks)
        total = (time.perf_counter() - t0) * 1000

    codes = [r[0] for r in results]
    latencies = sorted([r[1] for r in results])
    ok = sum(1 for c in codes if 200 <= c < 300)
    errors = n - ok
    p50 = latencies[int(n * 0.5)]
    p95 = latencies[int(n * 0.95)]
    p99 = latencies[int(n * 0.99)]

    print(f"\n{'='*50}")
    print(f"  {label}")
    print(f"  n={n}  ok={ok}  errors={errors}  total={total:.0f}ms")
    print(f"  p50={p50:.0f}ms  p95={p95:.0f}ms  p99={p99:.0f}ms")
    print(f"  error_rate={errors/n*100:.1f}%")
    status = "✅ PASS" if errors/n < 0.05 and p95 < 5000 else "❌ FAIL"
    print(f"  {status} (target: p95 < 5000ms, error_rate < 5%)")
    return errors/n < 0.05 and p95 < 5000

async def main():
    # Warm up the personalize cache with one request first
    print("Warming up personalize cache...")
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{BASE}/agents/personalize/rahul")
        print(f"  Warm-up: {r.status_code}")

    # Test 1: /community/metrics (no LLM, pure mock/cache)
    await run_batch(
        "GET /community/metrics (100 concurrent)",
        lambda c: hit(c, f"{BASE}/community/metrics"),
        n=100,
    )

    # Test 2: /agents/personalize/rahul (cached — should be fast)
    await run_batch(
        "POST /agents/personalize/rahul (100 concurrent, cache warm)",
        lambda c: hit(c, f"{BASE}/agents/personalize/rahul", "POST"),
        n=100,
    )

    # Test 3: /users/rahul (pure mock lookup)
    await run_batch(
        "GET /users/rahul (100 concurrent)",
        lambda c: hit(c, f"{BASE}/users/rahul"),
        n=100,
    )

asyncio.run(main())
