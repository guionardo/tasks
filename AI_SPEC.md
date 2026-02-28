# AI Specification - Tasks TUI Manager

## 1. Purpose

This document defines an operational specification for AI agents that will analyze, maintain, or evolve the **Tasks TUI Manager** project.

Main AI objective:

- maintain current functional behavior;
- implement changes incrementally and safely;
- preserve architectural simplicity;
- prioritize reliability in filesystem and Git operations.

## 2. Product Context

The system is a **TUI** (terminal user interface), built with **Textual**, for managing development tasks based on Git repositories.

Each task represents a local workspace cloned from a Git remote and organized by status:

- `in_progress`
- `done`
- `archive`

## 3. Primary User Flows

### 3.1 Run Application

1. User runs `tasks` or `python -m tasks`.
2. System processes CLI arguments (`--config-path`, `--tasks-folder`, `--log-level`, `--log-file`).
3. Global context is initialized.
4. `MainApp` starts and opens the tasks screen.

### 3.2 Create New Task

1. User opens the creation screen (`n`).
2. Provides task id, repository, and description.
3. System computes task version (auto-increment when needed).
4. Executes `git clone`.
5. Creates `TASK/` folder and `<task-id>.md` file.
6. Updates persisted configuration (`.tasks.yaml`).

### 3.3 Task Status Transition

- `in_progress -> done` (shortcut `>`)
- `done -> in_progress` (shortcut `<`)
- `done -> deleted` (shortcut `x`)
- `done -> archive zip` (shortcut `a`)

### 3.4 Open in Editor

1. User selects a task.
2. System calls configured editor (`config.editor`, default `cursor`).
3. For `cursor`/`code`, opens `TASK/<task-id>.md` with `-g` when available.

## 4. Functional Scope

### 4.1 Included

- TUI execution;
- YAML configuration read/write;
- repository discovery in directories;
- task operations (create, move, delete, archive);
- logging in memory buffer and rotating file.

### 4.2 Excluded (Current Scope)

- advanced Git authentication;
- multi-tenant profile/config;
- distributed or remote synchronization of task state;
- HTTP API.

## 5. Technical Architecture

### 5.1 Module Layout

- `tasks.__main__`: entrypoint.
- `tasks.tui.*`: UI/screens.
- `tasks.tui.context`: global context and config/tasks loading.
- `tasks.config.config`: configuration model and persistence.
- `tasks.service.task_service`: task business rules.
- `tasks.service.logging_service`: setup/log buffer/export.
- `tasks.git.git_config`: `.git/config` reading and repo discovery.
- `tasks.task.task`: `Task` entity and id parser.

### 5.2 State and Persistence

- Configuration persisted in `<config-path>/.tasks.yaml`.
- Tasks persisted in directory structure under `tasks_folder`.
- Logs persisted in:
  - memory (for logs screen),
  - `<config-path>/tasks.log` with time-based rotation.

## 6. Data Contracts

### 6.1 Task Identity

- Expected format: `<number>-<version>`.
- When version is not provided, assume `0`.
- Example:
  - input: `123`
  - normalized: `123-0`

### 6.2 Task Folder Naming

- `in_progress/<task-id>-<repository-name>`
- `done/<task-id>-<repository-name>`
- `archive/<task-id>-<project-name>-<repository-name>.zip`

### 6.3 Config File (`.tasks.yaml`)

Minimum fields:

- `config_path`
- `repos`
- `unique_repos`
- `base_repos_directory`
- `last_sync`
- `tasks_folder`

## 7. Non-Functional Requirements for AI Changes

### 7.1 Reliability

- never assume directories exist without validation;
- explicitly handle subprocess and filesystem errors;
- avoid data loss in status transitions.

### 7.2 Simplicity

- prefer small, local changes;
- avoid introducing extra layers unnecessarily;
- keep service APIs simple and explicit.

### 7.3 Compatibility

- preserve current TUI shortcut and screen behavior;
- preserve task directory layout;
- preserve `.tasks.yaml` format unless changes are planned.

### 7.4 Observability

- keep logging clear for critical flows:
  - clone;
  - task movement;
  - archiving;
  - IO/subprocess failures.

## 8. Current Known Gaps (Baseline)

- task creation (`new_task`) still runs synchronously on the creation screen and may block UI during long operations.
- navigation flow in `MainApp` uses recursive `push_screen` for task screen refresh.
- forms (`Setup`/`NewTask`) still use manual validation; no native Textual validation yet.
- tasks `DataTable` experience can improve (sorting by `Task ID`, width adjustments in smaller terminals).
- Git authentication/access troubleshooting (SSH/HTTPS) is not yet documented in `README.md`.
- remote discovery/parsing is already robust, but may need refinements for less common Git scenarios.
- `get_task_oneliner` depends on `agent` CLI; without it, it falls back to the first line of the description.

## 9. AI Implementation Guidelines

### 9.1 Change Strategy

1. Read target files and map impact.
2. Implement minimal change.
3. Validate local execution of affected commands.
4. Update documentation when there is a functional change.

### 9.2 Testing Strategy

For each business rule change:

- add/adjust focused unit tests;
- avoid dependence on external environment;
- use temporary directories and subprocess mocks.

### 9.3 Documentation Strategy

Update `README.md` whenever there are:

- new CLI arguments;
- new task flow;
- change in folder/config structure;
- change in build/distribution.
- always write documentation in English.

## 10. Acceptance Criteria for AI Tasks

A change is considered done when:

- the main TUI behavior remains functional;
- there is no regression in task creation/movement flows;
- configuration continues to serialize correctly in YAML;
- relevant documentation is updated;
- changes are small, readable, and clearly intentional.

## 11. Suggested Roadmap for AI

### Short Term

- migrate task creation (`new_task`) to `Worker` in `NewTask` screen;
- apply native Textual validation (`textual.validation`) in `Setup` and `NewTask`;
- improve tasks `DataTable` (sorting and column responsiveness).

### Medium Term

- review `MainApp` navigation/refresh flow to reduce `push_screen` recursion;
- document Git authentication/access troubleshooting (SSH/HTTPS) in `README.md`;
- refine handling of less common Git scenarios (worktrees and non-standard remotes).

### Long Term

- export/import of task snapshots;
- support templates for `TASK/<id>.md` files;
- optional integration with work item providers.

## 12. Operational Prompt for Future AI Agents

Use this project with the following priorities:

1. preserve current user flow in the TUI;
2. prefer simplicity and incremental changes;
3. do not break task folder structure;
4. keep `.tasks.yaml` compatibility;
5. cover changes with portable tests;
6. keep README consistent with real behavior.
