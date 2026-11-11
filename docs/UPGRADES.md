# Desktop and reliability upgrades — 2026-11-11

Development version: `0.1.0.dev1` (pre-alpha). This version identifies the installable build; it does not close the human usability/handoff gates or reinterpret historical changelog versions.

## Four views

Generate contains the current result, language, Generate, Copy, Add to Favorites and feedback. Library contains source search, add/edit, import review and phrase export. Favorites and History have their own filters, management dialogs and exports. Advanced holds manual generation, batch work, tags, profiles, gallery/statistics, cleanup and image export. Help remains available from its menu, F1 and the visible header button. Ctrl+Shift+P searches visible and advanced actions; Ctrl+F focuses Library search.

## Shared data and automatic migration

Desktop and CLI resolve the same location, in this order:

1. `--data-dir /absolute/or/relative/path` (relative paths resolve once at startup).
2. `MALIPHORS_INATOR_DATA_DIR`.
3. `${XDG_DATA_HOME:-~/.local/share}/maliphors-inator/data`.

The chosen location appears in the desktop footer and `maliphors-inator-cli --data-path`. A default first launch automatically copies existing data without removing or overwriting source files. It prefers the current Daily Test data directory, then the former-brand Daily Test directory, then the launch working directory, then the bundled resource library. Only the first source containing `malaphors.json` is used. `migration.json` records the source and copied filenames. Existing destinations are not merged automatically. An explicit data-directory override starts with its own contents; import or restore into it when needed.

Migration copies known phrase, history, favorite, rating, template, profile, UI-preference and generation-preference files. It acquires the source session lock and removes newly copied files if migration fails. Close legacy app sessions before the first migration; older versions may not honor the lock. Source files and the installed Daily Test snapshot remain untouched. The Daily Test launcher continues to use its separate sandbox; use the regular app and CLI for the shared main store.

The desktop/CLI entry points hold `.session.lock` for the whole session. A second writer fails with the path in its error message. Embedded direct `MalaphorGenerator` users must coordinate their own session lock. No cloud or cross-computer sync is provided.

## Automatic backup and restore preview

Normal desktop/CLI startup creates a known-state ZIP in `data/backups`, retaining the latest 14 startup backups. The import-review and cleanup workflows also keep pre-change backups. Backups / Restore creates a portable ZIP and lists local snapshots. Preview validates known filenames, schemas, size and checksums before approval, shows which files will change, and states that omitted files remain unchanged.

Restore rechecks the archive fingerprint after approval, creates a safety backup, and replaces only its known files. A failed replacement rolls back already-written files, including malformed original bytes; if rollback itself fails, the error identifies the safety backup. This is an exception-recovery mechanism, not a power-loss multi-file transaction. Keep external backups. Legacy Daily Test archives with known state filenames are accepted without a manifest; new archives include SHA-256 checksums. Restore rejects unknown/duplicate paths and archives over 100 MB uncompressed.

After desktop restore, active collections, search, preferences and feedback reload; undo/redo is cleared. The CLI requires an explicit confirmation flag:

```bash
maliphors-inator-cli --backup saved.zip
maliphors-inator-cli --restore-preview saved.zip
maliphors-inator-cli --restore saved.zip --confirm-restore
```

A session that reports unreadable data should restore a known-good backup before continuing edits. Safety archives may contain damaged originals and can require manual inspection instead of automatic restore.

## Generation feedback

Ratings now save before changing memory. Random generation weights source pairs using saved ratings, excludes avoided ordered pairs and prefers results absent from the latest 20 saved outputs. If the library has no fresh combinations, it may repeat an unblocked result. More Like This prefers pairs sharing an original source with the displayed result, while still preferring fresh output. This is a local heuristic, not semantic AI similarity.

Avoid This Combination persists the displayed ordered pair. Advanced → Manage Avoided Combinations can unblock it. Explicit or advanced generation cannot save an avoided pair until it is unblocked. If every usable pair is blocked, generation reports that more phrases or unblocking is needed. For large libraries the chooser samples a bounded candidate pool rather than allocating every possible pair.

## Import review

Library → Import Malaphors reads phrase-library JSON into a review table with new/duplicate/invalid statuses and inclusion toggles. Select a row to edit its complete JSON object, preserving optional metadata. Save Row Correction revalidates it. Included invalid rows block saving; exclude them or correct them. Exact-original duplicates, including within the incoming file, are skipped.

Apply Reviewed Import reclassifies against the current library, backs up and saves once before changing memory/search. Cancellation during read/validation leaves data unchanged. JSON imports are limited to 25 MB; split larger files. CLI `--preview-import incoming.json` prints statuses without changing the library, while `--import-file` retains the strict all-valid import contract.

## Responsive operations

Import read/apply, cleanup preview/commit, backup inspection/write/restore and batch generation use worker threads. Tk widgets are touched only on the main thread; a queue carries progress and results. Progress dialogs prevent concurrent UI edits. Cancel interrupts between records or before commit; an atomic save already underway finishes safely. Cleanup checks that its reviewed library has not changed. Batch cancellation retains already-saved results and reports the completed count. Closing the app requests cancellation and waits for work before final save.

Some legacy advanced single-result operations and separate Qt utilities remain synchronous. A very large JSON parse, ZIP compression or atomic write is not interruptible midway, but it runs outside the Tk event handler in the upgraded workflows.

## Linux build and optional utilities

Core runtime requirements are Pillow plus OS-provided Tkinter. PyQt5/PyQt6 are optional utilities, installed with `pip install '.[qt-tools]'` or `-r qt-requirements.txt`. Tests separately install their Qt test dependencies. The wheel has `maliphors-inator` and `maliphors-inator-cli` entry points and bundles the phrase library, user guide, changelog, license and Qt UI definitions.

Build the wheel and versioned Linux installer archive:

```bash
python -m pip install build
python scripts/build_linux_release.py
```

If this host lacks `ensurepip`, use the existing system-pip fallback to install `build`, `setuptools>=77` and `wheel` into the chosen environment, then run `python scripts/build_linux_release.py --no-isolation`.

Extract `dist/maliphors-inator-0.1.0.dev1-linux.tar.gz` and run `sh install_linux.sh`. The installer creates a private environment and application-menu entry; it requires Python/Tk, venv or a system pip fallback, and dependency access. It does not bundle a Python interpreter or Qt. Windows/macOS packaging is outside this Linux-first pass. No public release is published automatically.

## GitHub checks

`.github/workflows/ci.yml` runs on pushes, pull requests and manual dispatch. Linux/Python 3.12 and 3.14 jobs install GUI dependencies, run pytest under Xvfb, build the wheel/archive, smoke-test an installed wheel outside the checkout and upload test/package artifacts. A workflow run is evidence only when its actual result is recorded; adding the YAML alone does not prove hosted CI passed.
