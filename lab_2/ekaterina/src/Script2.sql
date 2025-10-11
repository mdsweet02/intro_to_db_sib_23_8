CREATE SCHEMA IF NOT EXISTS public;
SET search_path TO public;

-- Тип для способов оплаты (создаём только если не существует)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tip_oplaty') THEN
        CREATE TYPE tip_oplaty AS ENUM ('наличные', 'карта', 'онлайн');
    END IF;
END$$;

-- Удаление старых таблиц
DROP TABLE IF EXISTS oplata, kvitanciya, nachisleniya, dolg, tarif,
tipnachisleniya, lichschet, uchastki, rabotniki, katplat CASCADE;

-- Родительские таблицы

-- Категории плательщиков
CREATE TABLE katplat (
    id SERIAL PRIMARY KEY,
    nazvanie VARCHAR(100) NOT NULL UNIQUE,
    procent NUMERIC(5,2) NOT NULL DEFAULT 100 CHECK (procent > 0 AND procent <= 200)
);

INSERT INTO katplat (nazvanie, procent) VALUES
('Физическое лицо', 100),
('Юридическое лицо', 120),
('ИП', 110),
('Организация', 130),
('Квартира', 100),
('Частный дом', 90),
('Муниципальный объект', 80),
('Коммерческая фирма', 150),
('ЖСК', 100),
('Общежитие', 70);

-- Работники (бухгалтеры, сотрудники)
CREATE TABLE rabotniki (
    id SERIAL PRIMARY KEY,
    fio VARCHAR(150) NOT NULL
);

INSERT INTO rabotniki (fio) VALUES
('Иванов И.И.'),('Петров П.П.'),('Сидоров С.С.'),('Ким А.А.'),
('Бекова А.С.'),('Тулеуова М.А.'),('Назаров Д.К.'),('Жумабаев Е.Н.'),
('Орлова В.А.'),('Кузнецов В.И.');

-- Участки (с указанием бухгалтера)
CREATE TABLE uchastki (
    id SERIAL PRIMARY KEY,
    nazvanie VARCHAR(100) NOT NULL UNIQUE,
    buhgalter_id INT REFERENCES rabotniki(id) ON DELETE SET NULL ON UPDATE CASCADE
);

INSERT INTO uchastki (nazvanie, buhgalter_id) VALUES
('Северный', 1),('Южный', 2),('Восточный', 3),('Западный', 4),('Центральный', 5),
('Новый район',6),('Промзона',7),('Микрорайон 1',8),('Микрорайон 2',9),('Пригород',10);

-- Лицевые счета
CREATE TABLE lichschet (
    id SERIAL PRIMARY KEY,
    nomer VARCHAR(50) UNIQUE NOT NULL,
    fio VARCHAR(150) NOT NULL,
    kolvo_zhilcov INT NOT NULL DEFAULT 1 CHECK (kolvo_zhilcov > 0),
    adres VARCHAR(200) NOT NULL,
    lgotnik BOOLEAN DEFAULT FALSE,
    katplat_id INT REFERENCES katplat(id) ON DELETE SET NULL ON UPDATE CASCADE,
    uchastok_id INT REFERENCES uchastki(id) ON DELETE SET NULL ON UPDATE CASCADE
);

INSERT INTO lichschet (nomer, fio, kolvo_zhilcov, adres, katplat_id, uchastok_id) VALUES
('LS001','Иванов Иван Иванович',3,'ул. Ленина, 10',1,1),
('LS002','Петров Петр Петрович',2,'ул. Гагарина, 5',2,2),
('LS003','Сидорова Анна Сергеевна',4,'ул. Абая, 15',3,3),
('LS004','Ким Алексей Николаевич',1,'ул. Мира, 25',4,4),
('LS005','Бекова Алия Сагидовна',2,'ул. Назарбаева, 30',5,5),
('LS006','Тулеуова Мадина А.',3,'ул. Байтурсынова, 50',6,6),
('LS007','Назаров Данияр К.',1,'ул. Торайгырова, 11',7,7),
('LS008','Жумабаев Ерлан Н.',2,'ул. Сатпаева, 9',8,8),
('LS009','Орлова Виктория А.',4,'ул. Естая, 22',9,9),
('LS010','Кузнецов Виктор И.',5,'ул. Кунаева, 17',10,10);

