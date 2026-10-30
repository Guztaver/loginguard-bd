from pathlib import Path
import re
import json
import textwrap
from xml.sax.saxutils import escape

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable, Preformatted

ROOT = Path(__file__).resolve().parents[1]
RESULTS_FILE = ROOT / 'evidencias' / 'resumo.json'
RESULTS = json.loads(RESULTS_FILE.read_text(encoding='utf-8')) if RESULTS_FILE.exists() else None
OUT = ROOT / 'output' / 'pdf' / 'LoginGuard_Entrega_OAT_BD.pdf'
OUT.parent.mkdir(parents=True, exist_ok=True)
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialBold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFont(TTFont('Consolas', 'C:/Windows/Fonts/consola.ttf'))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='ArialBold', italic='Arial', boldItalic='ArialBold')
NAVY = colors.HexColor('#13334B')
TEAL = colors.HexColor('#007E87')
LIGHT = colors.HexColor('#EFF5F7')
INK = colors.HexColor('#253746')
WIDTH = A4[0] - 88
styles = {
    'body': ParagraphStyle('body', fontName='Arial', fontSize=10, leading=14.1, textColor=INK, spaceAfter=8),
    'small': ParagraphStyle('small', fontName='Arial', fontSize=8.6, leading=11.5, textColor=INK, spaceAfter=6),
    'cell': ParagraphStyle('cell', fontName='Arial', fontSize=8.4, leading=11, textColor=INK),
    'th': ParagraphStyle('th', fontName='ArialBold', fontSize=8.4, leading=11, textColor=colors.white),
    'h1': ParagraphStyle('h1', fontName='ArialBold', fontSize=23, leading=28, textColor=NAVY, spaceAfter=14),
    'h2': ParagraphStyle('h2', fontName='ArialBold', fontSize=12, leading=16, textColor=TEAL, spaceBefore=9, spaceAfter=7),
    'kicker': ParagraphStyle('kicker', fontName='ArialBold', fontSize=9, leading=13, textColor=TEAL, spaceAfter=9),
    'code': ParagraphStyle('code', fontName='Consolas', fontSize=7.5, leading=9, textColor=INK),
}
story = []

def p(text, style='body'):
    return Paragraph(text, styles[style])

def add(text, style='body'):
    story.append(p(text, style))

def heading(text):
    add(text, 'h2')

def page(kicker, title):
    if story:
        story.append(PageBreak())
    add(kicker.upper(), 'kicker')
    add(title, 'h1')

def table(headers, rows, widths, size='cell'):
    data = [[p(escape(str(x)), 'th') for x in headers]]
    data += [[p(escape(str(x)), size) for x in row] for row in rows]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [LIGHT, colors.white]),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, TEAL),
        ('LINEBELOW', (0, 1), (-1, -1), 0.25, colors.HexColor('#D9E3E8')),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))

def callout(title, text):
    t = Table([[p(title, 'h2')], [p(text, 'small')]], colWidths=[WIDTH])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor('#C7DDE0')),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 3),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 10),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))

class Architecture(Flowable):
    def __init__(self):
        Flowable.__init__(self)
        self.width, self.height = WIDTH, 116

    def draw(self):
        c = self.canv
        boxes = [(0, 58, 112, ['Operadores', 'Admin / Suporte / Auditor']),
                 (133, 58, 121, ['Terminal Python', 'Consultas parametrizadas']),
                 (275, 58, 232, ['SQL Server', 'GRANT / DENY e mascaramento'])]
        for x, y, w, lines in boxes:
            c.setFillColor(LIGHT)
            c.setStrokeColor(TEAL)
            c.roundRect(x, y, w, 47, 5, fill=1, stroke=1)
            c.setFillColor(NAVY)
            c.setFont('ArialBold', 9)
            c.drawCentredString(x + w/2, y + 29, lines[0])
            c.setFont('Arial', 7.4)
            c.drawCentredString(x + w/2, y + 13, lines[1])
        c.setStrokeColor(TEAL)
        for x in [112, 254]:
            c.line(x, 81, x+20, 81)
            c.line(x+20, 81, x+16, 84)
            c.line(x+20, 81, x+16, 78)
        for x, w, label in [(0, 150, 'Conta'), (175, 157, 'Credencial'), (357, 150, 'TentativaLogin')]:
            c.setFillColor(NAVY)
            c.roundRect(x, 3, w, 31, 4, fill=1, stroke=0)
            c.setFillColor(colors.white)
            c.setFont('ArialBold', 9)
            c.drawCentredString(x + w/2, 15, label)
        c.line(391, 58, 391, 44)
        c.line(75, 44, 432, 44)
        for x in [75, 253, 432]:
            c.line(x, 44, x, 34)

