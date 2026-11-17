#!/usr/bin/env python3
"""Fetch the image's verified Benchmarks release into the user's cache."""

import argparse
import json
from pathlib import Path
import tempfile

from source_lock import PROVENANCE, commit_id, fetch_benchmark, load_lock, verify_cache


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, default=Path('/cache'))
    parser.add_argument('--verify-cache', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    lock = load_lock()
    inventory = json.loads((PROVENANCE / 'image.json').read_text())
    commit = commit_id(inventory['benchmark_commit'])
    cache = args.cache.resolve()
    destination = cache / 'benchmarks'
    try:
        if args.verify_cache or destination.exists() or destination.is_symlink():
            verify_cache(destination, commit, lock['files'])
            if not args.verify_cache:
                print(f'Benchmarks {lock["version"]} ({commit}) already prepared in {destination}')
            return

        cache.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.benchmarks-download-', dir=cache) as tmp:
            extracted = Path(tmp) / 'benchmarks'
            fetch_benchmark(extracted, commit, lock)
            extracted.rename(destination)
    except ValueError as error:
        parser.error(f'{error} Use a fresh cache if the mounted cache belongs to another release.')
    print(f'Prepared Benchmarks {lock["version"]} ({commit}) in {destination}')


if __name__ == '__main__':
    main()
