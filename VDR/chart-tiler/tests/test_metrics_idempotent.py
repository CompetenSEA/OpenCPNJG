import importlib.util
import sys
from pathlib import Path

import prometheus_client

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def load_module(tag: str):
    spec = importlib.util.spec_from_file_location(f"tileserver_{tag}", ROOT / "tileserver.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore
    return module


def test_metrics_idempotent(monkeypatch):
    reg = prometheus_client.CollectorRegistry()
    prometheus_client.registry.REGISTRY = reg
    prometheus_client.metrics.REGISTRY = reg

    m1 = load_module("a")
    count1 = len(list(m1._prom_registry.collect()))

    m2 = load_module("b")
    count2 = len(list(m2._prom_registry.collect()))

    assert count1 == count2