members = [
    ('Luid Moura Santana', '262070177'),
    ('Alex Gabriel Alves Dos Santos', '241070261'),
    ('Filipe Alves Ferreira Rocha', '222700092'),
    ('Gustavo Muniz dos Anjos', '241070612'),
]
repo = 'https://github.com/Guztaver/loginguard-bd'
link = f'<link href="{repo}" color="#007E87">github.com/Guztaver/loginguard-bd</link>'

page('OAT | Parte comum e Parte de Segurança', 'LoginGuard')
add('Gestão de logins, contas e acessos pelo terminal', 'h2')
add('<b>Grupo:</b> LoginGuard<br/><b>Disciplina:</b> Segurança e Otimização de Banco de Dados<br/><b>Documento:</b> entrega inicial de arquitetura e planejamento')
table(['Nome completo', 'Matrícula'], members, [WIDTH-110, 110])
add(f'<b>Repositório do projeto:</b> {link}', 'small')
heading('Problema, público e resultado esperado')
add('Equipes de suporte precisam cadastrar contas, controlar bloqueios e investigar acessos sem expor credenciais ou permitir alterações por pessoas sem autorização. Quando o projeto funcionar, cada operador terá acesso apenas às operações e aos dados necessários ao seu trabalho.')
heading('Escopo da versão mínima')
add('Programa de terminal em Python conectado ao SQL Server, com cadastro, autenticação, bloqueio e desbloqueio, três perfis de operação e histórico de tentativas. O projeto gerencia contas de usuários do sistema. As identidades que se conectam ao banco formam uma camada separada de autorização.')
add('O recorte corresponde à Parte comum e à Parte de Segurança. A interface será terminal e os dados operacionais serão totalmente fictícios. O MVP será desenvolvido em três semanas, conforme o canvas.')
callout('Estado real da entrega',
        'Base SQL Server criada e carregada: 50 contas, 50 credenciais sem senha e 500 eventos iniciais; após o experimento, 200.500 eventos. Os testes de permissão passaram e as consultas foram medidas antes e depois dos índices, com planos reais preservados. O aplicativo e a autenticação continuam previstos para as próximas semanas.'
        if RESULTS else
        'A proposta e os cinco scripts SQL estão no repositório. O aplicativo e a autenticação ainda serão implementados. A execução dos scripts e a carga do banco não foram comprovadas: o SQL Express local permanece parado. Os planos de teste deste documento não representam resultados já obtidos.')
add('O repositório está privado. O professor precisa ter acesso para avaliar o código pelo link. Os scripts de criação/carga e de permissões também estão reproduzidos nos apêndices deste PDF.', 'small')

page('Parte comum | Canvas de uma página', 'Canvas do projeto')
rows = [
 ('Problema e usuário', 'Contas sem controle de bloqueio e permissões excessivas. Usuários: administrador, suporte e auditor.'),
 ('Entrada', 'Nome e e-mail fictícios, identificador de conta, senha digitada de forma oculta e comandos no terminal.'),
 ('Saída', 'Resultado genérico da autenticação, confirmação de operações, situação das contas e histórico de tentativas.'),
 ('Maior risco', 'Leitura indevida de hashes ou alteração de contas por usuário sem permissão.'),
 ('Proteções', 'Papéis mínimos, DENY explícito, credenciais separadas, hash Argon2id e mascaramento de e-mail/IP.'),
 ('MVP em três semanas', 'Cadastro, login, bloqueio/desbloqueio, três perfis, histórico e duas consultas otimizadas.'),
 ('Dados e escala', ('Carga inicial executada' if RESULTS else 'Carga inicial prevista') + ': 50 contas, 50 registros de credencial sem senha e 500 eventos fictícios. Experimento: mais 200 mil eventos.'),
 ('Como provar', 'Testes por papel e comparação de leituras lógicas, tempo e plano antes/depois dos índices.'),
]
table(['Elemento', 'Definição'], rows, [112, WIDTH-112])
heading('Arquitetura em caixas')
story.append(Architecture())
add('O terminal, a autenticação e o acesso restrito do serviço são componentes planejados. Os scripts já descrevem as tabelas e as permissões dos três papéis humanos.', 'small')
add('<b>Semana 1:</b> banco, carga e permissões. <b>Semana 2:</b> terminal e autenticação. <b>Semana 3:</b> testes, índices e evidências.', 'small')

