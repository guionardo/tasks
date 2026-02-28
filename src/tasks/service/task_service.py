import json
import os
import shutil
import subprocess
import tempfile
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

from tasks.config.config import Config
from tasks.consts import TaskStatus
from tasks.git import GitConfig
from tasks.service.logging_service import get_logger
from tasks.task.task import Task, parse_task_id


def new_task(
    config: Config,
    task_id: str,
    remote_url: str,
    task_description: str,
) -> tuple[Task, str]:
    """Create a new task, cloning the repository and creating the task helper files
    returns the new task and a message to be displayed to the user
    """
    logger = get_logger(__name__)
    logger.info('Creating new task: %s for %s', task_id, remote_url)
    logger.info('Task description: %s', task_description)
    task_dict = OrderedDict()

    tasks_folder = config.doing_tasks_directory
    task_number, task_version = parse_task_id(task_id)

    if existing_tasks := get_existing_tasks(config, task_number):
        last_task = existing_tasks[-1]

        if not task_description:
            # Get the last task description and increment the task version
            task_readme_file = Path(last_task.directory) / 'TASK' / f'{last_task.id}.md'
            if task_readme_file.exists():
                with open(task_readme_file, 'r') as f:
                    task_description = f.read()
                task_dict['task_description'] = '* Using last task description'

        old_task_version = f'{task_number}-{task_version}'
        task_version = str(int(last_task.id.split('-')[1]) + 1)
        task_dict['task_version'] = (
            f'New task [{task_number}-{task_version}] - {old_task_version} already exists'
        )

    else:
        task_version = '0'
        task_dict['task_version'] = f'New task {task_number}-{task_version}'

    task_id = f'{task_number}-{task_version}'

    project_name, repository_name = GitConfig.get_repo_names(remote_url)
    task_dict['project_name'] = (
        f'* Project name: {project_name} / Repository name: {repository_name}'
    )
    new_task_folder = tasks_folder / f'{task_id}-{repository_name}'
    task: Task = None
    try:
        new_task_folder = clone_repository(remote_url, new_task_folder)
        task_dict['git'] = f'* Cloned repository {remote_url} to {new_task_folder}'
        if not new_task_folder.exists():
            raise RuntimeError(
                f'Failed to clone repository: {remote_url} to {new_task_folder}'
            )
        # Create task helper files
        task_helper_folder = new_task_folder / 'TASK'
        task_helper_folder.mkdir(parents=True, exist_ok=True)
        task_dict['task_helper'] = f'Created task helper folder {task_helper_folder}'
        with open(task_helper_folder / '.gitignore', 'w') as f:
            f.write('*\n')

        with open(task_helper_folder / f'{task_id}.md', 'w') as f:
            f.write(task_description)

        repo = GitConfig(directory=str(new_task_folder))
        config.unique_repos[repository_name] = remote_url
        config.save()
        task = Task(
            task_id,
            repo,
            TaskStatus.IN_PROGRESS,
            datetime.fromtimestamp(new_task_folder.stat().st_ctime),
            datetime.now(),
        )

        task.oneliner = get_task_oneliner(task_description)
    except Exception as e:
        task_dict['error'] = f'* Error: {e}'

    message = '\n'.join(str(line) for line in task_dict.values())
    for line in task_dict.values():
        logger.info(line)
    return task, message


def get_task_data_candidate(
    config: Config, task_id: str, repository_name: str
) -> tuple[str, str, str]:
    """Get the last task data candidate for a given task id
    Returns the new task id, last task description, last task oneliner, and repository name"""
    task_number, task_version = parse_task_id(task_id)
    new_task_folder = (
        Path(config.doing_tasks_directory) / f'{task_id}-{repository_name}'
    ).as_posix()
    if not (existing_tasks := get_existing_tasks(config, task_number)):
        return f'{task_number}-{task_version}', '', '', '', ''

    last_task = existing_tasks[-1]
    task_description, task_oneliner = '', ''

    # Get the last task description and increment the task version
    task_readme_file = Path(last_task.directory) / 'TASK' / f'{last_task.id}.md'
    if task_readme_file.exists():
        with open(task_readme_file, 'r') as f:
            task_description = f.read()
    task_oneliner_file = Path(last_task.directory) / 'TASK' / 'oneliner.txt'
    if task_oneliner_file.exists():
        with open(task_oneliner_file, 'r') as f:
            task_oneliner = f.read()
    task_version = str(int(task_version) + 1)

    task_id = f'{task_number}-{task_version}'
    new_task_folder = (
        Path(config.doing_tasks_directory)
        / f'{task_id}-{last_task.repo.repository_name}'
    ).as_posix()

    return (
        task_id,
        task_description,
        task_oneliner,
        last_task.repo.repository_name,
        new_task_folder,
    )


