# Validation status

The 0.3.1 recipe targets Linux amd64 and the pinned Python 3.12 Bookworm base image. The [Concordance source lock](concordance-source.lock.json) records the SHA-256 of each public 0.3.1 source file. The image records the Git commit that matched the lock at build time and reuses that commit when bootstrapping the mounted cache.

## AmpliconSuite Cross-Version Concordance 0.3.1

Track the current Linux amd64 build, component tests and publication in [GitHub Actions](https://github.com/YenningC/AmpliconSuite-Cross-Version-Concordance-Environments/actions).

GitHub Actions builds the Linux image and tests AC launches across the locked Suite panel, both BFBArchitect releases with CBC, the reference AA launch, Clarabel, both CNVkit CBS versions, and the artificial reporting demo. It runs the smoke tests before manual GHCR publication. Licensed historical AA runs require the user's solver client and authorization. Patient compatibility requires separate data.

## Historical releases

The 0.3.0 image was published with digest `sha256:2273905bd8417cfd2d63af8f25e29c36383b70d2298954ebd834e7ca91959710`. [0.3.0 environment tests](https://github.com/YenningC/AmpliconSuite-Cross-Version-Concordance-Environments/actions/runs/44041555708) · [0.3.0 publication](https://github.com/YenningC/AmpliconSuite-Cross-Version-Concordance-Environments/actions/runs/44042036496)

The 0.2.0 image passed the Linux build and synthetic component tests in [GitHub Actions](https://github.com/YenningC/AmpliconSuite-Cross-Version-Concordance-Environments/actions/runs/44028252316). Its ten Suite recipes passed the previous source preparation and configuration checks. The image pins the historical 0.2.0 source.
