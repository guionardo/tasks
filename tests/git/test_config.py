import unittest

import pytest

from tasks.git import find_repos, get_root_directory
from tasks.git.git_config import GitConfig


class TestConfig(unittest.TestCase):
    def test_config(self):
        test_path = __file__
        directory = get_root_directory(test_path)
        config = GitConfig(directory=directory)
        self.assertEqual(config.project_name, 'guionardo')
        self.assertEqual(config.repository_name, 'tasks')
        self.assertEqual(config.remote_name, 'origin')
        self.assertIn(
            config.remote_url,
            [
                'git@github.com:guionardo/tasks.git',
                'https://github.com/guionardo/tasks',
            ],
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
                'ssh://somewhere.com.br:22/guionardo/tasks/_git/tasks',
                ('tasks', 'tasks'),
            ),
            (
                'https://dev.azure.com/guionardo/tasks/_git/tasks',
                ('tasks', 'tasks'),
            ),
        ]
        for remote_url, expected in cases:
            with self.subTest(remote_url=remote_url):
                self.assertEqual(GitConfig.get_repo_names(remote_url), expected)
