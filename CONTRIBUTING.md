# Contributing

Contributions are welcome. Follow the [code of conduct](CODE_OF_CONDUCT.md). The [proprietary license](LICENSE) remains authoritative; discuss substantial contributions and permission with the maintainer before starting.

## How to contribute

1. Fork the repository and create a feature branch.
2. Make your changes and add or update tests where appropriate.
3. Run the relevant test commands before submitting a pull request.
4. Open a pull request with a clear summary of the change.

## Project layout

- Python app files live at the repository root for maliphors-inator.
- The current checkout contains the Python application; milestones and gates live in [ROADMAP.md](ROADMAP.md).
- The project is pre-alpha with daily developer testing. Use [TESTING.md](TESTING.md) for the current pytest commands.

## Alpha handoff

The next stage is defined by [alpha.md](alpha.md): working core workflows, sufficiently stable architecture, and another developer able to continue from the code and docs. Follow the [handoff check](TESTING.md#developer-handoff-check) and record evidence in [ROADMAP.md](ROADMAP.md#alpha-readiness). Alpha readiness is in progress; the project remains pre-alpha.

## Notes

- Keep the documentation in sync with any user-facing changes.
- Avoid committing local build artifacts or generated data files.
- Follow the canonical [versioning policy](VERSIONING.md) and update
  [CHANGELOG.md](CHANGELOG.md) when changes affect users or developers.

## Alpha technical checkpoint

On 2026-10-01, the reviewed snapshot passed 214 tests, dependency checks, the real-dialog walkthrough, and backup recovery. Architecture review and initial Ubuntu 26.04.1/Python 3.14.4/Tk 8.6.17 validation are complete. The application remains pre-alpha pending human usability review and independent developer handoff. See the [current gates](ROADMAP.md#alpha-readiness) and [validation record](RELEASE_PROCESS.md#alpha-technical-validation-on-2026-10-01).

## Coding standards

Use four-space Python indentation, `snake_case` functions/variables and `PascalCase` classes. Match surrounding style and keep changes focused. Put generation and persistence rules in `MalaphorGenerator`; keep Tk interaction in the UI and argparse routing in the CLI. Reuse the atomic JSON writer, preserve existing data formats and phrase metadata, and report failed operations accurately. Do not introduce a second persistence path for a UI feature. Use the standard-library logger rather than print for runtime diagnostics, and avoid logging private phrase data.

## Branch and commit conventions

Branch from current `main`; use a descriptive branch such as `feature/search-help` or `fix/import-error`. Automation may use `codex/` branches. Keep `main` reviewable and avoid rewriting shared history. Use small, coherent commits with imperative subjects, for example `Add searchable local help`. Explain the reason for non-obvious changes in the commit body. No mandatory commit prefix is currently enforced.

## Pull request requirements

Describe the problem, resulting behavior, relevant issue and validation commands/results. Include screenshots for visible UI changes and explain data-format or compatibility changes. Update affected user/help docs and the Unreleased changelog. Keep new dependencies justified and declared. Report skipped or blocked tests plainly; historical passes do not validate a new build. A maintainer reviews the scope and merges after required checks and concerns are resolved.

## Testing requirements

Run focused checks for affected behavior using [TESTING.md](TESTING.md), and the full suite before release readiness. Persistence changes need failure-path and reload coverage with disposable data. UI changes need real-widget checks and an interactive usability pass; mock blocking file/message dialogs only where that is the test's intended boundary. Documentation-only changes require command/path and local-link checks. Never test destructive operations on personal daily data.

## Questions and reports

Open ordinary bugs and proposals in [GitHub Issues](https://github.com/richardnoragon/maliphors-inator/issues). Use richardnoragon@mac.com for private contribution questions, security reports or conduct concerns. See [SECURITY.md](SECURITY.md) for vulnerability-report contents.
