from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header

from tasks.service.logging_service import get_logger
from tasks.service.task_service import (
    archive_task,
    delete_done_task,
    move_task_to_doing,
    move_task_to_done,
    open_task_in_editor,
)
from tasks.task.task import Task, TaskStatus
from tasks.tui.context import ContextClass
from tasks.tui.new_task_screen import NewTask

# ACTIONS
NEW_TASK = 'new_task'
OPEN_IN_EDITOR = 'open_in_editor'
MOVE_TO_DONE = 'move_to_done'
MOVE_TO_DOING = 'move_to_doing'
DELETE_DONE = 'delete_done'
REFRESH_TASKS = 'refresh_tasks'
ARCHIVE_TASK = 'archive_task'


class Tasks(Screen, ContextClass):
    CSS_PATH = 'tasks_screen.tcss'

    BINDINGS = [
        ('n', NEW_TASK, 'New task'),
        ('e', OPEN_IN_EDITOR, 'Open task in editor'),
        ('>', MOVE_TO_DONE, 'Move task to done'),
        ('<', MOVE_TO_DOING, 'Move task to doing'),
        ('x', DELETE_DONE, 'Delete done task'),
        ('r', REFRESH_TASKS, 'Refresh tasks'),
        ('a', ARCHIVE_TASK, 'Archive task'),
    ]

    doing_tasks: list[Task] = []
    done_tasks: list[Task] = []
    doing_tasks_by_row_key: dict[object, Task] = {}
    done_tasks_by_row_key: dict[object, Task] = {}

    current_task: Task | None = reactive(None, bindings=True)

    def __init__(self, *args, **kwargs) -> None:
        self.selected_task_id = kwargs.pop('selected_task_id', None)
        self.refresh_tasks = kwargs.pop('refresh_tasks', False)
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            self.doing_tasks = self.context.get_doing_tasks(refresh=self.refresh_tasks)
            doing_table = self._build_tasks_table(
                table_id='doing_tasks',
                tasks=self.doing_tasks,
                selected_task_id=self.selected_task_id,
            )
            doing_table.border_title = 'Doing Tasks'
            yield doing_table

            self.done_tasks = self.context.get_done_tasks(refresh=self.refresh_tasks)
            done_table = self._build_tasks_table(
                table_id='done_tasks',
                tasks=self.done_tasks,
                selected_task_id=self.selected_task_id,
            )
            done_table.border_title = 'Done Tasks'
            yield done_table

        yield Footer()

    def _build_tasks_table(
        self, table_id: str, tasks: list[Task], selected_task_id: str | None
    ) -> DataTable:
        table = DataTable(id=table_id, cursor_type='row')
        table.add_column('Task ID', width=12)
        table.add_column('Repository', width=28)
        table.add_column('Oneliner')
        table.zebra_stripes = True

        task_map = {}
        selected_row_index = None
        for i, task in enumerate(tasks):
            row_key = table.add_row(
                task.id,
                task.repo.repository_name,
                task.oneliner,
                key=task.id,
                label=task.short_name,
            )
            task_map[row_key] = task
            if selected_task_id == task.id:
                selected_row_index = i

        if selected_row_index is not None:
            table.move_cursor(row=selected_row_index, column=0, scroll=True)

        if table_id == 'doing_tasks':
            self.doing_tasks_by_row_key = task_map
        else:
            self.done_tasks_by_row_key = task_map

        return table

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id == 'doing_tasks':
            self.current_task = self.doing_tasks_by_row_key.get(event.row_key)
        elif event.data_table.id == 'done_tasks':
            self.current_task = self.done_tasks_by_row_key.get(event.row_key)
        else:
            self.current_task = None
        get_logger(__name__).info('Current task: %s', self.current_task)

    def on_mount(self) -> None:
        if doing_tasks := self.query_one('#doing_tasks', DataTable):
            doing_tasks.focus()

        self.refresh_bindings()

    def action_new_task(self) -> None:
        def check_new_task_result(result) -> None:
            if not result:
                return
            self.app.notify(result[1], severity='success' if result[0] else 'error')
            if result[2]:
                self.dismiss(result[2])

        self.app.push_screen(NewTask(), check_new_task_result)

    def action_open_in_editor(self) -> None:
        if error_message := open_task_in_editor(self.context.config, self.current_task):
            self.app.notify(
                message=error_message,
                title='Failed to open task in editor',
                severity='error',
            )
            return

        self.app.notify(message='Task opened in editor', severity='success')
        self.app.exit()

    def action_move_to_done(self) -> None:
        if not self.can_move_to_done():
            self.app.notify(
                message=f'Task {self.current_task.id} is done already', severity='error'
            )
            return
        if error_message := move_task_to_done(self.context.config, self.current_task):
            self.app.notify(message=error_message, severity='error')
            return
        self.app.notify(
            message=f'Task {self.current_task.id} moved to done', severity='success'
        )
        self.dismiss(self.current_task.id)

    def action_move_to_doing(self) -> None:
        if not self.can_move_to_doing():
            self.app.notify(
                message=f'Task {self.current_task.id} is not done', severity='error'
            )
            return
        if error_message := move_task_to_doing(self.context.config, self.current_task):
            self.app.notify(message=error_message, severity='error')
            return
        self.app.notify(
            message=f'Task {self.current_task.id} moved to doing', severity='success'
        )
        self.dismiss(self.current_task.id)

    def action_delete_done(self) -> None:
        if not self.can_delete_done():
            self.app.notify(message='Task is not done', severity='error')
            return
        if error_message := delete_done_task(self.context.config, self.current_task):
            self.app.notify(message=error_message, severity='error')
            return
        self.app.notify(message='Task deleted', severity='success')
        self.dismiss(self.current_task.id)

    def action_refresh_tasks(self) -> None:
        self.dismiss('00000-0')

    def action_archive_task(self) -> None:
        if not self.can_archive_task():
            self.app.notify(
                message=f'Task {self.current_task.id} is not done', severity='error'
            )
            return
        try:
            message = archive_task(self.context.config, self.current_task)
            self.app.notify(message=message, severity='success')
            self.dismiss('00000-0')
        except Exception as e:
            self.app.notify(message=f'{e}', severity='error')

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Check if an action may run."""
        result = True
        if action == NEW_TASK:
            result = True
        elif action == OPEN_IN_EDITOR:
            result = self.can_open_in_editor()
        elif action == MOVE_TO_DONE:
            result = self.can_move_to_done()
        elif action == MOVE_TO_DOING:
            result = self.can_move_to_doing()
        elif action == DELETE_DONE:
            result = self.can_delete_done()
        elif action == ARCHIVE_TASK:
            result = self.can_archive_task()

        else:
            return True

        return result

    def can_open_in_editor(self) -> bool:
        return (self.current_task is not None) or None

    def can_move_to_done(self) -> bool:
        return self.current_task and self.current_task.status != TaskStatus.DONE

    def can_move_to_doing(self) -> bool:
        return self.current_task and self.current_task.status == TaskStatus.DONE

    def can_delete_done(self) -> bool:
        return self.current_task and self.current_task.status == TaskStatus.DONE

    def can_archive_task(self) -> bool:
        return self.current_task and self.current_task.status == TaskStatus.DONE


def task_tooltip(task) -> str:
    return (
        f'[b]{task.repo.project_name} - {task.repo.repository_name}[/b]\n\n'
        f'{task.short_directory}\n\n[i]{task.oneliner}[/i]'
    )
