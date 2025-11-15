CREATE FUNCTION dbo.Функция_сумма_оплаты_подписчика
(
    @КодПодписчика INT
)
RETURNS DECIMAL(10,2)
AS
BEGIN
    DECLARE @Сумма DECIMAL(10,2);

    SELECT @Сумма = SUM(Сумма_оплаты)
    FROM dbo.Оплата
    WHERE Код_подписчика = @КодПодписчика;

    RETURN ISNULL(@Сумма, 0);
END;
GO

CREATE FUNCTION dbo.Функция_стоимость_подписки
(
    @ИндексИздания VARCHAR(20),
    @ДатаНачала DATE,
    @ДатаОкончания DATE
)
RETURNS DECIMAL(10,2)
AS
BEGIN
    DECLARE @ЦенаМесяц DECIMAL(10,2);
    DECLARE @Месяцев INT;

    SELECT @ЦенаМесяц = Цена_за_месяц
    FROM dbo.Издание
    WHERE Индекс_издания = @ИндексИздания;

    SET @Месяцев = DATEDIFF(MONTH, @ДатаНачала, @ДатаОкончания);

    RETURN ISNULL(@ЦенаМесяц, 0) * @Месяцев;
END;
GO

CREATE FUNCTION dbo.Функция_короткое_ФИО
(
    @ПолноеФИО NVARCHAR(255)
)
RETURNS NVARCHAR(255)
AS
BEGIN
    DECLARE @Фам NVARCHAR(100), @Имя NVARCHAR(100), @Отч NVARCHAR(100);

    -- Предполагается формат "Фамилия Имя Отчество"
    SELECT 
        @Фам = PARSENAME(REPLACE(@ПолноеФИО,' ','.'), 3),
        @Имя = PARSENAME(REPLACE(@ПолноеФИО,' ','.'), 2),
        @Отч = PARSENAME(REPLACE(@ПолноеФИО,' ','.'), 1);

    RETURN 
        @Фам + N' ' +
        LEFT(@Имя, 1) + N'.' +
        LEFT(@Отч, 1) + N'.';
END;
GO
