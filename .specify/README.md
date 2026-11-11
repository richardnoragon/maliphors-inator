# Speckit Project Structure

This directory contains the specification-driven development framework for the maliphors-inator project.

## Current repository status

The application is pre-alpha, with alpha readiness in progress as of 2026-10-01. [Stage definitions](../alpha.md) describe the developer-handoff threshold; [ROADMAP.md](../ROADMAP.md#alpha-readiness) owns current evidence and open gates. Framework/specification version numbers do not establish application maturity. The application already includes the primary Python/Tkinter workflow, CLI capability, phrase database tooling, persistence, gallery features, and supporting settings/logging modules. The artifacts in this directory document the current backlog and roadmap rather than a purely speculative greenfield plan.

## Directory Structure

```
.specify/
├── extensions.yml              # Speckit extensions and hooks configuration
├── speckit.config.json         # Speckit version and capabilities tracking
├── memory/
│   ├── constitution.md         # Project constitution (non-negotiable principles)
│   └── [other project memory files]
├── features/
│   └── [feature-name]/         # Individual feature specifications
│       ├── spec.md            # Feature specification
│       ├── plan.md            # Implementation plan
│       └── tasks.md           # Actionable tasks
└── templates/
    └── [reusable templates]
```

## Getting Started with Speckit

### Available Commands

The project integrates the following speckit commands via GitHub Copilot:

1. **`/speckit-specify`** - Create or update a feature specification
2. **`/speckit-clarify`** - Ask clarifying questions to refine specs
3. **`/speckit-plan`** - Generate implementation plan from spec
4. **`/speckit-tasks`** - Create actionable tasks from plan
5. **`/speckit-analyze`** - Analyze artifacts for consistency
6. **`/speckit-implement`** - Execute implementation tasks
7. **`/speckit-checklist`** - Generate feature checklists
8. **`/speckit-constitution`** - Update project constitution
9. **`/speckit-converge`** - Assess codebase against spec
10. **`/speckit-taskstoissues`** - Convert tasks to GitHub issues

### Workflow

1. **Start with a feature idea** → Run `/speckit-specify "Your feature description"`
2. **Clarify requirements** → Run `/speckit-clarify` for targeted questions
3. **Create a plan** → Run `/speckit-plan` to design the implementation
4. **Generate tasks** → Run `/speckit-tasks` to break down into actionable items
5. **Implement** → Run `/speckit-implement` to execute tasks
6. **Analyze quality** → Run `/speckit-analyze` to check for consistency
7. **Track in GitHub** → Run `/speckit-taskstoissues` to create issues

## Configuration

### extensions.yml
Defines hooks and extensions for the speckit workflow:
- **Pre-execution hooks:** Validation before major steps
- **Post-execution hooks:** Actions after implementation
- **Extensions:** Additional capabilities and integrations

### constitution.md
The project constitution outlines:
- Mission and core principles
- Architectural guardrails
- Non-negotiable standards
- Review checkpoints
- Version management policies

### speckit.config.json
Tracks:
- Speckit version (currently: 2.0.0)
- Project metadata
- Enabled capabilities
- Configuration preferences

### Versioning Discipline

The canonical project policy lives in [../VERSIONING.md](../VERSIONING.md).
Use that page for release rules, changelog discipline, rollout guidance, and
review expectations.

## Features Workflow

When starting a new feature:

```bash
# Create feature directory
mkdir -p .specify/features/feature-name

# Run speckit commands (in GitHub Copilot)
/speckit-specify "Your feature description"
/speckit-clarify
/speckit-plan
/speckit-tasks
/speckit-implement
```

This creates:
- `.specify/features/feature-name/spec.md`
- `.specify/features/feature-name/plan.md`
- `.specify/features/feature-name/tasks.md`

## Project Constitution

The project constitution in `memory/constitution.md` is **non-negotiable** within the speckit workflow. All specs, plans, and tasks must align with:

- Quality First (tests, types, documentation)
- User Experience (simplicity, performance, feedback)
- Maintainability (modularity, documentation, versioning)
- Openness (contributions, transparency, collaboration)

See `memory/constitution.md` for complete details.

## Speckit Version

**Current Version:** 2.0.0  
**Framework:** github-spec-kit  
**Last Updated:** 2026-09-08

For updates and documentation, visit: https://github.com/github/github-spec-kit

## Integration Points

### VS Code / GitHub Copilot
- Speckit agents and prompts are integrated with VS Code's GitHub Copilot Chat
- Use `/speckit-*` commands in Copilot Chat to interact with the framework
- Skills are defined in `../../.github/skills/`
- Agents are defined in `../../.github/agents/`
- Prompts are defined in `../../.github/prompts/`

### Git Workflow
- Speckit hooks integrate with git operations
- Feature branches recommended for spec-driven features
- Commit history tracks specification evolution

### Testing Integration
- Tests should be defined in tasks.md
- Test results inform implementation status
- Coverage requirements enforced by constitution

## Best Practices

1. **Always start with specification** - Don't skip the spec step
2. **Use clarification** - Ask targeted questions before planning
3. **Document decisions** - Include rationale in plans
4. **Break down tasks** - Keep tasks small and focused
5. **Test thoroughly** - Include tests in every task
6. **Review early** - Get feedback at each checkpoint
7. **Track progress** - Use GitHub issues for visibility
8. **Reflect on constitution** - Ensure alignment with principles
9. **Version releases consistently** - Use semantic versioning and update the
    changelog for user-facing changes

## Support

For issues or questions about speckit:
- Check the skill files in `.github/skills/speckit-*/SKILL.md`
- Review the agent documentation in `.github/agents/`
- Consult the project constitution for principles and policies
- Refer to the workflow documentation above

---

**Note:** This structure enables specification-driven development, ensuring clear requirements, thoughtful planning, and intentional implementation aligned with the project's core principles.

## Alpha technical checkpoint

On 2026-10-01, the reviewed snapshot passed 214 tests, dependency checks, the real-dialog walkthrough, and backup recovery. Architecture review and initial Ubuntu 26.04.1/Python 3.14.4/Tk 8.6.17 validation are complete. The application remains pre-alpha pending human usability review and independent developer handoff. See the [current gates](../ROADMAP.md#alpha-readiness) and [validation record](../RELEASE_PROCESS.md#alpha-technical-validation-on-2026-10-01).
