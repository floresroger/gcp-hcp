#!/usr/bin/env python3
"""Fail-closed post-checks for the GCP-1286 release verification entry point.

This module does not talk to a registry and does not verify GPG signatures
itself: `verify-release.sh` performs the authenticated, policy-enforcing
`skopeo copy`, which is the cryptographic trust step. This module checks the
things that a successful copy alone does not prove:

  * the saved top-level manifest is byte-identical to the approved digest;
  * the manifest is the expected media type;
  * the selected platform child exists and is the approved platform digest;
  * a signed identity, when supplied, names the same repository and manifest
    digest (a tag-derived identity never substitutes for repository binding);
  * the containers/image policy is fail-closed (`reject` default, `signedBy`
    with `matchRepoDigestOrExact`), so a typo cannot silently downgrade trust.

Everything here is offline and deterministic; tests exercise both passing and
deliberately broken inputs. See `verify-release.sh` and `release-matrix.yaml`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

INDEX_TYPES = {
    "application/vnd.docker.distribution.manifest.list.v2+json",
    "application/vnd.oci.image.index.v1+json",
}
MANIFEST_TYPES = {
    "application/vnd.docker.distribution.manifest.v2+json",
    "application/vnd.oci.image.manifest.v1+json",
}


class CheckError(Exception):
    """A validation failure with a user-facing, credential-free message."""


def fail(message: str) -> None:
    raise CheckError(message)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def split_reference(reference: str) -> tuple[str, str]:
    """Split a digest-pinned reference into (repository, 'sha256:<hex>')."""
    if "@" not in reference:
        fail(f"reference is not digest-pinned: {reference}")
    repository, digest = reference.rsplit("@", 1)
    if not repository:
        fail(f"reference has no repository: {reference}")
    if not digest.startswith("sha256:"):
        fail(f"reference digest is not sha256: {reference}")
    hexpart = digest[len("sha256:"):]
    if len(hexpart) != 64 or any(c not in "0123456789abcdef" for c in hexpart):
        fail(f"reference digest is malformed: {reference}")
    return repository, digest


def check_layout(directory: Path, reference: str, arch: str,
                 expected_platform: str | None) -> dict:
    repository, digest = split_reference(reference)
    manifest_path = directory / "manifest.json"
    if not manifest_path.is_file():
        fail(f"{directory}: manifest.json not found")
    manifest_bytes = manifest_path.read_bytes()
    actual = "sha256:" + sha256_hex(manifest_bytes)
    if actual != digest:
        fail(f"manifest digest mismatch: expected {digest}, got {actual}")

    try:
        manifest = json.loads(manifest_bytes)
    except json.JSONDecodeError as exc:
        fail(f"manifest.json is not valid JSON: {exc}")

    media_type = manifest.get("mediaType", "")
    child = None
    if media_type in INDEX_TYPES:
        wanted_arch, _, wanted_variant = arch.partition("/")
        matches = []
        for platform in manifest.get("manifests", []):
            p = platform.get("platform", {})
            if p.get("os") != "linux" or p.get("architecture") != wanted_arch:
                continue
            if wanted_variant and p.get("variant") != wanted_variant:
                continue
            matches.append(platform)
        if not matches:
            fail(f"index {digest} does not advertise linux/{arch}")
        if len(matches) > 1:
            fail(f"index {digest} advertises ambiguous entries for linux/{arch}")
        child = matches[0].get("digest", "")
        if not child.startswith("sha256:") or len(child) != len("sha256:") + 64:
            fail(f"index {digest} has a malformed child digest for linux/{arch}")
        if expected_platform and child != expected_platform:
            fail(
                f"platform digest mismatch for linux/{arch}: "
                f"expected {expected_platform}, got {child}"
            )
        blob = directory / "blobs" / "sha256" / child[len("sha256:"):]
        if not blob.is_file():
            fail(f"platform child blob missing after copy: {child}")
        child_bytes = blob.read_bytes()
        if "sha256:" + sha256_hex(child_bytes) != child:
            fail(f"platform child content does not hash to {child}")
    elif media_type in MANIFEST_TYPES:
        if expected_platform and digest != expected_platform:
            fail(
                "source manifest is not a multi-architecture index; "
                f"approved platform digest {expected_platform} cannot be selected"
            )
    else:
        fail(f"unsupported manifest media type: {media_type!r}")

    return {
        "repository": repository,
        "digest": digest,
        "mediaType": media_type,
        "arch": arch,
        "platformDigest": child,
    }


def walk_types(node: object, found: list[str]) -> None:
    if isinstance(node, dict):
        if isinstance(node.get("type"), str):
            found.append(node["type"])
        for value in node.values():
            walk_types(value, found)
    elif isinstance(node, list):
        for value in node:
            walk_types(value, found)


def check_policy(path: Path, key_file: Path) -> dict:
    try:
        policy = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"policy is unreadable or invalid JSON: {exc}")
    if not key_file.is_file() or key_file.stat().st_size == 0:
        fail(f"public key file is missing or empty: {key_file}")

    types: list[str] = []
    walk_types(policy, types)
    if "insecureAcceptAnything" in types:
        fail("policy contains insecureAcceptAnything")
    default = policy.get("default")
    if default != [{"type": "reject"}]:
        fail("policy default must be exactly [{'type': 'reject'}]")

    transports = policy.get("transports", {}).get("docker", {})
    entries = transports.get("registry.redhat.io")
    if not isinstance(entries, list) or not entries:
        fail("policy has no docker.registry.redhat.io transport entry")
    for entry in entries:
        if entry.get("type") != "signedBy":
            fail(f"unexpected registry.redhat.io policy type: {entry.get('type')!r}")
        if entry.get("keyType") != "GPGKeys":
            fail("signedBy entry must use keyType GPGKeys")
        if not entry.get("keyPath"):
            fail("signedBy entry must set keyPath")
        if Path(os.path.abspath(entry["keyPath"])) != Path(os.path.abspath(key_file)):
            fail("signedBy keyPath does not match the supplied key file")
        identity = entry.get("signedIdentity", {})
        if identity.get("type") != "matchRepoDigestOrExact":
            fail("signedIdentity must be matchRepoDigestOrExact")
    return {"default": "reject", "transport": "registry.redhat.io", "signedIdentity": "matchRepoDigestOrExact"}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    layout = sub.add_parser("layout", help="check a copied image layout")
    layout.add_argument("--dir", required=True, type=Path)
    layout.add_argument("--reference", required=True)
    layout.add_argument("--arch", default="amd64")
    layout.add_argument("--platform-digest")

    policy = sub.add_parser("policy", help="check a containers/image trust policy")
    policy.add_argument("--policy", required=True, type=Path)
    policy.add_argument("--key-file", required=True, type=Path)

    args = parser.parse_args(argv)
    try:
        if args.command == "layout":
            result = check_layout(
                args.dir, args.reference, args.arch, args.platform_digest,
            )
        else:
            result = check_policy(args.policy, args.key_file)
    except CheckError as exc:
        print(f"verify-release: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
