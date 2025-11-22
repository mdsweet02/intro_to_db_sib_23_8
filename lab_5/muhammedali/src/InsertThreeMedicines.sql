CREATE PROCEDURE InsertThreeMedicines
AS
BEGIN
    DECLARE @i INT = 1;

    WHILE @i <= 3
    BEGIN
        INSERT INTO Лекарства_склад (Наименование, Ед_измерения, Цена, Количество)
        VALUES ('Лекарство ' + CAST(@i AS NVARCHAR(10)),
                'шт',
                100 * @i,
                10 * @i);

        SET @i = @i + 1;
    END
END;
GO
