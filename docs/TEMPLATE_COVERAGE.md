# Project template coverage

Audit date: 2026-11-11. Source: [Project Documents Templates](../Project%20Documents%20Templates/TOC.md). The outlines have been adapted to the current Python/Tk application. This is an implementation map, not a new release-stage declaration.

| Template | Implementation and evidence |
| --- | --- |
| ARCHITECTURE | [Architecture](../ARCHITECTURE.md) covers modules, the generator as state owner, JSON relationships, shared behavior, CLI/Tk adapters, direct callbacks, auto-save and extension boundaries. A hub/plugin/database is not currently present. |
| CHANGELOG | [Changelog](../CHANGELOG.md) groups versioned changes and Unreleased additions, changes and fixes. |
| CODE_OF_CONDUCT | [Conduct policy](../CODE_OF_CONDUCT.md) defines behavior, scope, private reporting, enforcement and reconsideration. |
| CONTRIBUTING | [Contributor guide](../CONTRIBUTING.md) defines coding standards, branches, PR requirements, commit conventions and tests. |
| DECISIONS | [Decision log](../DECISIONS.md) records decisions, reasons and consequences, including the current rebrand and assistance system. |
| FAQ | [FAQ](../FAQ.md) answers real setup, usage, format, recovery, compatibility and reporting questions. |
| LICENSE | [License reference](../LICENSE.md) links the authoritative proprietary [LICENSE](../LICENSE); no new reuse permission is implied. |
| README | [README](../README.md) covers overview, actual screenshots, features, installation, quick start, architecture, roadmap, license and contribution links. |
| RELEASE_PROCESS | [Release process](../RELEASE_PROCESS.md) covers feature freeze, candidate creation, recorded trial periods, maintainer approval and regression gates. No unperformed trial is marked complete. |
| ROADMAP | [Roadmap](../ROADMAP.md) separates completed gates, near-term plans and future directions. |
| SECURITY | [Security](../SECURITY.md) states maintenance scope, private vulnerability reporting, local storage and backups. |
| TESTING | [Testing](../TESTING.md) defines strategy, acceptance walkthroughs, regressions, disposable datasets and release validation. |
| TOC | [Documentation index](../TOC.md) links every active document. |
| USER_GUIDE | [User guide](../USER_GUIDE.md) covers installation, import, managing content, common workflows and backup/restore. The source template's accidental trailing newline in its filename was corrected. |
| help_outline | [Assistance standard](USER_ASSISTANCE.md) maps onboarding, real-control tours, contextual help, smart empty states, tooltips, action search, local articles, guided tasks, diagnostics, concepts and discovery to implemented UI. Generic library/hash/NAS examples are adapted to phrase data; remote AI is an optional future extension. |

## Verification

The 2026-11-11 pass uses real-widget regression checks in [test_user_assistance.py](../test_user_assistance.py) alongside the existing suite, checks local document links and captures main/help screenshots from disposable data. The application remains pre-alpha. Human usability and independent handoff remain pending; see the [roadmap](../ROADMAP.md#alpha-readiness).

Final automated result: **228 passed in 7.48 seconds** on Linux/Python 3.14.4 with the available Tk display. Command: `.venv/bin/python -m pytest -q -o log_cli=false`. All **235 local document/image targets** checked in top-level Markdown and `docs/*.md` resolve; `git diff --check` passed. Main/help screenshots were captured and inspected, and help-window button visibility has real-widget regression coverage.

The subsequent [seven-upgrade pass](UPGRADES.md) expands the suite to 252 passing tests and verifies Linux packaging/CI on Python 3.12 and 3.14. See the [release evidence](../RELEASE_PROCESS.md#seven-upgrade-validation-on-2026-11-11) for the reviewed implementation and remaining human gates.
