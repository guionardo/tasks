import tempfile
from datetime import datetime
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch

from tasks.config.config import Config
from tasks.consts import TaskStatus
from tasks.service.task_service import clone_repository, new_task


class TestTaskService(TestCase):
    @patch('tasks.service.task_service.subprocess.run')
    def test_clone_repository(self, mock_run):
        repo_url = 'https://example.com/org/repo.git'
        with tempfile.TemporaryDirectory() as tmp_dir:
            new_task_folder = Path(tmp_dir) / 'test_tasks'
            mock_run.return_value = Mock(returncode=0, stdout=b'', stderr=b'')
            cloned_path = clone_repository(repo_url, new_task_folder)

            self.assertEqual(cloned_path, new_task_folder)
            mock_run.assert_called_once_with(
                ['git', 'clone', repo_url, str(new_task_folder)],
                check=False,
                env=clone_repository.__globals__['os'].environ,
                capture_output=True,
                cwd=str(new_task_folder.parent),
            )


class TestNewTask(TestCase):
    @patch('tasks.service.task_service.get_task_oneliner', return_value='test oneliner')
    @patch('tasks.service.task_service.get_existing_tasks', return_value=[])
    @patch('tasks.service.task_service.clone_repository')
    def test_new_task(
        self, mock_clone_repository, _mock_get_existing_tasks, _mock_oneliner
    ):
        repo_url = 'https://example.com/org/repo.git'
        with tempfile.TemporaryDirectory() as tmp_dir:
            new_task_folder = Path(tmp_dir) / 'test_tasks'
            config = Config(config_path=tmp_dir, tasks_directory=str(new_task_folder))
            task_description = """# Description
            This is a test task description.
            """
            task_output_folder = config.doing_tasks_directory / '1234-0-repo'
            git_config_folder = task_output_folder / '.git'
            git_config_folder.mkdir(parents=True, exist_ok=True)
            (git_config_folder / 'config').write_text(
                '[remote "origin"]\n\turl = https://example.com/org/repo.git\n',
                encoding='utf-8',
            )

            mock_clone_repository.return_value = task_output_folder
            task, message = new_task(config, '1234-0', repo_url, task_description)

            self.assertIn('New task 1234-0', message)
            self.assertIsNotNone(task)
            self.assertEqual(task.id, '1234-0')
            self.assertEqual(task.repo.remote_url, repo_url)
            self.assertEqual(task.status, TaskStatus.IN_PROGRESS)
            self.assertIsInstance(task.created_at, datetime)
            self.assertIsInstance(task.updated_at, datetime)
            self.assertGreaterEqual(task.updated_at, task.created_at)
            self.assertTrue(task_output_folder.exists())
            self.assertTrue((task.directory / '.git').exists())
