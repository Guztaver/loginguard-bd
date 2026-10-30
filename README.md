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

## Como preparar a base
Em uma instância de laboratório SQL Server 2016 ou superior, execute os scripts numerados no SSMS, na ordem. O primeiro cria exclusivamente o banco `LoginGuardAcademico` e interrompe se ele já existir. Os scripts 04 e 05 são opcionais para o estudo de desempenho. Execute com uma conta de implantação autorizada; os usuários `demo_*` não possuem senha nem acesso de rede.

## Estado atual e entrega
Este repositório contém a proposta e os scripts iniciais; o aplicativo de terminal e a autenticação ainda serão implementados. A carga deixa todas as contas bloqueadas e sem hash de senha: não são contas utilizáveis. Não foi possível executar os scripts nesta sessão porque o serviço SQL Express estava parado e o início do serviço foi negado pelo Windows. Não há evidência de base carregada ou de testes aprovados ainda.

Antes de entregar: executar e registrar os scripts. O repositório é privado; o professor precisará de acesso para consultar o link. Cada integrante precisa enviar sua própria entrega pelo canal da turma no prazo informado de 27/10. Não adicionar senhas, strings de conexão com segredo ou dados reais ao repositório.
