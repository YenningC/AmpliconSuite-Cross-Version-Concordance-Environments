#!/usr/bin/env python3
"""Fetch one checked-out Benchmarks release into the user's own cache."""
import argparse
from pathlib import Path
import tempfile

from build_runtime import BENCHMARK_COMMIT, fetch_benchmark


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, default=Path('/cache'))
    args = parser.parse_args()
    cache = args.cache.resolve()
    cache.mkdir(parents=True, exist_ok=True)
    destination = cache / 'benchmarks'
    if destination.exists():
        marker = destination / '.benchmarks-commit'
        if marker.is_file() and marker.read_text().strip() == BENCHMARK_COMMIT:
            print(f'Benchmarks {BENCHMARK_COMMIT} already prepared in {destination}')
            return
        parser.error(f'{destination} exists and is not the pinned checkout. Use another cache.')
    with tempfile.TemporaryDirectory(prefix='.benchmarks-download-', dir=cache) as tmp:
        temporary = Path(tmp)
        extracted = temporary / 'benchmarks'
        fetch_benchmark(temporary, extracted)
        extracted.rename(destination)
    print(f'Prepared Benchmarks {BENCHMARK_COMMIT} in {destination}')


if __name__ == '__main__':
    main()
