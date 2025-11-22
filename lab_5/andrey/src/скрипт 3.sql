CREATE PROCEDURE Insert_Four_Priemshiki
AS
BEGIN
    DECLARE @i INT = 1;

    WHILE @i <= 4
    BEGIN
        INSERT INTO Приемщик (Код_приемщика, ФИО)
        VALUES (
            (SELECT ISNULL(MAX(Код_приемщика), 0) + 1 FROM Приемщик),
            CONCAT(N'Приемщик №', @i)
        );

        SET @i += 1;
    END
END;
GO
