# Tasks TUI Manager

Aplicação de terminal (TUI) para organizar tarefas de desenvolvimento baseadas em repositórios Git.

Com ela você pode:

- criar uma task a partir de um repositório remoto;
- trabalhar com status (`in_progress`, `done`, `archive`);
- abrir a task no editor configurado;
- arquivar tasks concluídas em `.zip`;
- visualizar e exportar logs da sessão.

## Requisitos

- Python `>=3.12`
- `uv` (recomendado para execução)
- Git disponível no `PATH`
- acesso ao repositório remoto usado nas tasks (SSH/HTTPS)
- CLI `agent` do Cursor no `PATH` (opcional, recomendada para gerar oneliner com `Ctrl+G`)

## Instalação

```bash
uv sync
```

## Executar

```bash
uv run tasks
```

Alternativa:

```bash
uv run python -m tasks
```

## Opções da CLI

```bash
uv run tasks --help
```

Argumentos principais:

- `--config-path`: diretório onde o `.tasks.yaml` será salvo;
- `--tasks-folder`: diretório raiz das tasks;
- `--log-level`: nível de log (ex.: `INFO`, `DEBUG`);
- `--log-file`: caminho do arquivo de log.

Exemplo:

```bash
uv run tasks --config-path ~/.config/tasks --tasks-folder ~/tasks
```

## Estrutura das Pastas

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

## Atalhos da Interface

Atalhos globais:

- `esc`: sair da aplicação
- `s`: abrir tela de setup
- `l`: abrir tela de logs

Na tela de tasks:

- `n`: nova task
- `e`: abrir task no editor
- `>`: mover para `done`
- `<`: mover para `in_progress`
- `x`: deletar task `done`
- `r`: atualizar lista de tasks
- `a`: arquivar task `done`

## Fluxo de Uso

1. Crie uma task informando ID, repositório e descrição.
2. A ferramenta clona o repositório em `in_progress/<task-id>-<repository-name>`.
3. A pasta `TASK/` com arquivo markdown da task é criada automaticamente.
4. Ao concluir, mova para `done` e, se quiser, arquive para `archive`.

## Logs

- Logs ficam disponíveis na tela `Logs`.
- O arquivo principal fica em `<config-path>/tasks.log`.

## Setup da CLI `agent` (Cursor)

A funcionalidade de gerar oneliner (`Ctrl+G` na tela de nova task) usa a CLI `agent`.

### 1) Instalar e autenticar

- Instale o Cursor no ambiente onde a TUI roda.
- Garanta que a CLI `agent` esteja disponível no `PATH`.
- Faça login no Cursor/CLI conforme seu ambiente.

### 2) Validar instalação

```bash
agent --help
```

Se o comando responder ajuda/uso, a CLI está disponível.

### 3) Comportamento quando `agent` não está disponível

Se a CLI `agent` não estiver configurada, a TUI continua funcionando e usa fallback:

- o oneliner vira a primeira linha da descrição da task.

Ou seja, a geração automática melhora a qualidade do resumo, mas não bloqueia o fluxo de criação.

## Documentação Técnica

Detalhes de arquitetura, testes, estrutura interna e manutenção estão em `DEVELOPMENT.md`.
