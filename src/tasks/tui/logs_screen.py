from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, Header, Log

from tasks.service.logging_service import get_log_bytes, save_log_to_file
from tasks.tui.context import ContextClass


class Logs(Screen, ContextClass):
    CSS_PATH = 'logs_screen.tcss'
    TITLE = 'Logs'

    def compose(self) -> ComposeResult:
        yield Header()
        yield Log()
        with Horizontal():
            yield Button('Save', id='save')
            yield Button('Close', id='close')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'close':
            self.app.pop_screen()
        if event.button.id == 'save':
            if log_file := save_log_to_file():
                self.app.notify(
                    title='Logs saved', message=str(log_file), severity='success'
                )
            else:
                self.app.notify(
                    title='Failed to save logs',
                    message='Please try again',
                    severity='error',
                )
                self.app.pop_screen()
            return

    def on_mount(self) -> None:
        log_text = get_log_bytes().decode('utf-8')
        log: Log = self.query_one(Log)
        log.write(log_text)
