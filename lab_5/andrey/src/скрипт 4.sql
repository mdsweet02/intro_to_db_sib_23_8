CREATE FUNCTION Get_Lens_Stock_Cost (@Артикул INT)
RETURNS MONEY
AS
BEGIN
    DECLARE @Стоимость MONEY;

    SELECT @Стоимость = Цена * Доступное_количество
    FROM Линзы
    WHERE Артикул_линзы = @Артикул;

    RETURN @Стоимость;
END;
GO
