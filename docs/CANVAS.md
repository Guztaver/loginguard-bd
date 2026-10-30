# LoginGuard — canvas de uma página

**Grupo:** LoginGuard.

**Componentes (nome completo e matrícula):**
- Luid Moura Santana - matrícula 262070177.
- Alex Gabriel Alves Dos Santos - matrícula 241070261.
- Filipe Alves Ferreira Rocha - matrícula 222700092.
- Gustavo Muniz dos Anjos - matrícula 241070612.  
**Disciplina:** Segurança e Otimização de Banco de Dados

| Elemento | Proposta |
|---|---|
| Problema | Contas sem controle de bloqueio, permissões excessivas e dificuldade para investigar tentativas de acesso. |
| Usuários | Administrador de contas, equipe de suporte e auditor. |
| O que muda | Cada perfil executa apenas as operações autorizadas e consegue consultar o histórico necessário à sua função. |
| Entrada | Nome e e-mail fictícios, identificador de conta, senha digitada de forma oculta e comandos pelo terminal. |
| Saída | Resultado genérico da autenticação, confirmação das operações, contas com dados mascarados e relatórios de tentativas. |
| Arquitetura em caixas | [Operador] → [Terminal Python] → [Consultas parametrizadas / autenticação] → [SQL Server: permissões, contas, credenciais e histórico]. |
| Maior risco | Um usuário consultar hashes de senha ou alterar contas sem autorização. |
| Proteções | Papéis mínimos no banco, DENY explícito, credenciais separadas, hash Argon2id na aplicação e mascaramento do e-mail/IP. |
| Prova | Executar operações como usuários de cada papel; leitura de credenciais e alteração do histórico devem ser negadas. Testar SQL Injection no terminal quando implementado. |
| Otimização | Histórico por conta e ranking de falhas por período; comparar leituras lógicas, tempo e plano antes/depois de índices. |
| MVP em três semanas | Cadastro, login, bloqueio/desbloqueio, três perfis, histórico e duas consultas otimizadas. |
| Dados | 50 contas e 500 tentativas fictícias na carga inicial; 200 mil eventos adicionais para o experimento. |

**Semana 1:** banco, carga e permissões. **Semana 2:** terminal e autenticação. **Semana 3:** testes, índices e documentação das evidências.

**Link do repositório:** https://github.com/Guztaver/loginguard-bd