page('Parte de Segurança | Modelo de dados', 'Campos e proteção')
add('<b>Banco escolhido:</b> SQL Server 2016 ou superior. Não há campos públicos: os metadados são internos e os dados de contato/credenciais são sensíveis.')
rows = [
 ('Conta', 'ContaId', 'Interno', 'PK; acesso por papel.'),
 ('Conta', 'Nome', 'Interno', 'Fictício; leitura limitada aos operadores.'),
 ('Conta', 'Email', 'Sensível', 'Máscara email(); DENY UNMASK.'),
 ('Conta', 'Bloqueado', 'Interno', 'Alteração apenas pelo administrador.'),
 ('Conta', 'CriadoEm', 'Interno', 'Leitura por papel; padrão UTC.'),
 ('Credencial', 'ContaId', 'Interno', 'PK e FK; tabela separada e restrita.'),
 ('Credencial', 'HashSenha', 'Sensível', 'Argon2id na aplicação; DENY SELECT aos três papéis humanos.'),
 ('Credencial', 'AtualizadoEm', 'Interno', 'Restrito junto às credenciais.'),
 ('TentativaLogin', 'TentativaId', 'Interno', 'PK; histórico somente leitura para operadores autorizados.'),
 ('TentativaLogin', 'ContaId', 'Interno', 'FK opcional; não copia nome ou e-mail.'),
 ('TentativaLogin', 'OcorridoEm', 'Interno', 'Filtro temporal; histórico protegido.'),
 ('TentativaLogin', 'Sucesso', 'Interno', 'Resultado da tentativa; acesso por papel.'),
 ('TentativaLogin', 'IpOrigem', 'Sensível', 'Máscara default(); omitido da view de histórico.'),
]
table(['Tabela', 'Campo', 'Classe', 'Proteção prevista'], rows, [92, 90, 60, WIDTH-242])
heading('Relacionamentos e dados iniciais')
add('Conta (1) para Credencial (0..1); Conta (1) para TentativaLogin (0..N). Uma tentativa para conta inexistente pode usar ContaId = NULL.', 'small')
add('A carga usa nomes "Pessoa Fictícia N", e-mails @example.invalid e IPs 192.0.2.0/24. Os eventos são sintéticos. Todas as contas começam bloqueadas e com HashSenha = NULL; não são contas utilizáveis.', 'small')
add('O Argon2id será aplicado por biblioteca na aplicação, com salt e parâmetros incluídos no hash. O CHECK do banco valida apenas o prefixo. Mascaramento não substitui autorização nem elimina inferências; a conexão futura deverá usar TLS com certificado validado.', 'small')

