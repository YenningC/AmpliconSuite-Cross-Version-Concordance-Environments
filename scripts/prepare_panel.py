#!/usr/bin/env python3
"""Fetch exact upstream AA/AC source into a reusable, user-owned cache."""

import argparse
from pathlib import Path

from ascompare.common import atomic_json
from ascompare.versions import load_lock, prepare_component


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path('/sources'))
    parser.add_argument('--versions', nargs='+', help='Defaults to all ten locked Suite versions')
    args = parser.parse_args()
    lock = load_lock()
    panel = {entry['id']: entry for entry in lock['versions'] if entry.get('suite')}
    selected = list(dict.fromkeys([lock['reference_version'], *(args.versions or panel)]))
    unknown = set(selected) - panel.keys()
    if unknown:
        parser.error('Unknown release: ' + ', '.join(sorted(unknown)))
    out = args.out.resolve()
    rows = []
    for version in selected:
        row = {'id': version}
        for name in ('aa', 'ac'):
            component = panel[version][name]
            source = prepare_component(component, out)
            entrypoint = source / component['entrypoint']
            if not entrypoint.is_file():
                raise FileNotFoundError(entrypoint)
            row[name + '_source'] = str(source)
            row[name + '_script'] = str(entrypoint)
        rows.append(row)
    atomic_json(out / 'prepared_panel.json', {'reference_version': lock['reference_version'], 'sources': rows})
    print(f'Prepared {len(rows)} locked Suite recipes in {out}.')


if __name__ == '__main__':
    main()
