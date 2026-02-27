import tempfile
from datetime import datetime
from pathlib import Path
from unittest import TestCase

from src.tasks.config.config import Config
from src.tasks.consts import TaskStatus
from src.tasks.service.task_service import clone_repository, new_task


class TestTaskService(TestCase):
    def test_clone_repository(self):
        repo_url = 'ssh://titania.wk.com.br:22/WK/Platform-Core/_git/wk-platform-organization-api'
        with tempfile.TemporaryDirectory() as tmp_dir:
            new_task_folder = Path(tmp_dir) / 'test_tasks'
            clone_repository(repo_url, new_task_folder)
            self.assertTrue(new_task_folder.exists())
            self.assertTrue((new_task_folder / '.git').exists())


class TestNewTask(TestCase):
    def test_new_task(self):
        repo_url = 'ssh://titania.wk.com.br:22/WK/Platform-Core/_git/wk-platform-organization-api'
        now = datetime.now()
        with tempfile.TemporaryDirectory() as tmp_dir:
            new_task_folder = Path(tmp_dir) / 'test_tasks'
            config = Config(config_path=tmp_dir, tasks_directory=str(new_task_folder))
            task_description = """# Description
            This is a test task description.
            """
            task = new_task(config, '1234-0', repo_url, task_description)

            self.assertEqual(task.id, '1234-0')
            self.assertEqual(task.repo.remote_url, repo_url)
            self.assertEqual(task.status, TaskStatus.IN_PROGRESS)
            self.assertGreater(task.created_at, now)
            self.assertGreater(task.updated_at, now)
            self.assertTrue(new_task_folder.exists())
            self.assertTrue((task.directory / '.git').exists())

            config.save()

            new_config = Config(
                config_path=tmp_dir, tasks_directory=str(new_task_folder)
            )

            print(new_config.to_dict())
