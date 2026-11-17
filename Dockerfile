# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm@sha256:0f086103b026048cc50cb5da25ec435c023c5241a83fc44daea593377abc61c4

ARG TARGETARCH
ARG CONCORDANCE_COMMIT=ae4d13edec26500558686c2c9fa31da0e9673c40
COPY requirements/ /opt/environment-requirements/
RUN test "$TARGETARCH" = amd64 \
    && apt-get update \
    && apt-get install -y --no-install-recommends samtools bedtools coinor-cbc libgomp1 r-base-core r-bioc-dnacopy \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/opt/concordance-venvs/concordance/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    MPLBACKEND=Agg \
    OPENBLAS_NUM_THREADS=1 \
    OMP_NUM_THREADS=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
COPY concordance-source.lock.json /opt/concordance-source.lock.json
COPY scripts/ /opt/environment-scripts/
RUN CONCORDANCE_COMMIT="$CONCORDANCE_COMMIT" /usr/local/bin/python /opt/environment-scripts/build_runtime.py
COPY LICENSE THIRD_PARTY.md /opt/environment-provenance/
RUN chmod +x /opt/environment-scripts/entrypoint.sh /opt/environment-scripts/smoke.sh
WORKDIR /work
ENTRYPOINT ["/opt/environment-scripts/entrypoint.sh"]
CMD ["help"]
