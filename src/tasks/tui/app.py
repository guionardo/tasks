from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from tasks import __version__
from tasks.service.logging_service import get_logger, setup_logging
from tasks.tui.logs_screen import Logs
from tasks.tui.settings_screen import Setup
from tasks.tui.tasks_screen import Tasks


class MainApp(App):
    CSS_PATH = 'main.tcss'
    TITLE = 'Task Manager'
    SUB_TITLE = f'Manage your tasks - Version {__version__}'
    SCREENS = {
        'setup': Setup,
        'tasks': Tasks,
        'logs': Logs,
    }
    BINDINGS = [
        ('q', 'exit', 'Quit the app'),
        ('s', "push_screen('setup')", 'Setup'),
        ('t', "push_screen('tasks')", 'Tasks'),
        ('l', "push_screen('logs')", 'Logs'),
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        setup_logging()
        get_logger().info('App initialized')

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def action_exit(self) -> None:
        self.exit()

    def on_mount(self) -> None:
        def check_tasks_screen(*args) -> None:
            tasks_args = dict(
                refresh_tasks=bool(args), selected_task_id=args[0] if args else None
            )
            self.push_screen(Tasks(**tasks_args), check_tasks_screen)

        self.push_screen(Tasks(), check_tasks_screen)
