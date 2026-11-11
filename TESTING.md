# Testing Guide

The project is pre-alpha. Automated regression checks support daily developer testing; passing them does not establish alpha readiness. Record milestone gates and daily results in [ROADMAP.md](ROADMAP.md#release-milestones).

## Install and run

Follow the virtual environment setup in [README.md](README.md#installation), then install the test dependencies from the repository root:

```bash
python -m pip install -r requirements.txt -r test-requirements.txt
python -m pytest
```

Use `python -m pytest` to select the active environment explicitly. Tkinter must be installed through your Python distribution or operating system. PyQt6 is required during test collection because `conftest.py` imports it.

The full suite needs a graphical display for Tk tests. On headless Linux with Xvfb installed:

```bash
xvfb-run -a python -m pytest
```

Qt's offscreen setting does not provide a Tk display. GUI markers are not exhaustive: the desktop entry-point subprocess test also starts Tk. Selecting `-m 'not gui'` does not guarantee a display-free run.

## Developer handoff check

This is an open [alpha-readiness gate](ROADMAP.md#alpha-readiness). A developer other than the original author should:

1. Start from a clean checkout of the reviewed build and follow the README to install dependencies.
2. Run both the desktop app and CLI, then run the test suite using this guide.
3. Use temporary data to generate, search, import/export, favorite, close, and reopen; inspect the actual controls and dialogs for usability.
4. Follow the [backup guidance](USER_GUIDE.md#files-and-backups) to back up and restore temporary data, then verify the restored content.
5. Use the architecture and contribution guides to locate a behavior, make a small change, and validate it without direct author assistance.
6. Record the date, build, OS/Python/display environment, reviewer, commands/results, documentation gaps, and reproducible issues in the roadmap. Fix gaps and repeat affected checks before marking handoff complete.

A scripted dialog walkthrough provides workflow evidence; the independent developer must still assess usability and whether the documentation is sufficient to continue development.

## Focused checks

```bash
python -m pytest test_maliphors_inator_logic.py test_cli.py
python -m pytest test_maliphors_inator_ui.py test_logging.py test_release_readiness.py
python -m pytest test_release_readiness.py
```

The first command covers logic and CLI unit tests without opening windows. Prefer these pytest commands over the legacy `run_tests.ps1` and `run_tests.bat` wrappers; the wrappers run selected files and do not discover the current full suite.

## Coverage and isolation

| File | Checks |
| --- | --- |
| [test_maliphors_inator_logic.py](test_maliphors_inator_logic.py) | Generation, search, metadata, persistence, import/export, and other generator features. |
| [test_cli.py](test_cli.py) | CLI routing and formatting with a mocked generator. |
| [test_maliphors_inator_ui.py](test_maliphors_inator_ui.py) | Real Tk widgets with selected generator/dialog mocks, plus persistence checks. |
| [test_logging.py](test_logging.py) | Qt log display, formatting, clear, and export. |
| [test_release_readiness.py](test_release_readiness.py) | Both CLI entry points in subprocesses, real desktop startup, visible buttons, file import/export, shutdown, and state reload. |

`conftest.py` changes into a temporary directory for each test. Release checks copy the bundled phrase library there, keeping repository history and favorites unchanged. Tests use real local files; file pickers and informational dialogs are mocked where interaction would block automation.

The suite does not establish full coverage of every dialog, all malformed inputs, concurrent writers, or every operating system. The standalone PyQt5 settings editor has no dedicated test module.

## Daily developer pass

1. Back up data with the app closed, or use a disposable copy of the checkout.
2. Start `python main.py`, generate a result, and save a favorite.
3. Import a valid phrase JSON file and verify that its contents appear in search.
4. Export originals, generated history, and favorites as JSON and text; inspect the files.
5. Close and reopen the app to check history and favorites.
6. Record the build, environment, result, and reproducible issues in the roadmap's daily testing table.

Run relevant automated checks after fixes and the full suite before advancing a milestone. Keep failures affecting startup or saved data open until verified.

## Recorded baseline

On 2026-09-30, the working tree based on `68feba7` passed **135 tests** in a disposable Linux/Python 3.14.4 environment. Runtime and test dependency installation and `pip check` also passed. See [validation evidence](RELEASE_PROCESS.md#validation-evidence-for-the-next-milestone).

This is a dated result for that working tree, not a claim that subsequent changes or untested platforms pass.

## Daily failure checks and real-dialog walkthrough

The 2026-09-30 daily pass passed **174 tests**, including [test_daily_testing.py](test_daily_testing.py). Those checks cover malformed imports, unchanged state after failed saves, read-only export targets, cancelled file dialogs and deletion, async cancellation, and desktop/CLI error feedback. Permission checks require a non-root POSIX user and skip where those semantics are unavailable.

To drive actual Linux/Tk buttons, file pickers, and message boxes in a graphical session:

```bash
python scripts/desktop_walkthrough.py
```

The script creates a temporary data directory and prints its location. It verifies generation, favorites, import, cancelled import, six JSON/text exports, exit, and reopen. It attempts to save a screenshot there; an unsupported compositor can prevent capture while functional checks still pass. It uses Linux/Tk dialog widget names and is separate from portable pytest checks. It is scripted interaction, not a human usability review.

## Daily launcher checks

`test_daily_launcher.py` checks first-launch seeding, preserving saved data on relaunch, ZIP backups, and refusing a second writer. It runs real Tk windows briefly against temporary data on Linux.

```bash
python -m pytest test_daily_launcher.py
```

The installed launcher also accepts `--smoke-test` to open and close the window automatically. Set `MALIPHORS_INATOR_DAILY_DATA_DIR` to a temporary directory to isolate that check from daily data.

Recorded launcher checkpoint on 2026-09-30: **176 tests passed** in the full suite, as recorded in [ROADMAP.md](ROADMAP.md#daily-test-installation-on-this-laptop). This is historical evidence; the 2026-10-01 documentation alignment did not rerun runtime validation.

## Alpha technical pass on 2026-10-01

The isolated working-tree snapshot passed **214 tests** on Ubuntu 26.04.1, Python 3.14.4, and Tk 8.6.17 with display `:0`. Dependency installation and `python -m pip check` passed. The real-dialog walkthrough passed; screenshot capture remains unavailable on this display. See the [validation record and fingerprint](RELEASE_PROCESS.md#alpha-technical-validation-on-2026-10-01).

[test_alpha_readiness.py](test_alpha_readiness.py) covers interrupted writes, unchanged state after failed mutations, metadata/search preservation, persistent undo/redo, unreadable-file protection, duplicate-only generation, auto-save overlap, recovery, deletion error dialogs, and tooltip hover. [test_daily_launcher.py](test_daily_launcher.py) also restores data from the launcher's ZIP backup and verifies it after reopening.

```bash
python -m pytest test_alpha_readiness.py test_daily_launcher.py
python -m pytest
python scripts/desktop_walkthrough.py
```

The same agent rehearsed a small CLI help-text change and validated both entry points in the isolated copy, then restored the file. This supports the handoff instructions but does not complete the independent developer or human usability gates.

## User assistance regression and acceptance

`python -m pytest test_user_assistance.py` covers local search and related articles, onboarding preference preservation and save failures, guided generation/favorite validation with real files, no-result help, action execution, tour resize/cancel cleanup, F1 from a child entry, read-only diagnostics and demo-process isolation/cleanup. Real Tk windows require a display. Launcher tests also check that the new module ships in isolated bundles.

Follow the [assistance acceptance checks](docs/USER_ASSISTANCE.md#acceptance-checks) for human review. In particular, verify readable sizing, keyboard traversal, first launch/relaunch, cancel/replay, an import cancellation and actual restored data. Automated checks do not establish usability or independent handoff.
