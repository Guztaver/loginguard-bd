# Executar com privilégios de administrador somente quando for conveniente.
# Inicia apenas o serviço já instalado, sem instalar software, abrir rede ou reiniciar.
$ErrorActionPreference = 'Stop'
$taskProjectRoot = Split-Path -Parent $PSScriptRoot
$taskLogDirectory = Join-Path $taskProjectRoot 'tmp\setup'
New-Item -ItemType Directory -Path $taskLogDirectory -Force | Out-Null
$taskLog = Join-Path $taskLogDirectory 'inicio-servico.txt'
try {
    $taskService = Get-Service -Name 'MSSQL$SQLEXPRESS'
    if ($taskService.Status -ne 'Running') {
        Start-Service -Name 'MSSQL$SQLEXPRESS'
        $taskService.WaitForStatus('Running', [TimeSpan]::FromSeconds(45))
    }
    'Serviço SQL Express em execução. Nenhum reinício do Windows foi solicitado.' |
        Set-Content -LiteralPath $taskLog -Encoding utf8
} catch {
    $_.Exception.Message | Set-Content -LiteralPath $taskLog -Encoding utf8
    exit 1
}
