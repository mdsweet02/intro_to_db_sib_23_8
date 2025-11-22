CREATE FUNCTION GetMedicinesMoreExpensiveThan (@MinPrice DECIMAL(10,2))
RETURNS TABLE
AS
RETURN
(
    SELECT *
    FROM Лекарства_склад
    WHERE Цена > @MinPrice
);
GO
