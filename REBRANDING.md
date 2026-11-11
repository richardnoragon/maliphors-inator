# maliphors-inator rebranding record

On 2026-10-10, the project adopted **maliphors-inator** across its current product identity, GitHub repository, local workspace, runtime modules, and daily-test installation. It was previously known as **malaphors-rs** and publicly branded **Malaphors-inator**. The new spelling uses **maliphors**, with an **i**.

The rebrand does not change the development stage: the application remains pre-alpha, with human usability review and independent developer handoff still pending. Existing uncommitted development work was retained. No commit, tag, release, or source push was made as part of this change.

## Passes and completion

| Pass | Scope | Result |
| --- | --- | --- |
| 1. Inventory and preservation | Identify current branding, historical evidence, data, and existing edits | Complete; a pre-change working-file backup was captured and historical content compared afterward. |
| 2. Current product and internals | Rename runtime modules, GUI class, logging identity, imports, tests, current guides, and specification metadata | Complete; CLI and desktop entry points use the new modules. |
| 3. Repository and workspace | Rename GitHub repository, refresh its description and origin URL, rename checkout and editor workspace | Complete; GitHub identity was read back and verified. |
| 4. Daily installation and verification | Install a renamed snapshot, preserve saved data, validate launchers and workflows, record evidence | Complete; 217 tests, real-dialog walkthrough, and installed smoke test passed. |

## Current naming

