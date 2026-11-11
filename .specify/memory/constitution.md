# Project Constitution: maliphors-inator

**Version:** 2.1\
**Last Updated:** 2026-10-10\
**Status:** Active\
**Framework:** github-spec-kit 2.0.0

> Product branding note: this project is publicly presented as “maliphors-inator.” Repository, workspace, runtime modules, and application identity follow the current name. See [rebranding](../../REBRANDING.md); historical evidence and domain data retain their original names.

---

## Table of Contents

1. [Mission & Vision](#mission--vision)
2. [Project Scope & Audience](#project-scope--audience)
3. [Core Principles](#core-principles)
4. [Technology & Architecture](#technology--architecture)
5. [Quality Standards](#quality-standards)
6. [Development Workflow](#development-workflow)
7. [Code Organization](#code-organization)
8. [Specification-Driven Development](#specification-driven-development)
9. [Review Checkpoints](#review-checkpoints)
10. [Non-Negotiable Standards](#non-negotiable-standards)
11. [Versioning & Releases](#versioning--releases)
12. [Governance & Amendments](#governance--amendments)

---

## Mission & Vision

### Mission

The Malaphors Generator is a playful Python desktop application for creating and exploring creative blends of phrases, idioms, and proverbs. The project serves as both an educational tool for language exploration and an entertaining application for language enthusiasts.

### Vision

Build an elegant, well-tested, and maintainable tool that makes it easy and delightful to discover creative linguistic combinations while serving as a reference implementation for specification-driven Python development practices.

### Project Character

This is a **personal/educational project** maintained primarily for:
- Learning and experimentation in software design
- Demonstrating best practices in Python development (testing, type hints, documentation)
- Providing a reference example of specification-driven development workflows
- Serving the creator's interests in language play and creative writing

---

## Project Scope & Audience

### Scope

**In Scope:**
- Python/Tkinter desktop application (primary implementation)
- JSON-based phrase database management
- History, favorites, and logging features
- Settings and preferences management via GUI
- Testing and documentation

**Out of Scope (for now):**
- Network/cloud features
- Mobile applications
- Real-time collaboration
- External API integrations

### Primary Implementation vs. Experimental

- **Primary:** Python 3.10+ with Tkinter; application pre-alpha, alpha readiness in progress.
- **Earlier experimental direction:** Rust/Tauri; no such implementation is present in this checkout.
- [Development-stage definitions](../../alpha.md) govern maturity; [ROADMAP.md](../../ROADMAP.md#alpha-readiness) records evidence and open gates. Framework/constitution versions do not declare application readiness.

### Intended Audience

- Individual language enthusiasts and writers
- Developers learning Python best practices
- Contributors interested in specification-driven development
- Educators using it as a reference project

**Note:** This is NOT a product with external users requiring SLAs or support commitments.

---

## Core Principles

### 1. Quality First
All code reflects professionalism and best practices:
- Comprehensive test coverage (MUST be ≥80% for all changes)
- Python type hints required for all public APIs
- Clear, descriptive variable and function names
- Follow PEP 8 style guidelines (enforced via linting)
- Docstrings for all modules, classes, and public functions

**Rationale:** High quality code serves as both a learning resource and ensures maintainability for future contributions.

### 2. User Experience (Delight in Simplicity)
The application should be intuitive and responsive:
- Simple, uncluttered UI (Tkinter appropriateness)
- Fast phrase generation (minimal latency)
- Clear error messages that guide users to resolution
- Cross-platform compatibility (Windows, macOS, Linux)
- Accessible settings and data management

**Rationale:** A tool is only valuable if it's enjoyable and straightforward to use.

### 3. Maintainability & Learning
Code structure should be educational and maintainable:
- Keep modules focused and single-purpose (DRY principle)
- Explicit is better than implicit (Zen of Python)
- Trade-offs documented in code comments or ADR files
- Backward compatibility maintained where reasonable
- Dependencies chosen pragmatically for real benefit

**Rationale:** Future contributors (including the author in 6 months) should be able to understand and extend the code confidently.

### 4. Pragmatic Problem-Solving
Choose solutions based on real value, not dogma:
- Use established libraries when they genuinely improve code quality
- Don't add dependencies for marginal benefits
- Accept "good enough" over "perfect" when diminishing returns appear
- Refactor when clarity improves substantially
- Technical decisions are driven by the project's educational mission

**Rationale:** Perfectionism can inhibit learning and progress in a personal project.

---

## Technology & Architecture

### Technology Stack (Locked Decisions)

**Primary Implementation:**
- **Language:** Python 3.10+
- **GUI Framework:** Tkinter (included with Python)
- **Data Format:** JSON (human-readable, portable)
- **Testing:** pytest (with coverage.py for metrics)
- **Linting/Formatting:** (configured in workspace as appropriate)

**Secondary Implementation (Experimental):**
- **Language:** Rust
- **Framework:** Tauri (for desktop packaging)
- **Status:** Historical direction; implementation absent from this checkout

### Architectural Decisions

**Data Management:**
- Phrase database stored in JSON for portability and human readability
- No external database dependencies (SQLite or otherwise)
- Settings and favorites in separate JSON files for organization
- Export/import functionality available for data portability

**Module Separation:**
- `maliphors_inator_logic.py` - Core generation algorithm and data management (business logic)
- `maliphors_inator_ui.py` - Tkinter GUI implementation (presentation layer)
- `log_manager.py` - Logging interface and history
- `settings_manager.py` - Settings persistence and GUI
- `main.py` - Application entry point

**No External Services:**
- Application functions offline
- No cloud storage, authentication, or remote logging
- All data remains local and user-controlled

### Dependency Philosophy

**Pragmatic Approach:**
- Add a dependency only if it provides significant value
- Prefer well-maintained packages from recognized sources
- For each new dependency, document the justification in code comments
- Evaluate trade-off: benefit gained vs. maintenance burden and installation size
- Minimize transitive dependencies

**Current Dependency Review:**
- Required packages should be listed in `requirements.txt` with rationale
- Test dependencies in `test-requirements.txt` (separated from runtime)
- Quarterly reviews to identify unused or redundant packages

---

## Quality Standards

### Test Coverage Requirements (Non-Negotiable)

| Component | Minimum Coverage | Notes |
|-----------|-----------------|-------|
| `maliphors_inator_logic.py` | 85% | Core business logic |
| `log_manager.py` | 80% | Data management |
| `settings_manager.py` | 80% | Settings and persistence |
| `maliphors_inator_ui.py` | 70% | UI is harder to test; focus on business logic within UI |

**Coverage Measurement:**
```bash
pytest --cov=. --cov-report=term-missing
```

**Enforcement:**
- Coverage reports generated before merge
- Features/fixes cannot reduce overall coverage
- New code must meet or exceed component minimums

### Code Style & Standards

**Python Standards:**
- PEP 8 compliance (indentation, naming, spacing)
- Type hints on all function signatures (Python 3.10+)
- Docstrings in Google or NumPy format for all public APIs
- No bare `except` clauses (always specify exception type)
- Use `logging` module instead of `print()` for debugging

**Import Organization:**
```python
# Standard library
import json
import logging
from pathlib import Path

# Third-party libraries
import tkinter

# Local modules
from maliphors_inator_logic import MalaphorGenerator
```

### Documentation Standards

**Inline Documentation:**
- Docstrings for modules (describe purpose and high-level structure)
- Docstrings for classes (describe responsibility)
- Docstrings for public methods/functions (describe parameters, return, side effects)
- Comments for WHY, not WHAT (code should be self-documenting)

**Project Documentation:**
- `README.md` maintained for installation, usage, structure
- `CONTRIBUTING.md` provides development guidelines
- Architecture decisions documented in `docs/ADR/` folder (when complexity warrants)

---

## Development Workflow

### Feature Development Process

**For all features (no exceptions):**

1. **Specification Phase** (`/speckit-specify`)
   - Describe the feature in plain language
   - Include acceptance criteria
   - Identify dependencies or risks

2. **Clarification Phase** (`/speckit-clarify`)
   - Ask targeted questions about ambiguities
   - Refine specification based on answers

3. **Planning Phase** (`/speckit-plan`)
   - Design the implementation approach
   - Identify modules to create/modify
   - Document trade-offs and alternatives

4. **Tasks Phase** (`/speckit-tasks`)
   - Break plan into actionable, sized tasks
   - Order by dependency
   - Assign acceptance criteria per task

5. **Implementation Phase** (`/speckit-implement`)
   - Execute tasks in order
   - Write tests alongside code
   - Verify against acceptance criteria

6. **Analysis Phase** (`/speckit-analyze`)
   - Check artifacts for consistency
   - Verify spec-plan-tasks alignment
   - Identify gaps before release

### Branch & Commit Practices

**Branching:**
- Feature branch: `feature/short-description`
- Bugfix branch: `fix/issue-description`
- Experiment branch: `exp/investigation-description`

**Commits:**
- Clear, atomic commits ("one idea per commit")
- Commit message format: `type: brief description\n\nOptional longer explanation`
- Example: `feat: add random generation algorithm\n\nImplements Fisher-Yates shuffle for phrase selection`

**Merge Requirements:**
- All tests pass locally
- Test coverage maintained or improved
- Code review (if working with others)
- No debug code or commented-out sections in final commit

---

## Code Organization

### Project Structure

```
maliphors-inator/
├── main.py                    # Application entry point
├── maliphors_inator_logic.py          # Core business logic
├── maliphors_inator_ui.py             # Tkinter GUI
├── log_manager.py             # Logging interface
├── settings_manager.py        # Settings management
├── malaphors.json             # Phrase database
├── favorites.json             # User favorites
│
├── test_*.py                  # Test files (pytest)
├── conftest.py                # Shared test configuration
├── pytest.ini                 # Pytest configuration
│
├── .github/
│   ├── agents/                # Speckit agents (10 workflows)
│   ├── prompts/               # Speckit prompts
│   └── skills/                # Speckit skills
│
├── .specify/                  # Specification-driven development
│   ├── memory/
│   │   └── constitution.md    # This file (project law)
│   ├── features/              # Feature specifications
│   └── README.md              # Speckit documentation
│
├── docs/                      # Documentation (optional)
│   └── ADR/                   # Architectural Decision Records
│
├── requirements.txt           # Runtime dependencies
├── test-requirements.txt       # Test-only dependencies
├── README.md                  # Project README
├── CONTRIBUTING.md            # Contribution guide
└── LICENSE                    # MIT License
```

### Module Responsibilities

| Module | Responsibility | Test File |
|--------|-----------------|-----------|
| `maliphors_inator_logic.py` | Phrase loading, generation, history/favorites | `test_maliphors_inator_logic.py` |
| `maliphors_inator_ui.py` | Tkinter GUI components, event handling | `test_maliphors_inator_ui.py` |
| `log_manager.py` | Logging to file, retrieving log entries | `test_logging.py` |
| `settings_manager.py` | Settings CRUD, persistence, GUI | `test_settings_manager.py` |
| `main.py` | Application initialization and bootstrap | Integration tests |

---

## Specification-Driven Development

### Core Concepts

This project uses **github-spec-kit (v2.0.0)** for structured development:

1. **Spec** - "What are we building?"
2. **Plan** - "How will we build it?"
3. **Tasks** - "What are the concrete steps?"
4. **Implement** - "Execute the tasks"
5. **Analyze** - "Does everything align?"

### Required Artifacts

For each feature, create:
- `.specify/features/{feature-name}/spec.md` - Requirements and acceptance criteria
- `.specify/features/{feature-name}/plan.md` - Architecture and design
- `.specify/features/{feature-name}/tasks.md` - Action items with acceptance criteria

### Constitution Authority

**This constitution is non-negotiable within the speckit workflow.** All specs, plans, and tasks MUST align with these principles. If a principle conflicts with a feature requirement:
1. Document the conflict in the task notes
2. Escalate for decision (principles take precedence by default)
3. If amendment is needed, update this constitution explicitly
4. Never reinterpret the constitution to accommodate a feature

---

## Review Checkpoints

These checkpoints ensure quality and alignment:

### Specification Review
**Before moving to planning:**
- [ ] Feature purpose is clear ("why" is documented)
- [ ] Acceptance criteria are testable (not vague)
- [ ] Dependencies are identified (other features, libraries, etc.)
- [ ] Success metrics are defined

### Planning Review
**Before creating tasks:**
- [ ] Design aligns with architecture principles
- [ ] Trade-offs are documented (why this design, not alternatives)
- [ ] Existing code reuse is maximized
- [ ] Test strategy is outlined

### Implementation Review (Code Review)
**Before merging:**
- [ ] Tests pass and coverage maintained
- [ ] Code follows style and documentation standards
- [ ] Docstrings and comments explain non-obvious logic
- [ ] No debug code or commented-out sections
- [ ] Commits are clear and atomic

### Release Review
**Before shipping (if applicable):**
- [ ] Changelog updated with feature description
- [ ] Version number bumped correctly
- [ ] README updated if user-facing changes
- [ ] No known critical bugs or regressions

---

## Non-Negotiable Standards

### Must Do (✅ Mandatory)

- ✅ **No feature ships without tests** - Tests define correctness
- ✅ **Test coverage ≥80%** - Measure and maintain it
- ✅ **Type hints on public APIs** - They serve as documentation
- ✅ **PEP 8 compliance** - Enforced via linting
- ✅ **Clear docstrings** - Every module, class, and public function
- ✅ **Atomic, clear commits** - History should be readable
- ✅ **Tests run locally before push** - No CI-driven debugging
- ✅ **Specification-first development** - Use `/speckit-specify` before coding

### Must NOT Do (❌ Prohibited)

- ❌ **Debug code in commits** - No `print()`, `pdb`, or commented-out sections
- ❌ **Bare `except:` clauses** - Always specify the exception type
- ❌ **Unhandled exceptions in UI** - Users should never see a crash without an error dialog
- ❌ **Hardcoded paths or credentials** - Use environment variables or config files
- ❌ **Massive commits** - One feature/fix per commit
- ❌ **Breaking changes without major version bump** - Respect semantic versioning
- ❌ **Dependencies without rationale** - Document why each is needed
- ❌ **Silent failures** - Log errors even if recovering gracefully

---

## Versioning & Releases

### Semantic Versioning (MAJOR.MINOR.PATCH)

- **MAJOR** (e.g., 2.0.0): Breaking changes, major feature overhaul, architecture changes
- **MINOR** (e.g., 1.2.0): New features, backward compatible
- **PATCH** (e.g., 1.1.1): Bug fixes, performance improvements, documentation

### Release Process

1. All features and fixes must pass tests and code review
2. Update version number in relevant files (setup.py, __init__.py, etc.)
3. Update CHANGELOG.md with release notes
4. Create git tag: `git tag v1.2.0`
5. Push tag: `git push origin v1.2.0`

### Release Cadence

**Ad-hoc:** Features are released when they're ready, not on a fixed schedule.
- When enough valuable features accumulate, publish a release
- Every release should increase user or developer value
- Announce changes in release notes

---

## Governance & Amendments

### Authority & Maintenance

This constitution represents the **agreed-upon law** for the Malaphors Generator project. It provides:
- **Predictability** - Contributors know the standards
- **Consistency** - All decisions respect the same principles
- **Clarity** - No ambiguity about what's expected

### Amending the Constitution

If circumstances change or principles need updating:

1. **Identify the conflict or gap** - Document specifically which principle is limiting or unclear
2. **Propose an amendment** - Update this document with rationale for the change
3. **Run `/speckit-constitution`** - Formalize the amendment in the workflow
4. **Commit with clear message** - Example: `docs: amend constitution (testing requirement: lower to 75% for UI)`

### When Constitution Conflicts Arise

If a feature or bug fix conflicts with this constitution:
1. **DO NOT ignore the constitution** - Work within it or amend it
2. **Document the conflict** - Explain why the principle doesn't fit
3. **Choose one:**
   - Modify the feature to comply with the constitution, OR
   - Propose a constitution amendment (documented, explicit)
4. **Never compromise silently** - Every deviation should be intentional and recorded

---

## Appendix: Quick Reference

### Essential Commands (Speckit Workflow)

```bash
# Start a feature
/speckit-specify "Feature description"

# Clarify requirements
/speckit-clarify

# Plan the implementation
/speckit-plan

# Break into tasks
/speckit-tasks

# Execute tasks
/speckit-implement

# Check quality and alignment
/speckit-analyze
```

### Testing Quick Reference

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=term-missing

# Run specific test file
pytest test_maliphors_inator_logic.py

# Run specific test function
pytest test_maliphors_inator_logic.py::test_generate_random_malaphor
```

### Style & Quality Checks

```bash
# Check PEP 8 compliance
flake8 .

# Check type hints (if mypy is installed)
mypy .
```

---

## Document Metadata

| Field | Value |
|-------|-------|
| **Title** | Project Constitution: Malaphors Generator |
| **Version** | 2.0 |
| **Last Updated** | 2026-09-07 |
| **Next Review** | 2026-12-07 (quarterly) |
| **Authority** | Project founder and speckit framework |
| **Ratification Date** | 2026-09-07 |
| **Status** | Active & Binding |

---

**Note:** This constitution is the single source of truth for project governance. When in doubt, consult this document. When it needs updating, amend it explicitly.

**Constitution Authority Statement:** This document supersedes all verbal agreements and implicit understandings. It is non-negotiable within the speckit workflow scope. Any conflict with this constitution requires explicit amendment, never silent reinterpretation.
