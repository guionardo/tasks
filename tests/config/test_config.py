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
