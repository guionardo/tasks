from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from tasks.consts import TaskStatus
from tasks.git import GitConfig


@dataclass
class Task:
    id: str
    repo: GitConfig
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    @property
    def name(self) -> str:
        return f'{self.repo.project_name}/{self.repo.repository_name}'

    @property
    def archive_name(self) -> str:
        return Path(
            f'{self.id}-{self.repo.project_name}-{self.repo.repository_name}'
        ).as_posix()

    @property
    def short_name(self) -> str:
        return f'{self.id} - {self.repo.repository_name}'

    @property
    def description(self) -> str:
        return self.repo.readme_description

    @property
    def directory(self) -> Path:
        return Path(self.repo.directory)

    @property
    def short_directory(self) -> str:
        return str(self.directory).replace(str(Path.home()), '~')


def parse_task_id(task_id: str) -> tuple[str, str]:
    """Extract the task number and the iteration number from the task id
    Ex: 1234-0 -> (1234, 0)
    Ex: 1234 -> (1234, 0)
    """
    parts = task_id.split('-', 2)[:2]
    if len(parts) == 2 and parts[1].isdigit():
        return parts[0], parts[1]
    return parts[0], '0'
