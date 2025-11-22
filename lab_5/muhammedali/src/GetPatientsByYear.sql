CREATE PROCEDURE GetPatientsByYear
    @Year INT
AS
BEGIN
    SELECT *
    FROM Пациенты
    WHERE Пол = 'М'
      AND YEAR(Дата_рождения) = @Year;
END;
GO
