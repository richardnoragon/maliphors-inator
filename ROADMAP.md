# Roadmap

This roadmap publishes the milestones and gates for maliphors-inator’s pre-alpha development. Current work focuses on daily developer testing, core workflow stability, and accurate documentation.

## Rebranding on 2026-10-10

Current identity: **maliphors-inator**, previously known as malaphors-rs and Malaphors-inator. The [rebranding record](REBRANDING.md) tracks implementation, GitHub, workspace, daily-test migration, and validation. Dated installation and validation records below describe their original snapshots; current launch instructions are in [USER_GUIDE.md](USER_GUIDE.md).

## Current direction

**Status as of 2026-10-01: pre-alpha; technical alpha checks passed, human reviews pending.** The reviewed snapshot passes 214 tests and the real-dialog walkthrough. Architecture, saved-data risks, backup recovery, and the initial supported environment have been reviewed. Alpha still requires the human desktop walkthrough and independent developer handoff under the [stage definitions](alpha.md).

This file is the current source for milestone status and development gates. Supporting implementation planning lives in [.specify/features/improvements-roadmap/plan.md](.specify/features/improvements-roadmap/plan.md); versioning policy and user-visible changes live in [VERSIONING.md](VERSIONING.md) and [CHANGELOG.md](CHANGELOG.md).

## Near-term priorities

### 1. Pre-alpha readiness

- [x] Validate the desktop startup path with real Tk widgets and `main.py` smoke coverage.
- [x] Confirm both CLI entry points and documented generation, search, import, and export commands.
- [x] Verify generation, JSON/text export, phrase import, history, and favorites using real files and reload checks.
- [x] Update the changelog with user-visible fixes.
- [x] Publish the next milestone note and development gates below; record user-visible fixes in [CHANGELOG.md](CHANGELOG.md).

