# Architecture

maliphors-inator is a pre-alpha Python application with a Tkinter desktop UI, a CLI, and local JSON storage. Developers test it daily; milestone status and gates are maintained in [ROADMAP.md](ROADMAP.md).

## Modules and entry points

| File | Responsibility |
| --- | --- |
| [main.py](main.py) | Starts `MaliphorsInatorApp` with no arguments; delegates arguments to the CLI. |
| [maliphors_inator_ui.py](maliphors_inator_ui.py) | Tkinter controls, dialogs, clipboard, theme, and desktop lifecycle. |
| [maliphors_inator_cli.py](maliphors_inator_cli.py) | Generation, source phrase search, phrase import/export, and output formatting. |
| [maliphors_inator_logic.py](maliphors_inator_logic.py) | `MalaphorGenerator`, `PhraseIndex`, generation, persistence, and undo/redo snapshots. |
| [settings_manager.py](settings_manager.py) | Separate PyQt5 JSON editor using `settings_manager.ui`. |
| [log_manager.py](log_manager.py) | Separate PyQt6 logging window using `log_manager.ui`. |

The settings and log windows have their own script entry points; the main Tkinter app does not launch them. The current checkout contains no Rust/Tauri application directory. Files such as `malaphors.py.old` and `log_manager_ template.py` are historical material, not startup paths.

## Runtime flow

1. Each desktop session or CLI invocation creates its own generator.
2. The generator loads the resolved data directory and builds a phrase search index.
3. User actions call generator methods. Normal single generation/search remain synchronous; import, cleanup, backup and batch workflows use worker threads.
4. `DesktopWorkflows` coordinates a worker, cancellation event and a queue polled by Tk. Workers do not touch widgets. Legacy advanced callbacks still include synchronous/`asyncio.run` paths.
5. The desktop starts a background auto-save thread with a 300-second interval. Leaving the main loop calls `close`, stops auto-save, and flushes history and favorites.

The CLI starts no auto-save thread. Its generation paths save history during the command. `generate_multiple` returns suggestions without saving them itself; the CLI explicitly persists those results.

## Local data

State paths below are resolved under `MalaphorGenerator.data_dir`. Desktop and CLI use the same explicit flag/environment/default resolution in `app_storage.py`. The default is the XDG user data directory; startup copies legacy data once and records its source. Import/export destinations remain user-selected paths. See [upgrade architecture and migration](docs/UPGRADES.md).

| File | Shape and purpose |
| --- | --- |
| `malaphors.json` | Object containing `proverbs`: phrase objects with `original`, `beginning`, and `ending`; optional `language`, `tags`, and `source`. |
| `history.json` | Array of generated records with `malaphor`, `source1`, `source2`, and `timestamp`. The loader also accepts an object containing `history`. |
| `favorites.json` | Object containing `favorites`: an array of strings, which may include displayed source text. |
| `ratings.json` | Saved ratings for source phrase pairs. |
| `generation_templates.json` | Saved generation templates. |
| `settings_profiles.json` | Named settings profiles. |
| `ui_preferences.json` | Desktop preferences, including theme. |

Runtime files are created as the corresponding features are used. History exports wrap records in a `history` object. Phrase JSON exports can be reimported; history and favorites exports are separate formats. The history loader preserves optional generation metadata. Invalid records are excluded from the in-memory view and block overwriting the original history file until recovery and restart.

## Search and state changes

`PhraseIndex` indexes phrase text; `search` caches results and can fall back to substring matching. Imports merge phrases by exact `original` text, skip duplicates, rebuild the index, and clear cached searches. Import validates required text fields and optional language/source/tag types before saving, and updates memory and search only after the save succeeds. Core phrase add/edit/delete/reorder operations also save before updating the active library and refresh search. Editing preserves phrase metadata. Broader cleanup remains a separate feature.

`UndoRedoStack` stores a bounded set of in-memory snapshots for supported deletions. The generator’s undo/redo entry points persist a restored collection before advancing the stack and refresh phrase search. The stack itself is lost on exit; it is not a backup.

## Dependencies and constraints

