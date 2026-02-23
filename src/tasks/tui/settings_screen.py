from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Header, Input, Label

from tasks.tui.context import ContextClass, get_context


class Setup(Screen, ContextClass):
    tasks_folder: str

    def compose(self) -> ComposeResult:
        yield Header('Settings')
        self.tasks_folder = self.context.config.tasks_folder
        with Vertical():
            yield Label('Tasks folder', classes='label')
            yield Input(
                placeholder='Tasks folder',
                value=str(get_context().config.tasks_folder),
                id='tasks_folder',
            )
            with Horizontal():
                yield Button('Save', variant='primary', id='save')
                yield Button('Cancel', variant='default', id='cancel')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'save':
            get_context().config.tasks_folder = self.tasks_folder
            get_context().config.save()
            self.app.notify('Setup saved', severity='success')

        self.app.pop_screen()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        match event.input.id:
            case 'tasks_folder':
                tasks_folder = event.input.value.replace('~', str(Path.home()))
                if Path(tasks_folder).is_dir():
                    self.tasks_folder = tasks_folder
                else:
                    self.app.notify('Invalid tasks folder', severity='error')
                    self.tasks_folder = ''
