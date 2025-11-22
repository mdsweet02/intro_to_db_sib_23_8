CREATE VIEW dbo.vw_Пациенты_мужчины AS
SELECT
    Код_пациента,
    ФИО,
    Пол,
    Дата_рождения,
    DATEDIFF(YEAR, Дата_рождения, GETDATE()) AS Возраст
FROM dbo.Пациенты
WHERE Пол = 'М' 
  AND DATEDIFF(YEAR, Дата_рождения, GETDATE()) BETWEEN 25 AND 40;