-- Типы начислений
CREATE TABLE tipnachisleniya (
    id SERIAL PRIMARY KEY,
    nazvanie VARCHAR(100) NOT NULL UNIQUE,
    priznak VARCHAR(50) NOT NULL DEFAULT 'текущее' CHECK (priznak IN ('текущее','дополнительное'))
);

INSERT INTO tipnachisleniya (nazvanie, priznak) VALUES
('Вода','текущее'),('Газ','текущее'),('Электричество','текущее'),('Отопление','текущее'),
('Вывоз мусора','текущее'),('Интернет','дополнительное'),('Домофон','дополнительное'),
('Телефон','дополнительное'),('Канализация','текущее'),('Техобслуживание','дополнительное');

-- Тарифы
CREATE TABLE tarif (
    id SERIAL PRIMARY KEY,
    tipnachisleniya_id INT NOT NULL REFERENCES tipnachisleniya(id) ON DELETE CASCADE ON UPDATE CASCADE,
    summa_na_chel NUMERIC(10,2) NOT NULL CHECK (summa_na_chel > 0),
    data_nachala DATE DEFAULT CURRENT_DATE,
    data_okonchaniya DATE
);

INSERT INTO tarif (tipnachisleniya_id, summa_na_chel, data_nachala) VALUES
(1,250.50,'2025-01-01'),(2,500.00,'2025-01-01'),(3,300.75,'2025-01-01'),
(4,800.00,'2025-01-01'),(5,150.00,'2025-01-01'),(6,200.00,'2025-01-01'),
(7,100.00,'2025-01-01'),(8,180.00,'2025-01-01'),(9,220.00,'2025-01-01'),
(10,90.00,'2025-01-01');

-- Дочерние таблицы

-- Долг на начало месяца
CREATE TABLE dolg (
    id SERIAL PRIMARY KEY,
    lichschet_id INT NOT NULL REFERENCES lichschet(id) ON DELETE CASCADE ON UPDATE CASCADE,
    mesyac VARCHAR(20) NOT NULL,
    god INT CHECK (god BETWEEN 2000 AND 2100),
    summa NUMERIC(10,2) NOT NULL CHECK (summa >= 0),
    data_obnovleniya DATE DEFAULT CURRENT_DATE
);

INSERT INTO dolg (lichschet_id, mesyac, god, summa) VALUES
(1,'Январь',2025,100.50),(2,'Февраль',2025,200.00),(3,'Март',2025,0),
(4,'Апрель',2025,150.25),(5,'Май',2025,300.00),(6,'Июнь',2025,75.00),
(7,'Июль',2025,0),(8,'Август',2025,90.00),(9,'Сентябрь',2025,50.00),(10,'Октябрь',2025,0);

-- Квитанции
CREATE TABLE kvitanciya (
    id SERIAL PRIMARY KEY,
    nomer VARCHAR(50) UNIQUE NOT NULL,
    lichschet_id INT NOT NULL REFERENCES lichschet(id) ON DELETE CASCADE ON UPDATE CASCADE,
    mesyac VARCHAR(20) NOT NULL,
    god INT CHECK (god BETWEEN 2000 AND 2100),
    data_vypuska DATE DEFAULT CURRENT_DATE,
    summa_dolga NUMERIC(10,2) DEFAULT 0 CHECK (summa_dolga >= 0),
    summa_nachisleniya NUMERIC(10,2) DEFAULT 0 CHECK (summa_nachisleniya >= 0),
    summa_skidki NUMERIC(10,2) DEFAULT 0 CHECK (summa_skidki >= 0),
    summa_k_oplate NUMERIC(10,2) DEFAULT 0 CHECK (summa_k_oplate >= 0)
);

