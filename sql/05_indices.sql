USE LoginGuardAcademico;
GO
-- Opções exigidas pelo SQL Server para índices filtrados, inclusive no sqlcmd.
SET ANSI_NULLS ON;
SET ANSI_PADDING ON;
SET ANSI_WARNINGS ON;
SET ARITHABORT ON;
SET CONCAT_NULL_YIELDS_NULL ON;
SET QUOTED_IDENTIFIER ON;
SET NUMERIC_ROUNDABORT OFF;
GO
CREATE INDEX IX_Tentativa_Conta_Data
ON dbo.TentativaLogin (ContaId, OcorridoEm DESC)
INCLUDE (Sucesso);

CREATE INDEX IX_Tentativa_Falha_Data_Conta
ON dbo.TentativaLogin (OcorridoEm, ContaId)
WHERE Sucesso = 0;
GO
-- Repetir as consultas do script 04 com o mesmo volume e os mesmos parâmetros.
-- As medições executadas pelo validador são preservadas em evidencias/.
