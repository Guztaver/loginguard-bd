USE LoginGuardAcademico;
GO
-- Executar este bloco de carga uma vez. Não apaga nem substitui dados existentes.
-- Gera números sem depender da quantidade de objetos de sistema.
DECLARE @quantidade int = 200000;
;WITH digito AS (
    SELECT n FROM (VALUES(0),(1),(2),(3),(4),(5),(6),(7),(8),(9)) AS d(n)
), numeros AS (
    SELECT TOP (@quantidade)
        ROW_NUMBER() OVER (ORDER BY a.n,b.n,c.n,d.n,e.n,f.n) AS n
    FROM digito a CROSS JOIN digito b CROSS JOIN digito c
    CROSS JOIN digito d CROSS JOIN digito e CROSS JOIN digito f
)
INSERT dbo.TentativaLogin (ContaId, OcorridoEm, Sucesso, IpOrigem)
SELECT 1 + ((n - 1) % 50),
       DATEADD(SECOND, CONVERT(int, n * 10), CONVERT(datetime2(0), '20261001', 112)),
       CASE WHEN n % 3 = 0 THEN 0 ELSE 1 END,
       CONCAT('192.0.2.', 1 + (n % 254))
FROM numeros;
SELECT COUNT_BIG(*) AS TotalEventos FROM dbo.TentativaLogin;
GO
-- Repetir APENAS este bloco de consultas depois de aplicar o script 05.
-- No SSMS: habilitar o plano real (Ctrl+M) e salvar a aba Mensagens.
SET STATISTICS IO ON;
SET STATISTICS TIME ON;
DECLARE @conta int = 12,
        @inicio datetime2(0) = '2026-10-20T00:00:00',
        @fim datetime2(0) = '2026-10-22T00:00:00';

-- Q1: últimos acessos de uma conta no período.
SELECT TOP (50) ContaId, OcorridoEm, Sucesso
FROM dbo.TentativaLogin
WHERE ContaId = @conta AND OcorridoEm >= @inicio AND OcorridoEm < @fim
ORDER BY OcorridoEm DESC;

-- Q2: contas com mais falhas no período.
SELECT TOP (10) ContaId, COUNT_BIG(*) AS Falhas
FROM dbo.TentativaLogin
WHERE Sucesso = 0 AND OcorridoEm >= @inicio AND OcorridoEm < @fim
  AND ContaId IS NOT NULL
GROUP BY ContaId
ORDER BY Falhas DESC, ContaId;
SET STATISTICS IO OFF;
SET STATISTICS TIME OFF;
GO
