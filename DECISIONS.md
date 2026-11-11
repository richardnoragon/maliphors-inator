# Project Decisions

This document records the key decisions reflected in the current workspace and the implementation that exists today. It is meant to capture the real project direction as represented by the code, docs, and release artifacts in this repository.

## Status

The repository contains an active pre-alpha Python application under daily developer testing. The core implementation includes a Tkinter desktop app, CLI entry points, phrase generation logic, persistent JSON data files, and supporting settings/logging workflows.

## Current naming decision on 2026-10-10

The project is now `maliphors-inator`. This supersedes decision 5 below while preserving that decision as history. Runtime modules are `maliphors_inator_cli.py`, `maliphors_inator_logic.py`, and `maliphors_inator_ui.py`; the GUI class is `MaliphorsInatorApp`. Historical paths below refer to the previous layout. See [REBRANDING.md](REBRANDING.md) for the complete mapping.

## Decision log

### 1. Keep the primary product as a Python desktop application

Decision:
- The main runtime experience is built in Python and centered on the Tkinter GUI in [malaphor_ui.py](malaphor_ui.py).
- The startup path is routed through [main.py](main.py), which invokes the GUI by default and the CLI when command-line arguments are present.

Rationale:
- The repository already contains a working product surface, tests, and UI flows.
- The main app behavior is implemented in Python files at the repository root rather than in a framework-first or service-based architecture.

Consequences:
- The app is simple to run and inspect locally.
- The project depends on Python and Tkinter as its core runtime model.
- Most user-facing functionality is intentionally packaged as a desktop app rather than a web service.

### 2. Use a single generator engine as the application core

Decision:
- The central behavior lives in `MalaphorGenerator` inside [malaphor_logic.py](malaphor_logic.py).
- The CLI and GUI both delegate to that engine for generation, search, import/export, and persistence actions.

Rationale:
- This approach keeps generation rules and stored state in one place instead of duplicating logic across UI and CLI code.
- The codebase already reflects this pattern across the current implementation.

Consequences:
- The generator is the primary behavior owner for phrase logic and data management.
- The UI layer stays more focused on interaction and presentation.
- Future feature work likely extends the generator rather than reproducing logic in multiple places.

### 3. Use JSON as the project’s persistence model

Decision:
- Phrase data is stored in [malaphors.json](malaphors.json).
- Generated history is stored in [history.json](history.json).
- Favorites are stored in [favorites.json](favorites.json).
- Runtime UI settings are written to `ui_preferences.json` when the app runs.

Rationale:
- The project is a local, file-based desktop app, not a database-backed service.
- This matches the repo’s current implementation and keeps the setup simple.

Consequences:
- The app is easy to run without external infrastructure.
- Persistence is local and file-based, which is simple but not designed for large-scale multi-user data management.
- Data durability depends on consistent file handling and backup discipline.

### 4. Keep the CLI and GUI as separate but complementary entry points

Decision:
- [main.py](main.py) is the application entry point.
- [malaphor_cli.py](malaphor_cli.py) exposes argparse-driven command-line actions for generation, search, import, and export.
- The Tkinter GUI remains the primary end-user experience.

Rationale:
- The current workspace includes both interactive and non-interactive workflows.
- The app is small enough that one shared generator can support both views cleanly.

Consequences:
- Contributors need to maintain both interactive and CLI flows as the project evolves.
- The command-line surface acts as an operational complement rather than a separate product identity.

### 5. Preserve internal naming stability while shipping public branding as Malaphors-inator

Decision:
- Public-facing documentation and UI branding use the name “Malaphors-inator.”
- Internal module names remain historically stable to avoid breaking current code paths.

Rationale:
- The project docs and UI clearly reflect the public product name in the current workspace.
- The codebase includes historical names that are meaningful to the current implementation and should not be churned unnecessarily.

Consequences:
- Public branding is consistent for users and contributors.
- Internal file and module naming may not perfectly match the product name in every case.
- This is an intentional compatibility tradeoff to reduce churn while improving external clarity.

