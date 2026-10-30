# Execução do laboratório

O SQL Server Express já está instalado neste computador. Não é necessário reinstalar o servidor para este projeto. O serviço `MSSQL$SQLEXPRESS` precisa estar em execução, e a conta que executa os scripts precisa ter permissão de implantação no SQL Server.

## Preparação administrativa mínima

O arquivo `tools/iniciar_sqlserver.ps1` inicia somente esse serviço. Ele não altera o tipo de inicialização, não abre portas, não muda permissões de usuários e não reinicia o Windows. Precisa ser executado com privilégios de administrador quando for conveniente. O resultado fica em `tmp/setup/inicio-servico.txt`.

Uma tentativa anterior de instalar o LocalDB silenciosamente foi recusada pelo instalador por falta de privilégios administrativos. Depois de autorização explícita do usuário, uma única solicitação administrativa iniciou o serviço SQL Server já instalado. Nenhuma instalação do LocalDB foi concluída e nenhum reinício do computador foi realizado.

## Validação sem elevação

Depois de iniciar o serviço, executar a partir da raiz do repositório:

```powershell
python tools/executar_validacao.py
```

O validador usa autenticação integrada do Windows e o `sqlcmd` instalado. O Python precisa apenas da biblioteca padrão para essa etapa. Não contém senha nem string de conexão com segredo.

Ele cria o banco dedicado `LoginGuardAcademico`, executa os scripts de criação/carga e permissões, testa os papéis, gera 200 mil eventos adicionais e mede duas consultas antes e depois dos índices. Cada fase tem uma execução de aquecimento e cinco amostras. Os quatro planos XML são planos reais, com contadores de execução. Os resultados das consultas precisam permanecer idênticos.

Não se apagam bancos nem se limpa o cache global. O validador interrompe se o banco já existir. A opção `--resume` permite retomar somente um banco com a propriedade `LoginGuardValidador=loginguard-bd-v1`, inserida pelo próprio validador; nessa retomada, apenas os dois índices do experimento são removidos e recriados.

## Evidências e PDF

Uma execução bem-sucedida produz `evidencias/resumo.json`, logs de carga/permissões, as amostras de estatísticas e quatro arquivos `.sqlplan`. O resumo inclui as contagens finais e os hashes SHA-256 dos scripts executados. O arquivo de resumo só é produzido depois que toda a validação termina sem falhas.

A validação de 30/10/2026 foi concluída. O banco permanece disponível em `.\SQLEXPRESS`, banco `LoginGuardAcademico`, com 50 contas, 50 credenciais sem senha e 200.500 eventos fictícios. Os três papéis humanos e as duas views foram instalados; os testes passaram. Consultar `evidencias/README.md` para os resultados e limites das medições. O serviço não teve seu tipo de inicialização alterado.

O validador chama `sqlcmd -I` para habilitar QUOTED_IDENTIFIER. O script 05 declara também as opções SET exigidas para criar índices filtrados. Isso corrige a diferença entre as opções padrão de ferramentas de linha de comando e do SSMS.

Para atualizar o PDF com resultados reais, executar `python tools/gerar_pdf.py` em um Python com ReportLab. Sem o resumo de uma execução bem-sucedida, o documento mantém o estado de execução pendente. Os arquivos temporários e instaladores ficam em `tmp/`, ignorado pelo Git.
