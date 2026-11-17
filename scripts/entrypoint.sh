#!/bin/sh
set -eu

command_name=${1:-help}
if [ "$#" -gt 0 ]; then shift; fi
scripts=/opt/environment-scripts
python=/opt/benchmarks-venvs/benchmark/bin/python

case "$command_name" in
  help|-h|--help)
    echo 'AmpliconSuite Benchmarks Environments'
    echo 'Commands: bootstrap, prepare-panel, configure-runtime, asbench, environment-smoke, inventory'
    echo 'Read the environment repository README for mounts and solver licensing.'
    exit 0
    ;;
  bootstrap) exec "$python" "$scripts/bootstrap.py" "$@" ;;
  inventory) cat /opt/environment-provenance/image.json; exit 0 ;;
esac

export ASBENCH_CHECKOUT=/cache/benchmarks
"$python" "$scripts/bootstrap.py" --verify-cache
# The comparison interpreter loads the separately fetched Benchmarks checkout.
# A user-mounted solver SDK is configured per Suite runtime.
export PYTHONPATH="$ASBENCH_CHECKOUT"

case "$command_name" in
  asbench) exec "$python" -m ascompare.benchmark "$@" ;;
  prepare-panel) exec "$python" "$scripts/prepare_panel.py" "$@" ;;
  configure-runtime) exec "$python" "$scripts/configure_runtime.py" "$@" ;;
  environment-smoke) exec "$scripts/smoke.sh" "$@" ;;
  *) echo "Unknown command: $command_name" >&2; exit 2 ;;
esac
