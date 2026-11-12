# GCP-1286 runtime bundles (generated artifact ref)

This branch exists so both clusters of the disposable GCP-1286 Dev AIO pair can
sync manifests. It is **not** a review ref and must not be merged into #166. The
reviewed tooling lives in `tools/gitops-bootstrap/` on
`gcp-1286/release-matrix`.

- **Why this ref exists:** `bootstrap-gitops/` intentionally carries no child
  bundle, so Config Sync needs a published directory to point at. These
  directories are the assembled output for the pair; they are not applied until
  the B5 grant is exercised.
- **Built from commit:** `dd0b1e0be5dada97f4b86a211e330bd40fcddff7` (scoped
  operator identity, `--scoped-rbac`).
- **Global project ID:** `gcp-hcp-commons-dev` (real value for the Dev AIO
  target, not the synthetic fixture).
- **Scoped mode:** `--scoped-rbac`. The bundle owns
  `gitops-application-controller-interim-parity` and `gitops-argocd-server`, and
  the manager keeps one qualified `bind` limited to those two names. The
  controller keeps the interim-parity wildcard as the recorded residual
  ([GCP-1433](https://redhat.atlassian.net/browse/GCP-1433) tracks the
  replacement).
- **Toolchain:** helm v4.3.1, kubectl v1.37.1 (kustomize v5.8.1), yq v4.54.1.
- **Review status:** assembled, digest-recorded, **not applied, not referenced
  by any cluster**.

## Reproduce

From the worktree root:

```
bash tools/gitops-bootstrap/assemble.sh --type mc --global-project-id gcp-hcp-commons-dev \
  --scoped-rbac --output-dir <new-dir>/mc \
  --shared-crds-output <new-dir>/parent-artifacts/shared-crds.yaml

bash tools/gitops-bootstrap/assemble.sh --type region --global-project-id gcp-hcp-commons-dev \
  --scoped-rbac --output-dir <new-dir>/region
```

Output is deterministic for a fixed toolchain and input. Compare against the
digests below.

## Config Sync targets

| Variable | Value |
|---|---|
| `configsync_git_repo` | `https://github.com/floresroger/gcp-hcp.git` |
| `configsync_git_revision` | the full SHA of this branch's head commit |
| `configsync_git_dir_mc` | `bundles/gcp1286/dev/rflores-gcp1286/us-central1/mc` |
| `configsync_git_dir_region` | `bundles/gcp1286/dev/rflores-gcp1286/us-central1/region` |

Each parent directory carries its own `10-gitops-rootsync.yaml`. Both pin
revision `2f728e69db178c235e73345a42b5781395653e8a`, the commit that added the
child bundles. That commit stays reachable; the parent files at the branch head
are what Config Sync applies first.

`parent-artifacts/shared-crds.yaml` is not synced by either directory. It is the
three shared Application/ApplicationSet/AppProject CRDs, and
`parent-{mc,region}/03-shared-crds.yaml` are byte-identical copies. The same
bytes are committed at `bootstrap-gitops/parent-artifacts/shared-crds.yaml`,
where the offline suite checks them against a fresh assembly and
`tests/golden.sha256`.

## Digests

### Child bundles

| File | `mc` | `region` |
|---|---|---|
| `controller-rbac.yaml` | `bd7058c5544cc57917c22a050ece70bdc362a8961b707624a67c4133021cffa0` | `a4ff4712518b7e8ed2e686326492e657c05c7273f3dd08fe3930e6a7b9e775d4` |
| `crds.yaml` | `a823bfbbd0e1543e00354353abf0405f80cc4336711ce04d91cf4077a2704f0f` | `a823bfbbd0e1543e00354353abf0405f80cc4336711ce04d91cf4077a2704f0f` |
| `gitops-instance.yaml` | `655874f09e71ca789500437d589f40d04c2327696fe2c3ff38505998cac3933f` | `fe16d36c6287d9de33c8b85e66f736b973e6ab003bd9e0381a66b066d1dc8824` |
| `kustomization.yaml` | `774cdb14fe071369f4232636876a3ddfcb9dece78e05aeeca03bb693949e8de9` | `774cdb14fe071369f4232636876a3ddfcb9dece78e05aeeca03bb693949e8de9` |
| `networkpolicy.yaml` | `09fe3194f68f95a808c2fed0ace142ed02428d96a613084c624bd27423ed1b48` | `52c5ab2296b17347e8b3661d5561fdfef3c4e0cb9cdb7e0c976de97b0c53291a` |
| `operator.yaml` | `e9f7120efba7de4a97fa0f4ec36783a20c433660c1b08d62946eba5bf5e72535` | `e9f7120efba7de4a97fa0f4ec36783a20c433660c1b08d62946eba5bf5e72535` |
| `registry.yaml` | `7967d011755fd0bbc1019404819842df07cdfcd51d38523eba464a1c8cf90b14` | `ef9ef7dfe59c6d581b97016a3cc18ad9799e8b8777d5ec7d4418c6a012c43a5b` |
| `scoped-rbac.yaml` | `75dbd7c1cd34275e0805809968fadb7566c54e2a22014cc3020767a8a27d61d4` | `f9cb9c3579a4f1165cebe49ee7f07581322273a711db0897337477f0c383719c` |

### Parent directories

| File | `parent-mc` | `parent-region` |
|---|---|---|
| `00-argocd-namespace.yaml` | `e650d6401b7c1f4d606d6155527d68775bb470b4a7f228a5eef45b7c7c6dc677` | `e650d6401b7c1f4d606d6155527d68775bb470b4a7f228a5eef45b7c7c6dc677` |
| `01-external-secrets-namespace.yaml` | `c8f63da4949aa9a807251c20f2227a4054526b5143018f221ed2a339ac02570a` | `c8f63da4949aa9a807251c20f2227a4054526b5143018f221ed2a339ac02570a` |
| `02-external-secrets-controller.yaml` | `8efeb97eb2677cad340e93e4185d7e552a4e7ec768f308ac6364adcf35f04014` | `8efeb97eb2677cad340e93e4185d7e552a4e7ec768f308ac6364adcf35f04014` |
| `03-shared-crds.yaml` | `61c7bb96e7cd3f1fa962700518446c5e30dd3c2d841972842c9e0d403a17acb6` | `61c7bb96e7cd3f1fa962700518446c5e30dd3c2d841972842c9e0d403a17acb6` |
| `04-secret-store.yaml` | `ecc71a17206325df380ebd709885052341057e08f4b5d847b17c44735500dac7` | `ecc71a17206325df380ebd709885052341057e08f4b5d847b17c44735500dac7` |
| `05-service-account.yaml` | `d43ed2b1069413fbff2f661bbebd00411d5229f510b2eb197fad8ab1571ce78b` | `d43ed2b1069413fbff2f661bbebd00411d5229f510b2eb197fad8ab1571ce78b` |
| `06-cluster-metadata-template.yaml` | `6945709b585114f699409693cf0d568bf894f52fea818d9126a556eadf87e103` | `6945709b585114f699409693cf0d568bf894f52fea818d9126a556eadf87e103` |
| `07-external-secret-argocd-cluster.yaml` | `3d8c72e8500fc075a85a88b609d4ded5a59ead5b9b072126b2b23efdcc409aee` | `3d8c72e8500fc075a85a88b609d4ded5a59ead5b9b072126b2b23efdcc409aee` |
| `08-external-secret-git-credentials.yaml` | `cf561abce1bcfb4a6849795951f32d4d25681fac085f58925606a0bc82b81074` | `cf561abce1bcfb4a6849795951f32d4d25681fac085f58925606a0bc82b81074` |
| `09-root-applicationset.yaml` | `96ab06bc16ba02177c26b9ce0de9acecfcca1c6cd0b5f884d86d6d37056fc50c` | `96ab06bc16ba02177c26b9ce0de9acecfcca1c6cd0b5f884d86d6d37056fc50c` |
| `10-gitops-rootsync.yaml` | `f0e1c63afaf61d919368266e3180bd8e7b237143f93e7ed43c49f8d5f4641584` | `7005bd61de1c0c38cc753845e25f3050c0e8688cbefbd5e366c1db1e20eb95ee` |

### Shared artifact

| File | SHA-256 |
|---|---|
| `parent-artifacts/shared-crds.yaml` | `61c7bb96e7cd3f1fa962700518446c5e30dd3c2d841972842c9e0d403a17acb6` |
| `bootstrap-gitops/parent-artifacts/shared-crds.yaml` | `61c7bb96e7cd3f1fa962700518446c5e30dd3c2d841972842c9e0d403a17acb6` |
