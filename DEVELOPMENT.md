# Development Guide

This document contains technical information for maintenance and evolution of the project.

For user instructions, see `README.md`.

## Architecture

### Entry point and execution

- CLI script: `tasks = "tasks.__main__:main"` in `pyproject.toml`.
- Main flow:
  1. Parse arguments (`--config-path`, `--tasks-folder`, `--log-level`, `--log-file`).
  2. Initialize context/configuration.
  3. Start Textual application (`MainApp`).

### Main layers

- `src/tasks/tui/`
  - Textual screens (`Tasks`, `NewTask`, `Setup`, `Logs`) and `.tcss` styles.
- `src/tasks/service/task_service.py`
  - Business rules: create, move, delete, archive task, open editor, clone repo.
- `src/tasks/config/config.py`
  - Configuration model and YAML serialization (`.tasks.yaml`).
- `src/tasks/git/git_config.py`
  - Repository discovery and remote parsing.
- `src/tasks/task/task.py`
  - `Task` entity and ID parser.

## Configuration Details

Default configuration file:

- `<config-path>/.tasks.yaml`

Relevant fields:

- `config_path`
- `repos`
- `unique_repos` (`repository_name -> remote_url`)
- `base_repos_directory`
- `last_sync`
- `tasks_folder`

## Git Parsing (current status)

- Remote discovery prioritizes `git` CLI:
  - `git remote`
  - `git remote get-url --push`
  - fallback to `git remote get-url` and `git config --get remote.<name>.url`
- If needed, there is fallback to reading `.git/config`.
- `get_repo_names` supports:
  - HTTPS
  - SSH (`ssh://...`)
  - SCP-like (`git@host:org/repo.git`)
  - Azure DevOps with `/_git/`.

## Logs (implementation)

- Initialized at app startup.
- Destinations:
  - in-memory buffer (logs screen)
  - rotating file at `<config-path>/tasks.log`
- Handler: `TimedRotatingFileHandler` (2-minute interval, `backupCount=10`).

## Build and Packaging

- Backend: `uv_build`
- Include source and styles in build:
  - `[tool.uv.build-backend]`
  - `source-include = ["**/*.tcss", "**/*.py"]`

## Tests

Run:

```bash
uv run pytest -q
```

Run non-integration tests only:

```bash
uv run pytest -q -m "not integration"
```

Run integration tests only:

```bash
uv run pytest -q -m "integration"
```

Validated local state:

- `7 passed, 5 subtests passed`

Notes:

- Service tests use mocks to avoid environment/network dependencies.
- New tests should keep the same isolation pattern (fixtures/mocks).

## Project Structure

```text
src/tasks/
  __main__.py
  config/config.py
  consts/__init__.py
  git/git_config.py
  service/
    logging_service.py
    task_service.py
  task/task.py
  tui/
    app.py
    args.py
    context.py
    logs_screen.py
    new_task_screen.py
    settings_screen.py
    tasks_screen.py
    *.tcss
tests/
  config/
  git/
  service/
```

## Known Limitations

- Remote discovery is more robust now, but may still need adjustments for uncommon Git scenarios.
- `get_task_oneliner` depends on `agent` CLI; without it, the service falls back to the first line of the description.

## TO-DO

- [ ] Replace `RadioSet`-based lists with `DataTable` in task listing screens.
- [ ] Migrate task creation (`new_task`) to `Worker` in `NewTask` screen to avoid UI blocking during clone/processing.
- [ ] Review `MainApp` navigation flow to reduce recursive `push_screen` and adopt a more predictable refresh/screen-switching strategy.
- [ ] Apply native Textual validation (`textual.validation`) in forms (`Setup` and `NewTask`) with inline feedback.
- [ ] Improve tasks `DataTable` experience (sort by `Task ID`, width adjustments for smaller terminals).
- [ ] Document Git authentication/access troubleshooting (SSH/HTTPS) in `README.md`.
- [ ] Refine remote discovery/parsing for less common Git scenarios (worktrees, non-standard remotes, etc.).
- [ ] Implement pipy push
- [ ] Update README to allow install from pipy or from github
