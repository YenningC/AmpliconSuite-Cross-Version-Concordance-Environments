#!/usr/bin/env python3
"""Build the Linux runtime inside the container. Downloads only public software."""

import hashlib
import json
from pathlib import Path
import platform
import os
import shutil
import subprocess
import sys
import tempfile
import venv


from source_lock import PROVENANCE, SOURCE_LOCK, fetch_source, load_lock, resolve_commit


VENV_ROOT = Path('/opt/concordance-venvs')
REQUIREMENTS = Path('/opt/environment-requirements')


def run(*command):
    subprocess.run([str(part) for part in command], check=True)


def pip(python, *arguments):
    run(python, '-m', 'pip', 'install', '--no-cache-dir', *arguments)


def make_venv(name, shared=True):
    root = VENV_ROOT / name
    venv.EnvBuilder(with_pip=True, system_site_packages=shared).create(root)
    return root / 'bin/python'


def install_bfb(concordance_python, ac_python, suite, directory, code):
    prepare = '''
import sys
from ascompare.versions import load_lock, prepare_component
from pathlib import Path
entry = next(row for row in load_lock()['versions'] if row['id'] == sys.argv[1])
print(prepare_component(entry['bfb'], Path(sys.argv[2])))
'''
    source = subprocess.check_output(
        [concordance_python, '-c', prepare, suite, directory], text=True,
        env={**os.environ, 'PYTHONPATH': str(code)},
    ).strip()
    destination = directory / f'{suite}-bfb-build'
    # Keep the verified source intact while setuptools creates its build files.
    shutil.copytree(source, destination)
    pip(ac_python, '--no-deps', '--no-build-isolation', destination)


def save_inventory(pythons, commit, lock):
    PROVENANCE.mkdir()
    for name, python in pythons.items():
        packages = subprocess.check_output([python, '-m', 'pip', 'freeze', '--all'], text=True)
        (PROVENANCE / f'{name}.freeze.txt').write_text(packages)
    packages = subprocess.check_output(['dpkg-query', '-W', '-f=${Package}\t${Version}\t${source:Package}\t${source:Version}\n'], text=True)
    (PROVENANCE / 'debian-packages.tsv').write_text(packages)
    (PROVENANCE / 'image.json').write_text(json.dumps({
        'concordance_version': lock['version'],
        'concordance_commit': commit,
        'concordance_file_lock_sha256': hashlib.sha256(SOURCE_LOCK.read_bytes()).hexdigest(),
        'concordance_file_lock': str(SOURCE_LOCK),
        'python': platform.python_version(),
        'runtime_scope': 'Linux x86_64; CBC only; CNVkit CBS only',
        'omitted_backends': ['Mosek (optional user-mounted client)', 'Gurobi', 'pomegranate HMM stack'],
        'source_lock': '/cache/concordance/versions.lock.json',
    }, indent=2) + '\n')


def main():
    if (sys.platform, platform.machine(), sys.version_info[:2]) != ('linux', 'x86_64', (3, 12)):
        raise SystemExit('Build requires Linux x86_64 and Python 3.12')
    lock = load_lock()
    try:
        commit = resolve_commit(os.environ.get('CONCORDANCE_COMMIT'))
        with tempfile.TemporaryDirectory(prefix='build-concordance-') as tmp:
            directory = Path(tmp)
            code = directory / 'concordance'
            fetch_source(code, commit, lock)
            build_environments(directory, code, commit, lock)
    except ValueError as error:
        raise SystemExit(str(error)) from error


def build_environments(directory, code, commit, lock):
    pip(sys.executable, 'setuptools==80.9.0', 'wheel==0.45.1', '-r', REQUIREMENTS / 'common.txt')
    # CNVkit is an optional BFB CLI dependency too. The modern tier shares its
    # libraries. CBS does not need the optional pomegranate/PyTorch HMM backend.
    pip(sys.executable, '--no-deps', '--no-build-isolation', 'CNVkit==0.9.13')
    concordance = make_venv('concordance')
    aa = make_venv('aa')
    ac101 = make_venv('ac-bfb101')
    ac102 = make_venv('ac-bfb102')
    cnv13 = make_venv('cnvkit-0.9.13')
    pip(cnv13, '--ignore-installed', '--no-deps', '--no-build-isolation', 'CNVkit==0.9.13')
    cnv14 = make_venv('cnvkit-0.9.14', shared=False)
    pip(cnv14, '-r', REQUIREMENTS / 'cnvkit-0.9.14.txt')
    run(cnv14, '-m', 'pip', 'check')
    run(cnv14, cnv14.parent / 'cnvkit.py', 'version')
    cnv10 = make_venv('cnvkit-0.9.10', shared=False)
    pip(cnv10, 'setuptools==80.9.0', 'wheel==0.45.1', '-r', REQUIREMENTS / 'cnvkit-0.9.10.txt')
    # The old CBS CLI imports pomegranate at startup but never runs the HMM.
    pip(cnv10, '--no-deps', '--no-build-isolation', 'pomegranate==1.1.2', 'CNVkit==0.9.10')
    for python, suite in ((ac101, 'suite-1.6.0'), (ac102, 'suite-1.6.2')):
        pip(python, 'PuLP==3.3.0')
        install_bfb(concordance, python, suite, directory, code)
    save_inventory({
        'concordance': concordance, 'aa': aa, 'ac-bfb101': ac101, 'ac-bfb102': ac102,
        'cnvkit-0.9.10': cnv10, 'cnvkit-0.9.13': cnv13, 'cnvkit-0.9.14': cnv14,
    }, commit, lock)


if __name__ == '__main__':
    main()
