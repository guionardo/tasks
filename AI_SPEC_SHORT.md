# AI Spec (Short) - Tasks TUI Manager

## Objective

Maintain and evolve the task management TUI application with small, safe changes compatible with current behavior.

## Quick Context

- Terminal app built with **Textual**.
- Each task clones a Git repository into a local workspace.
- Supported statuses:
  - `in_progress`
  - `done`
  - `archive` (zip)

## Critical Flows

1. **Run app**: parse CLI -> setup context -> open `Tasks`.
2. **New task**: validate id -> resolve version -> `git clone` -> create `TASK/<id>.md`.
3. **Transitions**:
   - `in_progress -> done`
   - `done -> in_progress`
   - `done -> delete`
   - `done -> archive`
4. **Open in editor**: uses `config.editor` (default `cursor`).

## Contracts that must not break

- Folder structure:
  - `<tasks_folder>/in_progress/<task-id>-<repo>`
  - `<tasks_folder>/done/<task-id>-<repo>`
  - `<tasks_folder>/archive/<task-id>-<project>-<repo>.zip`
- Config persisted in `<config-path>/.tasks.yaml`.
- TUI shortcuts must keep working.

## Main Modules

- `tasks.__main__` (entrypoint)
- `tasks.tui.*` (UI)
- `tasks.tui.context` (state and config access)
- `tasks.service.task_service` (business rules)
- `tasks.config.config` (YAML)
- `tasks.git.git_config` (Git metadata)
- `tasks.service.logging_service` (logs)

## Rules for AI

- Prioritize simplicity: avoid large refactors without need.
- Handle IO/subprocess errors explicitly.
- Do not change data layout without migration/documentation.
- Update `README.md` when functional behavior changes.
- Always write documentation in English.
- Prefer portable tests (without local environment dependencies).

## Baseline of known issues

- task creation is still synchronous in `NewTask` screen (can block UI in long operations);
- main refresh/navigation still uses recursive `push_screen` in `MainApp`;
- forms still use manual validation (no `textual.validation`);
- tasks `DataTable` can improve in ID sorting and responsiveness;
- Git authentication/access troubleshooting (SSH/HTTPS) is not yet documented in `README.md`;
- Git parsing is already more robust, but may still need refinements for less common cases;
- `get_task_oneliner` depends on `agent` CLI (with fallback to first line of description).

## Definition of Done

- main TUI flow remains functional;
- no regression in task operations;
- YAML config remains compatible;
- relevant documentation is updated;
- change is clear, small, and verifiable.

## Suggested prompt for agents

"Implement incremental changes without breaking task flows, preserving folder structure and `.tasks.yaml` compatibility. Prioritize filesystem/Git robustness, add portable tests, and update documentation whenever functional behavior changes."
