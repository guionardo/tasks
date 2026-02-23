import os
from dataclasses import dataclass, field
from typing import Generator


@dataclass
class GitConfig:
    directory: str = field(default='.')
    is_git_directory: bool = field(default=False, init=False)
    remote_name: str = field(default='', init=False)
    remote_url: str = field(default='', init=False)
    project_name: str = field(default='', init=False)
    repository_name: str = field(default='', init=False)
    readme_description: str = field(default='', init=False)

    def __post_init__(self):
        self.directory = os.path.abspath(self.directory)
        if not os.path.exists(os.path.join(self.directory, '.git', 'config')):
            return

        remote_name, remote_url = '', ''
        for line in open(os.path.join(self.directory, '.git', 'config')).readlines():
            line = line.strip()
            if line.startswith('[remote "'):
                remote_name = line.split('"')[1]
            if remote_name and line.startswith('url = '):
                remote_url = line.split('=')[1].strip()
                break

        if not (remote_name and remote_url):
            return

        project_name, repository_name = self.get_repo_names(remote_url)
        if not (project_name and repository_name):
            return

        self.remote_name = remote_name
        self.remote_url = remote_url
        self.is_git_directory = True
        self.project_name = project_name
        self.repository_name = repository_name
        self.readme_description = self.get_readme_description(self.directory)

    @staticmethod
    def get_repo_names(remote_url: str) -> tuple[str, str]:
        names = remote_url.replace('_git/', '').split('/')
        if len(names) > 2:
            return names[-2], names[-1].replace('.git', '')
        return '', ''

    def get_readme_description(self, directory: str) -> str:
        readme_path = os.path.join(directory, 'README.md')
        if not os.path.exists(readme_path):
            return ''
        for line in open(readme_path, 'r').readlines():
            if line.startswith('# '):
                return line.removeprefix('# ').strip()
        return ''


def find_repos(base_path: str) -> Generator[GitConfig, None, None]:
    for root, dirs, _ in os.walk(base_path):
        if '.git' in dirs:
            yield GitConfig(directory=root)


def get_root_directory(directory: str) -> str:
    directory = os.path.abspath(directory)

    current = directory
    while not os.path.exists(os.path.join(current, '.git')) and current != '/':
        current = os.path.dirname(current)
    return current if os.path.exists(os.path.join(current, '.git')) else None
