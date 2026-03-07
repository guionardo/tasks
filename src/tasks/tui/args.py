from argparse import ArgumentParser
from pathlib import Path

default_config_path = Path.home() / '.config' / 'tasks'
parser = ArgumentParser()
parser.add_argument(
    '--config-path',
    type=str,
    default=default_config_path,
    help='Directory to store the configurations',
)
parser.add_argument(
    '--tasks-folder',
    type=str,
    default=Path.home() / 'tasks',
    help='Directory to store the tasks',
)
parser.add_argument(
    '--log-level',
    type=str,
    default='INFO',
    help='Log level',
)
parser.add_argument(
    '--log-file',
    type=str,
    default=default_config_path / 'tasks.log',
    help='Log file',
)


def get_args() -> tuple[Path, Path, str, Path]:
    args = parser.parse_args()

    config_path = Path(args.config_path).expanduser()
    tasks_folder = Path(args.tasks_folder).expanduser()
    log_file = Path(args.log_file).expanduser()

    config_path.mkdir(parents=True, exist_ok=True)
    tasks_folder.mkdir(parents=True, exist_ok=True)

    return config_path, tasks_folder, args.log_level, log_file
