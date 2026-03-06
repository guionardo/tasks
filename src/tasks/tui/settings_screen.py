from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Header, Input

from tasks.tui.context import ContextClass


class Setup(Screen, ContextClass):
    @property
    def tasks_directory(self) -> str:
        return self.query_one('#tasks_directory', Input).value

    @tasks_directory.setter
    def tasks_directory(self, value: str) -> None:
        self.query_one('#tasks_directory', Input).value = validate_directory(value)

    @property
    def base_repos_directory(self) -> str:
        return self.query_one('#base_repos_directory', Input).value

    @base_repos_directory.setter
    def base_repos_directory(self, value: str) -> None:
        self.query_one('#base_repos_directory', Input).value = validate_directory(value)

    @property
    def editor(self) -> str:
        return self.query_one('#editor', Input).value

    @editor.setter
    def editor(self, value: str) -> None:
        self.query_one('#editor', Input).value = value

    @property
    def cursor_api_key(self) -> str:
        return self.query_one('#cursor_api_key', Input).value

    @cursor_api_key.setter
    def cursor_api_key(self, value: str) -> None:
        self.query_one('#cursor_api_key', Input).value = value

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical():
            tasks_directory = Input(
                placeholder='Tasks directory',
                id='tasks_directory',
                value=str(self.context.config.tasks_directory),
            )
            tasks_directory.border_title = 'Tasks directory'
            tasks_directory.border_subtitle = (
                'You can use ~ to represent the home directory'
            )
            yield tasks_directory

            base_repos_directory = Input(
                placeholder='Base repos directory',
                id='base_repos_directory',
                value=str(self.context.config.base_repos_directory),
            )
            base_repos_directory.border_title = 'Base repos directory'
            base_repos_directory.border_subtitle = (
                'You can use ~ to represent the home directory'
            )
            yield base_repos_directory

            editor = Input(
                placeholder='Editor',
                id='editor',
                value=str(self.context.config.editor),
            )
            editor.border_title = 'Editor'
            editor.border_subtitle = 'code, cursor, etc.'
            yield editor

            cursor_api = Input(
                placeholder='Cursor API key (optional)',
                id='cursor_api_key',
                value=str(self.context.config.cursor_api_key),
            )
            cursor_api.border_title = 'Cursor API key (optional)'
            yield cursor_api

            with Horizontal():
                yield Button('Save', variant='primary', id='save')
                yield Button('Cancel', variant='default', id='cancel')

    def on_mount(self, _) -> None:
        self.tasks_directory = self.context.config.tasks_directory
        self.base_repos_directory = self.context.config.base_repos_directory
        self.editor = self.context.config.editor
        self.cursor_api_key = self.context.config.cursor_api_key

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
                self.tasks_directory == self.context.config.tasks_directory
                and self.base_repos_directory
                == self.context.config.base_repos_directory
                and self.editor == self.context.config.editor
                and self.cursor_api_key == self.context.config.cursor_api_key
            ):
                self.app.notify('No changes to save', severity='information')
                self.app.pop_screen()
                return

            self.context.config.tasks_directory = self.tasks_directory
            self.context.config.base_repos_directory = self.base_repos_directory
            self.context.config.editor = self.editor
            self.context.config.cursor_api_key = self.cursor_api_key
            self.context.config.save()
            self.app.notify(
                'Setup saved - Please restart the app', severity='information'
            )

        self.app.pop_screen()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        match event.input.id:
            case 'tasks_directory':
                self.tasks_directory = validate_directory(event.input.value)

            case 'base_repos_directory':
                self.base_repos_directory = validate_directory(event.input.value)

            case 'editor':
                self.editor = event.input.value


def validate_directory(directory: str | Path) -> str:
    directory = Path(directory).expanduser()
    if directory.is_dir():
        return directory.absolute().as_posix()
    return ''
