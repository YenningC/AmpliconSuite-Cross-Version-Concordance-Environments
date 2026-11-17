#!/bin/sh
# Run only after bootstrap and prepare-panel in an empty synthetic workspace.
set -eu
root=${1:-/tmp/environment-smoke}
mkdir -p "$root"
python=/opt/concordance-venvs/concordance/bin/python

Rscript -e 'cat(as.character(packageVersion("DNAcopy")), "\n")'
cd "$CONCORDANCE_CHECKOUT"
"$python" -m ascompare.concordance demo --out "$root/results-only"
test -s "$root/results-only/report.md"
test -s "$root/results-only/cohort_compatibility_metrics.tsv"
test -s "$root/results-only/sample_reports.md"
for test_file in test_concordance_batch.py test_concordance_cohort_plot.py test_concordance_progress.py; do
  "$python" -m unittest discover -s tests -p "$test_file" -v
done
/opt/concordance-venvs/aa/bin/python scripts/probe_clarabel.py \
  --sources /sources --out "$root/clarabel-probes.json"
"$python" /opt/environment-scripts/smoke_components.py /sources/prepared_panel.json
for version in 0.9.10 0.9.13; do
  CNVKIT_SMOKE_PYTHON="/opt/concordance-venvs/cnvkit-$version/bin/python" \
    CNVKIT_SMOKE_VERSION="$version" \
    CNVKIT_SMOKE_EXTRA_PATH=/usr/bin \
    CNVKIT_SMOKE_ARTIFACTS="$root/cnvkit-$version-matched" \
    "$python" -m unittest discover -s tests -p test_concordance_cnv.py -k test_actual_cnvkit -v
done
CNVKIT_SMOKE_PYTHON=/opt/concordance-venvs/cnvkit-0.9.13/bin/python \
  CNVKIT_SMOKE_VERSION=0.9.13 CNVKIT_SMOKE_REFERENCE_MODE=flat \
  CNVKIT_SMOKE_EXTRA_PATH=/usr/bin CNVKIT_SMOKE_ARTIFACTS="$root/cnvkit-0.9.13-flat" \
  "$python" -m unittest discover -s tests -p test_concordance_cnv.py -k test_actual_cnvkit -v