page('Parte de Segurança | Papéis e ameaças', 'Quem pode fazer o quê')
rows = [
 ('Consultar contas com e-mail mascarado', 'Sim', 'Sim', 'Sim'),
 ('Cadastrar conta e alterar nome, e-mail ou bloqueio', 'Sim', 'Não', 'Não'),
 ('Inserir/atualizar hash para cadastro ou redefinição', 'Sim¹', 'Não', 'Não'),
 ('Ler hashes de senha', 'DENY', 'DENY', 'DENY'),
 ('Consultar histórico sem IP', 'Sim', 'Não', 'Sim'),
 ('Inserir, alterar ou excluir histórico diretamente', 'DENY', 'DENY', 'DENY'),
 ('Alterar papéis ou estrutura do banco', 'Não concedido', 'Não concedido', 'Não concedido'),
]
table(['Operação', 'Administrador', 'Suporte', 'Auditor'], rows, [WIDTH-225, 83, 71, 71])
add('¹ Por componente confiável que gera o hash. O administrador funcional pode substituir hashes, mas não ler seu conteúdo. Identidades de teste: demo_admin, demo_suporte e demo_auditor, todas WITHOUT LOGIN.', 'small')
add('Os DENYs aparecem em Credencial (SELECT) e TentativaLogin (INSERT, UPDATE, DELETE). Suporte e auditor também têm escrita negada em Conta e Credencial. Nenhum dos três papéis recebe UNMASK.', 'small')
heading('Ameaça principal e como demonstrar a correção')
add('<b>Escalonamento de privilégio:</b> o suporte tenta desbloquear uma conta, ler hashes ou se adicionar ao papel de administrador. O auditor tenta apagar o histórico.')
table(['Teste previsto', 'Resultado esperado'], [
 ('Suporte: SELECT em Credencial', 'Erro de permissão.'),
 ('Suporte: UPDATE em Conta', 'Erro de permissão; conta preservada.'),
 ('Suporte: ALTER ROLE de administrador', 'Erro de permissão; papel preservado.'),
 ('Auditor: DELETE em TentativaLogin', 'Erro de permissão; histórico preservado.'),
 ('Consulta autorizada pela view', 'Leitura funciona; e-mail aparece mascarado.'),
], [WIDTH/2, WIDTH/2])
add('O script sql/03_testes_permissoes.sql usa EXECUTE AS USER. Critério: operações proibidas são negadas e permitidas funcionam. ' + ('Testes executados e aprovados antes e depois do experimento; logs em evidencias/.' if RESULTS else 'Testes ainda não executados.'), 'small')
add('Teste adicional planejado: usar uma entrada de SQL Injection no terminal e verificar que ela é tratada como dado por consultas parametrizadas. O serviço de autenticação terá identidade restrita própria. Não usar db_owner/sysadmin; donos dos objetos e sysadmin não ficam limitados por esses DENYs.', 'small')

page('Parte de Segurança | Plano de otimização', 'Duas consultas sob volume')
table(['Consulta candidata a gargalo', 'Índice proposto'], [
 ('Q1. Últimas 50 tentativas de uma conta em um período.', '(ContaId, OcorridoEm DESC) INCLUDE (Sucesso)'),
 ('Q2. Dez contas com mais falhas em um período.', 'Filtrado: (OcorridoEm, ContaId) WHERE Sucesso = 0'),
], [WIDTH/2, WIDTH/2])
heading('Geração de volume')
add('O script 01 prevê 50 contas, 50 registros de credencial e 500 tentativas. O script 04 acrescenta 200 mil eventos por geração numérica, distribuídos entre contas e horários. A quantidade pode ser ajustada na variável @quantidade. Não há resultados reais de autenticação na massa.')
heading('Medição antes e depois')
add('1. Executar a criação/carga e a carga adicional antes dos índices. Habilitar o plano de execução real no SSMS e SET STATISTICS IO, TIME ON.<br/>2. Executar uma rodada de aquecimento e cinco medições das duas consultas.<br/>3. Aplicar sql/05_indices.sql e repetir apenas as consultas com o mesmo volume e parâmetros.<br/>4. Comparar a mediana do tempo, leituras lógicas e plano de execução. Confirmar resultados equivalentes.')
add('Não limpar cache global de instância compartilhada. Considerar o efeito de aquecimento e de estatísticas. Medir também o custo dos índices nas escritas e no armazenamento. As consultas são candidatas a gargalo; o experimento deverá comprovar se são lentas no equipamento.', 'small')
if RESULTS:
    table(['Medição executada', 'Antes', 'Depois'], [
        (q + ': mediana de leituras lógicas',
         RESULTS['medicoes']['antes'][q]['mediana_leituras_logicas'],
         RESULTS['medicoes']['depois'][q]['mediana_leituras_logicas']) for q in ['Q1', 'Q2']
    ] + [
        (q + ': mediana de tempo SQL (ms)',
         RESULTS['medicoes']['antes'][q]['mediana_elapsed_sql_ms'],
         RESULTS['medicoes']['depois'][q]['mediana_elapsed_sql_ms']) for q in ['Q1', 'Q2']
    ], [WIDTH-150, 75, 75])