def read_task_from_directory(directory: Path) -> Task | None:
    # Ex: tasks/in_progress/00001-0-repository_name
    logger = get_logger(__name__)
    logger.info('Reading task: %s', directory)
    task_number, task_version = parse_task_id(directory.stem)
    task_id = f'{task_number}-{task_version}'

    repo = GitConfig(directory=str(directory))
    if not repo.is_git_directory:
        return None

    if TaskStatus.DONE.value in str(directory):
        status = TaskStatus.DONE
    elif TaskStatus.IN_PROGRESS.value in str(directory):
        status = TaskStatus.IN_PROGRESS
    else:
        status = TaskStatus.TODO

    created_at = datetime.fromtimestamp(directory.stat().st_ctime)
    updated_at = datetime.fromtimestamp(directory.stat().st_mtime)

    task = Task(
        id=task_id,
        repo=repo,
        status=status,
        created_at=created_at,
        updated_at=updated_at,
    )

    oneliner_file = directory / 'TASK' / 'oneliner.txt'
    if oneliner_file.exists():
        with open(oneliner_file.as_posix(), 'r') as f:
            task.oneliner = f.read().strip()
    else:
        os.makedirs(oneliner_file.parent, exist_ok=True)

        task_file = directory / 'TASK' / f'{task_id}.md'
        if task_file.exists():
            with open(task_file.as_posix()) as f:
                task_description = f.read().strip()
            task.oneliner = get_task_oneliner(task_description)
            with open(oneliner_file.as_posix(), 'w') as f:
                f.write(task.oneliner.strip())
        else:
            task.oneliner = task.description
    logger.info('Task: %s', task)
    return task


def clone_repository(remote_url: str, new_task_folder: Path) -> Path:
    if not remote_url:
        raise ValueError('remote_url cannot be empty')

    parent_folder = new_task_folder.parent
    parent_folder.mkdir(parents=True, exist_ok=True)
    args = ['git', 'clone', remote_url, str(new_task_folder)]
    logger = get_logger(__name__)
    logger.info('Cloning repository: %s', args)
    res = subprocess.run(
        args,
        check=False,
        env=os.environ,
        capture_output=True,
        cwd=str(parent_folder),
    )
    logger.info('Result: %s', res.returncode)
    logger.info('Output: %s', res.stdout.decode('utf-8', errors='replace'))
    logger.info('Error: %s', res.stderr.decode('utf-8', errors='replace'))

    if res.returncode == 0:
        return new_task_folder
    else:
        output = (res.stderr + res.stdout).decode('utf-8', errors='replace')
        raise RuntimeError(
            f'Failed to clone repository: {remote_url} to {new_task_folder}\n'
            f'Command: {" ".join(args)}\n'
            f'Output: {output}'
        )


def get_existing_tasks(config: Config, task_number: str) -> list[Task]:
    tasks = []
    logger = get_logger(__name__)
    logger.info('Getting existing tasks for %s', task_number)
    for task_folder in [config.doing_tasks_directory, config.done_tasks_directory]:
        for task_folder in task_folder.iterdir():
            if task_folder.is_dir():
                task = read_task_from_directory(task_folder)
                if task and task.id.startswith(f'{task_number}-'):
                    tasks.append(task)
                    logger.info(' + Found task: %s', task)
    tasks.sort(key=lambda x: x.id)
    logger.info(' + Found %d tasks', len(tasks))
    return tasks


def open_task_in_editor(config: Config, task: Task) -> str | None:
    if editor := config.editor:
        cmd_args = [editor, str(task.repo.directory)]
        task_file = Path(task.directory) / 'TASK' / f'{task.id}.md'
        if task_file.exists() and editor in ['cursor', 'code']:
            cmd_args.extend(['-g', str(task_file)])
        logger = get_logger(__name__)
        logger.info('Opening task in editor: %s', cmd_args)
        result = subprocess.run(
            args=cmd_args,
            cwd=str(task.repo.directory),
            env=os.environ,
            capture_output=True,
        )
        if result.returncode != 0:
            return (result.stdout + result.stderr).decode('utf-8', errors='replace')

    else:
        return 'Editor is not set'


