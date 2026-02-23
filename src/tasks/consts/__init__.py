from enum import Enum


class TaskStatus(Enum):
    TODO = 'todo'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'
    ARCHIVE = 'archive'
