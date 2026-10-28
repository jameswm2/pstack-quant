# Verification record

The coordinator verified the implementation on 2026-10-28. These checks establish local package and evidence behavior, not research validity or native cross-host model execution.

## Local behavior

`python3 -m unittest discover -s tests -v` passed all 27 behavioral tests on Python 3.14 after the final recovery fix. The implementation owner also ran the earlier 24-test suite on Python 3.12. Tests exercise the public CLI, concurrent budget accounting, retry conflicts, missing or altered artifacts, review bindings and declared independence, failed attempts, and relocated installation without Git metadata.

`python3 tools/check_package.py` passed for all seven shared skills. Both host manifests, marketplace paths, local links, provenance, and example paths passed. `git diff --check main...HEAD` reported no whitespace errors.

Two fresh standalone demo runs produced matching development data, metrics, and source files. The coordinator compared their SHA-256 digests. Both runs generated only development rows, left the holdout ungenerated, and created no review receipts. Inspection returned code `1` with valid integrity, a negative development outcome, blocked research disposition, and four missing independent review seats. This is the intended partial-dossier result.

The future-information negative control returned code `1` with `AssertionError: future information at decision time`. It failed at the temporal boundary rather than an unrelated exception.

During implementation, focused regression tests first failed with `symlink is not allowed` for a normal parent alias and `runner silently ignored changed registered splits` for an unsupported registered design. Both tests pass after their fixes. The coordinator reran them in the complete suite.

Independent review found a receipt-recovery defect. Before its fix, interrupted review and decision staging caused `unsafe or invalid identifier`, exit `2`, and invalid integrity. The regression tests and fresh independent CLI verification now preserve valid complete or incomplete evidence, report interrupted staging, and still reject malformed published receipts, pending files, and symlinks. The [review record](review.md) describes the panel and forward test.

## Host discovery

The installed Codex CLI reported version `0.160.0`. This command enumerated the final package with the correct identity, version, local source, and installation policy without changing user configuration:

```sh
codex -c 'marketplaces.pstack-quant.source_type="local"' \
  -c 'marketplaces.pstack-quant.source="/absolute/path/to/pstack-quant"' \
  plugin list --available --json --marketplace pstack-quant
```

Discovery is verified. Installation into a user's host profile and research execution by a native host model are not verified by listing a package.

The local environment has no Claude Code CLI. A separate CI job invokes the official CLI's manifest validator, but CI cannot run remotely until repository publication succeeds. Neither static checks nor manifest validation establish native Claude research execution.

## Delivery

The target is `https://github.com/jameswm2/pstack-quant`. The connected GitHub integration can read it, but rejected initial file creation with HTTP 403, `Resource not accessible by integration`. Shell GitHub access also failed DNS resolution. A browser fallback requires approval unavailable in this session. No remote file, branch, or pull request was created.

The local Git repository, installable archive, and Git bundle are prepared for delivery. Publishing the implementation to the requested repository remains outstanding and requires a working write-capable connection. No alternate hosting, account changes, merge, or public plugin release was attempted.
