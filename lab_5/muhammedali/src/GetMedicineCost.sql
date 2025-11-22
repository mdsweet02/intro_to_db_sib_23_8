CREATE PROCEDURE GetMedicineCost
    @MedID INT
AS
BEGIN
    SELECT Код_лекарства,
           Наименование,
           Цена,
           Количество,
           (Цена * Количество) AS Итоговая_стоимость
    FROM Лекарства_склад
    WHERE Код_лекарства = @MedID;
END;
GO
