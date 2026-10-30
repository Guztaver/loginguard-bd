# Evidências da execução de BD

Execução concluída em **30/10/2026**, às **15:17 (America/Sao_Paulo)**, no SQL Server Express 2022, versão **16.0.1210.3**. Banco: `LoginGuardAcademico`.

## Base carregada

| Tabela | Carga inicial | Após gerar volume |
|---|---:|---:|
| Conta | 50 | 50 |
| Credencial | 50 | 50 |
| TentativaLogin | 500 | 200.500 |

Todos os dados operacionais são fictícios. Credenciais têm HashSenha = NULL e contas permanecem bloqueadas. Os eventos de sucesso/falha são dados sintéticos, não autenticações produzidas por aplicativo funcional.

## Segurança

O script 03 terminou sem falhas antes e depois dos índices. Os logs mostram e-mails como `pXXX@XXXX.com`, negação de SELECT em Credencial para suporte e administrador, negação de UPDATE em Conta pelo suporte, negação de alteração de papel e negação de DELETE no histórico pelo auditor. As consultas permitidas funcionaram.

Arquivos: `03_testes_permissoes.txt` e `06_testes_finais.txt`. A prova é de permissões e mascaramento no banco; não é um teste de autenticação ou de SQL Injection de um aplicativo, que ainda não foi implementado.

## Desempenho

Cada consulta e fase teve um aquecimento e cinco amostras. A tabela usa as medianas das cinco amostras, com o mesmo volume e os mesmos filtros. Não houve limpeza do cache global nem alteração de configuração da instância.

| Consulta | Leituras antes | Leituras depois | Tempo SQL antes | Tempo SQL depois |
|---|---:|---:|---:|---:|
| Q1: últimas 50 tentativas de uma conta | 1.064 | 3 | 17 ms | 4 ms |
| Q2: ranking de falhas por período | 1.064 | 626 | 24 ms | 29 ms |

Os resultados das duas consultas foram comparados e são idênticos nas duas fases. Q1 melhorou. Q2 reduziu leituras, mas não melhorou a mediana de tempo; não se declara ganho de velocidade para Q2. A atividade concorrente do computador e os tempos curtos limitam a interpretação das durações.

O plano de Q1 mudou de varredura do índice clustered e ordenação para busca em `IX_Tentativa_Conta_Data`. Em Q2, o plano final usou esse mesmo índice e agregação por fluxo; o índice filtrado foi criado, mas não foi escolhido automaticamente pelo otimizador neste experimento.

## Arquivos para conferência

- `01_criacao_carga.txt`: confirma 50 contas, 50 credenciais e 500 tentativas iniciais.
- `04_volume_carga.txt`: confirma 200.500 eventos após carga adicional.
- `contagens_finais.txt`: confirma o volume final.
- `antes_Q1_0.txt` e equivalentes: rodada 0 é aquecimento; rodadas 1 a 5 são amostras.
- `antes_Q1.sqlplan`, `antes_Q2.sqlplan`, `depois_Q1.sqlplan`, `depois_Q2.sqlplan`: planos reais com contadores de execução.
- Arquivos `*_resultado.txt`: resultados comparados antes/depois.
- `resumo.json`: medianas, amostras, versão e hashes SHA-256 dos arquivos locais executados; as terminações de linha fazem parte desses hashes.

O tempo `wall_sqlcmd_ms` do resumo inclui abertura da conexão e saída do cliente. Não equivale ao tempo exclusivo da consulta. O campo de duração da carga adicional está nulo porque a carga ocorreu antes da retomada da validação; sua contagem e execução estão preservadas no log, sem inventar uma duração.
