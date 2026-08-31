from pathlib import Path

from rescuebench.catalog import BenchmarkCatalog


def test_catalog_rejects_unknown_case(tmp_path: Path) -> None:
    (tmp_path / "benchmarks").mkdir()
    catalog = BenchmarkCatalog(tmp_path)
    try:
        catalog.load("missing")
    except KeyError:
        pass
    else:
        raise AssertionError("missing case should raise KeyError")
