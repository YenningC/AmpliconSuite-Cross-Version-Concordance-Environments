# Validation status

The 0.3.0 recipe targets Linux amd64 and the pinned Python 3.12 Bookworm base image. The [Benchmarks source lock](benchmarks-source.lock.json) records the SHA-256 of each public 0.3.0 source file. The image records the Git commit that matched the lock at build time and reuses that commit when bootstrapping the mounted cache.

## Benchmarks 0.3.0

Local checks verified source extraction against the complete 87-file release inventory, refusal of modified and invalid archives, and refusal of a modified cache. They also checked Python, shell and workflow syntax. The 0.3.0 Linux image build, synthetic component smoke tests and GHCR publication are pending GitHub Actions.

GitHub Actions builds the Linux image and tests AC launches across the locked Suite panel, both BFBArchitect releases with CBC, the reference AA launch, Clarabel, both CNVkit CBS versions, and the artificial reporting demo. It runs the smoke tests before manual GHCR publication. Licensed historical AA runs require the user's solver client and authorization. Patient compatibility requires separate data.

## Benchmarks 0.2.0

The previous image passed the Linux build and synthetic component tests in [GitHub Actions](https://github.com/YenningC/AmpliconSuite-Benchmarks-Environments/actions/runs/44028252316). Its ten Suite recipes passed the previous source preparation and configuration checks. [The published 0.2.0 image](https://github.com/YenningC/AmpliconSuite-Benchmarks-Environments/pkgs/container/ampliconsuite-benchmarks-environments) pins the 0.2.0 Benchmarks source.
