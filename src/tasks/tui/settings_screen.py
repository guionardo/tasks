from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Header, Input

from tasks.tui.context import ContextClass, get_context


class Setup(Screen, ContextClass):
    tasks_directory: str
    base_repos_directory: str
    editor: str

    def compose(self) -> ComposeResult:
        yield Header('Settings')
        self.tasks_directory = self.context.config.tasks_directory
        with Vertical():
            tasks_directory = Input(
                placeholder='Tasks directory',
                id='tasks_directory',
                value=str(get_context().config.tasks_directory),
            )
            tasks_directory.border_title = 'Tasks directory'
            tasks_directory.border_subtitle = (
                'You can use ~ to represent the home directory'
            )
            yield tasks_directory

            base_repos_directory = Input(
                placeholder='Base repos directory',
                id='base_repos_directory',
                value=str(get_context().config.base_repos_directory),
            )
            base_repos_directory.border_title = 'Base repos directory'
            base_repos_directory.border_subtitle = (
                'You can use ~ to represent the home directory'
            )
            yield base_repos_directory

            editor = Input(
                placeholder='Editor',
                id='editor',
                value=str(get_context().config.editor),
            )
            editor.border_title = 'Editor'
            editor.border_subtitle = 'code, cursor, etc.'
            yield editor

            with Horizontal():
                yield Button('Save', variant='primary', id='save')
                yield Button('Cancel', variant='default', id='cancel')

    def on_mount(self, event) -> None:
        self.tasks_directory = get_context().config.tasks_directory
        self.base_repos_directory = get_context().config.base_repos_directory
        self.editor = get_context().config.editor

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'save':
            if (
                not self.tasks_directory
                or not self.base_repos_directory
                or not self.editor
            ):
                self.app.notify('Please fill in all fields', severity='error')
                return
            if (
                self.tasks_directory == get_context().config.tasks_directory
                and self.base_repos_directory
                == get_context().config.base_repos_directory
                and self.editor == get_context().config.editor
            ):
                self.app.notify('No changes to save', severity='info')
                self.app.pop_screen()
                return

            get_context().config.tasks_directory = self.tasks_directory
            get_context().config.base_repos_directory = self.base_repos_directory
            get_context().config.editor = self.editor
            get_context().config.save()
            self.app.notify('Setup saved - Please restart the app', severity='success')

        self.app.pop_screen()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        match event.input.id:
            case 'tasks_directory':
                self.tasks_directory = validate_directory(event.input.value)

            case 'base_repos_directory':
                self.base_repos_directory = validate_directory(event.input.value)

            case 'editor':
                self.editor = event.input.value


def validate_directory(directory: str) -> str:
    directory = Path(directory).expanduser()
    if directory.is_dir():
        return directory.absolute().as_posix()
