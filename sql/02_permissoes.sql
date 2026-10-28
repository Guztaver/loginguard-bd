USE LoginGuardAcademico;
GO
CREATE VIEW dbo.vContas AS
SELECT ContaId, Nome, Email, Bloqueado, CriadoEm FROM dbo.Conta;
GO
CREATE VIEW dbo.vHistorico AS
SELECT TentativaId, ContaId, OcorridoEm, Sucesso FROM dbo.TentativaLogin;
GO
CREATE ROLE lg_administrador AUTHORIZATION dbo;
CREATE ROLE lg_suporte AUTHORIZATION dbo;
CREATE ROLE lg_auditor AUTHORIZATION dbo;
GO
GRANT SELECT ON OBJECT::dbo.vContas TO lg_administrador, lg_suporte, lg_auditor;
GRANT SELECT ON OBJECT::dbo.vHistorico TO lg_administrador, lg_auditor;
GRANT INSERT ON OBJECT::dbo.Conta TO lg_administrador;
-- Permite localizar a conta no WHERE do UPDATE sem expor as demais colunas.
GRANT SELECT ON OBJECT::dbo.Conta (ContaId) TO lg_administrador;
GRANT UPDATE ON OBJECT::dbo.Conta (Nome, Email, Bloqueado) TO lg_administrador;
GRANT INSERT ON OBJECT::dbo.Credencial TO lg_administrador;
GRANT UPDATE ON OBJECT::dbo.Credencial (HashSenha, AtualizadoEm) TO lg_administrador;
DENY SELECT ON OBJECT::dbo.Credencial TO lg_administrador, lg_suporte, lg_auditor;
DENY INSERT, UPDATE, DELETE ON OBJECT::dbo.Conta TO lg_suporte, lg_auditor;
DENY INSERT, UPDATE, DELETE ON OBJECT::dbo.Credencial TO lg_suporte, lg_auditor;
DENY INSERT, UPDATE, DELETE ON OBJECT::dbo.TentativaLogin TO lg_administrador, lg_suporte, lg_auditor;
DENY UNMASK TO lg_administrador, lg_suporte, lg_auditor;
GO
CREATE USER demo_admin WITHOUT LOGIN;
CREATE USER demo_suporte WITHOUT LOGIN;
CREATE USER demo_auditor WITHOUT LOGIN;
ALTER ROLE lg_administrador ADD MEMBER demo_admin;
ALTER ROLE lg_suporte ADD MEMBER demo_suporte;
ALTER ROLE lg_auditor ADD MEMBER demo_auditor;
GO
-- Nenhum destes usuários é db_owner. Não usar sysadmin para demonstrar DENY.
-- SELECT das views funciona por cadeia de propriedade; o mascaramento continua aplicável.
