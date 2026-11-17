#!/usr/bin/env python3
"""Configure pinned AmpliconSuite Cross-Version Concordance runtimes inside the environment image."""

import argparse
import copy
import json
import os
from pathlib import Path
import sys

from ascompare.benchmark import FIXED_REFERENCE
from ascompare.benchmark_cnv import load_builtin_map
from ascompare.versions import _check_source, load_lock


def read_object(path):
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def verified_entrypoint(prepared_source, component_name, component):
    root = Path(prepared_source[f"{component_name}_source"])
    entrypoint = root / component["entrypoint"]
    declared = Path(prepared_source[f"{component_name}_script"])
    if not root.is_absolute() or not declared.is_absolute() or declared != entrypoint:
        raise ValueError(f"Invalid {component_name.upper()} path for {prepared_source['id']}. Run prepare-panel inside the container.")
    _check_source(root, component)
    if not entrypoint.is_file():
        raise ValueError(f"Missing locked {component_name.upper()} entrypoint: {entrypoint}")
    return str(entrypoint)


def executable(path):
    if not path.is_file() or not os.access(path, os.X_OK):
        raise ValueError(f"Runtime executable is unavailable: {path}. Run configure-runtime inside the environment image.")
    # A venv Python may be a symlink. Resolving it would select the base Python.
    return str(path.absolute())


def ac_environment(lock_entry):
    bfb = lock_entry.get("bfb")
    if bfb and bfb["version"] == "1.0.1":
        return "ac-bfb101"
    if not bfb or bfb["version"] == "1.0.2":
        return "ac-bfb102"
    raise ValueError(f"The image has no exact BFBArchitect runtime for {lock_entry['id']}")


