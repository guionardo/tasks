# Tasks TUI Manager

Aplicação terminal (TUI) para gerenciar tarefas de desenvolvimento baseadas em repositórios Git.
Cada tarefa clona um repositório para uma pasta de trabalho, permite mover estados (`in_progress`, `done`) e cria artefatos auxiliares para documentação da task.

## Visão Geral

O projeto oferece um fluxo simples para trabalho orientado a tasks:

- Criar uma task a partir de um `remote_url` Git.
- Clonar o repositório em uma estrutura padronizada.
- Organizar tasks por status.
- Abrir task diretamente no editor configurado.
- Arquivar task concluída em `.zip`.
- Visualizar e exportar logs da execução.

A interface é construída com **Textual** e executa no terminal.

## Principais Funcionalidades

- **Gestão de tasks por status**
  - `in_progress` (em andamento)
  - `done` (concluídas)
  - `archive` (zipadas)
- **Criação de task com versionamento automático**
  - Exemplo: se `123-0` já existir, cria `123-1`, `123-2`, etc.
- **Descoberta de repositórios Git**
  - Lê `.git/config`, identifica `remote`, `project_name` e `repository_name`.
- **Abertura no editor**
  - Usa `config.editor` (default: `cursor`) para abrir diretório da task.
- **Logs em memória + arquivo**
  - Exibição no screen de logs e persistência manual (`Save`) para `.log`.

## Arquitetura

### Entry point e execução

- Script CLI: `tasks = "tasks.__main__:main"` em `pyproject.toml`.
- Fluxo principal:
  1. Parse dos argumentos (`--config-path`, `--tasks-folder`).
  2. Inicialização de contexto/configuração.
  3. Subida da aplicação Textual (`MainApp`).

### Camadas principais

- `src/tasks/tui/`
  - Telas Textual (`Tasks`, `NewTask`, `Setup`, `Logs`) e estilos `.tcss`.
- `src/tasks/service/task_service.py`
  - Regra de negócio: criar, mover, deletar, arquivar task, abrir editor, clone Git.
- `src/tasks/config/config.py`
  - Modelo de configuração e serialização em YAML (`.tasks.yaml`).
- `src/tasks/git/git_config.py`
  - Extração de metadados de repositório e descoberta de repos em árvore.
- `src/tasks/task/task.py`
  - Entidade `Task` e parser de ID.

## Requisitos

- Python `>=3.12`
- `uv` para build/execução (recomendado no projeto)
- Git instalado e acessível no `PATH`
- Acesso ao remoto Git utilizado nas tasks (SSH/HTTPS conforme ambiente)

Dependências declaradas:

- `textual[syntax]`
- `pyyaml`
- `pytest`

## Instalação e Execução

### 1) Instalar dependências

```bash
uv sync
```

### 2) Executar aplicação

```bash
uv run python -m tasks
```

ou via script:

```bash
uv run tasks
```

### 3) Ver ajuda da CLI

```bash
uv run python -m tasks --help
```

Argumentos disponíveis:

- `--config-path`: diretório onde o arquivo `.tasks.yaml` é salvo.
- `--tasks-folder`: diretório raiz onde as tasks serão armazenadas.

Exemplo:

```bash
uv run tasks --config-path ~/.config/tasks --tasks-folder ~/tasks
```

## Estrutura de Dados e Pastas

### Arquivo de configuração

Por padrão, a configuração é salva em:

- `<config-path>/.tasks.yaml`

Campos relevantes:

- `config_path`
- `repos` (metadados de repositórios encontrados)
- `unique_repos` (`repository_name -> remote_url`)
- `base_repos_directory`
- `last_sync`
- `tasks_folder`

### Estrutura esperada de tasks

```text
<tasks_folder>/
  in_progress/
    123-0-repository-a/
      .git/
      TASK/
        .gitignore
        123-0.md
  done/
    123-0-repository-a/
  archive/
    123-0-project-repository-a.zip
```

## Atalhos da Interface (TUI)

### Globais (`MainApp`)

- `q`: sair da aplicação
- `s`: abrir tela de setup
- `t`: abrir tela de tasks
- `l`: abrir tela de logs

### Tela de tasks (`Tasks`)

- `n`: nova task
- `e`: abrir task no editor
- `>`: mover para `done`
- `<`: mover para `in_progress`
- `x`: deletar task `done`
- `r`: refresh de tasks
- `a`: arquivar task `done`

## Fluxo de Nova Task

1. Usuário informa ID da task (ex.: `123` ou `123-0`), repositório e descrição.
2. Sistema calcula versão final:
   - se já existe task com o mesmo número, incrementa versão.
3. Faz `git clone` para `in_progress/<task-id>-<repository-name>`.
4. Cria pasta `TASK/` e arquivo markdown `<task-id>.md`.
5. Atualiza `.tasks.yaml` com repositório descoberto.

## Logs

- Logging inicializado no startup da aplicação.
- Destinos:
  - buffer em memória (para tela `Logs`)
  - `app.log` com rotação (`5 MB`, `backupCount=5`)
- Tela de logs permite salvar snapshot em arquivo timestampado:
  - `YYYY-MM-DD-HH-MM-SS.log`

## Build e Empacotamento

O projeto usa `uv_build` como backend e inclui assets `.tcss` no build:

- `[tool.uv.build-backend]`
  - `source-include = ["**/*.tcss", "**/*.py"]`

Isso garante que os estilos da TUI sejam distribuídos junto com o pacote.

## Testes

Executar:

```bash
uv run pytest -q
```

Estado atual observado:

- Parte dos testes depende de caminhos/repositórios específicos do ambiente local.

Recomendação:

- Substituir dependências externas por fixtures/mocks para tornar testes portáveis.

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

- `src/tasks/service/config_service.py` está vazio.
- Versão em `src/tasks/__init__.py` pode divergir da versão em `pyproject.toml`.
- Alguns testes ainda não refletem a estrutura atual de pacotes.
- O parser de `.git/config` é simples e assume formato padrão de remote.

## Próximos Passos Sugeridos

- Harmonizar versão do pacote em um único ponto de verdade.
- Melhorar robustez de parsing Git (múltiplos remotes/protocolos).
- Criar suíte de testes totalmente isolada de ambiente local.
- Adicionar seção de troubleshooting para problemas de autenticação Git (SSH/HTTPS).