### 6. Treat documentation and release-readiness as a first-class concern

Decision:
- The project uses [README.md](README.md), [CHANGELOG.md](CHANGELOG.md), [VERSIONING.md](VERSIONING.md), and [.specify](.specify) as active project artifacts.
- The release plan under [.specify/features/improvements-roadmap](.specify/features/improvements-roadmap) is oriented toward stability, documentation parity, and release-readiness rather than broad speculative expansion.

Rationale:
- The repository already contains a functional app; the next priority is not greenfield feature creation but stabilization and consistency.
- This decision is explicit in the current roadmap and changelog material.

Consequences:
- Documentation serves as a production artifact, not just a historical note.
- The team is expected to keep project status aligned with actual implementation.
- Release work is gated on validation and consistency rather than feature backlog expansion alone.

### 7. Follow semantic versioning and changelog discipline

Decision:
- The repository uses semantic versioning as the official release policy in [VERSIONING.md](VERSIONING.md).
- User-facing changes are expected to be recorded in [CHANGELOG.md](CHANGELOG.md).

Rationale:
- The project has explicit versioning governance guidance in the current workspace.
- This keeps release artifacts consistent and reviewable.

Consequences:
- Releases are expected to be traceable and predictable.
- Breaking changes require clear version increments and release note updates.
- Contributors are encouraged to treat docs and changelog changes as part of the release process.

### 8. Document the implementation present in the checkout

The current checkout contains the Python desktop app and CLI. Earlier documentation described a `malaphor-rs` Rust/Tauri directory that is absent here. Architecture and installation guidance therefore cover the existing Python implementation. Any future implementation needs its own verified paths and setup instructions.

### 9. Keep the current legal posture proprietary

Decision:
- The repository license is set to a proprietary arrangement in [LICENSE](LICENSE).

Rationale:
- This matches the project’s current legal and product-state direction.
- The repository and user-facing materials reflect that the code is not currently distributed under an open-source permissive license.

Consequences:
- The project has explicit usage restrictions.
- Contributors should align any distribution or reuse plans with the repository’s legal requirements before external publication.

### 10. Define alpha by working workflows and developer handoff

As of 2026-10-01, adopt the [development-stage definitions](alpha.md). Alpha requires the core purpose to work end-to-end, sufficiently stable architecture, understood data risks, major workflow tests, and another developer able to continue from the code and documentation. Beta requires reliable real use by ordinary users. Missing polish and unfinished enhancement backlog items can remain at alpha.

The project remains pre-alpha, with alpha readiness in progress. [ROADMAP.md](ROADMAP.md#alpha-readiness) owns the evidence and open gates. Stage decisions and version publication are separate; existing package/framework version numbers do not demonstrate readiness.

## Cross-cutting patterns

These principles show up repeatedly across the current workspace:

- Favor a simple local workflow over a heavy service architecture.
- Keep the codebase focused on a working app and its immediate release-readiness needs.
- Treat documentation as part of the product, not a separate afterthought.
- Separate UI, CLI, and core logic in a clean but lightweight way.
- Prefer practical stability over speculative feature breadth.

## Summary

The current repository decisions are consistent with a project that is already built and operational, with emphasis on:

- a Python desktop app with a Tkinter interface,
- a single shared generator engine,
- lightweight JSON-based persistence,
- contributor-friendly docs and release discipline,
- public branding aligned to Malaphors-inator,
- and a stable release posture rather than broad greenfield expansion.

## Alpha technical checkpoint on 2026-10-01

The [architecture review](ARCHITECTURE.md#alpha-architecture-review-on-2026-10-01) confirms that the current boundaries and JSON storage support the core alpha scope without a major rewrite. JSON writes use atomic replacement; core mutations commit memory after successful persistence. Initial alpha validation/support is limited to Ubuntu 26.04.1/Python 3.14.4/Tk 8.6.17. The 214-test technical pass and backup recovery are complete; human usability and independent developer handoff still gate alpha declaration.
