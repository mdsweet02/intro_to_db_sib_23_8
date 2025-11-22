from db import get_table

# Попробуем вывести таблицу Оправы
try:
    df = get_table("Оправы")
    print(df)
except Exception as e:
    print("Ошибка:", e)
