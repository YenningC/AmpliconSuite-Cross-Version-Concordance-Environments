#!/usr/bin/env python3
"""Exercise real source identity, version/help and unlicensed CBC backends."""
import json
import os
from pathlib import Path
import sys

from ascompare.concordance_import import _probe_json, _verify_ac_runtime
from ascompare.versions import load_lock, verify_runtime
from configure_runtime import CNVKIT_VERSIONS, configure_manifest


def main():
    lock = load_lock()
    prepared = json.loads(Path(sys.argv[1]).read_text())
    panel = {entry['id']: entry for entry in lock['versions'] if entry.get('suite')}
    venvs = Path('/opt/concordance-venvs')
    base = {'mode': 'results_only', 'samples': [{'source_version': lock['reference_version']}]}
    env = dict(os.environ)
    for name in ('MOSEKLM_LICENSE_FILE', 'GRB_LICENSE_FILE'):
        env.pop(name, None)
    manifest, _ = configure_manifest(base, prepared, lock, venvs)
    for runtime in manifest['runtimes']:
        entry = panel[runtime['id']]
        result = _verify_ac_runtime(runtime, entry, env)
        if entry.get('bfb'):
            backend = _probe_json(result['bfb_probe']['stdout'])['selected_backend']
            if backend.lower() != 'cbc':
                raise RuntimeError(f'Unexpected default BFB backend for {runtime["id"]}: {backend}')
        print(f'{runtime["id"]}: AC source/launch verified', flush=True)
    base['mode'] = 'with_bam'
    configured, _ = configure_manifest(base, prepared, lock, venvs)
    cnv_versions = {row['version'] for row in configured['cnvkit_runtimes']}
    if cnv_versions != set(CNVKIT_VERSIONS):
        raise RuntimeError('The local comparator is missing a bundled CNVkit runtime')
    if any(row['cnvkit_version'] == '0.9.14' for row in configured['runtimes']):
        raise RuntimeError('The optional comparator replaced a native Suite CNVkit recipe')
    custom = {'version': '0.9.14', 'python': '/custom/python', 'script': '/custom/cnvkit.py',
              'env': {'PROFILE': 'custom'}}
    custom_base = {**base, 'cnvkit_runtimes': [custom]}
    retained, warnings = configure_manifest(custom_base, prepared, lock, venvs)
    if retained['cnvkit_runtimes'][0] != custom or custom_base['cnvkit_runtimes'] != [custom]:
        raise RuntimeError('CNVkit registry configuration changed a user-provided runtime')
    if not any('existing CNVkit 0.9.14' in message for message in warnings):
        raise RuntimeError('Custom comparator runtime was kept without reporting it')
    print('CNVkit registry: three bundled versions, native Suite mappings and custom entries verified', flush=True)
    reference, _ = configure_manifest(base, prepared, lock, venvs, [lock['reference_version']])
    runtime = reference['runtimes'][0]
    result = verify_runtime(runtime, panel[lock['reference_version']], env)
    if not result['ready']:
        raise RuntimeError('; '.join(result['diagnostics']))
    print(f'{runtime["id"]}: AA source/launch verified without commercial solvers', flush=True)


if __name__ == '__main__':
    main()
