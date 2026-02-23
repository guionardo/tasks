from dataclasses import dataclass, field
from pathlib import Path

from tasks.config.config import Config, load_config_from_file
from tasks.consts import TaskStatus
from tasks.git import GitConfig
from tasks.service.task_service import read_task_from_directory
from tasks.task.task import Task


@dataclass
class Context:
    config: Config = None

    _task_cache: dict[TaskStatus, list[Task]] = field(default_factory=dict)

    def _get_tasks(self, status: TaskStatus, refresh: bool = False) -> list[Task]:
        tasks = self._task_cache.get(status, [])
        if refresh or not tasks:
            tasks_folder = Path(self.config.tasks_folder) / status.value
            if not tasks_folder.exists():
                return []
            tasks = [
                t
                for t in [read_task_from_directory(p) for p in tasks_folder.iterdir()]
                if t is not None
            ]
            tasks.sort(key=lambda x: x.id)
            # self._task_cache[status] = tasks
        return tasks

    def get_doing_tasks(self, refresh: bool = False) -> list[Task]:
        return self._get_tasks(TaskStatus.IN_PROGRESS, refresh)

    def get_done_tasks(self, refresh: bool = False) -> list[Task]:
        return self._get_tasks(TaskStatus.DONE, refresh)

    def get_todo_tasks(self, refresh: bool = False) -> list[Task]:
        return self._get_tasks(TaskStatus.TODO, refresh)

    def get_all_tasks(self, refresh: bool = False) -> list[Task]:
        return (
            self._get_tasks(TaskStatus.TODO, refresh)
            + self._get_tasks(TaskStatus.IN_PROGRESS, refresh)
            + self._get_tasks(TaskStatus.DONE, refresh)
        )

    def get_all_repos(self) -> list[GitConfig]:
        if not self.config.repos:
            self.config.add_repos_from_base_directory(self.config.base_repos_directory)
            self.config.update()
            self.config.save()
        repos = {repo.repository_name: repo for repo in self.config.repos}
        return list(repos.values())


class ContextClass:
    @property
    def context(self) -> Context:
        return get_context()


_context: Context = None


def setup_context(
    config_path: str = Path.home(), tasks_folder: str = Path.home() / 'tasks'
):
    global _context

    config_file = Config.config_file_name(config_path)
    if config_file.exists():
        config = load_config_from_file(config_file)
        config.add_repos_from_base_directory(config.base_repos_directory)
    else:
        config = Config(config_path=config_path)

    _context = Context(config=config)
    _context.config.tasks_folder = tasks_folder


def get_context() -> Context:
    if not _context:
        setup_context()
    return _context
