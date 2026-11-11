# User Guide

Current stage: **pre-alpha; technical alpha checks passed, human reviews pending**. Initial validation covers Ubuntu 26.04.1/Python 3.14.4/Tk 8.6.17. Alpha means working core workflows and demonstrated developer handoff; see the [definitions](alpha.md) and [remaining gates](ROADMAP.md#alpha-readiness).

maliphors-inator is pre-alpha, with daily developer testing. It combines the beginning of one source phrase with the ending of another and saves results locally.

## Current desktop and data location

Use the **Generate**, **Library**, **Favorites** and **History** tabs. Generate keeps the result, copy/save actions and feedback together. Library searches source phrases and offers add/edit, import review and export. Advanced contains manual/batch generation, tags, cleanup, gallery, statistics and profiles. Ctrl+F focuses Library search; Ctrl+Shift+P searches all actions.

The normal desktop and CLI share `~/.local/share/maliphors-inator/data` (or the equivalent under `XDG_DATA_HOME`). `--data-dir PATH` overrides `MALIPHORS_INATOR_DATA_DIR`, which overrides the default. The desktop footer shows the path; `python main.py --data-path` prints it. Changing the working directory after startup does not redirect saved data.

A default first launch copies existing data automatically, leaving the originals intact. It prefers the current Daily Test data directory, then its former-brand directory, then the launch directory, then the bundled library. Only one source is used; `migration.json` records it. Existing destinations are not merged or overwritten. Close legacy versions before migration. Explicit data-directory overrides use their own contents. See [migration details](docs/UPGRADES.md#shared-data-and-automatic-migration).

Normal entry points prevent another desktop/CLI writer from opening the same directory. The old Daily Test remains an independent sandbox until you choose to update/install it; it does not follow the main store automatically.

**Feedback:** Rate the displayed result to influence random generation. More Like This shares a source while preferring fresh output. Avoid This Combination blocks that ordered pair; undo it through Advanced → Manage Avoided Combinations. Recent results are suppressed when fresh combinations exist; a small exhausted library can repeat unblocked outputs.

**Import review:** Library → Import Malaphors previews new, duplicate and invalid rows. Select a row, edit its JSON, Save Row Correction, or toggle Include / Exclude Selected. Included invalid rows must be corrected or excluded. Apply Reviewed Import skips duplicates and saves once; cancellation before commit leaves data unchanged. Files over 25 MB must be split.

**Backups:** Backups / Restore lists automatic snapshots, creates portable ZIPs and previews restores. Normal startup retains 14 startup snapshots. Import/cleanup keep pre-change backups. A restore lists changed files, validates data/checksums and requires approval; omitted files remain unchanged. It saves a safety backup before replacement and reloads the desktop state afterwards. For manual filesystem copies, close all writers first. Restore rejects archives over 100 MB uncompressed. See [backup details](docs/UPGRADES.md#automatic-backup-and-restore-preview).

**Long operations:** Import, cleanup, batch work and backup workflows show progress without freezing the main event loop. Cancel is checked before commit or between records. A save already committing finishes safely; cancelling a batch keeps completed saved results. Closing the app requests cancellation and waits before final save.

## Daily test version on this laptop

Open **maliphors-inator Daily Test** from the application menu or double-click its desktop shortcut. The title shows the pre-alpha build ID. The installed snapshot runs independently of the source checkout.

- Installed files and environment: `~/.local/share/maliphors-inator-daily/`.
- Saved phrases, history, favorites, and preferences: `~/.local/share/maliphors-inator-daily/data/`.
- Launch log: `data/daily-test.log` inside that directory.
- Backups: `data/backups/`; the launcher keeps the latest 14 startup snapshots of existing JSON files.

The first launch copies the bundled phrase library and starts with fresh history/favorites. Later launches and code updates keep your daily data. The launcher prevents two daily-test instances from writing at once. Close it before restoring a backup; extract the desired ZIP into the data directory after preserving a copy of the current files. Core app sessions launched separately are not covered by this lock.

To install an updated snapshot after testing changes, close the Daily Test app and run from the repository root:

```bash
python3 scripts/install_daily_test.py
```

This Linux installer uses the available `pip`, `xdg-user-dir`, and `desktop-file-validate` commands. It creates a dedicated environment, installs runtime dependencies, and updates the menu/desktop shortcuts. Existing daily data is left in place. If `XDG_DATA_HOME` is set, that location replaces `~/.local/share`.

## Install and start

Follow [README installation](README.md#installation) to create a virtual environment and install dependencies. With that environment active, run:

```bash
python main.py
```

With no arguments, `main.py` opens the desktop app. With arguments it runs the CLI. Saved data uses the shared location described above; exports and import filenames can still be relative to the launch directory.

## Desktop workflows

- **Generate:** choose a language or keep `all`, then click Generate. At least two source phrases must match. Missing language metadata defaults to English.
- **Manual Combine:** choose source phrases to combine yourself.
- **Add to Favorites:** saves the displayed result, including its source text. Manage Favorites lets you review saved entries and export them.
- **Manage History:** review generated entries; the main window shows the latest ten.
- **Manage Phrases / Add New Proverb:** inspect and edit source phrases or add another phrase.
- **Tag Management / Generate by Category:** assign tags and generate from a tag shared by at least two phrases.
- **Import Malaphors:** select a source phrase JSON file in the format below.
- **Export Originals / Export Generated:** choose `.json` or `.txt` to export the phrase library or generated history. Favorites export is available in Manage Favorites.

Import/export dialogs report completion or failure. Cancelling the file picker makes no changes. Unavailable languages and failed generation/favorite saves show an error.

The app also includes gallery, statistics, theme, image export, and power-user dialogs. PNG export requires Pillow, installed by the runtime requirements. These features remain subject to daily testing.

Generation writes history; adding favorites writes favorites. The desktop also saves history and favorites every five minutes and flushes them when its main loop exits. The new import/backup/cleanup/batch workflows use background workers; some legacy advanced operations remain synchronous.

## Help and first steps

On first launch, Getting Started explains phrases, history and favorites. Create New Phrase and Import Existing Data use the current library; Try Demo opens a separate temporary app whose edits are discarded. Done / Skip for now saves onboarding completion. Replay it from Help whenever needed.

Use the Help menu or Help (F1) button for the feature tour, guided tasks, user guide, searchable help, troubleshooting, keyboard shortcuts, release notes, reporting and About. F1 in a major dialog opens its relevant article. The tour highlights actual controls with Back/Next/Finish/Cancel. It does not perform actions automatically.

Guided Tasks walks through generation/favorites, import, or safe backup/recovery. Saved-data steps validate actual changes; manual steps require your confirmation. Cancelling a guide stops instruction but keeps actions already completed. Backup instructions require closing the app before copying/restoring; the guide does not replace files.

Ctrl+Shift+P searches actions. Ctrl+F focuses source search in the Library tab. Ctrl+G generates, Ctrl+H opens history and Ctrl+S saves a favorite. Ctrl+C keeps normal text copy in editable fields; elsewhere it copies the displayed result. Help → Keyboard Shortcuts lists all bindings. Search Help searches local documentation, not your phrases.

Troubleshooting shows read-only directory/count/recovery diagnostics and links symptoms to next steps. Reports are never sent automatically. Ordinary bugs go to GitHub Issues; private security or conduct reports go to richardnoragon@mac.com. See the [assistance standard](docs/USER_ASSISTANCE.md) for the full framework.

## CLI commands

Both `python main.py` with arguments and `python maliphors_inator_cli.py` accept these options:

```bash
python main.py --help
python main.py --generate --count 3
python main.py --generate --language en --output-format json
python main.py --generate --smart --count 5
python main.py --search bird --output-format json
python main.py --import-file incoming.json
python main.py --export originals.json
python main.py --export originals.txt --export-format text
```

Create `incoming.json` using the example below before running its import command. Generated output supports `plain`, `markdown`, or `json`. Search supports JSON or a list of matching source phrase text; it does not search generated history or favorites.

To filter by category, first assign a tag to at least two source phrases, then use, for example, `--generate --category humor`. The bundled data is not guaranteed to contain that tag. Smart generation uses saved pair ratings and falls back to ordinary generation when no ratings exist.

### Current CLI limits

- Use one action per invocation. Conflicting actions return an error.
- Use category, language, and smart options separately. With category plus language, only language is applied; smart generation ignores language; category takes priority over smart.
- `--count` defaults to 1; values below 1 become 1. Ordinary multi-result generation avoids duplicate suggestions and may return fewer results than requested when combinations are exhausted.
- Import returns 0 when it saves new phrases and 1 for no additions or failure. Export returns 0 on success and 1 on failure. Invalid arguments return 2. Generation with insufficient matching phrases or a failed history write reports an error and returns 1.
- Invoking `maliphors_inator_cli.py` without an action exits without output. `main.py` with no arguments starts the desktop.
- The CLI covers generation, source search, and phrase import/export. Favorites management, history export, clipboard actions, and the other dialogs are desktop features.

## Import format

Save this as `incoming.json`:

```json
{
  "proverbs": [
    {
      "original": "A stitch in time saves nine",
      "beginning": "A stitch in time",
      "ending": "saves nine",
      "language": "en",
      "tags": ["wisdom"]
    },
    {
      "original": "The early bird catches the worm",
      "beginning": "The early bird",
      "ending": "catches the worm",
      "language": "en",
      "tags": ["wisdom"]
    }
  ]
}
```

Each phrase needs `original`, `beginning`, and `ending` strings. Language, tags, and source attribution are optional. Invalid required fields or optional metadata types reject the entire import. Failed library saves leave the active phrase collection unchanged. Exact duplicate `original` values are skipped, including duplicates within the incoming file. If these example phrases already exist in your library, the import reports no additions.

Import merges source phrases. Generated history and favorites JSON exports cannot be imported through this action. Text exports are for reading and sharing, not JSON reimport.

Import in the desktop updates that session's phrase search. A CLI import does not refresh an already-running desktop session. Close the desktop before changing its data through another process, then reopen it; simultaneous writers can overwrite one another's state.

## Files and backups

The app uses `malaphors.json`, `history.json`, and `favorites.json` in the selected shared data directory. Ratings, templates, profiles, and UI preferences also have local JSON files as those features are used; see [the complete inventory](ARCHITECTURE.md#local-data).

To back up or restore:

1. Close the app and wait for any CLI commands to finish.
2. Copy the local JSON files to a separate backup directory.
3. To restore, preserve a copy of the current files, replace them with the backed-up versions, and restart.

Normal source/installed entry points make startup backups and lock the selected data directory. They provide no cross-computer synchronization service. The daily-test launcher separately keeps startup backups of its data directory; see [daily-test usage](#daily-test-version-on-this-laptop). Phrase exports alone do not back up history, favorites, or preferences.

If startup reports that saved data needs recovery, the named files were unreadable or structurally invalid. The app protects those paths from overwrite for that session. Keep a copy of the damaged files, close all app/CLI sessions, restore the affected JSON files using the steps above, and restart. Do not keep editing data in the recovery session.

For a daily-test ZIP backup, extract it into a separate temporary directory first, inspect the JSON files, then copy them into the closed app’s daily data directory. Keep the current data separately before replacing it. Both ordinary backup restoration and daily ZIP recovery were tested on 2026-10-01.

JSON saves now preserve the existing destination when serialization, flush, or replacement fails. Failed core edits/deletions keep the previous state; successful undo/redo of deletions survives reopening. Continue to use backups and a single writer per data directory.

## Troubleshooting

- **No matching phrases:** check the displayed data directory, inspect its `malaphors.json`, and choose a language/tag with at least two entries.
- **Tkinter cannot be imported:** install Tk support for your Python distribution; the CLI imports shared code that also requires Tkinter.
- **No display:** run the desktop in a graphical session. CLI commands can run without a display.
- **Files seem unchanged:** check the working directory and destination, and reopen any other session that had already loaded the old data.

## Separate utilities

After installing `qt-requirements.txt`, `python settings_manager.py` opens the PyQt5 JSON editor; `python log_manager.py` opens the PyQt6 log window. Run from the repository root. They are separate processes, so the standalone log window does not receive logs from another running desktop process. The JSON editor validates JSON syntax, not the application's full phrase schema.

## Rebranding compatibility

The application is now **maliphors-inator**. On an existing installation, the new daily-test data directory links to the previous `malaphors-inator-daily/data` directory, preserving saved data, backups, and the shared session lock. Keep that old data directory. Old build snapshots remain unchanged. New installations use the new directory directly. See [REBRANDING.md](REBRANDING.md) for all name changes.