else:
    table(['Evidência a coletar', 'Antes', 'Depois'], [
     ('Q1: leituras lógicas / mediana ms / plano', 'Pendente', 'Pendente'),
     ('Q2: leituras lógicas / mediana ms / plano', 'Pendente', 'Pendente'),
     ('Linhas por tabela e custo de carga', 'Pendente', 'Pendente'),
    ], [WIDTH-150, 75, 75])
heading('Critério e cronograma')
add('Meta: reduzir leituras lógicas sem alterar o resultado das consultas. Não declarar ganho percentual antes da medição.')
table(['Semana', 'Resultado mínimo planejado'], [
 ('1', 'Banco criado, dados carregados e permissões verificadas.'),
 ('2', 'Terminal, cadastro, Argon2id e autenticação com parâmetros.'),
 ('3', 'Ataques de teste, comparação de índices e evidências documentadas.'),
], [65, WIDTH-65])

page('Parte comum e Segurança | Conferência', 'Entrega e limitações atuais')
table(['Exigência da atividade', 'Material e estado atual'], [
 ('Título, público e problema', 'Apresentados na abertura.'),
 ('Identificação do grupo e integrantes', 'Nomes e matrículas na primeira página.'),
 ('Canvas de uma página', 'Página 2, com arquitetura em caixas.'),
 ('Repositório e README', 'Repositório criado; README disponível no projeto.'),
 ('Modelo, campos e proteção', 'Página 3 e script 01.'),
 ('Três papéis com DENY', 'Página 4 e script 02.'),
 ('Ameaça e prova', 'Testes executados e aprovados; logs em evidencias/.' if RESULTS else 'Plano e script 03; execução pendente.'),
 ('Duas consultas e volume', 'Página 5; scripts 04 e 05.'),
 ('Base inicial carregada', 'EXECUTADO: 50 contas, 50 credenciais e 500 eventos iniciais.' if RESULTS else 'PENDENTE: scripts disponíveis; carga não comprovada.'),
], [170, WIDTH-170])
heading('Preparação da base')
add('Em uma instância de laboratório SQL Server, executar os scripts 01 e 02 no SSMS com uma identidade de implantação autorizada. O banco dedicado chama-se LoginGuardAcademico. O script 01 interrompe se ele já existir, sem sobrescrever dados. Depois executar o script 03 e guardar a saída.')
add('Os scripts 04 e 05 suportam o experimento de desempenho. O programa de terminal ainda não foi implementado. ' +
    ('A carga e os testes de BD foram executados; os dados e as medições estão detalhados na página seguinte.' if RESULTS else
     'Em 30/10/2026, a tentativa de conexão à instância local SQLEXPRESS falhou e o serviço foi encontrado parado. Não se afirma que a carga ou os testes passaram.'), 'small')
heading('Repositório e envio')
add(f'{link}<br/>Repositório privado: o professor deverá ter acesso para avaliar os arquivos. Cada participante deve fazer seu próprio envio. O prazo informado na atividade foi 27/10.', 'small')
heading('Referências técnicas')
refs = [
 ('Microsoft: DENY e exceções de permissão', 'https://learn.microsoft.com/en-us/sql/t-sql/statements/deny-transact-sql'),
 ('Microsoft: Dynamic Data Masking e limitações', 'https://learn.microsoft.com/en-us/sql/relational-databases/security/dynamic-data-masking'),
 ('OWASP: Password Storage Cheat Sheet', 'https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html'),
 ('OWASP: SQL Injection Prevention Cheat Sheet', 'https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html'),
]
for title, url in refs:
    add(f'<link href="{url}" color="#007E87">{title}</link>', 'small')
add('Apoio de IA: Codex na preparação da proposta, documentação e scripts iniciais. Todos os integrantes devem revisar e saber explicar cada parte do projeto.', 'small')

