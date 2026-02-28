import tempfile
import unittest
from pathlib import Path

import pytest

from tasks.config.config import Config


@pytest.mark.integration
class TestConfig(unittest.TestCase):
    def test_config(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / '.tasks.yaml'
            config = Config(
                config_path=tmp_dir, base_repos_directory=Path.home() / 'dev'
            )
            config.save()

            config2 = Config.load(config_file)
            self.assertDictEqual(config.unique_repos, config2.unique_repos)
            self.assertEqual(
                str(config.base_repos_directory), str(config2.base_repos_directory)
            )
            self.assertListEqual(config.repos, config2.repos)


# class TestConfigService(TestCase):
#     def test_save_and_load_config_yaml(self):
#         with tempfile.TemporaryDirectory() as tmp_dir:
#             config_file = Path(tmp_dir) / '.tasks.yaml'
#             repo = GitConfig(directory=tmp_dir)
#             repo.is_git_directory = True
#             repo.remote_name = 'origin'
#             repo.remote_url = 'https://example.com/org/repo.git'
#             repo.project_name = 'org'
#             repo.repository_name = 'repo'
#             repo.readme_description = 'Repo Description'

#             config = Config(config_path=tmp_dir, tasks_folder='')
#             config.repos = [repo]
#             config.unique_repos = {'repo': repo.remote_url}
#             config.base_repos_directory = tmp_dir
#             config.last_sync = 123
#             config.tasks_folder = str(Path(tmp_dir) / 'tasks')

#             save_config_to_file(config, config_file)
#             loaded = load_config_from_file(config_file)

#             self.assertIsInstance(loaded, Config)
#             self.assertEqual(loaded.config_path, tmp_dir)
#             self.assertEqual(loaded.base_repos_directory, tmp_dir)
#             self.assertEqual(loaded.last_sync, 123)
#             self.assertEqual(loaded.tasks_folder, str(Path(tmp_dir) / 'tasks'))
#             self.assertEqual(loaded.unique_repos, {'repo': repo.remote_url})
#             self.assertEqual(len(loaded.repos), 1)
#             self.assertEqual(loaded.repos[0].directory, tmp_dir)
#             self.assertEqual(loaded.repos[0].repository_name, 'repo')
#             self.assertEqual(loaded.repos[0].remote_url, repo.remote_url)

#     def test_load_missing_file_returns_default_config(self):
#         with tempfile.TemporaryDirectory() as tmp_dir:
#             config_file = Path(tmp_dir) / '.tasks.yaml'
#             loaded = load_config_from_file(config_file)
#             self.assertIsInstance(loaded, Config)
#             self.assertEqual(loaded.config_path, tmp_dir)
#             self.assertEqual(loaded.repos, [])