Validated on 2026-09-30: **135 tests passed** in a disposable Linux/Python 3.14.4 environment. See [validation evidence](RELEASE_PROCESS.md#validation-evidence-for-the-next-milestone). This is a pre-alpha development checkpoint. Public release publication and version tagging are outside this milestone.

### 2. Documentation alignment

- [x] Synchronize [README.md](README.md) with desktop features, CLI scope, and separate utilities.
- [x] Align installation and usage instructions with the Python files present in this checkout.
- [x] Maintain [ARCHITECTURE.md](ARCHITECTURE.md), [TESTING.md](TESTING.md), [SECURITY.md](SECURITY.md), [USER_GUIDE.md](USER_GUIDE.md), and [RELEASE_PROCESS.md](RELEASE_PROCESS.md).
- [x] Remove stale implementation claims and document the active pre-alpha app under daily developer testing.

Documentation checkpoint, 2026-09-30: reviewed entry points, dependencies, storage, and test configuration; checked 88 local documentation links and eight CLI examples in a temporary data directory. Corrected references to an absent Rust/Tauri directory and documented CLI limits, import formats, separate Qt tools, and backup behavior. At that checkpoint no private reporting channel was planned; the current private contact is now published in [SECURITY.md](SECURITY.md).

Ongoing gate: update affected docs and the changelog whenever behavior changes. These completed documentation checks do not close the interactive testing or alpha-readiness gates below.

### 3. Runtime stability

- preserve the current local JSON-backed persistence model
- keep auto-save, history, and favorites handling resilient
- maintain stable search and import/export behavior
- verify the generator continues to handle common user workflows without regressions

## Template and assistance implementation — 2026-11-11

- [x] Apply the document outlines, add FAQ/conduct/index/license reference, and publish the [coverage map](docs/TEMPLATE_COVERAGE.md).
- [x] Add offline onboarding, isolated demo, control tour, guided tasks, article search, F1 context help, troubleshooting and action search; document the [assistance standard](docs/USER_ASSISTANCE.md).
- [x] Bundle help with daily snapshots and add real-widget/lifecycle regression checks. Full suite: 228 passed in 7.48 seconds on Linux/Python 3.14.4; 235 local doc/image targets resolve; screenshots captured and inspected using disposable data.
- [ ] Complete human acceptance of the assistance workflows and incorporate findings into the open usability gate.

This pass does not declare alpha or replace the dated technical evidence below. Remote AI help remains an optional future design requiring a provider/data-handling decision.

## Release milestones

### Pre-alpha milestone 1 — Core workflow baseline

**Status: automated gate passed on 2026-09-30; daily developer testing continues.**

Milestone note: Desktop import/export and phrase editing now execute correctly, CLI batch output is saved to history, imported phrases appear in search immediately, and favorites export supports JSON and text. Startup controls fit the window, shutdown flushes saved state, and installation uses the app’s runtime dependencies. At this initial checkpoint, the full suite passed 135 tests on Linux/Python 3.14.4; later passes are recorded below.

Gates:

- [x] Install runtime and test dependencies in a disposable environment.
- [x] Pass the full automated suite, including real desktop startup and both CLI entry points.
- [x] Verify generation, import/export, history, and favorites with real files and reload checks.
- [x] Record user-visible changes and test evidence.
- [ ] Complete a developer’s interactive walkthrough of the updated window, dialogs, and saved data during daily testing.

Evidence: [release regression tests](test_release_readiness.py), [validation record](RELEASE_PROCESS.md#validation-evidence-for-the-next-milestone), and [changelog](CHANGELOG.md).

### Pre-alpha milestone 2 — Daily testing and fixes

**Status: this development pass completed; daily testing continues. The project remains pre-alpha.**

For each daily testing pass, record the date, commit or working-tree description, environment, result, and any reproducible issue below. Fix failures affecting startup or saved data before advancing the baseline.

Gates for the 2026-09-30 pass:

- [x] Drive the real desktop controls and file dialogs: generate, favorite, import, export originals/history/favorites as JSON and text, exit, and reopen to verify saved data. Completed with scripted Tk interaction; file pickers and message boxes were not mocked.
- [x] Check cancellation and failure paths: cancelled file pickers and favorite deletion, batch/event/task cancellation, malformed imports, read-only files, and invalid export destinations.
- [x] Fix reproduced issues and add regression coverage for library integrity, user-visible errors, cancellation, and filtered favorite deletion.
- [x] Run the full suite after fixes and update the changelog: **174 tests passed**.

Remaining review: a developer’s visual/usability check. Screenshot capture failed on the available display, so the scripted walkthrough does not establish visual quality or replace human feedback. This is also the remaining interactive review gate in milestone 1.

| Date | Build | Environment | Result | Follow-up |
| --- | --- | --- | --- | --- |
| 2026-09-30 | Baseline working tree based on `68feba7` | Linux, Python 3.14.4 | 135 automated tests passed; dependency check passed | Followed by the daily pass below |
| 2026-09-30 | Working tree based on `68feba7`, with daily failure-path fixes | Linux, Python 3.14.4, Tk display `:0` | 174 tests passed; real-dialog walkthrough passed, including six exports and reload | Visual/usability review remains open; repeat daily checks after changes |
| 2026-10-01 | Working tree based on `68feba7`; validation fingerprint `8822c84f51fe` | Ubuntu 26.04.1, Python 3.14.4, Tk 8.6.17, display `:0` | 214 tests passed in an isolated snapshot; dependency check, real-dialog walkthrough, and backup recovery passed | Human usability review and independent developer handoff remain open |

Reproducible findings fixed in this pass:

- Malformed imports were accepted, and failed saves could leave the active library changed. Imports now validate records before saving and update memory/search only after a successful save.
- Import/export failures and unavailable languages lacked usable desktop feedback. Dialogs now report outcomes; CLI generation failures return a readable error and exit code 1.
- Favorites export had no visible control. Manage Favorites now exposes it.
- Deleting a filtered favorite could remove the wrong entry. Selection now maps to the original index; cancellation preserves data.
- Async batch generation did not yield between entries, delaying cancellation scheduled on the same event loop. It now checks between entries.
- Favorites and generation could report success after persistence failed. The tested desktop and CLI paths now report failed writes.

Evidence and reproduction: [failure regression tests](test_daily_testing.py), [real-dialog walkthrough](scripts/desktop_walkthrough.py), and [daily validation record](RELEASE_PROCESS.md#daily-testing-pass-on-2026-09-30). All runs used temporary data; repository phrase/history/favorites files were preserved.

### Daily test installation on this laptop

**Installed: `20260930-8b9bffc8b7` — pre-alpha snapshot.**

Launch **Malaphors-inator Daily Test** from the application menu or desktop shortcut. Its dedicated Python environment and application snapshot live under `~/.local/share/malaphors-inator-daily`; saved data lives in its `data` directory. The launcher keeps 14 startup backups and prevents simultaneous daily-test writers.

- [x] Install a snapshot and a dedicated runtime environment outside the checkout.
- [x] Add application-menu and desktop launchers.
- [x] Verify startup, data preservation across launches, startup backups, and the session lock; full suite: **176 tests passed**.
- [x] Document daily use and updating in [USER_GUIDE.md](USER_GUIDE.md#daily-test-version-on-this-laptop).

Update after closing the app with `python3 scripts/install_daily_test.py`. Updating the code does not replace saved daily-test data. This installation does not change alpha-readiness or human visual-review gates.

### Alpha readiness

**Status: technical gates passed on 2026-10-01; human reviews pending. Alpha has not been declared. No release version or date selected.**

The [alpha checklist](alpha.md#alpha-checklist) applies to the Python/Tkinter app and CLI: generation, source phrase search/import/export, desktop history/favorites, and saved-state reload. Additional enhancement backlog items and separate Qt utilities do not expand this core scope automatically.

**Initial supported alpha environment:** Linux on Ubuntu 26.04.1 LTS, Python 3.14.4, Tk 8.6.17, with an available X11/XWayland display for the desktop. Windows, macOS, other Python versions, and other Linux configurations remain unvalidated. Python 3.10+ describes the code baseline, not a tested compatibility promise.

| Criterion | Current evidence | Remaining gate |
| --- | --- | --- |
| Core purpose and integrated workflows | 214 tests and the real-dialog walkthrough passed on the reviewed snapshot. Reproduced persistence and tooltip failures fixed. | Human visual/usability walkthrough. |
| Stable architecture | [Architecture review](ARCHITECTURE.md#alpha-architecture-review-on-2026-10-01): shared generator, UI/CLI boundaries, and local JSON support the core scope without a major rewrite. | Complete for the declared scope. |
| Developer handoff | Fresh dependency environment, isolated source snapshot, both entry points, full suite, and a small CLI change rehearsal passed. | A different developer must follow the guides and demonstrate a small change without author assistance. The agent rehearsal does not establish independence. |
| Understood data risks | Atomic JSON replacement, failed-change rollback, unreadable-file protection, persistent undo/redo, manual backup restoration, and daily ZIP recovery tested. [Remaining limits](ARCHITECTURE.md#dependencies-and-constraints) are documented. | Complete technical risk review; keep to one writer per data directory. |
| Sufficient documentation | Setup fallback, supported environment, recovery instructions, architecture, and handoff procedure updated. | Fix any gaps found by the independent reviewer. |
| Major workflow testing | 214 tests passed on Ubuntu/Python/Tk above; dependency check and actual file dialogs passed. | Complete for the declared environment; rerun after code changes. |

Completion checklist:

- [x] Implement the core purpose and provide integrated workflow regression coverage.
- [x] Document architecture, setup, usage, testing, and the development roadmap.
- [ ] Complete the developer visual/usability walkthrough already open in milestones 1 and 2.
- [ ] Record independent developer handoff using [TESTING.md](TESTING.md#developer-handoff-check), and resolve any documentation gaps it finds.
- [x] Review architecture stability, data-loss risks, and backup/restore for the alpha scope.
- [x] Declare the initial supported OS/Python environment and validate startup and core flows there.
- [x] Fix reproduced core workflow and saved-data failures and review the technical evidence.
- [ ] After both human reviews pass, record the alpha decision and reviewed build here; synchronize status across active documentation.

Evidence: [2026-10-01 validation record](RELEASE_PROCESS.md#alpha-technical-validation-on-2026-10-01), [source fingerprint manifest](docs/alpha-validation-2026-10-01.json), [alpha regression tests](test_alpha_readiness.py), and [daily-launcher recovery test](test_daily_launcher.py). The reviewed working-tree fingerprint is `8822c84f51fe10a229993e72414983265d27ca05581c640e0ed5138f05926078`; no commit or tag was created.

Alpha readiness does not require publishing a tag. Version selection, metadata reconciliation, and publication follow [RELEASE_PROCESS.md](RELEASE_PROCESS.md#later-alpha-or-external-release). The previously installed daily-test snapshot remains unchanged; use the reviewed source build for the remaining reviews.

### Beta and stable release — Future checkpoints

Beta requires representative ordinary-user trials demonstrating reliable real use, with data loss and primary workflow failures exceptional. A stable release requires the declared scope, supported environments, validation, and documented limitations to pass review. Neither checkpoint has been demonstrated or scheduled; see [stage definitions](alpha.md).

## Longer-term directions

These are candidate areas for future work, but they should stay subordinate to stability and maintainability:

- richer browsing and review experiences for generated malaphors
- stronger validation around external data imports
- additional quality-of-life controls in the desktop UI
- packaging and distribution improvements if the project expands beyond local development use

## Roadmap principles

- Keep the app local-first unless there is a strong reason to change the storage model.
- Prefer incremental improvements over broad rewrites.
- Treat documentation, release notes, and versioning as part of the product, not afterthoughts.
- Preserve internal module names unless a migration is explicitly planned.
- Validate release claims against the actual workspace state before publishing them.

## Checkpoints

Before moving a milestone forward, confirm that:

- the current version scope is documented
- release notes are up to date
- the user guide matches the supported workflows
- the tests or manual checks for the release scope have been completed
- no stale planning language remains in top-level docs

## Related files

- [README.md](README.md)
- [CHANGELOG.md](CHANGELOG.md)
- [VERSIONING.md](VERSIONING.md)
- [RELEASE_PROCESS.md](RELEASE_PROCESS.md)
- [.specify/features/improvements-roadmap/plan.md](.specify/features/improvements-roadmap/plan.md)