if RESULTS:
    page('Evidências executadas | Banco de dados', 'Resultados observados')
    add('<b>Execução (UTC):</b> ' + escape(RESULTS['executado_em_utc']) +
        '<br/><b>Banco:</b> ' + escape(RESULTS['banco']) +
        '<br/><b>Versão / edição:</b> ' + escape(RESULTS['versao_edicao']), 'small')
    table(['Verificação', 'Resultado'], [
        ('Contas / credenciais / eventos iniciais', '50 / 50 / 500'),
        ('Eventos após carga adicional', '200.500'),
        ('Permissões e mascaramento', 'Aprovados antes e depois do experimento.'),
        ('Resultados de Q1 e Q2', 'Idênticos nas duas fases.'),
        ('Protocolo por consulta e fase', '1 aquecimento + 5 medições; mediana das cinco.'),
    ], [190, WIDTH-190])
    for q in ['Q1', 'Q2']:
        heading(q + ' - planos reais')
        for phase in ['antes', 'depois']:
            measured = RESULTS['medicoes'][phase][q]
            add('<b>' + phase.capitalize() + ':</b> ' + escape(', '.join(measured['operadores'])) +
                '.<br/><b>Índices:</b> ' + escape(', '.join(measured['indices_no_plano'])), 'small')
    heading('Como conferir')
    add('O diretório evidencias/ preserva os logs SQL, os quatro arquivos .sqlplan com contadores reais, os resultados das consultas e o resumo.json. O resumo inclui o SHA-256 dos scripts executados. O validador é tools/executar_validacao.py.', 'small')
    add('Tempos muito curtos podem ser arredondados a 0 ms pelo SQL Server; as leituras lógicas e os planos complementam a análise. O tempo total do sqlcmd inclui abertura de conexão e não equivale ao tempo exclusivo da consulta. Não foi limpo o cache global. Resultados restritos a este volume, distribuição de dados e equipamento.', 'small')

for label, filename, title in [
    ('Apêndice A', '01_criacao_carga.sql', 'Script de criação e carga'),
    ('Apêndice B', '02_permissoes.sql', 'Papéis e permissões'),
]:
    page(label, title)
    add(f'Fonte: sql/{filename}. ' + ('Código executado; logs em evidencias/.' if RESULTS else 'Código disponibilizado, ainda sem validação de execução nesta entrega.'), 'small')
    raw = (ROOT / 'sql' / filename).read_text(encoding='utf-8')
    lines = []
    for line in raw.splitlines():
        lines.extend(textwrap.wrap(line, width=118, subsequent_indent='    ', replace_whitespace=False, drop_whitespace=False) or [''])
    story.append(Preformatted('\n'.join(lines), styles['code']))

def footer(c, doc):
    c.saveState()
    c.setStrokeColor(colors.HexColor('#D4E0E5'))
    c.line(44, 37, A4[0]-44, 37)
    c.setFont('Arial', 8)
    c.setFillColor(INK)
    c.drawString(44, 23, 'LoginGuard | OAT - Segurança e Otimização de BD')
    c.drawRightString(A4[0]-44, 23, str(doc.page))
    c.restoreState()

doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=44, rightMargin=44,
                        topMargin=40, bottomMargin=49, title='LoginGuard - Entrega OAT de Banco de Dados',
                        author='Grupo LoginGuard', subject='Parte comum e Parte de Segurança')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)

# Mantém a identificação das fontes em sincronia com o documento.
bullets = '\n'.join(f'- {name} - matrícula {enrollment}.' for name, enrollment in members)
for rel in ['README.md', 'docs/ENTREGA.md']:
    path = ROOT / rel
    content = path.read_text(encoding='utf-8')
    content = content.replace('**Grupo:** PREENCHER.', '**Grupo:** LoginGuard.')
    content = content.replace('**Componentes:** PREENCHER nome completo e matrícula de cada integrante.', '**Componentes:**\n' + bullets)
    path.write_text(content, encoding='utf-8')
path = ROOT / 'docs' / 'CANVAS.md'
content = path.read_text(encoding='utf-8')
content = content.replace('**Grupo:** PREENCHER • **Componentes (nome completo e matrícula):** PREENCHER', '**Grupo:** LoginGuard.\n\n**Componentes (nome completo e matrícula):**\n' + bullets)
path.write_text(content, encoding='utf-8')
