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
2. The generator loads data from the current working directory and builds a phrase search index.
3. User actions call generator methods. Generation and search run synchronously; file helpers include async methods.
4. Tk callbacks run async file helpers with `asyncio.run`. This completes the operation before returning to Tk, so large file operations can pause the interface.
5. The desktop starts a background auto-save thread with a 300-second interval. Leaving the main loop calls `close`, stops auto-save, and flushes history and favorites.

The CLI starts no auto-save thread. Its generation paths save history during the command. `generate_multiple` returns suggestions without saving them itself; the CLI explicitly persists those results.

## Local data

All paths below are relative to the **current working directory**. Run from the repository root to use the bundled phrase library. Export destinations are chosen by the user.

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
- [requirements.txt](requirements.txt) lists Pillow for PNG export, PyQt5 for settings, and PyQt6 for logging. SVG export uses the standard library.
- State is loaded into memory. Separate app/CLI processes do not synchronize changes or lock files.
- Generator JSON writes serialize first, write and fsync a temporary sibling file, then atomically replace the destination. A per-generator lock serializes history/favorites updates and auto-save. Invalid phrase/history/favorites/ratings files block overwriting that path for the session; the desktop warns about recovery. This is not a multi-file transaction or a power-loss durability guarantee. Text exports and separate Qt utilities retain their own write behavior. The separate daily-test launcher provides startup backups and a session lock for its own launches; it does not synchronize other app/CLI writers. Avoid simultaneous writers and close the app before restoring data.

## Validation

[TESTING.md](TESTING.md) covers logic tests, CLI tests with mocked generators, real Tk widgets with selected mocks, Qt logging tests, and subprocess/file checks in [test_release_readiness.py](test_release_readiness.py). The recorded 2026-09-30 passes progressed from 135 baseline tests to 174 after daily failure-path fixes and 176 after daily-launcher coverage. The 2026-10-01 alpha snapshot passes 214 tests, including backup recovery and failed-write regression coverage. The supported scope is Ubuntu 26.04.1/Python 3.14.4/Tk 8.6.17. Human review and independent developer handoff remain open in the [alpha-readiness checklist](ROADMAP.md#alpha-readiness).

## Alpha architecture review on 2026-10-01

The shared generator owns the core workflows and persistence; Tk and argparse remain separate interfaces. The existing module boundaries and JSON formats can support the declared alpha scope without a major rewrite. The technical review exercised fresh setup, both entry points, file round trips, save failures, and backup restoration; a database or UI-framework migration is not needed for these workflows.

The persistence changes are incremental and retain existing file formats. Remaining limitations are single-writer operation, in-memory loading, UI pauses during file operations, and no all-files transaction. Advanced cleanup, template/profile editing, and separate Qt tools retain narrower validation than the core alpha workflows. Extending scope to concurrent writers, large datasets, or ordinary-user reliability will require further design and testing. This review was performed by the coding agent; independent developer handoff remains open.
