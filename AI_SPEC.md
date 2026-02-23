# AI Specification - Tasks TUI Manager

## 1. Purpose

Este documento define uma especificação operacional para agentes de IA que irão analisar, manter ou evoluir o projeto **Tasks TUI Manager**.

Objetivo principal da IA:

- manter o comportamento funcional atual;
- implementar mudanças de forma incremental e segura;
- preservar simplicidade da arquitetura;
- priorizar confiabilidade em operações de filesystem e Git.

## 2. Product Context

O sistema é uma aplicação **TUI** (terminal user interface), construída com **Textual**, para gerenciamento de tarefas de desenvolvimento baseadas em repositórios Git.

Cada task representa um workspace local de trabalho clonado de um remoto Git e organizado por status:

- `in_progress`
- `done`
- `archive`

## 3. Primary User Flows

### 3.1 Run Application

1. Usuário executa `tasks` ou `python -m tasks`.
2. Sistema processa argumentos CLI (`--config-path`, `--tasks-folder`).
3. Contexto global é inicializado.
4. `MainApp` sobe e abre a tela de tasks.

### 3.2 Create New Task

1. Usuário abre tela de criação (`n`).
2. Informa task id, repositório e descrição.
3. Sistema calcula versão de task (auto incremento quando necessário).
4. Executa `git clone`.
5. Cria pasta `TASK/` e arquivo `<task-id>.md`.
6. Atualiza configuração persistida (`.tasks.yaml`).

### 3.3 Task Status Transition

- `in_progress -> done` (atalho `>`)
- `done -> in_progress` (atalho `<`)
- `done -> deleted` (atalho `x`)
- `done -> archive zip` (atalho `a`)

### 3.4 Open in Editor

1. Usuário seleciona task.
2. Sistema chama editor configurado (`config.editor`, default `cursor`).
3. Para `cursor`/`code`, abre o arquivo `TASK/<task-id>.md` com `-g` quando existir.

## 4. Functional Scope

### 4.1 Included

- execução TUI;
- leitura/escrita de configuração em YAML;
- descoberta de repositórios em diretórios;
- operações de task (create, move, delete, archive);
- logging em buffer de memória e arquivo rotativo.

### 4.2 Excluded (Current Scope)

- autenticação Git avançada;
- multi-tenant profile/config;
- sincronização distribuída ou remota de estado de tasks;
- API HTTP.

## 5. Technical Architecture

### 5.1 Module Layout

- `tasks.__main__`: entrypoint.
- `tasks.tui.*`: UI/screens.
- `tasks.tui.context`: contexto global e carregamento de config/tasks.
- `tasks.config.config`: modelo e persistência de configuração.
- `tasks.service.task_service`: regras de negócio de tasks.
- `tasks.service.logging_service`: setup/log buffer/export.
- `tasks.git.git_config`: leitura de `.git/config` e descoberta de repos.
- `tasks.task.task`: entidade `Task` e parser de id.

### 5.2 State and Persistence

- Configuração persistida em `<config-path>/.tasks.yaml`.
- Tasks persistidas em estrutura de diretórios sob `tasks_folder`.
- Logs persistidos em:
  - memória (para tela de logs),
  - `app.log` com rotação,
  - export manual timestampado.

## 6. Data Contracts

### 6.1 Task Identity

- Formato esperado: `<number>-<version>`.
- Quando versão não for informada, assumir `0`.
- Exemplo:
  - entrada: `123`
  - normalizado: `123-0`

### 6.2 Task Folder Naming

- `in_progress/<task-id>-<repository-name>`
- `done/<task-id>-<repository-name>`
- `archive/<task-id>-<project-name>-<repository-name>.zip`

### 6.3 Config File (`.tasks.yaml`)

Campos mínimos:

- `config_path`
- `repos`
- `unique_repos`
- `base_repos_directory`
- `last_sync`
- `tasks_folder`

## 7. Non-Functional Requirements for AI Changes

### 7.1 Reliability

- nunca assumir que diretórios existem sem validar;
- tratar explicitamente erros de subprocess e filesystem;
- evitar perda de dados em transições de status.

### 7.2 Simplicity

- preferir mudanças pequenas e locais;
- evitar introdução de camadas extras sem necessidade;
- manter API dos serviços simples e explícita.

### 7.3 Compatibility

- preservar comportamento de atalhos e telas da TUI;
- preservar layout de diretórios de tasks;
- preservar formato do `.tasks.yaml`, salvo mudanças planejadas.

### 7.4 Observability

- manter logging claro para fluxos críticos:
  - clone;
  - movimentação de task;
  - arquivamento;
  - falhas de IO/subprocess.

## 8. Current Known Gaps (Baseline)

- `src/tasks/service/config_service.py` está vazio.
- alguns testes usam imports antigos e quebram coleta.
- versionamento duplicado/inconsistente (`pyproject.toml` vs `tasks.__init__`).
- parser de `.git/config` é simples e não cobre casos avançados.

## 9. AI Implementation Guidelines

### 9.1 Change Strategy

1. Ler arquivos-alvo e mapear impacto.
2. Implementar alteração mínima.
3. Validar execução local dos comandos afetados.
4. Atualizar documentação quando houver mudança funcional.

### 9.2 Testing Strategy

Para cada mudança em regra de negócio:

- adicionar/ajustar testes unitários focados;
- evitar dependência de ambiente externo;
- usar diretórios temporários e mocks para subprocess.

### 9.3 Documentation Strategy

Atualizar `README.md` sempre que houver:

- novos argumentos CLI;
- novo fluxo de task;
- mudança em estrutura de pastas/config;
- mudança de build/distribuição.

## 10. Acceptance Criteria for AI Tasks

Uma alteração é considerada pronta quando:

- comportamento principal da TUI segue funcional;
- não há regressão em fluxos de criação/movimentação de tasks;
- configuração continua serializando corretamente em YAML;
- documentação relevante foi atualizada;
- mudanças são pequenas, legíveis e com intenção clara.

## 11. Suggested Roadmap for AI

### Short Term

- corrigir imports dos testes para namespace `tasks.*`;
- adicionar testes para `parse_task_id` e transições de status;
- alinhar versão do projeto em um único ponto de verdade.

### Medium Term

- robustecer parser Git para múltiplos remotes/protocolos;
- tornar `Config.__post_init__` mais previsível e testável;
- melhorar mensagens de erro para falhas de clone/editor.

### Long Term

- export/import de snapshots de tasks;
- suporte a templates de arquivo `TASK/<id>.md`;
- integração opcional com providers de work item.

## 12. Operational Prompt for Future AI Agents

Use este projeto com as seguintes prioridades:

1. preservar fluxo atual de usuário na TUI;
2. preferir simplicidade e mudanças incrementais;
3. não quebrar estrutura de pastas de tasks;
4. manter compatibilidade do `.tasks.yaml`;
5. cobrir alterações com testes portáveis;
6. manter README consistente com o comportamento real.
