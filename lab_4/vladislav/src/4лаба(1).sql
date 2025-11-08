CREATE VIEW Отчет_по_оплате_услуг_на_дату AS
SELECT 
    o.Код_оплаты,
    p.ФИО AS Пациент,
    v.ФИО AS Врач,
    o.Дата,
    o.Сумма_прихода
FROM Оплата o
JOIN Пациент p ON o.Код_пациента = p.Код_пациента
JOIN Врачи v ON o.Код_врача = v.Код_врача
WHERE o.Дата = '2025-11-06';
GO

CREATE VIEW График_приема_врача_на_дату AS
SELECT 
    r.Дата_приема,
    r.Время_начала,
    r.Время_окончания,
    p.ФИО AS Пациент,
    v.ФИО AS Врач
FROM Регистратура r
JOIN Пациент p ON r.Код_пациента = p.Код_пациента
JOIN Врачи v ON r.Код_врача = v.Код_врача
WHERE r.Код_врача = 7
  AND r.Дата_приема = '2025-11-06';
GO

CREATE VIEW Мужчины_по_возрасту AS
SELECT 
    Код_пациента,
    ФИО,
    Дата_рождения,
    Адрес,
    Телефон,
    Признак_льгот,
    DATEDIFF(YEAR, Дата_рождения, GETDATE()) -
        CASE 
            WHEN DATEADD(YEAR, DATEDIFF(YEAR, Дата_рождения, GETDATE()), Дата_рождения) > GETDATE() THEN 1
            ELSE 0
        END AS Возраст
FROM Пациент
WHERE Пол = 'М'
  AND DATEDIFF(YEAR, Дата_рождения, GETDATE()) -
      CASE 
          WHEN DATEADD(YEAR, DATEDIFF(YEAR, Дата_рождения, GETDATE()), Дата_рождения) > GETDATE() THEN 1
          ELSE 0
      END BETWEEN 30 AND 50;
GO