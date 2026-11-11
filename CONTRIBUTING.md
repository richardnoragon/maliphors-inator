# Contributing

Contributions are welcome.

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
