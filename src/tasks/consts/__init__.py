from enum import Enum
from pathlib import Path


class TaskStatus(Enum):
    TODO = 'todo'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'
    ARCHIVE = 'archive'


BASE_CONFIG_PATH = Path.home() / '.config' / 'tasks'
