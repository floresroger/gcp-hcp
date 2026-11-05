# GCP-1280 rehearsal bundles (generated artifact ref)

This branch exists so a cluster can sync manifests. It is **not** a review ref and must not be
merged into PR #166. The reviewed tooling lives in `tools/gitops-bootstrap/` on the PR branch.

- **Why this ref exists:** after the bulk reduction, `bootstrap-gitops/` intentionally contains no
  committed bundle, so the PR branch has no directory Config Sync can point at. These directories are
  the assembled output for the disposable Dev AIO pair.
- **Built from commit:** `874908b9252bc8aea37d79e0b491a8ef4713cea8` (tooling and pins; an ancestor of
  this branch).
- **Global project ID:** `gcp-hcp-commons-dev` (real value, not the synthetic fixture).
- **Toolchain:** helm v4.3.1, kubectl v1.37.1 (kustomize v5.8.1), yq v4.54.1 — the same versions the
  goldens were produced with.
- **Review status:** assembled, digest-recorded, **not applied, not referenced by any cluster**.

## Reproduce

From the worktree root:

```
bash tools/gitops-bootstrap/assemble.sh --type mc --global-project-id gcp-hcp-commons-dev \
  --output-dir <new-dir>/mc --shared-crds-output <new-dir>/parent-artifacts/shared-crds.yaml

bash tools/gitops-bootstrap/assemble.sh --type region --global-project-id gcp-hcp-commons-dev \
  --output-dir <new-dir>/region
```

Then compare against the digests below. Output is deterministic for a fixed toolchain and input.

## Config Sync targets

| Variable | Value |
|---|---|
| `configsync_git_repo` | `https://github.com/floresroger/gcp-hcp.git` |
| `configsync_git_revision` | the full SHA of this branch's head commit |
| `configsync_git_dir_mc` | `bundles/gcp1280/dev/rflores-gcp1280/northamerica-northeast2/mc` |
| `configsync_git_dir_region` | `bundles/gcp1280/dev/rflores-gcp1280/northamerica-northeast2/region` |

`parent-artifacts/shared-crds.yaml` is not synced by either directory. It is the three shared
Application/ApplicationSet/AppProject CRDs the parent retains, carried here for the later parent/child
wiring step.

## Digest note

`tools/gitops-bootstrap/tests/golden.sha256` pins the **synthetic** fixture
(`synthetic-global-project`) and therefore does not match this output. The digests below are the
guard for this real-input bundle; there is no second golden for it yet. That gap is recorded as a
known limitation.

## Assembled file digests

```
bd7058c5544cc57917c22a050ece70bdc362a8961b707624a67c4133021cffa0  ./mc/controller-rbac.yaml
a823bfbbd0e1543e00354353abf0405f80cc4336711ce04d91cf4077a2704f0f  ./mc/crds.yaml
655874f09e71ca789500437d589f40d04c2327696fe2c3ff38505998cac3933f  ./mc/gitops-instance.yaml
7fb3b38c9fe1dec7d5655ca738102766cba4b77bab62d134f52057dd44228720  ./mc/kustomization.yaml
09fe3194f68f95a808c2fed0ace142ed02428d96a613084c624bd27423ed1b48  ./mc/networkpolicy.yaml
799e94012a74145cbb69cffd484a62338ae568fb76522b9212090cf0b66b7dc5  ./mc/operator.yaml
7967d011755fd0bbc1019404819842df07cdfcd51d38523eba464a1c8cf90b14  ./mc/registry.yaml
61c7bb96e7cd3f1fa962700518446c5e30dd3c2d841972842c9e0d403a17acb6  ./parent-artifacts/shared-crds.yaml
a4ff4712518b7e8ed2e686326492e657c05c7273f3dd08fe3930e6a7b9e775d4  ./region/controller-rbac.yaml
a823bfbbd0e1543e00354353abf0405f80cc4336711ce04d91cf4077a2704f0f  ./region/crds.yaml
fe16d36c6287d9de33c8b85e66f736b973e6ab003bd9e0381a66b066d1dc8824  ./region/gitops-instance.yaml
7fb3b38c9fe1dec7d5655ca738102766cba4b77bab62d134f52057dd44228720  ./region/kustomization.yaml
52c5ab2296b17347e8b3661d5561fdfef3c4e0cb9cdb7e0c976de97b0c53291a  ./region/networkpolicy.yaml
799e94012a74145cbb69cffd484a62338ae568fb76522b9212090cf0b66b7dc5  ./region/operator.yaml
ef9ef7dfe59c6d581b97016a3cc18ad9799e8b8777d5ec7d4418c6a012c43a5b  ./region/registry.yaml
```

## Delta from the pinned synthetic golden

Generated a second time with `--global-project-id synthetic-global-project` and compared. That run
reproduced every golden digest it produces (14/14 files covered by the two runs), so the toolchain and
pins are consistent.

Against the real-input bundle, 13 of the 15 pinned files are **byte-identical**. Only the two registry
files differ, and the entire difference is one line each:

```
$ diff <synthetic>/mc/registry.yaml <real>/mc/registry.yaml
18c18
<       projectID: synthetic-global-project
---
>       projectID: gcp-hcp-commons-dev
```

The same single-line delta applies to `region/registry.yaml`. `parent-artifacts/shared-crds.yaml`
matches the pinned digest exactly (`61c7bb96…`), which is why it is identical to the artifact that was
committed before the bulk reduction.

Consequence: the existing goldens already guard 13 of these 15 real files implicitly. Only the two
project-specific registry files are unguarded, and their only variable is the global project ID.
