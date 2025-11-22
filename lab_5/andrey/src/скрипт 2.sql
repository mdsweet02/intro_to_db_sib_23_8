USE [optika];
GO

CREATE OR ALTER PROCEDURE Get_Orders_By_Priemshik_And_Date
    @КодПриемщика INT, 
    @Дата DATE           
AS
BEGIN
    SELECT *
    FROM Заказ
    WHERE код_приемщика = @КодПриемщика
      AND дата_оформления = @Дата;
END;
GO
