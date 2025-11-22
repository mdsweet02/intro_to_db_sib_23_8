CREATE TRIGGER trg_Insert_Подписчики
ON dbo.Подписчики
AFTER INSERT
AS
BEGIN
    IF EXISTS (
        SELECT 1 FROM inserted
        WHERE Признак_лица = 'физическое' AND Процент_льготы > 50
    )
    BEGIN
        -- Двойной %% вместо одного %
        RAISERROR('Процент льготы для физических лиц не может превышать 50%%', 16, 1);
        ROLLBACK TRANSACTION;
    END
END;
GO

-- Проверка при обновлении: адрес не должен быть пустым
CREATE TRIGGER trg_Update_Подписчики
ON dbo.Подписчики
AFTER UPDATE
AS
BEGIN
    IF EXISTS (
        SELECT 1 FROM inserted
        WHERE LTRIM(RTRIM(Адрес)) = ''
    )
    BEGIN
        RAISERROR('Адрес не может быть пустым', 16, 1);
        ROLLBACK TRANSACTION;
    END
END;
GO

-- Блокировка удаления подписчиков
CREATE TRIGGER trg_Delete_Подписчики
ON dbo.Подписчики
INSTEAD OF DELETE
AS
BEGIN
    RAISERROR('Удаление подписчиков запрещено', 16, 1);
    ROLLBACK TRANSACTION;
END;
GO