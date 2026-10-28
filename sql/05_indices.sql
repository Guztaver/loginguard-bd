USE LoginGuardAcademico;
GO
CREATE INDEX IX_Tentativa_Conta_Data
ON dbo.TentativaLogin (ContaId, OcorridoEm DESC)
INCLUDE (Sucesso);

CREATE INDEX IX_Tentativa_Falha_Data_Conta
ON dbo.TentativaLogin (OcorridoEm, ContaId)
WHERE Sucesso = 0;
GO
-- Repetir as consultas do script 04 com o mesmo volume e os mesmos parâmetros.
-- Não há resultados de benchmark até executar e registrar as medições.
