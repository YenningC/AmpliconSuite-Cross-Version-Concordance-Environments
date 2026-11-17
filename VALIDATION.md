# Validation status

The 0.4.0 recipe targets Linux amd64 and the pinned Python 3.12 Bookworm base image. The [Concordance source lock](concordance-source.lock.json) records the SHA-256 of each public 0.4.0 source file. The image records the Git commit that matched the lock at build time and reuses that commit when bootstrapping the mounted cache.

## AmpliconSuite Cross-Version Concordance 0.4.0

The 0.4.0 Linux image build, component tests and GHCR publication are pending. Track their actual status in [GitHub Actions](https://github.com/YenningC/AmpliconSuite-Cross-Version-Concordance-Environments/actions).

GitHub Actions builds the Linux image and tests AC launches across the locked Suite panel, both BFBArchitect releases with CBC, the reference AA launch, Clarabel, both CNVkit CBS versions, the artificial reporting demo, and the batch-import, cohort-plot and sample-progress regressions. It runs the smoke tests before manual GHCR publication. Licensed historical AA runs require the user's solver client and authorization. Patient compatibility requires separate data.

## Local checks for 0.4.0

The README batch commands were checked against the public CLI, batch input schema, runtime configurator and output names. All 10 Bash examples passed syntax checks. In the existing local Python environment, all 24 batch-import, cohort-plot and sample-progress tests passed on synthetic inputs. Runtime recipes, Python dependency pins, the base image and algorithm parameters are retained from the preceding environment release.

The Dockerfile pins published main-program commit [ea46c70cf9aa337d2a6189455532c8aba31ab2ef](https://github.com/YenningC/AmpliconSuite-Cross-Version-Concordance/commit/ea46c70cf9aa337d2a6189455532c8aba31ab2ef). All 98 files in its public GitHub source archive matched the audited main-program Git index and the complete environment source lock. The archive SHA-256 was `7963055c784dfcd4037ca75e9a3c4117aaa3cf56a33e848107a163bdd1fb05d4`. Container execution and scientific compatibility conclusions require their respective runtime and data validation.

## Historical releases

The 0.3.0 image was published with digest `sha256:2273905bd8417cfd2d63af8f25e29c36383b70d2298954ebd834e7ca91959710`. [0.3.0 environment tests](https://github.com/YenningC/AmpliconSuite-Cross-Version-Concordance-Environments/actions/runs/44041555708) · [0.3.0 publication](https://github.com/YenningC/AmpliconSuite-Cross-Version-Concordance-Environments/actions/runs/44042036496)

The 0.2.0 image passed the Linux build and synthetic component tests in [GitHub Actions](https://github.com/YenningC/AmpliconSuite-Cross-Version-Concordance-Environments/actions/runs/44028252316). Its ten Suite recipes passed the previous source preparation and configuration checks. The image pins the historical 0.2.0 source.
