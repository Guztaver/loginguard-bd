"""Executa a entrega de BD e preserva logs, planos reais e métricas.

Requer SQL Server em execução e sqlcmd no PATH. Não instala programas,
não solicita elevação, não apaga bancos e não limpa cache da instância.
"""
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import statistics
import subprocess
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'evidencias'
TMP = ROOT / 'tmp' / 'validacao'
DB = 'LoginGuardAcademico'
QUERIES = {
    'Q1': """SELECT TOP (50) ContaId, OcorridoEm, Sucesso
FROM dbo.TentativaLogin
WHERE ContaId = 12
  AND OcorridoEm >= '2026-10-20T00:00:00'
  AND OcorridoEm < '2026-10-22T00:00:00'
ORDER BY OcorridoEm DESC;""",
    'Q2': """SELECT TOP (10) ContaId, COUNT_BIG(*) AS Falhas
FROM dbo.TentativaLogin
WHERE Sucesso = 0 AND ContaId IS NOT NULL
  AND OcorridoEm >= '2026-10-20T00:00:00'
  AND OcorridoEm < '2026-10-22T00:00:00'
GROUP BY ContaId ORDER BY Falhas DESC, ContaId;""",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server', default=r'.\SQLEXPRESS')
    parser.add_argument('--resume', action='store_true',
                        help='Retoma somente um banco marcado por este validador.')
    args = parser.parse_args()
    sqlcmd = shutil.which('sqlcmd')
    if not sqlcmd:
        raise RuntimeError('sqlcmd não encontrado no PATH.')
    EVIDENCE.mkdir(exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)

    def execute(sql=None, source=None, name='comando', database=DB, persist=True):
        if source is None:
            source = TMP / (name + '.sql')
            source.write_text(sql, encoding='utf-8')
        command = [sqlcmd, '-S', args.server, '-E', '-I', '-d', database,
                   '-l', '10', '-t', '120', '-b', '-V', '16', '-f', '65001',
                   '-w', '65535', '-y', '0', '-i', str(source)]
        start = time.perf_counter()
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                timeout=150, check=False)
        output = result.stdout.decode('utf-8', errors='replace')
        if persist:
            (EVIDENCE / (name + '.txt')).write_text(output, encoding='utf-8')
        if result.returncode:
            raise RuntimeError(f'{name} falhou ({result.returncode}):\n{output}')
        return output, (time.perf_counter() - start) * 1000

    output, _ = execute(sql=f"SET NOCOUNT ON; SELECT CASE WHEN DB_ID(N'{DB}') IS NULL THEN 0 ELSE 1 END;",
                        database='master', name='verificacao_instancia', persist=False)
    exists = bool(re.search(r'^\s*1\s*$', output, re.M))
    if exists:
        if not args.resume:
            raise RuntimeError('Banco já existe. Nada foi alterado; use --resume apenas para retomar este laboratório.')
        marker, _ = execute(sql="SET NOCOUNT ON; SELECT CONVERT(nvarchar(128), value) FROM sys.extended_properties WHERE class = 0 AND name = N'LoginGuardValidador';",
                            name='verificacao_marcador', persist=False)
        if 'loginguard-bd-v1' not in marker:
            raise RuntimeError('Banco existente não foi identificado como laboratório deste validador. Nada foi alterado.')
    else:
        print('Criando e carregando a base fictícia...', flush=True)
        execute(source=ROOT / 'sql' / '01_criacao_carga.sql', database='master', name='01_criacao_carga')
        execute(sql="EXEC sys.sp_addextendedproperty @name=N'LoginGuardValidador', @value=N'loginguard-bd-v1';",
                name='marcador', persist=False)

    role, _ = execute(sql="SET NOCOUNT ON; SELECT CASE WHEN DATABASE_PRINCIPAL_ID(N'lg_administrador') IS NULL THEN 0 ELSE 1 END;",
                      name='papel_existe', persist=False)
    if re.search(r'^\s*0\s*$', role, re.M):
        execute(source=ROOT / 'sql' / '02_permissoes.sql', name='02_permissoes')
    print('Executando testes de permissão e mascaramento...', flush=True)
    execute(source=ROOT / 'sql' / '03_testes_permissoes.sql', name='03_testes_permissoes')

    counts, _ = execute(sql="SET NOCOUNT ON; SELECT (SELECT COUNT_BIG(*) FROM dbo.Conta), (SELECT COUNT_BIG(*) FROM dbo.Credencial), (SELECT COUNT_BIG(*) FROM dbo.TentativaLogin);",
                        name='contagens_iniciais')
    match = re.search(r'^\s*(\d+)\s+(\d+)\s+(\d+)\s*$', counts, re.M)
    if not match or tuple(map(int, match.groups()[:2])) != (50, 50):
        raise RuntimeError('A base não contém as 50 contas e 50 credenciais esperadas.')
    attempts = int(match[3])
    if attempts == 500:
        print('Gerando 200 mil eventos adicionais...', flush=True)
        script = (ROOT / 'sql' / '04_volume_consultas.sql').read_text(encoding='utf-8')
        # Executa apenas a carga. As duas consultas são medidas separadamente abaixo.
        load = script.split('-- Repetir APENAS este bloco')[0]
        _, load_ms = execute(sql=load, name='04_volume_carga')
    elif args.resume and attempts == 200500:
        load_ms = None
    else:
        raise RuntimeError(f'Volume inesperado de eventos: {attempts}. Não será modificado.')

    execute(sql="""IF EXISTS(SELECT 1 FROM sys.indexes WHERE name=N'IX_Tentativa_Conta_Data' AND object_id=OBJECT_ID(N'dbo.TentativaLogin'))
    DROP INDEX IX_Tentativa_Conta_Data ON dbo.TentativaLogin;
IF EXISTS(SELECT 1 FROM sys.indexes WHERE name=N'IX_Tentativa_Falha_Data_Conta' AND object_id=OBJECT_ID(N'dbo.TentativaLogin'))
    DROP INDEX IX_Tentativa_Falha_Data_Conta ON dbo.TentativaLogin;""", name='preparacao_sem_indices')

    measurements = {}
    results = {}
    plan_ns = {'sp': 'http://schemas.microsoft.com/sqlserver/2004/07/showplan'}
    for phase in ['antes', 'depois']:
        if phase == 'depois':
            execute(source=ROOT / 'sql' / '05_indices.sql', name='05_indices')
        print(f'Medindo consultas: {phase} dos índices...', flush=True)
        measurements[phase] = {}
        for query_name, query in QUERIES.items():
            observations = []
            for run in range(6):  # aquecimento + cinco amostras
                sql = 'SET NOCOUNT ON; SET LANGUAGE us_english;\nSET STATISTICS IO ON; SET STATISTICS TIME ON;\n' + query + '\nSET STATISTICS TIME OFF; SET STATISTICS IO OFF;'
                output, wall_ms = execute(sql=sql, name=f'{phase}_{query_name}_{run}')
                reads = re.findall(r"Table 'TentativaLogin'.*?logical reads (\d+)", output)
                execution = re.findall(r'SQL Server Execution Times:\s*CPU time = (\d+) ms,\s*elapsed time = (\d+) ms', output)
                if not reads or not execution:
                    raise RuntimeError(f'Estatísticas ausentes para {phase}/{query_name}. Consulte o log bruto.')
                observations.append({'leituras_logicas': sum(map(int, reads)),
                                     'cpu_ms': max(int(x[0]) for x in execution),
                                     'elapsed_sql_ms': max(int(x[1]) for x in execution),
                                     'wall_sqlcmd_ms': round(wall_ms, 3)})
            measured = observations[1:]
            measurements[phase][query_name] = {
                'aquecimento': observations[0], 'amostras': measured,
                'mediana_leituras_logicas': statistics.median(x['leituras_logicas'] for x in measured),
                'mediana_cpu_ms': statistics.median(x['cpu_ms'] for x in measured),
                'mediana_elapsed_sql_ms': statistics.median(x['elapsed_sql_ms'] for x in measured),
                'mediana_wall_sqlcmd_ms': statistics.median(x['wall_sqlcmd_ms'] for x in measured),
            }
            # Resultado sem estatísticas: comparação exata entre as duas fases.
            output, _ = execute(sql='SET NOCOUNT ON;\n' + query, name=f'{phase}_{query_name}_resultado')
            normalized = '\n'.join(line.rstrip() for line in output.splitlines() if line.strip())
            results.setdefault(query_name, {})[phase] = normalized
            plan_output, _ = execute(sql='SET NOCOUNT ON; SET STATISTICS XML ON;\n' + query + '\nSET STATISTICS XML OFF;',
                                     name=f'{phase}_{query_name}_plano_bruto')
            xml = re.search(r'<ShowPlanXML\b.*?</ShowPlanXML>', plan_output, re.S)
            if not xml:
                raise RuntimeError(f'Plano real ausente para {phase}/{query_name}.')
            tree = ET.fromstring(xml[0])
            operators = sorted(set(node.attrib['PhysicalOp'] for node in tree.findall('.//sp:RelOp', plan_ns)))
            indexes = sorted(set(node.attrib['Index'] for node in tree.findall('.//sp:Object', plan_ns) if 'Index' in node.attrib))
            if not tree.findall('.//sp:RunTimeCountersPerThread', plan_ns):
                raise RuntimeError('Plano obtido não contém contadores de execução real.')
            (EVIDENCE / f'{phase}_{query_name}.sqlplan').write_text(xml[0], encoding='utf-8')
            measurements[phase][query_name].update({'operadores': operators, 'indices_no_plano': indexes})

    for query_name, phases in results.items():
        if phases['antes'] != phases['depois']:
            raise RuntimeError(f'Os resultados de {query_name} mudaram após os índices.')
    final_counts, _ = execute(sql="SET NOCOUNT ON; SELECT (SELECT COUNT_BIG(*) FROM dbo.Conta), (SELECT COUNT_BIG(*) FROM dbo.Credencial), (SELECT COUNT_BIG(*) FROM dbo.TentativaLogin);",
                             name='contagens_finais')
    if not re.search(r'^\s*50\s+50\s+200500\s*$', final_counts, re.M):
        raise RuntimeError('Contagens finais divergentes do volume esperado.')
    version, _ = execute(sql="SET NOCOUNT ON; SELECT CONVERT(varchar(128), SERVERPROPERTY('ProductVersion')), CONVERT(varchar(128), SERVERPROPERTY('Edition'));",
                         name='versao_sqlserver')
    # Reexecuta os testes com os índices e volume final.
    execute(source=ROOT / 'sql' / '03_testes_permissoes.sql', name='06_testes_finais')
    summary = {'executado_em_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
               'banco': DB, 'versao_edicao': version.strip(),
               'contas': 50, 'credenciais': 50, 'tentativas_iniciais': 500,
               'tentativas_finais': 200500, 'carga_adicional_wall_ms': load_ms,
               'testes_permissoes': 'aprovados', 'resultados_consultas_identicos': True,
               'medicoes': measurements,
               'scripts_sha256': {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((ROOT/'sql').glob('*.sql'))}}
    (EVIDENCE / 'resumo.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    print('Validação concluída. Evidências em evidencias/.', flush=True)


if __name__ == '__main__':
    main()
