# Changelog

All notable changes to this project are recorded here using semantic versioning.

## [Unreleased]

### Rebranding on 2026-10-10
- Adopt `maliphors-inator` across the repository, workspace, current documentation, GUI, CLI, runtime modules, and daily launcher. See [REBRANDING.md](REBRANDING.md) for migration and validation. Earlier branding entries below describe their original changes.

### Added
- Installable Linux Daily Test snapshot with desktop/menu launchers, a dedicated environment, separate persistent data, 14 startup backups, rotating logs, and a single-session lock.
- Daily failure-path regression checks and a Linux/Tk walkthrough that drives real file dialogs using temporary data. The 2026-09-30 daily pass completed with 174 tests passing; visual review remains open.
- Public branding has been updated to Malaphors-inator in the main project docs and UI title, while internal module names remain historically stable to avoid breaking the current implementation.
- Release documentation is now aligned to the active project status instead of the older planning-only narrative.

### Changed
- 2026-10-01: Adopted concise development-stage definitions from `alpha.md` and aligned the roadmap, release/versioning guidance, contributor handoff checks, and specification status. Alpha readiness is in progress; the application remains pre-alpha pending the documented reviews and independent handoff. This documentation update does not select a release version or claim a new runtime validation pass.
- Aligned README, architecture, testing, security, user, and release guides with the pre-alpha Python implementation and daily developer gates in ROADMAP.md. Corrected CLI scope, storage/import behavior, separate Qt utility descriptions, and stale Rust/Tauri references; recorded that no private security-reporting channel is planned.
- Normalized project documentation to semantic versioning conventions.
- Added explicit release note guidance to the README, contributing guide, and speckit documentation.
- Removed stale `latest` wording from speckit configuration and update notes.
- Consolidated the versioning docs into [VERSIONING.md](VERSIONING.md).
- Implemented scheduled auto-save lifecycle hooks so the app persists history and favorites in a background thread without blocking the UI.
- Verified and documented Section 2 reliability/performance work: cancellation-safe async generation, malformed-history resilience, latency benchmarking, and paginated history access.
- Added language-aware generation support to the core generator and CLI, allowing `--language`-filtered malaphor output without breaking the existing generation flow.
- Completed the UI-side language selector so the main Tkinter app can generate within a chosen language while defaulting to all available phrase sets.

### Fixed
- Alpha technical pass, 2026-10-01: preserve existing JSON files on interrupted writes, keep core state unchanged after failed edits/deletions/reordering, protect unreadable saved files, persist deletion undo/redo, preserve metadata and refresh phrase search, and report generation/deletion write failures.
- Prevent duplicate-only generation from hanging and fix tooltip errors when hovering listboxes. Added recovery and regression checks; the isolated Ubuntu/Python 3.14.4 snapshot passed 214 tests and the real-dialog walkthrough. Human usability review and independent developer handoff remain open.
- Reject malformed phrase imports before changing the library; failed import saves leave memory and search unchanged.
- Show desktop import/export outcomes and generation/save errors; CLI generation failures return an error without a traceback.
- Expose favorites export in Manage Favorites and delete the correct favorite when the list is filtered.
- Allow asynchronous batch cancellation between generated entries, including cancellation scheduled on the same event loop.
- Report failed favorites/history writes in the tested generation and favorite workflows instead of claiming success.
- Desktop import/export and phrase add/edit/delete actions now execute their asynchronous operations. Favorites can be exported as JSON or text.
- CLI batch generation now saves its results to history.
- Imports skip duplicates within the incoming file and refresh search results immediately.
- Desktop shutdown stops auto-save and flushes history and favorites. Startup controls now wrap into visible rows.
- Log export works without an asyncio event loop; clearing logs also clears pending messages, and severity labels use brackets.
- Runtime requirements now include only Pillow and the Qt packages used by the app; installation instructions use the actual repository URL.

### Release note
The next pre-alpha development milestone restores desktop import/export and phrase editing, saves CLI batch results to history, and keeps imported phrases searchable without restarting. Favorites support JSON and text export, desktop controls fit the startup window, and shutdown flushes saved state. Installation now uses a focused runtime dependency list.

Validation on 2026-09-30: 135 tests passed on Linux with Python 3.14.4, including real desktop startup, both CLI entry points, file exports, imports, and history/favorites reload. See [release evidence](RELEASE_PROCESS.md#validation-evidence-for-the-next-milestone) and the reviewable regression checks in [test_release_readiness.py](test_release_readiness.py). This note describes the current working tree based on `68feba7`. Developers are testing daily; the published milestone and development gates live in [ROADMAP.md](ROADMAP.md#release-milestones). No tagged release is planned for this checkpoint.

## [2.0.0] - 2026-09-08

### Added
- Initialized the speckit framework with the `.specify/` directory structure.
- Added the project constitution and workflow documentation.

### Changed
- Upgraded the speckit framework to 2.0.0.
- Established the project as a specification-driven workflow with commit
  traceability.

### Notes
- Relevant commits: `4826181`, `487d099`

## [1.0.0] - 2026-09-08

### Added
- Consolidated the versioning guidance into a single canonical repository page.
