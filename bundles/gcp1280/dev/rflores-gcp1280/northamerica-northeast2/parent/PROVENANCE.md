# Parent set — RootSync reconciler memory measurement

Assembled 2026-11-09 for one purpose: measure whether a **default-sized** root reconciler
(512 Mi request/limit on GKE Autopilot) can apply the parent-owned set that Step 3 will sync.
This is a measurement fixture, not a published bundle and not the Step 3 deliverable.

Source: `gcp-hcp` at `874908b^` (the pinned parent base used by PR #166), plus the
shared-CRD artifact already in this repository at `../parent-artifacts/shared-crds.yaml`.
Contents follow the parent column of `bootstrap-gitops/README.md` (ownership table).

| file | bytes | sha256 |
| --- | --- | --- |
| 00-argocd-namespace.yaml | 146 | `e650d6401b7c1f4d606d6155527d68775bb470b4a7f228a5eef45b7c7c6dc677` |
| 01-external-secrets-namespace.yaml | 173 | `c8f63da4949aa9a807251c20f2227a4054526b5143018f221ed2a339ac02570a` |
| 02-external-secrets-controller.yaml | 1750951 | `8efeb97eb2677cad340e93e4185d7e552a4e7ec768f308ac6364adcf35f04014` |
| 03-shared-crds.yaml | 1840742 | `61c7bb96e7cd3f1fa962700518446c5e30dd3c2d841972842c9e0d403a17acb6` |
| 04-secret-store.yaml | 341 | `ecc71a17206325df380ebd709885052341057e08f4b5d847b17c44735500dac7` |
| 05-service-account.yaml | 187 | `d43ed2b1069413fbff2f661bbebd00411d5229f510b2eb197fad8ab1571ce78b` |
| 06-cluster-metadata-template.yaml | 573 | `6945709b585114f699409693cf0d568bf894f52fea818d9126a556eadf87e103` |
| 07-external-secret-argocd-cluster.yaml | 1044 | `3d8c72e8500fc075a85a88b609d4ded5a59ead5b9b072126b2b23efdcc409aee` |
| 08-external-secret-git-credentials.yaml | 546 | `cf561abce1bcfb4a6849795951f32d4d25681fac085f58925606a0bc82b81074` |
| 09-root-applicationset.yaml | 1974 | `96ab06bc16ba02177c26b9ce0de9acecfcca1c6cd0b5f884d86d6d37056fc50c` |

Totals: 10 files, 3,596,677 bytes, 53 documents, 26 CRDs (23 external-secrets + 3 shared Argo).
No credential values: the two ExternalSecrets reference Secret Manager keys and render nothing.

Deliberately excluded: `bootstrap/argocd/install.yaml` and the `argocd-cm` family. Those belong to the
legacy workload set that the operator replaces (the "Removed" and "Released" rows of the ownership
table), so they are not part of the parent set under test.
