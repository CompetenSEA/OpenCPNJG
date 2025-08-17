
"""Simple stress test harness for the tile server.

Sends requests at a steady rate and monitors the specified process RSS
memory usage.  The script exits with a non-zero status if any request fails
or the memory consumption grows beyond the allowed threshold.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import time

import httpx
import psutil


async def _run(url: str, duration: int, rps: int, proc: psutil.Process, mem_limit: int) -> int:
    """Return the maximum RSS observed while issuing tile requests."""

    start_rss = proc.memory_info().rss
    max_rss = start_rss
    async with httpx.AsyncClient(timeout=30.0) as client:
        end = time.time() + duration
        while time.time() < end:
            tick = time.perf_counter()
            tasks = [client.get(url) for _ in range(rps)]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            for resp in responses:
                if isinstance(resp, Exception) or getattr(resp, "status_code", 0) != 200:
                    raise RuntimeError("tile request failed")
            rss = proc.memory_info().rss
            max_rss = max(max_rss, rss)
            if rss - start_rss > mem_limit:
                raise RuntimeError("memory budget exceeded")
            # Sleep to maintain constant rate
            elapsed = time.perf_counter() - tick
            await asyncio.sleep(max(0, 1 - elapsed))
    return max_rss


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Tile URL to request repeatedly")
    parser.add_argument("--duration", type=int, default=600, help="Duration in seconds")
    parser.add_argument("--rps", type=int, default=10, help="Requests per second")
    parser.add_argument("--pid", type=int, default=None, help="PID of tile server process")
    parser.add_argument(
        "--mem-limit", type=int, default=50 * 1024 * 1024,
        help="Allowed RSS growth in bytes",
    )
    args = parser.parse_args()

    proc = psutil.Process(args.pid or os.getpid())
    max_rss = asyncio.run(_run(args.url, args.duration, args.rps, proc, args.mem_limit))
    print(f"max_rss={max_rss}")


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
