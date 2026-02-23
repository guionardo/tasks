from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    RadioButton,
    RadioSet,
    TextArea,
)

from tasks.git import GitConfig
from tasks.service.task_service import new_task
from tasks.tui.context import ContextClass


class NewTask[NewTaskResult](Screen, ContextClass):
    CSS_PATH = 'new_task_screen.tcss'
    TITLE = 'New Task'

    repos: list[GitConfig]
    ctx = dict(repository='', task='', description='')

    def compose(self) -> ComposeResult:
        yield Header()
        if repos := self.context.get_all_repos():
            with VerticalScroll():
                yield Label('Repositories')
                with RadioSet(id='repos', name='Repositories'):
                    for repo in repos:
                        yield RadioButton(
                            label=f'{repo.project_name}/{repo.repository_name}',
                            id=repo.repository_name,
                        )
            self.repos = repos
        with Vertical():
            yield Label('Repository')
            yield Input(placeholder='Repository', id='repository')
            yield Label('Task')
            yield Input(placeholder='Task', id='task')
            yield Label('Description')
            yield TextArea(placeholder='Description', id='description')
            yield Button('Create', variant='primary', id='create')
            yield Button('Cancel', variant='default', id='cancel')
        yield Footer()

    def on_mount(self) -> None:
        self.query_one('#repos').focus()

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        input: Input = self.query_one('#repository')
        input.value = self.repos[event.radio_set.pressed_index].remote_url
        self.query_one('#task').focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'create':
            task, message = new_task(
                self.context.config,
                self.ctx['task'],
                self.ctx['repository'],
                self.ctx['description'],
            )
            if task:
                self.dismiss((True, message, task.id))
            else:
                self.dismiss((False, message, ''))

        if event.button.id == 'cancel':
            self.dismiss((False, '', ''))

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        self.ctx[event.text_area.id] = event.text_area.text

    def on_input_changed(self, event: Input.Changed) -> None:
        self.ctx[event.input.id] = event.input.value
