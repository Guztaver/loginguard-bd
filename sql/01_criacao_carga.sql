-- Laboratório fictício. Execute no SSMS com uma identidade de implantação.
-- Se o banco já existir, interrompe sem alterar seu conteúdo.
USE master;
GO
IF DB_ID(N'LoginGuardAcademico') IS NOT NULL
BEGIN
    RAISERROR(N'Banco já existe. Não execute a carga novamente neste banco.', 16, 1);
    SET NOEXEC ON;
END;
GO
CREATE DATABASE LoginGuardAcademico;
GO
USE LoginGuardAcademico;
GO
CREATE TABLE dbo.Conta (
    ContaId int IDENTITY(1,1) NOT NULL CONSTRAINT PK_Conta PRIMARY KEY,
    Nome nvarchar(120) NOT NULL,
    Email varchar(254) MASKED WITH (FUNCTION = 'email()') NOT NULL,
    Bloqueado bit NOT NULL CONSTRAINT DF_Conta_Bloqueado DEFAULT (1),
    CriadoEm datetime2(0) NOT NULL CONSTRAINT DF_Conta_CriadoEm DEFAULT (SYSUTCDATETIME()),
    CONSTRAINT UQ_Conta_Email UNIQUE (Email)
);
CREATE TABLE dbo.Credencial (
    ContaId int NOT NULL CONSTRAINT PK_Credencial PRIMARY KEY,
    HashSenha varchar(512) NULL,
    AtualizadoEm datetime2(0) NOT NULL CONSTRAINT DF_Credencial_Data DEFAULT (SYSUTCDATETIME()),
    CONSTRAINT FK_Credencial_Conta FOREIGN KEY (ContaId) REFERENCES dbo.Conta(ContaId),
    CONSTRAINT CK_Credencial_Formato CHECK (HashSenha IS NULL OR HashSenha LIKE '$argon2id$%')
);
-- O CHECK valida apenas um prefixo. A biblioteca da aplicação deverá validar o hash.
CREATE TABLE dbo.TentativaLogin (
    TentativaId bigint IDENTITY(1,1) NOT NULL CONSTRAINT PK_TentativaLogin PRIMARY KEY,
    ContaId int NULL,
    OcorridoEm datetime2(0) NOT NULL,
    Sucesso bit NOT NULL,
    IpOrigem varchar(45) MASKED WITH (FUNCTION = 'default()') NOT NULL,
    CONSTRAINT FK_TentativaLogin_Conta FOREIGN KEY (ContaId) REFERENCES dbo.Conta(ContaId)
);
GO
SET XACT_ABORT ON;
BEGIN TRANSACTION;
DECLARE @n int = 1;
WHILE @n <= 50
BEGIN
    INSERT dbo.Conta (Nome, Email)
    VALUES (CONCAT(N'Pessoa Fictícia ', @n), CONCAT('pessoa', @n, '@example.invalid'));
    SET @n += 1;
END;
INSERT dbo.Credencial (ContaId, HashSenha)
SELECT ContaId, NULL FROM dbo.Conta;
-- Eventos históricos sintéticos: não correspondem a autenticações reais.
SET @n = 1;
WHILE @n <= 500
BEGIN
    INSERT dbo.TentativaLogin (ContaId, OcorridoEm, Sucesso, IpOrigem)
    VALUES (1 + ((@n - 1) % 50), DATEADD(MINUTE, @n, CONVERT(datetime2(0), '20261001', 112)),
            CASE WHEN @n % 3 = 0 THEN 0 ELSE 1 END,
            CONCAT('192.0.2.', 1 + (@n % 254)));
    SET @n += 1;
END;
COMMIT;
SELECT N'Conta' AS Tabela, COUNT_BIG(*) AS Linhas FROM dbo.Conta
UNION ALL SELECT N'Credencial', COUNT_BIG(*) FROM dbo.Credencial
UNION ALL SELECT N'TentativaLogin', COUNT_BIG(*) FROM dbo.TentativaLogin;
GO
