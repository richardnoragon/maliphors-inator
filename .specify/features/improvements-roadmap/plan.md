# Alpha Readiness Plan: maliphors-inator

**Feature:** improvements-roadmap

**Updated:** 2026-10-01

**Application status:** Pre-alpha; technical alpha checks passed, human reviews pending. No application release version or date selected.

## Goal and scope

Demonstrate the [alpha definition](../../../alpha.md): core purpose working end-to-end, sufficiently stable architecture, and another developer able to continue using the code and documentation. The [roadmap](../../../ROADMAP.md#alpha-readiness) is the source of truth for gate completion and evidence.

The scope is the existing Python/Tkinter app and CLI: generation, source phrase search/import/export, desktop history/favorites, and saved-state reload. Additional polish and enhancement backlog items remain optional unless needed for a core workflow or handoff. Separate Qt utilities are documented with their own entry points.

## Existing evidence

- Core workflow baseline: 135 tests passed on 2026-09-30.
- Daily failure-path fixes and scripted real-dialog walkthrough: 174 tests passed.
- Daily-test launcher coverage: 176 tests passed, as recorded in the roadmap.
- Setup, usage, architecture, testing, data constraints, and contribution guides exist.
- 2026-10-01: 214 tests, dependency checks, real-dialog walkthrough, backup restoration, architecture review, and isolated handoff rehearsal passed. Initial alpha scope is Ubuntu 26.04.1/Python 3.14.4/Tk 8.6.17; see the [validation record](../../../RELEASE_PROCESS.md#alpha-technical-validation-on-2026-10-01).

These are recorded Linux/Python 3.14.4 results. They do not establish independent handoff, human visual review, or validation on other environments.

## Remaining work

1. Complete the human desktop walkthrough and fix reproducible core failures.
2. Run the [independent developer handoff check](../../../TESTING.md#developer-handoff-check); repair any setup or documentation gaps.
3. Resolve findings from those human reviews, rerun affected checks, and record the alpha stage decision, build, date, and limitations in the roadmap. Update active documentation together.

Architecture/data-risk review, backup recovery, and supported-environment validation were completed in the 2026-10-01 technical pass.

## Publication

Alpha readiness and publication are separate decisions. If a release is prepared, choose its version, reconcile metadata and the historical changelog, and follow [RELEASE_PROCESS.md](../../../RELEASE_PROCESS.md) and [VERSIONING.md](../../../VERSIONING.md). Earlier plan/framework version labels such as `2.0.0` do not select the application's next version.

Beta requires reliable real use by ordinary users; stable release requires the declared scope and publication checks to pass review. Neither later checkpoint is scheduled.
