# Development and Release Process

The project has not reached alpha. Developers test daily, and [ROADMAP.md](ROADMAP.md#release-milestones) is the source for published milestones, gates, and current status. The current checkpoint does not require a public release or version tag.

## Current pre-alpha workflow

1. Choose a scoped improvement or reproduce an issue from daily testing.
2. Make the change and run relevant checks from [TESTING.md](TESTING.md).
3. Review user-visible behavior and update [CHANGELOG.md](CHANGELOG.md), the user guide, and other affected docs.
4. Record the build, environment, results, and unresolved issues in the roadmap.
5. Mark only evidenced gates complete. Automated success does not complete the interactive developer walkthrough or establish alpha readiness.

Use a disposable dataset for destructive testing. Check generation, import/export, history, and favorites, then close and reopen the app to verify persisted state. Keep startup and saved-data issues open until their fixes are verified.

## Documentation gate

Before marking a documentation checkpoint complete:

- Check commands and paths against the actual checkout and entry points.
- Distinguish desktop features from CLI actions and separate utilities.
- Describe current data formats, storage locations, and known limits.
- Keep pre-alpha status and pending manual checks explicit.
- Check relative links, and distinguish runtime-generated files from files already present.

## Alpha readiness review

Use the [stage definitions](alpha.md) and [roadmap checklist](ROADMAP.md#alpha-readiness). Review the core workflows, architecture stability, independent developer handoff, documentation, data risks and recovery, and tests for the declared supported environments. Record the reviewed build, date, reviewer, results, and limitations in the roadmap.

Only declare alpha when all readiness gates are evidenced. As of 2026-10-01, readiness is in progress and the project remains pre-alpha. The technical architecture/data/environment reviews passed later on 2026-10-01; human visual review and independent handoff remain open. See [technical validation](#alpha-technical-validation-on-2026-10-01). Alpha tolerates missing polish and secondary features; beta requires evidence of reliable use by ordinary users.

A stage decision does not itself require a tag or public release. When the decision changes, update README, roadmap, user/testing/architecture/security guides, decisions, contributor guidance, and active specification status together.

## Later alpha or external release

These steps apply when developers decide to prepare an external release:

- [ ] Confirm the intended stage against [alpha.md](alpha.md), complete its readiness gates, and document scope and supported platforms.
- [ ] Resolve issues affecting startup and core data workflows.
- [ ] Validate dependency installation and the full suite on the selected platforms.
- [ ] Complete an interactive walkthrough and record known limitations.
- [ ] Choose a semantic version using [VERSIONING.md](VERSIONING.md).
- [ ] Reconcile package metadata with the release history: `__init__.py` currently says `1.0.0`, while the changelog contains historical `1.0.0` and `2.0.0` documentation/framework entries. Those entries do not establish application alpha status.
- [ ] Review and commit the final scope, changelog, and installation guidance.
- [ ] Record developer approval and select the exact release commit.
- [ ] Create an immutable version tag and publish notes only for that reviewed commit.

If a release candidate is useful, freeze the chosen scope, tag a prerelease of the selected version, and record its trial results before promotion. Fixes during that period need regression checks and updated notes. No RC, trial completion, or public release is implied by the pre-alpha gates.

Current naming and rebranding validation: [REBRANDING.md](REBRANDING.md). The evidence below retains the paths and names used at each original checkpoint.

## Feature freeze and candidate trials

For a release candidate, record the selected scope, version, exact commit, supported environments and reviewer in the roadmap. Freeze feature additions; accept only reviewed fixes, documentation corrections and release blockers. A changed candidate gets a new prerelease identifier rather than moving an existing tag.

Trial the candidate in a clean installation with disposable data, then with backed-up representative data. Exercise first launch, help/tour, generation, search, imports/exports, favorites/history, shutdown/reopen and backup restoration. Record start/end dates, environments, participants, failures and fixes. The maintainer chooses the trial duration and acceptance scope before the trial starts; no default elapsed period counts as approval. Beta additionally requires ordinary-user reliability evidence under the stage definitions.

For every fix, run the affected regression checks; run the full suite and dependency checks for the final candidate. Repeat affected manual workflows. Startup failures, data loss or failed core save/recovery workflows block promotion. Record limitations and unvalidated environments in release notes.

## Release approval record

Before publication, record the version and commit, scope/freeze status, test commands/results, trial evidence, open issues, backup/migration instructions, license/dependency review and approving maintainer/date. The maintainer explicitly approves the reviewed candidate; automated passes alone do not approve a release. Publish the tag and notes for that exact commit, then verify installation from the published artifact. If a regression appears, document its impact and prepare a new reviewed fix release; do not silently replace an existing version.

## Template and user-assistance validation on 2026-11-11

The updated working tree based on `ea55ca8` passed **228 tests in 7.48 seconds** on Linux/Python 3.14.4 using the available Tk display. Command: `.venv/bin/python -m pytest -q -o log_cli=false`. This includes all existing data/CLI/desktop/launcher checks and 11 assistance checks covering first launch/relaunch, saved preferences and failure handling, real guided actions, cancelled import, article/action search, tour resize/cancel/finish, context help, read-only diagnostics, isolated demo cleanup and visible help controls.

Checked 235 local documentation/image targets and `git diff --check`; both passed. Captured and inspected main/help screenshots using disposable data. Test log: `/tmp/maliphors-template-tests.log` (temporary). Personal and installed daily-test datasets were not replaced. The installer now bundles help, but the user's installed snapshot has not been updated by this pass. Human usability review and independent handoff remain open; no release or stage promotion is implied.

## Validation evidence for the next milestone

Validated on 2026-09-30 against the working tree based on commit `68feba7`.

- Environment: Linux, Python 3.14.4, Tk with the available desktop display, PyQt6 6.11.0, Pillow 12.3.0, pytest 9.1.1.
- A disposable environment at `/tmp/malaphors-release-venv` successfully installed `requirements.txt` and `test-requirements.txt`. The previous requirements failed while building unrelated lxml; runtime requirements now match application imports.
- Command: `/tmp/malaphors-release-venv/bin/python -m pytest -q`.
- Result: **135 passed**, including the new `test_release_readiness.py` checks.
- Desktop: real Tk startup through `main.py`, visible action buttons, generation, favorites, JSON/text exports, duplicate-safe phrase import, refreshed search, event-loop shutdown, stopped auto-save, and persisted state reload.
- CLI: subprocess checks for both `main.py` and `malaphor_cli.py`, help, batch and smart generation, search, JSON/text export, import, duplicate-only exit status, and saved generation history.
- Test data lives in temporary directories; the repository’s phrase library, history, and favorites were preserved.

The milestone note and development gates are published in [ROADMAP.md](ROADMAP.md#release-milestones), with user-visible changes in [CHANGELOG.md](CHANGELOG.md#release-note). These are automated checks with real widgets and files; interactive visual review on Windows/macOS and a user trial period have not been completed. Large file operations invoked through desktop callbacks can briefly block the UI while they finish.

For a later alpha or external release, choose the milestone version, reconcile `__init__.py` (currently `1.0.0`) with the release history, review and commit the working tree, and complete the applicable publication checklist above. An RC trial is optional; beta user trials are a separate stage gate. No release tag or GitHub release has been created.

## Daily testing pass on 2026-09-30

The working tree based on `68feba7`, with the daily failure-path fixes, passed **174 tests** on Linux/Python 3.14.4:

```bash
/tmp/malaphors-release-venv/bin/python -m pytest -q
/tmp/malaphors-release-venv/bin/python scripts/desktop_walkthrough.py
```

The real-dialog walkthrough also passed: generate, add favorite, import, cancel import, export originals/history/favorites in JSON and text, confirm exit, and reopen with saved history/favorites and imported phrases. Its temporary evidence directory for this run was `/tmp/malaphors-daily-walkthrough-92vm9a3k`; temporary artifacts may be removed by the system, while the scripts and regression tests remain in the repository.

The new tests reproduce malformed input, read-only/invalid destinations, state preservation, cancellation, filtered deletion, and error feedback. The full pytest log for this local run is `/tmp/malaphors-daily-full.log`. No production dataset was modified. Screenshot capture was unavailable on the compositor; human visual/usability review remains open. This completes the recorded automated and scripted daily gates in [ROADMAP.md](ROADMAP.md#release-milestones), without advancing the project to alpha.

## Daily launcher checkpoint on 2026-09-30

The [roadmap installation record](ROADMAP.md#daily-test-installation-on-this-laptop) records **176 full-suite tests passed** after launcher coverage, including startup, data preservation, backups, and the session lock. This follows the 135-test baseline and 174-test daily failure-path pass above. The 2026-10-01 stage-definition update is documentation work and does not claim a new runtime test pass.

## Alpha technical validation on 2026-10-01

**Outcome: technical gates passed; application remains pre-alpha pending human usability review and independent developer handoff.**

- Build: working tree based on `68feba7`, including the alpha persistence/UI fixes; no commit/tag created. [Manifest](docs/alpha-validation-2026-10-01.json) fingerprint: `8822c84f51fe10a229993e72414983265d27ca05581c640e0ed5138f05926078`.
- Initial supported alpha environment: Ubuntu 26.04.1 LTS, Python 3.14.4, Tk 8.6.17, XWayland display `:0`. Qt tests used the configured offscreen backend. Other OS/Python configurations are unvalidated.
- Fresh dependency environment: `/tmp/malaphors-alpha-venv`. Standard venv creation exposed missing `ensurepip`; the README now documents the tested system-pip fallback. Installing both requirements files and `python -m pip check` passed.
- Isolated source snapshot: `/tmp/malaphors-alpha-review-yk30s4ae`, copied from tracked and untracked non-ignored working-tree files. This is a snapshot of the uncommitted build, not a clean checkout of `68feba7`.
- Full suite in that snapshot: **214 passed in 7.75 seconds**. Command: `/tmp/malaphors-alpha-venv/bin/python -m pytest -q -o log_cli=false`.
- Real-dialog walkthrough: passed generation, favorites, import, cancellation, six JSON/text exports, exit and reopen. Command: `/tmp/malaphors-alpha-venv/bin/python scripts/desktop_walkthrough.py`. Screenshot capture still failed on this display and provides no visual-review evidence.
- Data recovery: ordinary JSON backup/restore and daily-launcher ZIP restoration passed, including reopening with the saved library, history, and favorites. Tests use temporary data.
- Architecture review: shared generator, UI/CLI boundaries, and JSON storage support the core alpha scope without a major rewrite; remaining constraints are in [ARCHITECTURE.md](ARCHITECTURE.md#alpha-architecture-review-on-2026-10-01).
- Handoff rehearsal: the coding agent located the CLI parser, changed its help description in the isolated copy, verified both entry points, and restored the original source. An independent developer has not yet performed the required handoff.

Reproduced issues fixed: interrupted JSON writes could damage the destination; failed phrase edits/deletions/reordering could leave memory changed; history/favorite deletion and several generation modes ignored failed saves; undo/redo did not persist restored collections; malformed saved data could be overwritten; duplicate-only libraries could loop indefinitely; hovering a listbox could raise a tooltip error. Core phrase edits now preserve metadata and refresh search, and history reload retains generation metadata.

Temporary logs: `/tmp/malaphors-alpha-snapshot-tests.log`, `/tmp/malaphors-alpha-snapshot-install.log`, and `/tmp/malaphors-alpha-snapshot-walkthrough.log`. These may be removed by the system; the manifest, tests, and this summary are retained in the repository. The manifest hashes Python source/test files, the bundled phrase library, requirements, and pytest configuration; its fingerprint is SHA-256 of the sorted JSON file-hash mapping.

The installed daily-test snapshot and repository user-data files were not replaced. Use the reviewed source build for the remaining human reviews. After those pass and any findings are fixed/revalidated, record the alpha decision in the roadmap and synchronize the active status documents.
