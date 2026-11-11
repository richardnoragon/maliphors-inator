# Security Policy

Current stage: **pre-alpha; technical alpha checks passed, human reviews pending**. Alpha means working core workflows and demonstrated developer handoff; see the [definitions](alpha.md) and [remaining gates](ROADMAP.md#alpha-readiness).

maliphors-inator is a pre-alpha local desktop application and CLI. The current application code exposes no network service or authentication system. Its data and exports are stored as unencrypted local files.

## Maintenance scope

Developers test the active working tree daily. There is no established security support window for tagged releases or historical branches. Python 3.10+ is the code baseline; recorded validation currently covers Linux/Python 3.14.4. This is not a security certification or a tested platform matrix.

## Reporting an issue

Report suspected vulnerabilities privately to richardnoragon@mac.com. Use a subject identifying maliphors-inator and the affected revision. Do not include exploit details or sensitive data in public GitHub issues. Ordinary non-sensitive bugs can be reported through [GitHub Issues](https://github.com/richardnoragon/maliphors-inator/issues).

A report should identify the affected revision, relevant files, environment, reproduction steps, and impact. Remove personal data and credentials from logs or example files before sharing them. No response-time commitment has been established.

## Local files and imports

The app reads and writes data in the current working directory, including `malaphors.json`, `history.json`, `favorites.json`, ratings, templates, profiles, and UI preferences. See [the data inventory](ARCHITECTURE.md#local-data).

- Files inherit ordinary filesystem permissions; the app does not encrypt them or provide access controls.
- Import validates required phrase strings and optional language/source/tag types before merging. It does not impose a file-size limit or isolate untrusted input.
- Export and the standalone JSON editor can overwrite user-selected files.
- Generator JSON writes use a flushed temporary file and atomic replacement. This does not provide multi-file transactions, power-loss guarantees, or coordination between app/CLI processes; use one writer per data directory.
- Unreadable or structurally invalid phrase/history/favorites/ratings files are protected from overwrite for the session. The desktop reports recovery needs. Restore a known-good backup and restart. Text exports and separate editing utilities do not share all of these protections.

## Backup and recovery

Close all app and CLI sessions before copying or restoring state. Back up the local JSON files to a separate directory before imports, cleanup, or broad edits. To recover, keep a copy of the damaged files, replace the affected state with a known-good backup, and restart the app. Direct source launches do not create automatic backups. The daily-test launcher keeps 14 startup ZIP backups; recovery from those archives is covered by `test_daily_launcher.py`.

Keep the working directory and backups accessible only to intended users. Phrase text, favorites, history, logs, and exports may contain whatever users enter; avoid including sensitive content in shared test artifacts.

## Open development gates

Interrupted-write preservation and backup restoration passed the [2026-10-01 technical review](RELEASE_PROCESS.md#alpha-technical-validation-on-2026-10-01). Human usability and independent developer handoff remain open. Establish release support windows before external publication. Initial alpha validation covers Ubuntu 26.04.1/Python 3.14.4/Tk 8.6.17.
