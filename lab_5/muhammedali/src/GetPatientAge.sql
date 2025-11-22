CREATE FUNCTION GetPatientAge (@PatientID INT)
RETURNS INT
AS
BEGIN
    DECLARE @Age INT;

    SELECT @Age = DATEDIFF(YEAR, Дата_рождения, GETDATE())
    FROM Пациенты
    WHERE Код_пациента = @PatientID;

    RETURN @Age;
END;
GO