def configure_manifest(manifest, prepared, lock, venv_root, selected=None,
                       mosek_pythonpath=None, mosek_license=None):
    mode = manifest.get("mode")
    if mode not in ("with_bam", "results_only"):
        raise ValueError("mode must be with_bam or results_only")
    if (manifest.get("reference_version", FIXED_REFERENCE) != FIXED_REFERENCE
            or lock["reference_version"] != FIXED_REFERENCE
            or prepared["reference_version"] != FIXED_REFERENCE):
        raise ValueError(f"Expected the fixed Suite reference {FIXED_REFERENCE}")
    if manifest.get("version_lock"):
        raise ValueError("The bundled environments are mapped to the built-in lock. Remove version_lock from this manifest.")

    lock_entries = {entry["id"]: entry for entry in lock["versions"] if entry.get("suite")}
    source_list = prepared["sources"]
    sources = {source["id"]: source for source in source_list}
    if len(sources) != len(source_list):
        raise ValueError("Prepared panel has duplicate versions")
    target_versions = selected if selected is not None else manifest.get("target_versions", list(lock_entries))
    if (not isinstance(target_versions, list) or not target_versions
            or any(not isinstance(version, str) for version in target_versions)
            or len(set(target_versions)) != len(target_versions)):
        raise ValueError("Use a nonempty list of distinct Suite IDs, such as suite-1.6.2")
    targets = list(dict.fromkeys([FIXED_REFERENCE, *target_versions]))
    samples = manifest.get("samples")
    if not isinstance(samples, list) or not samples:
        raise ValueError("At least one sample with source_version is required")
    sample_sources = list(dict.fromkeys(sample["source_version"] for sample in samples))
    requested = targets.copy()
    if mode == "with_bam" and selected is None:
        requested = list(dict.fromkeys([*requested, *sample_sources]))
    for version in dict.fromkeys([*requested, *sample_sources]):
        if version not in lock_entries:
            raise ValueError(f"Suite ID {version} is absent from the built-in lock")

    recipes = load_builtin_map()["versions"]
    runtimes = []
    warnings = []
    if mode == "with_bam" and any(source not in requested for source in sample_sources):
        warnings.append("The selected subset omits a source Suite. Its rerun and source reproducibility check will remain unverified.")
    mosek_client_required = []
    mosek_license_required = []
    for version in requested:
        lock_entry = lock_entries[version]
        if version not in sources:
            raise ValueError(f"Prepared panel is missing {version}. Run prepare-panel inside the container.")
        source = sources[version]
        ac_bin = venv_root / ac_environment(lock_entry) / "bin"
        runtime = {
            "id": version,
            "ac_python": executable(ac_bin / "python"),
            "ac_script": verified_entrypoint(source, "ac", lock_entry["ac"]),
        }

        if mode == "with_bam":
            aa_version = lock_entry["aa"]["version"]
            solver = "clarabel" if aa_version.startswith("1.6.") else "mosek"
            recipe = recipes[version]
            if recipe["suite_commit"] != lock_entry["suite"]["commit"]:
                raise ValueError(f"CNVkit recipe does not match the locked Suite source for {version}")
            cnvkit_version = recipe["cnvkit_version"]
            cnvkit_bin = venv_root / f"cnvkit-{cnvkit_version}" / "bin"
            runtime.update(
                aa_python=executable(venv_root / "aa" / "bin" / "python"),
                aa_script=verified_entrypoint(source, "aa", lock_entry["aa"]),
                solver=solver,
                cnvkit_version=cnvkit_version,
                cnvkit_python=executable(cnvkit_bin / "python"),
                cnvkit_script=executable(cnvkit_bin / "cnvkit.py"),
            )
            commercial_env = {}
            if aa_version != "1.6.r2":
                if mosek_pythonpath:
                    commercial_env["PYTHONPATH"] = str(mosek_pythonpath)
                else:
                    mosek_client_required.append(version)
            if solver == "mosek":
                if mosek_license:
                    commercial_env["MOSEKLM_LICENSE_FILE"] = str(mosek_license)
                elif not os.environ.get("MOSEKLM_LICENSE_FILE"):
                    mosek_license_required.append(version)
            if commercial_env:
                runtime["env"] = commercial_env
        runtimes.append(runtime)

    if mosek_client_required:
        versions = ", ".join(mosek_client_required)
        warnings.append(f"{versions} need the user-supplied MOSEK Python client even when AA selects Clarabel. Use --mosek-pythonpath or make that client importable in the AA runtime.")
    if mosek_license_required:
        versions = ", ".join(mosek_license_required)
        warnings.append(f"{versions} use MOSEK for AA reconstruction. Set --mosek-license or a supported license-server environment before running them.")

    result = copy.deepcopy(manifest)
    result.update(reference_version=FIXED_REFERENCE, target_versions=targets, runtimes=runtimes)
    return result, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Base benchmark JSON manifest")
    parser.add_argument("--out", required=True, type=Path, help="New JSON file beside the input manifest")
    parser.add_argument("--prepared", type=Path, default=Path("/sources/prepared_panel.json"))
    parser.add_argument("--venv-root", type=Path, default=Path("/opt/benchmarks-venvs"))
    parser.add_argument("--versions", nargs="+", help="Limit runtime and target versions to these Suite IDs plus the fixed reference")
    parser.add_argument("--mosek-pythonpath", type=Path, help="Mounted directory containing the user-installed MOSEK Python package")
    parser.add_argument("--mosek-license", type=Path, help="Mounted MOSEK license filename, required for MOSEK AA solver runs")
    args = parser.parse_args()

    if args.input.resolve().parent != args.out.resolve().parent:
        parser.error("Keep the output beside the input manifest so relative paths retain their meaning")
    if args.out.exists():
        parser.error("Refusing to overwrite an existing manifest")

    try:
        if args.mosek_pythonpath and not args.mosek_pythonpath.is_dir():
            raise ValueError("--mosek-pythonpath must name a mounted directory")
        if args.mosek_license and not args.mosek_license.is_file():
            raise ValueError("--mosek-license must name a mounted file")
        result, warnings = configure_manifest(
            read_object(args.input), read_object(args.prepared), load_lock(), args.venv_root.absolute(),
            args.versions, args.mosek_pythonpath and args.mosek_pythonpath.resolve(),
            args.mosek_license and args.mosek_license.resolve(),
        )
        with args.out.open("x", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
            handle.write("\n")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))

    for warning in warnings:
        print(f"Warning: {warning}", file=sys.stderr)
    print(f"Configured {len(result['runtimes'])} version runtimes in {args.out}.")


if __name__ == "__main__":
    main()
