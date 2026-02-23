from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, RadioButton, RadioSet

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

    current_task: Task | None = reactive(None, bindings=True)

    def __init__(self, *args, **kwargs) -> None:
        self.selected_task_id = kwargs.pop('selected_task_id', None)
        self.refresh_tasks = kwargs.pop('refresh_tasks', False)
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            if doing_tasks := self.context.get_doing_tasks(refresh=self.refresh_tasks):
                self.doing_tasks = doing_tasks
                with Vertical():
                    yield Label(' Doing Tasks')
                    with RadioSet(id='doing_tasks'):
                        for task in doing_tasks:
                            yield RadioButton(
                                label=task.short_name,
                                id=f'doing_tasks_radio_{task.id}',
                                tooltip=task_tooltip(task),
                                compact=True,
                                value=self.selected_task_id == task.id,
                            )

            if done_tasks := self.context.get_done_tasks():
                self.done_tasks = done_tasks
                with Vertical():
                    yield Label(' Done Tasks')
                    with RadioSet(id='done_tasks'):
                        for task in done_tasks:
                            yield RadioButton(
                                label=task.short_name,
                                id=f'done_tasks_radio_{task.id}',
                                tooltip=task_tooltip(task),
                                compact=True,
                            )

        yield Footer()

    @property
    def selected_task(self) -> Task | None:
        if doing_radio_set := self.query_exactly_one('#doing_tasks'):
            if doing_radio_set.pressed_index >= 0:
                return self.doing_tasks[doing_radio_set.pressed_index]
        if done_radio_set := self.query_exactly_one('#done_tasks'):
            if done_radio_set.pressed_index >= 0:
                return self.done_tasks[done_radio_set.pressed_index]
        return None

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        if event.radio_set.id == 'doing_tasks':
            self.current_task = self.doing_tasks[event.radio_set.pressed_index]
            other_radio_set: RadioSet = self.query_exactly_one('#done_tasks')

        elif event.radio_set.id == 'done_tasks':
            self.current_task = self.done_tasks[event.radio_set.pressed_index]
            other_radio_set = self.query_exactly_one('#doing_tasks')

        else:
            self.current_task = None
            other_radio_set = None
        if other_radio_set:
            for button in other_radio_set.query('RadioButton'):
                button.value = False
        get_logger(__name__).info('Current task: %s', self.current_task)

    def on_mount(self) -> None:
        self.refresh_bindings()
        self.query_one('#done_tasks').focus()
        self.query_one('#doing_tasks').focus()

    def action_new_task(self) -> None:
        def check_new_task_result(result) -> None:
            self.app.notify(result[1], severity='success' if result[0] else 'error')
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
        return self.current_task is not None

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
        f'{task.repo.project_name}\n{task.repo.repository_name}\n{task.short_directory}'
    )
