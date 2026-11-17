# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm@sha256:0f086103b026048cc50cb5da25ec435c023c5241a83fc44daea593377abc61c4

ARG TARGETARCH
ARG BENCHMARKS_COMMIT
COPY requirements/ /opt/environment-requirements/
RUN test "$TARGETARCH" = amd64 \
    && apt-get update \
    && apt-get install -y --no-install-recommends samtools bedtools coinor-cbc libgomp1 r-base-core r-bioc-dnacopy \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/opt/benchmarks-venvs/benchmark/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    MPLBACKEND=Agg \
    OPENBLAS_NUM_THREADS=1 \
    OMP_NUM_THREADS=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
COPY benchmarks-source.lock.json /opt/benchmarks-source.lock.json
COPY scripts/ /opt/environment-scripts/
RUN BENCHMARKS_COMMIT="$BENCHMARKS_COMMIT" /usr/local/bin/python /opt/environment-scripts/build_runtime.py
RUN chmod +x /opt/environment-scripts/entrypoint.sh /opt/environment-scripts/smoke.sh
WORKDIR /work
ENTRYPOINT ["/opt/environment-scripts/entrypoint.sh"]
CMD ["help"]
