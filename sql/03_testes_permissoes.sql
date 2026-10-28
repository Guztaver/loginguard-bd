USE LoginGuardAcademico;
GO
SET NOCOUNT ON;
DECLARE @falhas int = 0, @erro int, @emailMascarado varchar(254);

EXECUTE AS USER = N'demo_suporte';
-- Deve retornar e-mails mascarados e permitir a consulta.
SELECT TOP (3) USER_NAME() AS Executor, ContaId, Email FROM dbo.vContas ORDER BY ContaId;
-- Predicados WHERE podem usar o valor original mesmo com DDM.
-- Validar o valor projetado para o usuário, não filtrar a coluna mascarada.
SELECT @emailMascarado = Email FROM dbo.vContas WHERE ContaId = 1;
IF @emailMascarado IS NULL OR @emailMascarado LIKE '%@example.invalid'
BEGIN
    PRINT N'FALHOU: e-mail sem máscara.';
    SET @falhas += 1;
END;
BEGIN TRY
    EXEC(N'SELECT HashSenha FROM dbo.Credencial;');
    PRINT N'FALHOU: suporte leu credenciais.'; SET @falhas += 1;
END TRY
BEGIN CATCH
    SET @erro = ERROR_NUMBER();
    IF @erro <> 229 BEGIN PRINT ERROR_MESSAGE(); SET @falhas += 1; END
    ELSE PRINT N'OK: SELECT em Credencial negado (229).';
END CATCH;
BEGIN TRANSACTION;
BEGIN TRY
    EXEC(N'UPDATE dbo.Conta SET Bloqueado = 0 WHERE ContaId = 1;');
    PRINT N'FALHOU: suporte alterou conta.'; SET @falhas += 1;
END TRY
BEGIN CATCH
    SET @erro = ERROR_NUMBER();
    IF @erro <> 229 BEGIN PRINT ERROR_MESSAGE(); SET @falhas += 1; END
    ELSE PRINT N'OK: UPDATE em Conta negado (229).';
END CATCH;
IF @@TRANCOUNT > 0 ROLLBACK;
BEGIN TRANSACTION;
BEGIN TRY
    EXEC(N'ALTER ROLE lg_administrador ADD MEMBER demo_suporte;');
    PRINT N'FALHOU: suporte elevou privilégios.'; SET @falhas += 1;
END TRY
BEGIN CATCH
    SET @erro = ERROR_NUMBER();
    IF @erro NOT IN (15151, 15247, 229)
    BEGIN PRINT ERROR_MESSAGE(); SET @falhas += 1; END
    ELSE PRINT N'OK: alteração do papel negada.';
END CATCH;
IF @@TRANCOUNT > 0 ROLLBACK;
REVERT;

EXECUTE AS USER = N'demo_auditor';
SELECT TOP (3) USER_NAME() AS Executor, * FROM dbo.vHistorico ORDER BY TentativaId;
BEGIN TRANSACTION;
BEGIN TRY
    EXEC(N'DELETE dbo.TentativaLogin WHERE TentativaId = 1;');
    PRINT N'FALHOU: auditor apagou histórico.'; SET @falhas += 1;
END TRY
BEGIN CATCH
    SET @erro = ERROR_NUMBER();
    IF @erro <> 229 BEGIN PRINT ERROR_MESSAGE(); SET @falhas += 1; END
    ELSE PRINT N'OK: DELETE em histórico negado (229).';
END CATCH;
IF @@TRANCOUNT > 0 ROLLBACK;
REVERT;

EXECUTE AS USER = N'demo_admin';
BEGIN TRANSACTION;
UPDATE dbo.Conta SET Bloqueado = 1 WHERE ContaId = 1;
IF @@ROWCOUNT <> 1 SET @falhas += 1;
ROLLBACK;
BEGIN TRY
    EXEC(N'SELECT HashSenha FROM dbo.Credencial;');
    PRINT N'FALHOU: administrador leu credenciais.'; SET @falhas += 1;
END TRY
BEGIN CATCH
    SET @erro = ERROR_NUMBER();
    IF @erro <> 229 BEGIN PRINT ERROR_MESSAGE(); SET @falhas += 1; END
    ELSE PRINT N'OK: administrador também não lê hashes.';
END CATCH;
REVERT;

IF @falhas > 0 THROW 51000, N'Houve falhas nos testes. Confira as mensagens.', 1;
PRINT N'Testes concluídos. Confira visualmente o mascaramento e arquive a saída.';
GO
