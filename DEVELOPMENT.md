# Development Guide

Este documento reúne informações técnicas para manutenção e evolução do projeto.

Para instruções de uso da ferramenta, consulte o `README.md`.

## Arquitetura

### Entry point e execução

- Script CLI: `tasks = "tasks.__main__:main"` em `pyproject.toml`.
- Fluxo principal:
  1. Parse dos argumentos (`--config-path`, `--tasks-folder`, `--log-level`, `--log-file`).
  2. Inicialização de contexto/configuração.
  3. Subida da aplicação Textual (`MainApp`).

### Camadas principais

- `src/tasks/tui/`
  - Telas Textual (`Tasks`, `NewTask`, `Setup`, `Logs`) e estilos `.tcss`.
- `src/tasks/service/task_service.py`
  - Regra de negócio: criar, mover, deletar, arquivar task, abrir editor e clonar repo.
- `src/tasks/config/config.py`
  - Modelo de configuração e serialização em YAML (`.tasks.yaml`).
- `src/tasks/git/git_config.py`
  - Descoberta de repositórios e parsing de remote.
- `src/tasks/task/task.py`
  - Entidade `Task` e parser de ID.

## Detalhes de Configuração

Arquivo de configuração padrão:

- `<config-path>/.tasks.yaml`

Campos relevantes:

- `config_path`
- `repos`
- `unique_repos` (`repository_name -> remote_url`)
- `base_repos_directory`
- `last_sync`
- `tasks_folder`

## Parsing de Git (status atual)

- Descoberta de remote prioriza `git` CLI:
  - `git remote`
  - `git remote get-url --push`
  - fallback para `git remote get-url` e `git config --get remote.<name>.url`
- Se necessário, há fallback para leitura de `.git/config`.
- `get_repo_names` cobre formatos:
  - HTTPS
  - SSH (`ssh://...`)
  - SCP-like (`git@host:org/repo.git`)
  - Azure DevOps com `/_git/`.

## Logs (implementação)

- Inicialização no startup da app.
- Destinos:
  - buffer em memória (screen de logs)
  - arquivo rotativo em `<config-path>/tasks.log`
- Handler: `TimedRotatingFileHandler` (intervalo de 2 minutos, `backupCount=10`).

## Build e Empacotamento

- Backend: `uv_build`
- Inclusão de fontes e estilos no build:
  - `[tool.uv.build-backend]`
  - `source-include = ["**/*.tcss", "**/*.py"]`

## Testes

Executar:

```bash
uv run pytest -q
```

Executar somente testes não integração:

```bash
uv run pytest -q -m "not integration"
```

Executar somente testes de integração:

```bash
uv run pytest -q -m "integration"
```

Estado local validado:

- `7 passed, 5 subtests passed`

Observações:

- Testes de serviço usam mocks para evitar dependência de rede/ambiente.
- Novos testes devem manter isolamento (fixtures/mocks).

## Estrutura do Projeto

```text
src/tasks/
  __main__.py
  config/config.py
  consts/__init__.py
  git/git_config.py
  service/
    logging_service.py
    task_service.py
  task/task.py
  tui/
    app.py
    args.py
    context.py
    logs_screen.py
    new_task_screen.py
    settings_screen.py
    tasks_screen.py
    *.tcss
tests/
  config/
  git/
  service/
```

## Limitações Conhecidas

- A descoberta de remote já é mais robusta, mas ainda pode precisar de ajuste para cenários Git incomuns.
- `get_task_oneliner` depende da CLI `agent`; sem ela, o serviço usa fallback para a primeira linha da descrição.

## Próximos Passos Sugeridos

- Separar testes unitários de integração (ex.: `@pytest.mark.integration`).
- Adicionar `pytest.ini` com marcadores e convenções de descoberta.
- Documentar troubleshooting para autenticação/acesso Git (SSH/HTTPS).
