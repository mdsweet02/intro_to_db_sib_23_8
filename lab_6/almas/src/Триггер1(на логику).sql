USE Туристическая_Фирма;
GO

CREATE TRIGGER trg_Tury_CountryCount
ON Туры
AFTER INSERT
AS
BEGIN
    DECLARE @Country NVARCHAR(100);

    -- Получаем страну, для которой был добавлен тур
    SELECT @Country = Наименование FROM inserted;

    -- Считаем количество туров в этой стране
    DECLARE @Count INT;
    SELECT @Count = COUNT(*) 
    FROM Туры
    WHERE Наименование = @Country;

    PRINT 'Количество туров в стране "' + @Country + '": ' + CAST(@Count AS VARCHAR(10));
END;
GO