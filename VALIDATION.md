# Validation status

The 0.4.0 recipe targets Linux amd64 and the pinned Python 3.12 Bookworm base image. The [Concordance source lock](concordance-source.lock.json) records the SHA-256 of each public 0.4.0 source file. The image records the Git commit that matched the lock at build time and reuses that commit when bootstrapping the mounted cache.

## AmpliconSuite Cross-Version Concordance 0.4.0

The 0.4.0 Linux image build, synthetic component tests, all 24 batch/cohort/progress regressions and GHCR publication passed in [run 44125577173](https://github.com/YenningC/AmpliconSuite-Cross-Version-Concordance-Environments/actions/runs/44125577173). The main-program Python 3.10 and 3.12 regressions also passed in [run 44124974765](https://github.com/YenningC/AmpliconSuite-Cross-Version-Concordance/actions/runs/44124974765).

GitHub Actions builds the Linux image and tests AC launches across the locked Suite panel, both BFBArchitect releases with CBC, the reference AA launch, Clarabel, both CNVkit CBS versions, the artificial reporting demo, and the batch-import, cohort-plot and sample-progress regressions. It runs the smoke tests before manual GHCR publication. Licensed historical AA runs require the user's solver client and authorization. Patient compatibility requires separate data.

Published tags `0.4.0` and `0.4.0-e4511660f40f` both resolve to `sha256:5861607cf0f08620b59e8ce6d106918d8aac3e7ec943696b7c24844998232266`. Anonymous GHCR manifest access was independently checked. The image was built from environment commit `e4511660f40f732a0d1422892fa9b56d8f11f6e2`; this documentation update does not change its runtime or source pin.

## Local checks for 0.4.0

The README batch commands were checked against the public CLI, batch input schema, runtime configurator and output names. All 10 Bash examples passed syntax checks. In the existing local Python environment, all 24 batch-import, cohort-plot and sample-progress tests passed on synthetic inputs. Runtime recipes, Python dependency pins, the base image and algorithm parameters are retained from the preceding environment release.

The Dockerfile pins published main-program commit [ea46c70cf9aa337d2a6189455532c8aba31ab2ef](https://github.com/YenningC/AmpliconSuite-Cross-Version-Concordance/commit/ea46c70cf9aa337d2a6189455532c8aba31ab2ef). All 98 files in its public GitHub source archive matched the audited main-program Git index and the complete environment source lock. The archive SHA-256 was `7963055c784dfcd4037ca75e9a3c4117aaa3cf56a33e848107a163bdd1fb05d4`. The hosted container checks validate the stated synthetic execution scope; patient compatibility still requires separate patient data and analysis.

## Historical releases

The 0.3.0 image was published with digest `sha256:2273905bd8417cfd2d63af8f25e29c36383b70d2298954ebd834e7ca91959710`. [0.3.0 environment tests](https://github.com/YenningC/AmpliconSuite-Cross-Version-Concordance-Environments/actions/runs/44041555708) · [0.3.0 publication](https://github.com/YenningC/AmpliconSuite-Cross-Version-Concordance-Environments/actions/runs/44042036496)

The 0.2.0 image passed the Linux build and synthetic component tests in [GitHub Actions](https://github.com/YenningC/AmpliconSuite-Cross-Version-Concordance-Environments/actions/runs/44028252316). Its ten Suite recipes passed the previous source preparation and configuration checks. The image pins the historical 0.2.0 source.
