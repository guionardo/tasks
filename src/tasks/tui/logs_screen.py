from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.events import ScreenResume
from textual.screen import Screen
from textual.widgets import Button, Header, RichLog,Footer

from tasks.service.logging_service import get_log_bytes
from tasks.tui.context import ContextClass


class Logs(Screen, ContextClass):
    TITLE = 'Logs'
    CSS = """RichLog {
    padding: 1;
    border: round $primary;
    width: 1fr;  
}"""

    BINDINGS = [
        ('escape', 'close', 'Close the logs screen'),
    ]
    def compose(self) -> ComposeResult:
        yield Header()
        rl = RichLog(highlight=True)
        rl.border_title = 'Logs'
        yield rl
        yield Footer()
       
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'close':
            self.app.pop_screen()

    # def on_mount(self) -> None:
    #     log_text = get_log_bytes().decode('utf-8')
    #     log: RichLog = self.query_one(RichLog)
    #     log.write(log_text)
    @on(ScreenResume)
    async def on_screen_resume(self, event) -> None:
        self.reload_log()

    def reload_log(self) -> None:
        log_text = get_log_bytes().decode('utf-8')
        log: RichLog = self.query_one(RichLog)
        log.clear()
        log.write(log_text)
