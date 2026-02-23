from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, RadioButton, RadioSet

from tasks.git import GitConfig
from tasks.tui.context import ContextClass


class ChooseRepositoryScreen[str](Screen, ContextClass):
    """Screen with a dialog to quit."""

    CSS_PATH = 'choose_repository_modal.tcss'
    TITLE = 'Choose Repository'
    BINDINGS = [
        ('escape', 'cancel', 'Cancel'),
        ('c', 'choose', 'Choose'),
    ]
    repos: list[GitConfig]

    chosen_repository: str

    def compose(self) -> ComposeResult:
        self.repos = self.context.get_all_repos()
        yield Header()

        with RadioSet(id='repos', name='Repositories'):
            for button in self.repos:
                yield RadioButton(
                    label=f'{button.project_name}/{button.repository_name}',
                    id=button.repository_name,
                )
        # yield Button('Choose', variant='success', id='choose')
        # yield Button('Cancel', variant='primary', id='cancel')
        yield Footer()

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        self.chosen_repository = self.repos[event.radio_set.pressed_index].remote_url

    def action_cancel(self) -> None:
        self.dismiss(None)

    def action_choose(self) -> None:
        self.dismiss(self.chosen_repository)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(self.chosen_repository)