| Surface | Current name | Previous name |
| --- | --- | --- |
| Product and window title | `maliphors-inator` | `Malaphors-inator` |
| GitHub repository | [richardnoragon/maliphors-inator](https://github.com/richardnoragon/maliphors-inator) | `richardnoragon/malaphors-rs` |
| Checkout directory | `Projects/maliphors-inator` | `Projects/malaphors-rs` |
| Editor workspace | `maliphors-inator.code-workspace` | `malaphors-rs.code-workspace` |
| CLI module | `maliphors_inator_cli.py` | `malaphor_cli.py` |
| Logic module | `maliphors_inator_logic.py` | `malaphor_logic.py` |
| UI module | `maliphors_inator_ui.py` | `malaphor_ui.py` |
| GUI application class | `MaliphorsInatorApp` | `MalaphorApp` |
| Logic and UI tests | `test_maliphors_inator_logic.py`, `test_maliphors_inator_ui.py` | `test_malaphor_logic.py`, `test_malaphor_ui.py` |
| Logger | `maliphors_inator` | `malaphor_logger` |
| New exported logs | `maliphors_inator_log_<timestamp>.txt` | `malaphor_log_<timestamp>.txt` |
| Daily-test application | `maliphors-inator Daily Test` | `Malaphors-inator Daily Test` |
| Daily installation and desktop entry | `maliphors-inator-daily` | `malaphors-inator-daily` |
| Daily data override | `MALIPHORS_INATOR_DAILY_DATA_DIR` | `MALAPHOR_DAILY_DATA_DIR` |
| Test environment flag | `MALIPHORS_INATOR_TEST_MODE` | `MALAPHOR_TEST_MODE` |

Hyphens identify the product and repository; underscores make Python module names valid identifiers. `main.py` remains the entry point. The old runtime modules and GUI class are no longer exported; external scripts must update their imports using this table. For example:

```python
from maliphors_inator_logic import MalaphorGenerator
from maliphors_inator_ui import MaliphorsInatorApp
```

## Workspace and contributor migration

Open `maliphors-inator.code-workspace` from the renamed checkout. On this laptop, the old checkout path is a compatibility symlink to the new directory so existing editor tabs and virtual-environment paths continue to resolve. Keep that link until any tools and environments referencing the old absolute path have been reconfigured or recreated.

The local origin is now `https://github.com/richardnoragon/maliphors-inator.git`. Other existing clones can update their origin with:

```bash
git remote set-url origin https://github.com/richardnoragon/maliphors-inator.git
```

Run the application and tests from the new checkout:

```bash
python main.py
python maliphors_inator_cli.py --help
python -m pytest
```

Use an environment with the dependencies from `requirements.txt` and `test-requirements.txt`, and an available display for the full test suite. The source changes remain local until reviewed and committed/pushed; renaming the GitHub repository does not publish these working-tree changes.

## Daily-test migration

The renamed installation lives at `~/.local/share/maliphors-inator-daily`, with application-menu and desktop entries named `maliphors-inator-daily.desktop`. The installed rebranded snapshot is `20261010-241a18bcfc`. Old desktop entry points were retired after the replacement entry validated.

When an old daily installation exists and the new destination has no data, the installer links the new `data` directory to `~/.local/share/malaphors-inator-daily/data`. Both builds therefore use the same saved files and session lock. Existing favorites, history, phrase libraries, backups, and logs are retained. **Keep the legacy data directory:** the new installation uses it through this link. Historical build snapshots and their metadata remain unchanged.

For a fresh installation, data is created under the new installation directory. If the destination already has its own data, the installer preserves it without merging or overwriting either collection. The legacy `MALAPHOR_DAILY_DATA_DIR` environment variable remains a fallback; `MALIPHORS_INATOR_DAILY_DATA_DIR` takes precedence.

Future updates use `python3 scripts/install_daily_test.py` after closing the application. The installer builds a separate snapshot and environment; it does not replace saved data.

## Historical records and domain terminology

Old release entries, dated roadmap and release evidence, the 2026-10-01 validation manifest, completed-task descriptions, implementation summaries, and `malaphors.py.old` retain their original names. `DECISIONS.md` records the new naming decision above the preserved earlier decisions. Historical links and paths describe the files as they were at those checkpoints; use the mapping above for today's equivalents.

The existing `CHANGELOG.md` entries remain intact, with a new rebranding entry added. Current guides, active specification text, backlog repository metadata, and executable examples use the new identity. Git history, tags, GitHub issue discussions, and historical release records were not rewritten.

“Malaphor” still names the kind of content the application creates. Domain identifiers such as `MalaphorGenerator`, `generate_malaphor`, and JSON `malaphor` fields remain appropriate. Data filenames including `malaphors.json`, `newmalaphors.json`, `history.json`, and `favorites.json` remain stable to preserve data compatibility. Generic utility names such as `log_manager.py` and `settings_manager.py` remain descriptive.

## Validation on 2026-10-10

- Full regression suite: **217 passed**, including renamed module imports, CLI flows, GUI title, data persistence, and three new daily-data migration checks.
- Real desktop walkthrough: passed buttons, file dialogs, import cancellation, six exports, exit, and reopen using temporary data. Screenshot capture was unavailable on this display; this is workflow evidence, not human visual approval.
- Installed daily snapshot: smoke test passed using temporary data. The new data path resolves to the original daily data directory; existing daily files were hashed before and after this check and remained unchanged.
- Historical comparison: preserved summaries, old source, dated validation manifest, tracked datasets, and historical sections matched the pre-rebrand working-file backup.
- GitHub repository name and description, local origin, new checkout location, workspace file, and installed desktop entry were verified.

The first test attempt found missing Pillow and async-test support in the local environment. Installing the declared dependencies resolved those five failures; the subsequent full suite passed.

Local recovery and evidence files are temporary and may be cleaned by the system: pre-change working-file backup `/tmp/rebrand-before-xdor6jmg`; test log `/tmp/maliphors-inator-tests.log`; dependency log `/tmp/maliphors-inator-dependencies.log`; installation log `/tmp/maliphors-inator-install.log`; desktop walkthrough log `/tmp/maliphors-inator-walkthrough.log`. The backup covers tracked and non-ignored untracked working files, not Git history or ignored environments/data. This record and the regression tests provide the durable rebranding evidence.
