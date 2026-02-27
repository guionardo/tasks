import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from tasks.consts import BASE_CONFIG_PATH, TaskStatus
from tasks.git import GitConfig, find_repos

CONFIG_FILE = '.tasks.yaml'


@dataclass
class Config:
    config_path: str = field(default=BASE_CONFIG_PATH)
    repos: list[GitConfig] = field(default_factory=list)
    unique_repos: dict[str, str] = field(default_factory=dict)
    base_repos_directory: str = field(default='')
    last_sync: int = field(default=0)
    tasks_directory: str = field(default='')
    editor: str = field(default='cursor')
    log_level: str = field(default=logging.INFO)
    log_file: str = field(default=(BASE_CONFIG_PATH / 'tasks.log').as_posix())

    def __post_init__(self):
        config_file = Path(self.config_path) / CONFIG_FILE

        base_repos_directory = self.base_repos_directory

        if config_file.exists():
            self = Config.load(config_file)

        if self.tasks_directory and int(time.time()) - self.last_sync > 60 * 60:
            self._find_repos()

        else:
            self.repos = []

        if base_repos_directory:
            self.add_repos_from_base_directory(base_repos_directory)
        if self.base_repos_directory:
            self.add_repos_from_base_directory(self.base_repos_directory)

        self.update()

    def _find_repos(self):
        """Read all repos from base_repos_directory and updates the unique_repos dictionary"""
        self.repos.clear()
        self.unique_repos.clear()
        for repo_folder in [self.tasks_directory, self.base_repos_directory]:
            for git_config in find_repos(repo_folder):
                self.repos.append(git_config)
                self.unique_repos[git_config.repository_name] = git_config.remote_url

    def to_dict(self) -> dict:
        as_dict = asdict(self)
        for key, value in asdict(self).items():
            if isinstance(value, Path):
                as_dict[key] = str(value)
            elif isinstance(value, list):
                as_dict[key] = [str(item) for item in value]
            elif isinstance(value, dict):
                as_dict[key] = {str(key): str(value) for key, value in value.items()}

        return as_dict

    def save(self):
        config_file = Path(self.config_path) / CONFIG_FILE
        save_config_to_file(self, config_file)

    @classmethod
    def load(cls, config_file: str) -> 'Config':
        return load_config_from_file(config_file)

    @staticmethod
    def config_file_name(config_path: str) -> Path:
        return Path(config_path) / CONFIG_FILE

    def update(self):
        for repo in self.repos:
            if str(repo.directory).startswith(str(self.base_repos_directory)):
                self.unique_repos[repo.repository_name] = repo.remote_url
                if not self.base_repos_directory:
                    self.base_repos_directory = repo.directory
                elif str(self.base_repos_directory).startswith(str(repo.directory)):
                    self.base_repos_directory = repo.directory

    @property
    def doing_tasks_directory(self) -> Path:
        p = Path(self.tasks_directory) / TaskStatus.IN_PROGRESS.value
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def done_tasks_directory(self) -> Path:
        p = Path(self.tasks_directory) / TaskStatus.DONE.value
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def archive_tasks_directory(self) -> Path:
        p = Path(self.tasks_directory) / TaskStatus.ARCHIVE.value
        p.mkdir(parents=True, exist_ok=True)
        return p

    def add_repos_from_base_directory(self, base_directory: str) -> 'Config':
        base_directory = Path(base_directory)

        for repo in find_repos(base_directory):
            if not repo.is_git_directory:
                continue
            self.repos.append(repo)
            self.unique_repos[repo.repository_name] = repo.remote_url
            if not self.base_repos_directory:
                self.base_repos_directory = repo.directory
            elif str(self.base_repos_directory).startswith(str(repo.directory)):
                self.base_repos_directory = repo.directory
        return self


_config: Config = None


def get_config() -> Config:
    global _config
    if not _config:
        _config = Config()
    return _config


def _marshal_git_config(repo: GitConfig) -> dict[str, Any]:
    return asdict(repo)


def _unmarshal_git_config(raw_repo: Any) -> GitConfig | None:
    if isinstance(raw_repo, str):
        return GitConfig(directory=raw_repo)
    if not isinstance(raw_repo, dict):
        return None

    directory = str(raw_repo.get('directory', '.'))
    repo = GitConfig(directory=directory)

    # Preserve serialized values for init=False fields when available.
    for field_name, value in raw_repo.items():
        if hasattr(repo, field_name):
            setattr(repo, field_name, value)
    return repo


def _marshal_config(config: Config) -> dict[str, Any]:
    return {
        'config_path': str(config.config_path),
        'repos': [_marshal_git_config(repo) for repo in config.repos],
        'unique_repos': {
            str(key): str(value) for key, value in config.unique_repos.items()
        },
        'base_repos_directory': str(config.base_repos_directory),
        'last_sync': int(config.last_sync),
        'tasks_folder': str(config.tasks_directory),
    }


def save_config_to_file(config: Config, config_file: str | Path) -> None:
    config_path = Path(config_file)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open('w', encoding='utf-8') as file:
        yaml.safe_dump(_marshal_config(config), file, sort_keys=False)


def load_config_from_file(config_file: str | Path) -> Config:
    config_path = Path(config_file)
    data: dict[str, Any] = {}

    if config_path.exists():
        with config_path.open('r', encoding='utf-8') as file:
            loaded = yaml.safe_load(file) or {}
            if isinstance(loaded, dict):
                data = loaded

    config = Config.__new__(Config)
    config.config_path = str(data.get('config_path', config_path.parent))
    config.repos = []
    for raw_repo in data.get('repos', []):
        repo = _unmarshal_git_config(raw_repo)
        if repo:
            config.repos.append(repo)

    unique_repos = data.get('unique_repos', {})
    if isinstance(unique_repos, dict):
        config.unique_repos = {
            str(key): str(value) for key, value in unique_repos.items()
        }
    else:
        config.unique_repos = {}

    config.base_repos_directory = str(data.get('base_repos_directory', ''))
    config.last_sync = int(data.get('last_sync', 0))
    config.tasks_directory = str(data.get('tasks_folder', ''))

    if not config.unique_repos:
        config.unique_repos = {
            repo.repository_name: repo.remote_url
            for repo in config.repos
            if repo.repository_name
        }

    if not config.base_repos_directory:
        for repo in config.repos:
            if not config.base_repos_directory:
                config.base_repos_directory = repo.directory
            elif str(config.base_repos_directory).startswith(str(repo.directory)):
                config.base_repos_directory = repo.directory

    return config
