# AI Spec (Short) - Tasks TUI Manager

## Objetivo

Manter e evoluir a aplicação TUI de gerenciamento de tasks com mudanças pequenas, seguras e compatíveis com o comportamento atual.

## Contexto Rápido

- App terminal com **Textual**.
- Cada task clona um repositório Git para workspace local.
- Status suportados:
  - `in_progress`
  - `done`
  - `archive` (zip)

## Fluxos Críticos

1. **Run app**: parse CLI -> setup context -> abre `Tasks`.
2. **New task**: valida id -> resolve versão -> `git clone` -> cria `TASK/<id>.md`.
3. **Transições**:
   - `in_progress -> done`
   - `done -> in_progress`
   - `done -> delete`
   - `done -> archive`
4. **Open in editor**: usa `config.editor` (default `cursor`).

## Contratos que não podem quebrar

- Estrutura de pastas:
  - `<tasks_folder>/in_progress/<task-id>-<repo>`
  - `<tasks_folder>/done/<task-id>-<repo>`
  - `<tasks_folder>/archive/<task-id>-<project>-<repo>.zip`
- Config persistida em `<config-path>/.tasks.yaml`.
- Atalhos da TUI devem permanecer funcionando.

## Módulos Principais

- `tasks.__main__` (entrypoint)
- `tasks.tui.*` (UI)
- `tasks.tui.context` (estado e acesso à config)
- `tasks.service.task_service` (regras de negócio)
- `tasks.config.config` (YAML)
- `tasks.git.git_config` (metadados Git)
- `tasks.service.logging_service` (logs)

## Regras para IA

- Priorizar simplicidade: evitar refactors amplos sem necessidade.
- Tratar erros de IO/subprocess explicitamente.
- Não alterar layout de dados sem migração/documentação.
- Atualizar `README.md` quando mudar comportamento funcional.
- Preferir testes portáveis (sem depender de ambiente local).

## Baseline de problemas conhecidos

- testes com imports antigos (`service`, `config`, `git`) quebram coleta;
- `config_service.py` vazio;
- possível divergência de versão (`pyproject.toml` vs `tasks.__init__`);
- parser de `.git/config` simples.

## Critério de pronto (Definition of Done)

- fluxo principal da TUI continua funcional;
- sem regressão nas operações de task;
- configuração YAML permanece compatível;
- documentação relevante atualizada;
- mudança clara, pequena e validável.

## Prompt sugerido para agentes

"Implemente mudanças incrementais sem quebrar os fluxos de task, preservando estrutura de pastas e compatibilidade do `.tasks.yaml`. Priorize robustez em operações de filesystem/Git, adicione testes portáveis e atualize a documentação quando houver mudança funcional."
