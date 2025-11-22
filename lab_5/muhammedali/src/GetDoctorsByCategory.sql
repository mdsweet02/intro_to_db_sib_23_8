CREATE PROCEDURE GetDoctorsByCategory
    @CategoryID INT
AS
BEGIN
    SELECT *
    FROM Врачи
    WHERE Код_категории = @CategoryID;
END;
GO
