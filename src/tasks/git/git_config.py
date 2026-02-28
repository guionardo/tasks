import os
import re
import subprocess
from dataclasses import dataclass, field
from typing import Generator
from urllib.parse import urlparse

from tasks.service.logging_service import get_logger


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
        logger = get_logger(__name__)
        self.directory = os.path.abspath(self.directory)
        if not os.path.exists(os.path.join(self.directory, '.git', 'config')):
            logger.warning('Not a git directory: %s', self.directory)
            return

        remote_name, remote_url = self._read_remote_from_git()
        if not (remote_name and remote_url):
            remote_name, remote_url = self._read_remote_from_config_file()

        if not (remote_name and remote_url):
            logger.warning(
                'Misconfigured git directory: %s - remote_name: %s, remote_url: %s',
                self.directory,
                remote_name,
                remote_url,
            )
            return

        project_name, repository_name = self.get_repo_names(remote_url)
        if not (project_name and repository_name):
            logger.warning(
                'Misconfigured git directory: %s - project_name: %s, repository_name: %s',
                self.directory,
                project_name,
                repository_name,
            )
            return

        self.remote_name = remote_name
        self.remote_url = remote_url
        self.is_git_directory = True
        self.project_name = project_name
        self.repository_name = repository_name
        self.readme_description = self.get_readme_description(self.directory)
        logger.info('%s', self)

    def _read_remote_from_git(self) -> tuple[str, str]:
        logger = get_logger(__name__)
        remotes_result = subprocess.run(
            args=['git', '-C', self.directory, 'remote'],
            check=False,
            capture_output=True,
            text=True,
        )
        if remotes_result.returncode != 0:
            return '', ''

        remotes = [line.strip() for line in remotes_result.stdout.splitlines() if line]
        if not remotes:
            return '', ''

        remote_name = 'origin' if 'origin' in remotes else remotes[0]

        for command in [
            ['git', '-C', self.directory, 'remote', 'get-url', '--push', remote_name],
            ['git', '-C', self.directory, 'remote', 'get-url', remote_name],
            [
                'git',
                '-C',
                self.directory,
                'config',
                '--get',
                f'remote.{remote_name}.url',
            ],
        ]:
            result = subprocess.run(
                args=command,
                check=False,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and result.stdout.strip():
                return remote_name, result.stdout.strip()
            if result.stderr.strip():
                logger.debug('Failed command %s: %s', command, result.stderr.strip())

        return '', ''

    def _read_remote_from_config_file(self) -> tuple[str, str]:
        current_remote_name = ''
        config_path = os.path.join(self.directory, '.git', 'config')
        for line in open(config_path, encoding='utf-8').readlines():
            line = line.strip()
            if line.startswith('[remote "'):
                current_remote_name = line.split('"')[1]
            if current_remote_name and line.startswith('url = '):
                remote_url = line.split('=', 1)[1].strip()
                if remote_url:
                    return current_remote_name, remote_url
        return '', ''

    @staticmethod
    def get_repo_names(remote_url: str) -> tuple[str, str]:
        remote_url = (remote_url or '').strip().rstrip('/')
        if not remote_url:
            return '', ''

        # Handle SCP-like syntax: git@host:org/repo.git
        scp_match = re.match(
            r'^(?:(?P<user>[^@/:]+)@)?(?P<host>[^:]+):(?P<path>.+)$', remote_url
        )
        if scp_match and not remote_url.startswith('file://'):
            path = scp_match.group('path')
        else:
            parsed = urlparse(remote_url)
            path = parsed.path
            if parsed.scheme == 'file' and not path and parsed.netloc:
                path = parsed.netloc

        names = [name for name in path.split('/') if name]
        if not names:
            return '', ''

        if '_git' in names:
            idx = names.index('_git')
            if idx > 0 and idx < len(names) - 1:
                project = names[idx - 1]
                repository = names[idx + 1]
                return project, repository.removesuffix('.git')

        if len(names) >= 2:
            return names[-2], names[-1].removesuffix('.git')
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
