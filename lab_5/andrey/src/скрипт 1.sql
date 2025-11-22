USE [optika];
GO

CREATE OR ALTER PROCEDURE Get_Orders_Not_Matching_CurrentDate
AS
BEGIN
    SELECT *
    FROM Заказы
    WHERE Срок_изготовления <> CAST(GETDATE() AS DATE);
END;
GO
