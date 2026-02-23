from argparse import ArgumentParser, Namespace
from pathlib import Path

parser = ArgumentParser()
parser.add_argument(
    '--config-path',
    type=str,
    default=Path.home(),
    help='Directory to store the config file',
)
parser.add_argument(
    '--tasks-folder',
    type=str,
    default=Path.home() / 'tasks',
    help='Directory to store the tasks',
)


def get_args() -> Namespace:
    args = parser.parse_args()

    config_path = Path(args.config_path).expanduser()
    tasks_folder = Path(args.tasks_folder).expanduser()

    if not config_path.exists():
        raise FileNotFoundError(f'Config path {config_path} does not exist')

    tasks_folder.mkdir(parents=True, exist_ok=True)

    return config_path, tasks_folder