def move_task_to_done(config: Config, task: Task) -> str | None:
    if (
        task.status == TaskStatus.DONE
        or task.directory.parent == config.done_tasks_directory
    ):
        return 'Task is already done'

    new_task_folder = (
        config.done_tasks_directory / f'{task.id}-{task.repo.repository_name}'
    )
    new_task_folder.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.move(task.directory, new_task_folder)
        task.status = TaskStatus.DONE
        task.updated_at = datetime.now()
        config.save()
    except Exception as e:
        return f'Failed to move task to done: {e}'


def move_task_to_doing(config: Config, task: Task) -> str | None:
    if task.status == TaskStatus.IN_PROGRESS:
        return 'Task is already in progress'
    new_task_folder = (
        config.doing_tasks_directory / f'{task.id}-{task.repo.repository_name}'
    )
    new_task_folder.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.move(task.directory, new_task_folder)
        task.status = TaskStatus.IN_PROGRESS
        task.updated_at = datetime.now()
        config.save()
    except Exception as e:
        return f'Failed to move task to doing: {e}'


def delete_done_task(config: Config, task: Task) -> str | None:
    if task.status != TaskStatus.DONE:
        return 'Task is not done'
    try:
        shutil.rmtree(task.directory)
        config.repos = [
            repo
            for repo in config.repos
            if str(repo.directory) != str(task.repo.directory)
        ]
        config.save()
    except Exception as e:
        return f'Failed to delete done task: {e}'


def archive_task(config: Config, task: Task) -> str | None:
    if task.status != TaskStatus.DONE:
        raise ValueError('Task is not done')
    try:
        os.makedirs(config.archive_tasks_directory, exist_ok=True)
        archive_file = Path(
            shutil.make_archive(
                base_name=str(Path(config.archive_tasks_directory) / task.archive_name),
                format='zip',
                root_dir=str(task.directory),
                verbose=True,
                logger=get_logger(__name__),
            )
        )
        if not archive_file.exists():
            raise FileNotFoundError('Failed to create archive file', str(archive_file))
        shutil.rmtree(task.directory)
        config.repos = [
            repo
            for repo in config.repos
            if str(repo.directory) != str(task.repo.directory)
        ]
        config.save()
        return f'Task {task.id} archived to {archive_file}'
    except Exception as e:
        raise ValueError(f'Failed to archive task: {e}')


def get_task_oneliner(description: str) -> str:
    logger = get_logger(__name__)
    if not description:
        logger.warning('oneliner: no description')
        return ''
    if description.count('\n') == 0:
        logger.warning('oneliner: using description as is')
        return description.strip()
    default_oneliner = ''.join(description.splitlines()[:1])
    if not shutil.which('agent'):  # Use cursor agent to generate the oneliner
        logger.warning('oneliner: no agent found. using default oneliner')
        return default_oneliner

    with tempfile.TemporaryDirectory(dir='.') as tmp_dir:
        task_file = Path(tmp_dir) / 'task.md'
        task_file.write_text(description)
        prompt = (
            f'create just a one line description from the content of @{task_file.as_posix()}. '
            'Output only the one line description, no other text. '
            'Use the same language as the description.'
        )

        result = subprocess.run(
            args=[
                'agent',
                '--output-format',
                'json',
                '--print',
                '--trust',
                prompt,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            logger.warning(
                'oneliner: failed to get oneliner: %s',
                result.stderr.decode('utf-8', errors='replace'),
            )
            return default_oneliner

        json_result = json.loads(result.stdout)
        if (
            json_result['type'] == 'result'
            and json_result['subtype'] == 'success'
            and not json_result['is_error']
        ):
            logger.info('oneliner: got oneliner: %s', json_result['result'])
            return json_result['result']

        logger.warning('oneliner: failed to get oneliner: %s', result.stdout)
        return default_oneliner

    # args = ['agent', 'generate', description]

    # agent "create a one line description from the content of @TASK/125364-0.md" --output-format json --print

    # {"type":"result","subtype":"success","is_error":false,"duration_ms":7172,"duration_api_ms":7172,"result":"Implement E2E tests for Company endpoints covering listing with filters/pagination, ID lookup, cache behavior, and context.","session_id":"198eb041-fdd9-401c-8646-961bd30e5e4f","request_id":"21e30550-9306-4a91-a529-9287a6245221"}