INSERT INTO kvitanciya (nomer, lichschet_id, mesyac, god, data_vypuska, summa_dolga, summa_nachisleniya, summa_skidki, summa_k_oplate) VALUES
('KV001',1,'Январь',2025,'2025-02-01',100,800,0,900),
('KV002',2,'Февраль',2025,'2025-02-01',200,1150,50,1300),
('KV003',3,'Март',2025,'2025-03-01',0,420,20,400),
('KV004',4,'Апрель',2025,'2025-04-02',150,220,10,360),
('KV005',5,'Май',2025,'2025-05-02',0,280,20,260),
('KV006',6,'Июнь',2025,'2025-06-03',75,330,0,405),
('KV007',7,'Июль',2025,'2025-07-04',0,770,30,740),
('KV008',8,'Август',2025,'2025-08-05',90,960,0,1050),
('KV009',9,'Сентябрь',2025,'2025-09-06',50,390,0,440),
('KV010',10,'Октябрь',2025,'2025-10-07',0,270,0,270),
('KV011',1,'Ноябрь',2025,'2025-11-01',0,300,0,300),
('KV012',2,'Декабрь',2025,'2025-12-01',0,320,0,320),
('KV013',3,'Январь',2026,'2026-01-01',10,420,0,430),
('KV014',4,'Февраль',2026,'2026-02-01',0,220,0,220),
('KV015',5,'Март',2026,'2026-03-01',0,180,0,180),
('KV016',6,'Апрель',2026,'2026-04-01',0,240,0,240),
('KV017',7,'Май',2026,'2026-05-01',0,500,0,500),
('KV018',8,'Июнь',2026,'2026-06-01',0,320,0,320),
('KV019',9,'Июль',2026,'2026-07-01',0,220,0,220),
('KV020',10,'Август',2026,'2026-08-01',0,150,0,150);

-- Начисления
CREATE TABLE nachisleniya (
    id SERIAL PRIMARY KEY,
    lichschet_id INT NOT NULL REFERENCES lichschet(id) ON DELETE CASCADE ON UPDATE CASCADE,
    tipnachisleniya_id INT NOT NULL REFERENCES tipnachisleniya(id) ON DELETE CASCADE ON UPDATE CASCADE,
    mesyac VARCHAR(20) NOT NULL,
    god INT CHECK (god BETWEEN 2000 AND 2100),
    summa NUMERIC(10,2) NOT NULL CHECK (summa >= 0),
    summa_skidki NUMERIC(10,2) DEFAULT 0 CHECK (summa_skidki >= 0),
    katplat_id INT REFERENCES katplat(id),
    kvitanciya_vypisana BOOLEAN DEFAULT FALSE
);

INSERT INTO nachisleniya 
(lichschet_id, tipnachisleniya_id, mesyac, god, summa, summa_skidki, katplat_id, kvitanciya_vypisana) 
VALUES
(1,1,'Январь',2025,300,0,1,TRUE),
(2,2,'Февраль',2025,500,50,2,TRUE),
(3,3,'Март',2025,420,20,3,TRUE),
(4,4,'Апрель',2025,220,10,4,TRUE),
(5,5,'Май',2025,280,20,5,TRUE),
(6,6,'Июнь',2025,330,0,6,TRUE),
(7,7,'Июль',2025,770,30,7,TRUE),
(8,8,'Август',2025,960,0,8,TRUE),
(9,9,'Сентябрь',2025,390,0,9,TRUE),
(10,10,'Октябрь',2025,270,0,10,TRUE),
(1,1,'Ноябрь',2025,300,0,1,TRUE),
(2,2,'Декабрь',2025,320,0,2,TRUE),
(3,3,'Январь',2026,420,0,3,TRUE),
(4,4,'Февраль',2026,220,0,4,TRUE),
(5,5,'Март',2026,180,0,5,TRUE),
(6,6,'Апрель',2026,240,0,6,TRUE),
(7,7,'Май',2026,500,0,7,TRUE),
(8,8,'Июнь',2026,320,0,8,TRUE),
(9,9,'Июль',2026,220,0,9,TRUE),
(10,10,'Август',2026,150,0,10,TRUE);


