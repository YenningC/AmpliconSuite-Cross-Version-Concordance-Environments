# Validation status

The environment repository was prepared for the fixed Benchmarks 0.2.0 panel. The base image is pinned to the Linux amd64 Python 3.12 Bookworm manifest digest. The Benchmarks source archive and its SHA-256 are pinned independently.

## Completed locally

- Verified that each pinned Python dependency and the optional Mosek client is available from PyPI. The checked target is Python 3.12 on Linux x86-64. The pure-Python intervaltree dependency is supplied as a source distribution.
- Downloaded the pinned Benchmarks archive, checked its SHA-256, extracted it and verified that a repeat `bootstrap` reuses the same checkout.
- Ran `prepare-panel` against cached official AA/AC source trees. All ten locked Suite recipes passed the source inventory checks.
- Verified generated manifests against the existing Benchmarks loader. Covered all ten mappings, the reference-only subset, AC-only, the Mosek client and license distinctions, and refusal of mismatched source paths.
- Ran the public artificial-output demo from the downloaded, pinned checkout and verified the report was created.
- Parsed the workflow and checked Python and shell syntax. The publish step follows successful container smoke tests and requires manual selection of the publish option.

These checks ran on macOS ARM. They verify the orchestration and source mapping. The build machine did not have a container engine, so the Linux image has not been built or pushed in this session.

## Required before a published image is ready

The included GitHub workflow builds the Linux image and runs real component smoke tests on artificial inputs. It checks AC launches and CBC for both BFB generations, the fixed reference AA launch, three Clarabel functions, two CNVkit CBS versions, and the public reporting demo. A successful publishing run supplies the registry digest. Consult the actual workflow log and image provenance for the built dependency versions.

Mosek-licensed historical AA runs require separately supplied authorization and a user-side runtime check. The public smoke test does not measure patient-level compatibility or establish that the historical algorithm runtimes reproduce every official environment.
