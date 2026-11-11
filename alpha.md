# Development stages

These project definitions were distilled from the original alpha discussion in this file on 2026-10-01. They define readiness; [ROADMAP.md](ROADMAP.md#alpha-readiness) records the evidence and current status. Version numbers and publication follow [VERSIONING.md](VERSIONING.md) and [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## Pre-alpha

The application is being implemented and validated. Core features may already work, but the alpha checklist has not yet been demonstrated in full.

## Alpha

Alpha is reached when the software demonstrates its intended purpose end-to-end, its architecture is sufficiently stable, and another developer can reasonably take over using the code and documentation.

Alpha is intended for developers and technically knowledgeable testers. Defects, incomplete secondary workflows, missing polish, and incremental design changes are expected.

### Alpha checklist

- The core purpose is implemented and usable.
- Major architectural decisions, module boundaries, configuration, and storage are documented; no major rewrite is expected for the agreed scope.
- The primary workflows work end-to-end, with the agreed alpha features integrated.
- Another developer can obtain the source, install dependencies, run and test the app, understand its architecture, and continue development without direct assistance from the original author.
- Data-loss risks and recovery steps are understood and documented; routine use does not routinely corrupt or destroy data.
- The README, installation instructions, architecture overview, and roadmap are sufficient for that handoff.
- Tests cover the major workflows, with recorded results and known limitations.

Polish, convenience features, performance tuning, advanced options, and completion of the entire enhancement backlog are not prerequisites. Record the supported environment and remaining limitations explicitly. A passing test count alone does not establish alpha.

## Beta

Beta is reached when ordinary users can reliably use the software for real work. Defects may remain, but data loss and primary workflow failures are exceptional.

Assess beta through representative user trials on the supported platforms, reliable daily use, and verified data recovery. Developer handoff alone does not establish beta.

## Release

For this project, a stable release is a reviewed build that meets its declared scope for ordinary users, with supported environments, installation and recovery guidance, passing validation, and no unresolved release-blocking defects. Remaining limitations are disclosed in the release notes.

This release definition extends the original alpha/beta discussion into a project publication gate. Publishing an alpha or beta prerelease does not declare the software stable. Stage readiness and the decision to publish a version are tracked separately.
