from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    TextArea,
)

from tasks.git import GitConfig
from tasks.service.task_service import new_task
from tasks.tui.choose_repository_modal import ChooseRepositoryScreen
from tasks.tui.context import ContextClass


class NewTask[NewTaskResult](Screen, ContextClass):
    CSS_PATH = 'new_task_screen.tcss'
    TITLE = 'New Task'
    BINDINGS = [
        ('r', 'choose_repository', 'Choose Repository'),
        ('escape', 'cancel', 'Cancel'),
    ]

    repos: list[GitConfig]
    ctx = dict(repository='', task='', description='')

    def action_choose_repository(self) -> None:
        def check_new_task_result(result) -> None:
            if result:
                self.app.notify(
                    message=result, title='Repository chosen', severity='success'
                )
                input: Input = self.query_one('#repository')
                input.value = result
                self.query_one('#task').focus()
            else:
                self.app.notify('No repository chosen', severity='error')

        self.app.push_screen(ChooseRepositoryScreen(), check_new_task_result)

    def action_cancel(self) -> None:
        self.dismiss((False, '', ''))

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Label('Repository')
            yield Input(placeholder='Repository', id='repository')
            yield Label('Task')
            yield Input(placeholder='Task', id='task')
            yield Label('Description')
            yield TextArea(placeholder='Description', id='description')
            yield Button('Create', variant='primary', id='create')
        yield Footer()

    def on_mount(self) -> None:
        pass

    # self.query_one('#repos').focus()

    # def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
    #     input: Input = self.query_one('#repository')
    #     input.value = self.repos[event.radio_set.pressed_index].remote_url
    #     self.query_one('#task').focus()

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

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        self.ctx[event.text_area.id] = event.text_area.text

    def on_input_changed(self, event: Input.Changed) -> None:
        self.ctx[event.input.id] = event.input.value
