CREATE FUNCTION Get_Services_More_Expensive (@MinPrice MONEY)
RETURNS TABLE
AS
RETURN
(
    SELECT *
    FROM Услуги
    WHERE Цена > @MinPrice
);
GO