-- Оплата
CREATE TABLE oplata (
    id SERIAL PRIMARY KEY,
    kvitanciya_id INT NOT NULL REFERENCES kvitanciya(id) ON DELETE CASCADE ON UPDATE CASCADE,
    lichschet_id INT REFERENCES lichschet(id),
    mesyac VARCHAR(20),
    god INT CHECK (god BETWEEN 2000 AND 2100),
    data_oplaty DATE DEFAULT CURRENT_DATE,
    summa NUMERIC(10,2) NOT NULL CHECK (summa >= 0),
    sposob_oplaty tip_oplaty DEFAULT 'наличные'
);

INSERT INTO oplata (kvitanciya_id, lichschet_id, mesyac, god, data_oplaty, summa, sposob_oplaty) VALUES
(1,1,'Январь',2025,'2025-02-05',900,'онлайн'), 
(2,2,'Февраль',2025,'2025-02-06',1300,'карта'), 
(3,3,'Март',2025,'2025-03-07',400,'наличные'),
(4,4,'Апрель',2025,'2025-04-03',360,'карта'), 
(5,5,'Май',2025,'2025-05-02',260,'наличные'), 
(6,6,'Июнь',2025,'2025-06-03',405,'онлайн'), 
(7,7,'Июль',2025,'2025-07-04',740,'карта'),
(8,8,'Август',2025,'2025-08-05',1050,'онлайн'), 
(9,9,'Сентябрь',2025,'2025-09-06',440,'карта'),
(10,10,'Октябрь',2025,'2025-10-07',270,'наличные'), 
(11,1,'Ноябрь',2025,'2025-11-02',300,'онлайн'), 
(12,2,'Декабрь',2025,'2025-12-03',320,'карта'), 
(13,3,'Январь',2026,'2026-01-04',430,'наличные'), 
(14,4,'Февраль',2026,'2026-02-05',220,'онлайн'),
(15,5,'Март',2026,'2026-03-06',180,'карта'), 
(16,6,'Апрель',2026,'2026-04-07',240,'онлайн'), 
(17,7,'Май',2026,'2026-05-08',500,'карта'),
(18,8,'Июнь',2026,'2026-06-09',320,'онлайн'), 
(19,9,'Июль',2026,'2026-07-10',220,'карта'), 
(20,10,'Август',2026,'2026-08-11',150,'наличные');

-- Индексы для внешних ключей

CREATE INDEX idx_lichschet_katplat ON lichschet(katplat_id);
CREATE INDEX idx_lichschet_uchastok ON lichschet(uchastok_id);
CREATE INDEX idx_uchastki_buhgalter ON uchastki(buhgalter_id);
CREATE INDEX idx_tarif_tip ON tarif(tipnachisleniya_id);
CREATE INDEX idx_nachisleniya_lichschet ON nachisleniya(lichschet_id);
CREATE INDEX idx_dolg_lichschet ON dolg(lichschet_id);
CREATE INDEX idx_kvitanciya_lichschet ON kvitanciya(lichschet_id);
CREATE INDEX idx_oplata_kvitanciya ON oplata(kvitanciya_id);
CREATE INDEX idx_lichschet_lgotnik ON lichschet(lgotnik);

-- Дополнительные обновления и связи
UPDATE lichschet SET lgotnik = TRUE WHERE id IN (2,4,6,8,10);

UPDATE tipnachisleniya 
SET priznak = CASE 
    WHEN id IN (6,7,8,10) THEN 'дополнительное'
    ELSE 'текущее'
END;

UPDATE kvitanciya
SET summa_k_oplate = summa_dolga + summa_nachisleniya - summa_skidki;
