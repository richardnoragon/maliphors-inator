# Versioning Policy

This is the canonical versioning page for the repository. It consolidates the
policy, governance, rollout, migration, and enforcement guidance that used to
live across multiple versioning documents.

## Purpose

Define the repository's release, tagging, and governance rules so changes stay
predictable, traceable, and reversible.

## Scope

This policy applies to source code, APIs, schemas, infrastructure artifacts,
documentation, release notes, and any other published project deliverable.

## Versioning Scheme

Semantic versioning is required for documented releases and tags.

- MAJOR: incompatible changes, including breaking API, schema, or behavior
  changes.
- MINOR: backward-compatible feature additions.
- PATCH: backward-compatible bug fixes and documentation corrections.
- Pre-release identifiers such as `-alpha`, `-beta`, and `-rc` MAY be used for
  staged releases.
- Build metadata such as `+commitSHA` or `+buildID` MAY be appended for
  traceability.

## Development stage and version numbers

[alpha.md](alpha.md) defines alpha, beta, and stable-release readiness; [ROADMAP.md](ROADMAP.md#alpha-readiness) records the current evidence. The application remains pre-alpha while alpha readiness is in progress. Existing `1.0.0` package metadata and historical `1.0.0`/`2.0.0` changelog or framework entries do not establish application maturity or choose the next application version.

Choose and reconcile application version metadata when preparing a reviewed release. A development-stage decision does not require publication; a prerelease tag must match the evidenced stage and the [release process](RELEASE_PROCESS.md).

## Release Discipline

- Every user-facing change MUST have a changelog entry in [CHANGELOG.md](CHANGELOG.md).
- Release notes MUST map to commits, pull requests, or other reviewable change
  records.
- Version tags MUST be immutable and must not use `latest`.
- Release metadata SHOULD remain traceable to the exact build or commit that
  produced it.

## API Versioning

- Public APIs MUST be explicitly versioned.
- Breaking API changes require a new MAJOR version.
- Deprecations SHOULD be announced at least one MINOR release before removal.

## Schema and Data Versioning

- Schema changes MUST be tracked with ordered migrations.
- Migration scripts MUST include rollback or recovery paths.
- Backward-compatible rollout patterns are preferred whenever practical.

## Infrastructure Artifacts

- Container images and similar artifacts MUST use immutable tags.
- Pipelines MUST embed commit SHA or equivalent build identifiers in release
  metadata.
- CI/CD checks SHOULD block publishing when a non-immutable tag is detected.

## Migration and Rollout

When a versioning policy change affects contributors, release tooling, or
runtime behavior, document the transition in a migration plan and rollout plan.

- Migration plans describe the adoption steps, owners, dependencies, and
  rollback strategy.
- Rollout plans describe the phases, validation gates, and communication path.
- User-facing versioning changes MUST be recorded in the changelog.

## Governance Review

- This policy SHOULD be reviewed at least annually, and sooner when release
  practice changes materially.
- Reviews MUST capture the standard under review, evidence, findings, decisions,
  and action items.
- Required evidence includes the changelog, release notes, CI logs, and any
  migration or rollout artifacts used for the change.

## Enforcement Checklist

Before a release is published, verify that:

- The version increment follows semantic versioning.
- The changelog contains the release entry.
- Public APIs are versioned correctly.
- Migrations are ordered and reversible.
- Artifacts use immutable tags.
- CI/CD checks validate the release metadata.

## Legacy Source Documents

The following files are retained only as deprecated source material and should
not be treated as canonical:

- Versioning  Standard  Policy.md
- Versioning  Governance Review Template.md
- Versioning Migration Plan Template.md
- Versioning Rollout Plan Template.md
- Versioning  Enforcement Checklist.md

## Changelog

- 2026-09-08: Consolidated the versioning guidance into this canonical page.
