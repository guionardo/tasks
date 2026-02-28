# Tasks TUI Manager

Terminal application (TUI) to organize development tasks based on Git repositories.

With it, you can:

- create a task from a remote repository;
- work with statuses (`in_progress`, `done`, `archive`);
- open the task in the configured editor;
- archive completed tasks as `.zip`;
- view and export session logs.

## Requirements

- Python `>=3.12`
- `uv` (recommended for execution)
- Git available in `PATH`
- access to the remote repository used in tasks (SSH/HTTPS)
- Cursor `agent` CLI available in `PATH` (optional, recommended for generating oneliner with `Ctrl+G`)

## Installation

```bash
uv sync
```

## Run

```bash
uv run tasks
```

Alternative:

```bash
uv run python -m tasks
```

## CLI Options

```bash
uv run tasks --help
```

Main arguments:

- `--config-path`: directory where `.tasks.yaml` will be saved;
- `--tasks-folder`: root directory for tasks;
- `--log-level`: log level (e.g. `INFO`, `DEBUG`);
- `--log-file`: log file path.

Example:

```bash
uv run tasks --config-path ~/.config/tasks --tasks-folder ~/tasks
```

## Folder Structure

```text
<tasks_folder>/
  in_progress/
    123-0-repository-a/
      .git/
      TASK/
        .gitignore
        123-0.md
  done/
    123-0-repository-a/
  archive/
    123-0-project-repository-a.zip
```

## Interface Shortcuts

Global shortcuts:

- `esc`: exit the application
- `s`: open setup screen
- `l`: open logs screen

On the tasks screen:

- `n`: new task
- `e`: open task in editor
- `>`: move to `done`
- `<`: move to `in_progress`
- `x`: delete `done` task
- `r`: refresh task list
- `a`: archive `done` task

## Usage Flow

1. Create a task by providing ID, repository, and description.
2. The tool clones the repository into `in_progress/<task-id>-<repository-name>`.
3. The `TASK/` folder with the task markdown file is created automatically.
4. When finished, move it to `done` and optionally archive it to `archive`.

## Logs

- Logs are available in the `Logs` screen.
- The main log file is stored at `<config-path>/tasks.log`.

## Cursor `agent` CLI Setup

The oneliner generation feature (`Ctrl+G` on the new task screen) uses the `agent` CLI.

### 1) Install and authenticate

- Install Cursor in the environment where the TUI runs.
- Ensure the `agent` CLI is available in `PATH`.
- Sign in to Cursor/CLI according to your environment.

### 2) Validate installation

```bash
agent --help
```

If the command shows help/usage output, the CLI is available.

### 3) Behavior when `agent` is not available

If the `agent` CLI is not configured, the TUI still works and uses a fallback:

- the oneliner becomes the first line of the task description.

So automatic generation improves summary quality, but it does not block task creation.

## Technical Documentation

Architecture, tests, internal structure, and maintenance details are available in `DEVELOPMENT.md`.