- Python 3.10+ is the code baseline; the recorded validation environment is Linux/Python 3.14.4.
- Tkinter is imported by the shared logic, so it must be installed for CLI use too. The CLI does not require a display; real desktop windows do.
- [requirements.txt](requirements.txt) lists Pillow for PNG export. [qt-requirements.txt](qt-requirements.txt) optionally installs PyQt5 for settings and PyQt6 for logging. SVG export uses the standard library.
- State is loaded into memory. Normal desktop/CLI entry points hold an exclusive Linux session lock for the chosen directory; embedded generators must arrange their own lock. There is no live cross-process synchronization.
- Generator JSON writes serialize first, write and fsync a temporary sibling file, then atomically replace the destination. A per-generator lock serializes history/favorites updates and auto-save. Invalid phrase/history/favorites/ratings files block overwriting that path for the session; the desktop warns about recovery. This is not a multi-file transaction or a power-loss durability guarantee. Text exports and separate Qt utilities retain their own write behavior. The separate daily-test launcher provides startup backups and a session lock for its own launches; it remains a separate sandbox. Main-store backup/restore is coordinated with the generator persistence lock; manual filesystem restores still require closing all writers.

## Validation

[TESTING.md](TESTING.md) covers logic tests, CLI tests with mocked generators, real Tk widgets with selected mocks, Qt logging tests, and subprocess/file checks in [test_release_readiness.py](test_release_readiness.py). The recorded 2026-09-30 passes progressed from 135 baseline tests to 174 after daily failure-path fixes and 176 after daily-launcher coverage. The 2026-10-01 alpha snapshot passes 214 tests, including backup recovery and failed-write regression coverage. The supported scope is Ubuntu 26.04.1/Python 3.14.4/Tk 8.6.17. Human review and independent developer handoff remain open in the [alpha-readiness checklist](ROADMAP.md#alpha-readiness).

## Alpha architecture review on 2026-10-01

The shared generator owns the core workflows and persistence; Tk and argparse remain separate interfaces. The existing module boundaries and JSON formats can support the declared alpha scope without a major rewrite. The technical review exercised fresh setup, both entry points, file round trips, save failures, and backup restoration; a database or UI-framework migration is not needed for these workflows.

The persistence changes are incremental and retain existing file formats. Remaining limitations are single-writer operation, in-memory loading, UI pauses during file operations, and no all-files transaction. Advanced cleanup, template/profile editing, and separate Qt tools retain narrower validation than the core alpha workflows. Extending scope to concurrent writers, large datasets, or ordinary-user reliability will require further design and testing. This review was performed by the coding agent; independent developer handoff remains open.

## Hub, services and interface adapters

There is no separate ecosystem hub or plugin host in this checkout. Within one process, `MalaphorGenerator` owns the active library and saved collections. The CLI and Tk UI are adapters over that shared service. The standalone Qt tools are independent processes; they do not share a live event bus or generator instance.

The storage is JSON rather than relational tables. History records retain source text, favorites retain displayed strings, and ratings identify source pairs. These are textual associations, not database foreign keys; editing a phrase does not cascade a rename through every collection. The search index is derived state rebuilt after library changes.

## Event communication and extensions

Tk commands and bindings call application methods directly; rendering is refreshed explicitly after successful changes. Background auto-save uses the generator lock. There is no cross-process notification, network synchronization, plugin discovery or dependency injection framework.

New generation/storage behavior should extend the generator and preserve format compatibility. New interfaces should call that service rather than duplicate persistence. New help topics and action mappings belong in `user_assistance.py`; the [assistance standard](docs/USER_ASSISTANCE.md) describes its boundaries. A future plugin system, shared hub or database would need an explicit decision covering lifecycle, ownership, migrations and concurrent writes before implementation.

## Upgrade modules (2026-11-11)

`app_storage.py` owns path resolution, migration, session locks and verified ZIP snapshots/restore. `library_workflows.py` plans cancellable imports and cleanup without writing. `desktop_workflows.py` owns Tk worker/progress/review dialogs. `app_resources.py` locates source or wheel resources; `app_version.py` is the single package-version source. `pyproject.toml` separates core, optional Qt and test dependencies. The Linux CI workflow runs GUI tests under Xvfb and packages/smoke-tests the wheel. The [upgrade guide](docs/UPGRADES.md) records operational limits and migration precedence.
