# Feature Specification: Comprehensive Improvements & Features Roadmap

**Feature ID:** improvements-roadmap\
**Version:** 1.1.0\
**Date:** 2026-10-01\
**Status:** Active backlog; application pre-alpha, alpha readiness in progress

Application stage follows [alpha.md](../../../alpha.md); current evidence and open gates are in [ROADMAP.md](../../../ROADMAP.md#alpha-readiness). This specification’s version and feature completion do not declare an application release. The full enhancement backlog is not required for alpha.

## Notes
- This repository already contains a functional Tkinter-based app, CLI, JSON phrase database, and supporting UI workflows.
- Versioning policy now lives in [../../../VERSIONING.md](../../../VERSIONING.md).
- Public branding uses “maliphors-inator”; current Python modules and repository names follow the rebrand documented in [REBRANDING.md](../../../REBRANDING.md).

## Current Implementation Snapshot

The codebase already includes the core foundation for the project:
- GUI generation workflow with favorites, history, search, and manual phrase selection
- JSON-based phrase persistence, settings, and logging support
- CLI generation/search/export interfaces
- Category-aware generation and gallery/statistics experiences
- Extensive built-in phrase database and import/export tooling

This roadmap file tracks the remaining backlog and planned refinements rather than the entire original feature set from a greenfield start.

## Overview

This feature organizes and tracks 37 identified improvements and new features across 6 categories:
1. UI/UX Enhancements (10 items)
2. Generation & Logic Features (8 items)
3. New Capabilities (8 items)
4. Data & Quality (4 items)
5. Testing & Reliability (4 items)
6. Performance & Optimization (3 items)

## Purpose

Create a prioritized, tracked set of GitHub issues to guide development efforts over the next quarter. Enable specification-driven feature delivery with clear impact/effort analysis for each item.

## Acceptance Criteria

- ✅ All 37 items converted to GitHub issues with consistent labeling
- ✅ Issues tagged by category (ui-ux, feature, data, testing, performance)
- ✅ Issues tagged by impact (high, medium, low)
- ✅ Issues tagged by estimated time (quick-win, medium, complex)
- ✅ Issues assigned to priority phases (Phase 1-4)
- ✅ Issues linked to roadmap milestones
- ✅ Each issue includes implementation details and acceptance criteria
- ✅ Dependency ordering respected (e.g., Phase 1 before Phase 2)

## Success Metrics

- All issues discoverable and filterable by label
- Teams can view "Phase 1" items as immediate priorities
- Clear "Quick Wins" for opportunistic implementation
- High-impact items clearly distinguished
- Each issue actionable without external context

## Scope

**In Scope:**
- All 37 improvement/feature suggestions
- Labeling and categorization
- Phased roadmap (4 phases)
- Acceptance criteria per issue
- Time and impact estimates

**Out of Scope:**
- Implementation of features
- Assigning to team members (can be done after creation)
- Creating dependencies/blockers between issues (can be added later)

## Related Documents

- Improvement Analysis: 37 suggestions with impact/time breakdown
- Project Constitution: Guides quality standards for all work
- Test Coverage Standards: Define testing requirements

## Open Questions

None - specification derived from comprehensive codebase analysis and recommendations.

## Alpha technical checkpoint

On 2026-10-01, the reviewed snapshot passed 214 tests, dependency checks, the real-dialog walkthrough, and backup recovery. Architecture review and initial Ubuntu 26.04.1/Python 3.14.4/Tk 8.6.17 validation are complete. The application remains pre-alpha pending human usability review and independent developer handoff. See the [current gates](../../../ROADMAP.md#alpha-readiness) and [validation record](../../../RELEASE_PROCESS.md#alpha-technical-validation-on-2026-10-01).
