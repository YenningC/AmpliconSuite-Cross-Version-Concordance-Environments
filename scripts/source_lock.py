"""Verify the Benchmarks file inventory before extracting GitHub archives."""

import hashlib
import io
import json
from pathlib import Path
import re
import tarfile
import urllib.error
import urllib.request


REPOSITORY = 'YenningC/AmpliconSuite-Benchmarks'
REPO_NAME = REPOSITORY.split('/')[1]
SOURCE_LOCK = Path(__file__).resolve().parents[1] / 'benchmarks-source.lock.json'
PROVENANCE = Path('/opt/environment-provenance')
MAX_SOURCE_BYTES = 16 * 1024 * 1024
MARKER = '.benchmarks-commit'


def commit_id(value):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{40}', value):
        raise ValueError('Expected a full 40-character Benchmarks Git commit')
    return value


def load_lock():
    lock = json.loads(SOURCE_LOCK.read_text())
    if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', lock['version']) or not lock['files']:
        raise ValueError('Invalid Benchmarks source lock')
    for path, digest in lock['files'].items():
        if ('\\' in path or any(part in ('', '.', '..') for part in path.split('/'))
                or path == MARKER or not re.fullmatch(r'[0-9a-f]{64}', digest)):
            raise ValueError(f'Invalid Benchmarks source lock entry: {path}')
    return lock


def resolve_commit(requested):
    if requested:
        return commit_id(requested)
    url = f'https://api.github.com/repos/{REPOSITORY}/git/ref/heads/main'
    try:
        with urllib.request.urlopen(url, timeout=45) as response:
            return commit_id(json.load(response)['object']['sha'])
    except urllib.error.URLError as error:
        raise ValueError('Unable to resolve Benchmarks main. Retry or provide BENCHMARKS_COMMIT.') from error


def verify_archive(archive, commit, expected):
    root = f'{REPO_NAME}-{commit_id(commit)}'
    directories = {root}
    for path in expected:
        directories.update(f'{root}/{parent}' for parent in Path(path).parents if parent != Path('.'))

    verified = {}
    seen = set()
    total_bytes = 0
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as source:
        for member in source:
            path = member.name
            if path in seen:
                raise ValueError(f'Duplicate Benchmarks archive member: {path}')
            seen.add(path)
            if member.isdir() and path in directories:
                continue
            relative = path.removeprefix(f'{root}/')
            if (path == relative or relative not in expected
                    or member.type not in (tarfile.REGTYPE, tarfile.AREGTYPE)):
                raise ValueError(f'Unexpected Benchmarks archive member: {path}')
            total_bytes += member.size
            if total_bytes > MAX_SOURCE_BYTES:
                raise ValueError('Benchmarks archive exceeds the extraction size limit')
            with source.extractfile(member) as handle:
                contents = handle.read()
            if hashlib.sha256(contents).hexdigest() != expected[relative]:
                raise ValueError(f'Benchmarks source SHA-256 mismatch: {relative}')
            verified[relative] = contents, member.mode & 0o111
    if verified.keys() != expected.keys():
        missing = ', '.join(sorted(expected.keys() - verified.keys()))
        raise ValueError(f'Missing Benchmarks source files: {missing}')
    return verified


def fetch_benchmark(destination, commit, lock):
    url = f'https://codeload.github.com/{REPOSITORY}/tar.gz/{commit_id(commit)}'
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            archive = response.read(MAX_SOURCE_BYTES + 1)
        if len(archive) > MAX_SOURCE_BYTES:
            raise ValueError('Benchmarks archive exceeds the download size limit')
        verified = verify_archive(archive, commit, lock['files'])
    except (ValueError, tarfile.TarError, EOFError, urllib.error.URLError) as error:
        raise ValueError(
            f'Could not verify Benchmarks {lock["version"]} at {commit}. '
            f'Publish the matching source to the main Benchmarks repository first. Cause: {error}'
        ) from error
    destination.mkdir()
    for relative, (contents, executable) in verified.items():
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(contents)
        if executable:
            path.chmod(path.stat().st_mode | executable)
    (destination / MARKER).write_text(commit + '\n')


def verify_cache(destination, commit, expected):
    if not destination.is_dir() or destination.is_symlink():
        raise ValueError('Mount the prepared cache at /cache and run bootstrap first.')
    present = set()
    for path in destination.rglob('*'):
        relative = path.relative_to(destination).as_posix()
        if path.is_symlink() or not (path.is_dir() or path.is_file()):
            raise ValueError(f'Invalid entry in Benchmarks source cache: {relative}')
        if path.is_dir():
            continue
        if relative == MARKER:
            if path.read_text().strip() != commit:
                raise ValueError('Benchmarks cache belongs to another commit.')
        else:
            if (relative not in expected or path.stat().st_size > MAX_SOURCE_BYTES
                    or hashlib.sha256(path.read_bytes()).hexdigest() != expected[relative]):
                raise ValueError(f'Invalid file in Benchmarks source cache: {relative}')
        present.add(relative)
    if present != {MARKER, *expected}:
        raise ValueError('Benchmarks cache is missing pinned source files.')
