# LoginGuard — gestão de contas e acessos pelo terminal

**Disciplina:** Segurança e Otimização de Banco de Dados (somente BD).  
**Grupo:** LoginGuard.  
**Componentes:**
- Luid Moura Santana - matrícula 262070177.
- Alex Gabriel Alves Dos Santos - matrícula 241070261.
- Filipe Alves Ferreira Rocha - matrícula 222700092.
- Gustavo Muniz dos Anjos - matrícula 241070612.  
**Repositório remoto:** https://github.com/Guztaver/loginguard-bd

## Problema e proposta
Uma equipe de suporte precisa cadastrar, bloquear e acompanhar contas sem expor credenciais ou permitir que qualquer funcionário altere os acessos. O LoginGuard será um programa de terminal conectado ao SQL Server, com três perfis de operação e consultas ao histórico de autenticação.

## Versão mínima em três semanas
Cadastro de contas, autenticação com senha, bloqueio/desbloqueio, perfis Administrador/Suporte/Auditor e histórico de tentativas. Dados integralmente fictícios. Não haverá interface web. IA e integração não fazem parte desta entrega.

## Conteúdo preparado
- `docs/ENTREGA.md`: proposta, modelo classificado, matriz de permissões, testes e cronograma.
- `docs/CANVAS.md`: canvas compacto para organizar em uma página.
- `sql/01_criacao_carga.sql`: banco dedicado, tabelas e carga fictícia.
- `sql/02_permissoes.sql`: três papéis, usuários de teste sem login e permissões com DENY.
- `sql/03_testes_permissoes.sql`: verificações de acesso e mascaramento.
- `sql/04_volume_consultas.sql`: carga adicional e duas consultas para medir antes da otimização.
- `sql/05_indices.sql`: índices; repetir as consultas anteriores para comparar.
- [Entrega da OAT em PDF](output/pdf/LoginGuard_Entrega_OAT_BD.pdf): identificação do grupo, canvas, parte de Segurança e apêndices SQL.
- [Execução e coleta de evidências](docs/EXECUCAO.md): validador automatizado, sem apagar bancos ou limpar cache global.

## Instalação e execução

Pré-requisitos do laboratório: SQL Server 2016 ou superior, SQL Server Management Studio (SSMS), `sqlcmd` e uma conta autorizada a criar o banco dedicado `LoginGuardAcademico`. Os scripts SQL não precisam de credenciais de aplicação: os usuários `demo_*` são identidades `WITHOUT LOGIN` usadas apenas com `EXECUTE AS USER`.

1. Clone o repositório e confira que está usando uma instância de laboratório.
2. No SSMS, execute `sql/01_criacao_carga.sql` e depois `sql/02_permissoes.sql`, `sql/03_testes_permissoes.sql`, na ordem.
3. Para reproduzir a medição, execute `sql/04_volume_consultas.sql`, capture as consultas com plano real e estatísticas IO/TIME, aplique `sql/05_indices.sql` e repita as consultas. A carga e o protocolo de medição estão descritos em `docs/EXECUCAO.md`.

O banco, os scripts e as evidências são a parte executável desta entrega. O programa de terminal Python ainda não foi implementado; portanto não há comando de inicialização de aplicação. Não rode novamente o script 01 sobre um banco existente: ele falha de propósito se `LoginGuardAcademico` já existir. Para detalhes sobre pré-requisitos e retomada segura do validador, consulte `docs/EXECUCAO.md`.

## Estrutura do projeto

- `sql/`: criação/carga fictícia, papéis, testes de permissão, consultas de volume e índices.
- `evidencias/`: logs, amostras, resultados, planos reais `.sqlplan` e resumo das medições.
- `docs/`: entrega detalhada, canvas e instruções de laboratório.
- `tools/`: inicialização opcional do serviço local SQL Server, validador e gerador do PDF.
- `output/pdf/`: PDF de entrega do grupo.

## Como preparar a base
Em uma instância de laboratório SQL Server 2016 ou superior, execute os scripts numerados no SSMS, na ordem. O primeiro cria exclusivamente o banco `LoginGuardAcademico` e interrompe se ele já existir. Os scripts 04 e 05 são opcionais para o estudo de desempenho. Execute com uma conta de implantação autorizada; os usuários `demo_*` não possuem senha nem acesso de rede.

## Estado atual e entrega
Em 30/10/2026, a base `LoginGuardAcademico` foi criada no SQL Server Express 2022 e carregada com 50 contas, 50 credenciais sem senha e 500 eventos iniciais. O experimento acrescentou 200 mil eventos, totalizando 200.500. Os testes de permissão e mascaramento passaram antes e depois dos índices. [Logs, planos reais e medições](evidencias/README.md) estão no repositório.

O aplicativo de terminal e a autenticação continuam previstos para o MVP. Todas as contas da carga estão bloqueadas e sem hash de senha: não são contas utilizáveis. A parte executável de BD foi validada.

O repositório está público e pode ser acessado pelo link acima. Cada integrante precisa enviar sua própria entrega pelo canal combinado em sala até 27/11/2026, às 23h59. Não adicionar senhas, strings de conexão com segredo ou dados reais ao repositório.
