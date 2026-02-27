from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import var
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    Markdown,
    RadioButton,
    RadioSet,
    TabbedContent,
    TabPane,
    TextArea,
)

from tasks.git import GitConfig
from tasks.service.task_service import (
    get_task_data_candidate,
    get_task_oneliner,
    new_task,
)
from tasks.tui.context import ContextClass


class NewTask(Screen, ContextClass):
    CSS_PATH = 'new_task_2_screen.tcss'
    TITLE = 'New Task 2'
    BINDINGS = [
        ('escape', 'cancel', 'Cancel'),
        ('ctrl+t', 'tab_task_details', 'Task details'),
    ]
    _is_composed: var[bool] = var(False)
    repos: list[GitConfig] = []

    task_id: var[str] = var('')

    chosen_repository: var[GitConfig] = var(None)
    repository_description: var[str] = var('')
    oneliner_description: var[str] = var('')
    new_task_folder: var[str] = var('')

    # Creation tab
    task_markdown: var[str] = var('')

    def action_tab_task_details(self) -> None:
        tabbed_content: TabbedContent = self.query_one('#new_task_main')
        tabbed_content.active = 'task_details'
        self.query_one('#task').focus()

    def compose(self) -> ComposeResult:
        self.repos = self.context.get_all_repos()
        yield Header()
        with TabbedContent(
            'Task details', 'Repository', 'Creation', id='new_task_main'
        ):
            with TabPane('Task details', id='task_details'):
                task_id = Input(placeholder='Task', id='task')
                task_id.border_title = 'Task'
                yield task_id

                description = TextArea(placeholder='Description', id='description')
                description.border_title = 'Description'
                yield description

                generate_button = Button(
                    'Generate with AI',
                    id='generate_oneliner',
                    tooltip='Generate the oneliner description with AI based on the description',
                )
                oneliner_input = Input(
                    placeholder='Oneliner description', id='oneliner_description'
                )
                horizontal = Horizontal(
                    generate_button,
                    oneliner_input,
                    classes='oneliner_description',
                    id='oneliner_description_horizontal',
                )
                yield horizontal

            with TabPane('Repository', id='repository'):
                with Horizontal(classes='label_input'):
                    yield Label('Repository')
                    yield Input(
                        placeholder='Repository',
                        id='repository',
                        value=self.chosen_repository.remote_url
                        if self.chosen_repository
                        else '',
                    )

                with RadioSet(id='repos', name='Repositories'):
                    for button in self.repos:
                        yield RadioButton(
                            label=f'{button.project_name}/{button.repository_name}',
                            id=button.repository_name,
                        )
            with TabPane('Creation', id='creation_tab'):
                with Horizontal(id='creation_horizontal'):
                    yield Markdown(id='creation_markdown')
                    yield Markdown(id='task_markdown')

                yield Button('Create', variant='primary', id='create')

        yield Footer()
        self._is_composed = True

    def on_mount(self) -> None:
        self.query_one('#task').focus()

    def watch_chosen_repository(self) -> None:
        if not self._is_composed:
            return
        self.query_one('#repository').value = (
            self.chosen_repository.remote_url if self.chosen_repository else ''
        )
        button: RadioButton
        chosen_repository_name = (
            self.chosen_repository.repository_name if self.chosen_repository else ''
        )
        self.new_task_folder = (
            Path(self.context.config.doing_tasks_directory)
            / f'{self.task_id}-{chosen_repository_name}'
        ).as_posix()
        for i, button in enumerate(self.query_one('#repos').query('RadioButton')):
            button.value = self.repos[i].repository_name == chosen_repository_name

    def get_creation_markdown(self) -> str:
        error_message, _ = self.new_task_validation()
        if error_message:
            return f"""# Task Creation: {error_message}"""

        repository_description = f'{self.chosen_repository.project_name}/{self.chosen_repository.repository_name}'

        return f"""# Task Creation: {self.task_id}

* Repository: {repository_description}
* Oneliner: {self.oneliner_description}
* New task folder: {self.new_task_folder}
"""

    @on(TabbedContent.TabActivated)
    async def tabbed_content_changed(self, event: TabbedContent.TabActivated) -> None:
        match event.pane.id:
            case 'creation_tab':
                self.query_one('#creation_markdown').update(
                    self.get_creation_markdown()
                )
                self.query_one('#task_markdown').update(self.task_markdown)
                # self.query_one('#create').disabled =  bool(self.new_task_validation())

            case 'task_details':
                pass
            case 'repository':
                pass

    @on(TextArea.Changed)
    async def update_markdown(self, event: TextArea.Changed) -> None:
        self.task_markdown = event.text_area.text

    @on(Input.Blurred)
    async def input_blurred(self, event: Input.Blurred) -> None:
        match event.input.id:
            case 'task':
                if event.input.value and '-' not in event.input.value:
                    event = Input.Submitted(event.input, event.value)
                    await self.input_submitted(event)

            case _:
                pass

    @on(Input.Submitted)
    async def input_submitted(self, event: Input.Submitted) -> None:
        match event.input.id:
            case 'task':
                if self.task_id == event.input.value:
                    return
                (
                    new_task_id,
                    task_description,
                    task_oneliner,
                    repository_name,
                    self.new_task_folder,
                ) = get_task_data_candidate(
                    self.context.config,
                    event.input.value,
                    self.chosen_repository.repository_name
                    if self.chosen_repository
                    else '',
                )
                self.task_id = new_task_id
                self.query_one('#task').value = self.task_id

                if not self.task_markdown:
                    self.task_markdown = task_description
                    self.query_one('#description').text = self.task_markdown

                for repo in self.repos:
                    if repo.repository_name == repository_name:
                        self.chosen_repository = repo
                        self.query_one('#repository').value = repo.remote_url
                        break

                if not self.oneliner_description:
                    self.oneliner_description = task_oneliner
                    self.query_one(
                        '#oneliner_description'
                    ).value = self.oneliner_description

    @on(Input.Changed)
    async def input_changed(self, event: Input.Changed) -> None:
        match event.input.id:
            case 'repository':
                for repo in self.repos:
                    if repo.remote_url == event.input.value:
                        self.chosen_repository = repo
                        break
            case _:
                pass

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        self.chosen_repository = self.repos[event.radio_set.pressed_index]
        input: Input = self.query_one('#repository')
        input.value = self.chosen_repository.remote_url

    @on(Button.Pressed)
    def generate_oneliner(self, event: Button.Pressed) -> None:
        match event.button.id:
            case 'generate_oneliner':
                input: Input = self.query_one('#oneliner_description')
                description_input: TextArea = self.query_one('#description')
                description = description_input.text
                if not description:
                    self.app.notify('Description is required', severity='error')
                    return
                description_input.loading = True
                horizontal: Horizontal = self.query_one(
                    '#oneliner_description_horizontal'
                )
                horizontal.loading = True
                self.oneliner_description = get_task_oneliner(description)
                input.value = self.oneliner_description
                input.loading = False
                horizontal.loading = False
            case 'create':
                error_message, focus_function = self.new_task_validation()
                if error_message:
                    self.app.notify(error_message, severity='error')
                    focus_function()
                    return

                task, message = new_task(
                    self.context.config,
                    self.task_id,
                    self.chosen_repository.remote_url,
                    self.task_markdown,
                )
                if task:
                    self.app.notify(message, title='Task created', severity='success')
                    self.dismiss((True, message, task.id))
                else:
                    self.app.notify(
                        message, title='Task creation failed', severity='error'
                    )
                    self.dismiss((False, message, ''))

    def new_task_validation(self) -> str:
        if '-' not in self.task_id:
            return 'Task ID is not valid', lambda: self.query_one('#task').focus()
        if not self.chosen_repository:
            return 'Repository is not chosen', lambda: self.query_one('#repos').focus()
        if not self.task_markdown:
            return 'Task description is not valid', lambda: self.query_one(
                '#description'
            ).focus()
        return '', None
