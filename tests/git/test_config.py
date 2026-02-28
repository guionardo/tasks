import unittest

import pytest

from tasks.git import find_repos, get_root_directory
from tasks.git.git_config import GitConfig


@pytest.mark.integration
class TestConfig(unittest.TestCase):
    def test_config(self):
        test_path = '/home/guionardofurlan/dev/tmp/wk-platform-organization-api/api'
        directory = get_root_directory(test_path)
        config = GitConfig(directory=directory)
        self.assertEqual(config.project_name, 'Platform-Core')
        self.assertEqual(config.repository_name, 'wk-platform-organization-api')
        self.assertEqual(config.remote_name, 'origin')
        self.assertEqual(
            config.remote_url,
            'ssh://titania.wk.com.br:22/WK/Platform-Core/_git/wk-platform-organization-api',
        )
        self.assertEqual(config.is_git_directory, True)


@pytest.mark.integration
class TestFindRepos(unittest.TestCase):
    def test_find_repos(self):
        for repo in find_repos('/home/guionardofurlan/dev'):
            print(repo)


class TestGetRepoNames(unittest.TestCase):
    def test_get_repo_names_supported_formats(self):
        cases = [
            (
                'https://github.com/org/repo.git',
                ('org', 'repo'),
            ),
            (
                'ssh://git@github.com:22/org/repo.git',
                ('org', 'repo'),
            ),
            (
                'git@github.com:org/repo.git',
                ('org', 'repo'),
            ),
            (
                'ssh://titania.wk.com.br:22/WK/Platform-Core/_git/wk-platform-organization-api',
                ('Platform-Core', 'wk-platform-organization-api'),
            ),
            (
                'https://dev.azure.com/org/Platform-Core/_git/wk-platform-organization-api',
                ('Platform-Core', 'wk-platform-organization-api'),
            ),
        ]
        for remote_url, expected in cases:
            with self.subTest(remote_url=remote_url):
                self.assertEqual(GitConfig.get_repo_names(remote_url), expected)
