# Validation status

The 0.3.0 recipe targets Linux amd64 and the pinned Python 3.12 Bookworm base image. The [Benchmarks source lock](benchmarks-source.lock.json) records the SHA-256 of each public 0.3.0 source file. The image records the Git commit that matched the lock at build time and reuses that commit when bootstrapping the mounted cache.

## Benchmarks 0.3.0

Local checks verified the complete 87-file source lock, invalid archive rejection, cache integrity and script syntax. GitHub Actions built the Linux amd64 image, prepared the locked sources and passed the synthetic component tests before publishing it to GHCR. The released image digest is `sha256:2273905bd8417cfd2d63af8f25e29c36383b70d2298954ebd834e7ca91959710`. [Environment test](https://github.com/YenningC/AmpliconSuite-Benchmarks-Environments/actions/runs/44041555708) · [Image publication](https://github.com/YenningC/AmpliconSuite-Benchmarks-Environments/actions/runs/44042036496)

GitHub Actions builds the Linux image and tests AC launches across the locked Suite panel, both BFBArchitect releases with CBC, the reference AA launch, Clarabel, both CNVkit CBS versions, and the artificial reporting demo. It runs the smoke tests before manual GHCR publication. Licensed historical AA runs require the user's solver client and authorization. Patient compatibility requires separate data.

## Benchmarks 0.2.0

The previous image passed the Linux build and synthetic component tests in [GitHub Actions](https://github.com/YenningC/AmpliconSuite-Benchmarks-Environments/actions/runs/44028252316). Its ten Suite recipes passed the previous source preparation and configuration checks. [The published 0.2.0 image](https://github.com/YenningC/AmpliconSuite-Benchmarks-Environments/pkgs/container/ampliconsuite-benchmarks-environments) pins the 0.2.0 Benchmarks source.
