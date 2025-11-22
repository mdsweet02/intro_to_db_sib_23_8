import pyodbc
import pandas as pd

CONNECTION_STRING = r"""
DRIVER={SQL Server};
SERVER=localhost\SQLEXPRESS;
DATABASE=optika;
Trusted_Connection=yes;
"""

def get_connection():
    return pyodbc.connect(CONNECTION_STRING)

def get_table(table_name):
    conn = get_connection()
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def insert_row(table, columns, values):
    conn = get_connection()
    cursor = conn.cursor()
    col_str = ", ".join(columns)
    q_marks = ", ".join("?" * len(values))
    query = f"INSERT INTO {table} ({col_str}) VALUES ({q_marks})"
    cursor.execute(query, values)
    conn.commit()
    conn.close()

def update_row(table, key_column, key_value, columns, values):
    conn = get_connection()
    cursor = conn.cursor()
    set_str = ", ".join([f"{col}=?" for col in columns])
    query = f"UPDATE {table} SET {set_str} WHERE {key_column} = ?"
    cursor.execute(query, values + [key_value])
    conn.commit()
    conn.close()

def delete_row(table, key_column, key_value):
    conn = get_connection()
    cursor = conn.cursor()
    query = f"DELETE FROM {table} WHERE {key_column} = ?"
    cursor.execute(query, key_value)
    conn.commit()
    conn.close()

def execute_query(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Словарь с первичными ключами
PK_MAP = {
    "Оправы": ["Артикул_оправы"],
    "Линзы": ["Артикул_линзы"],
    "Услуги": ["Код_услуги"],
    "Приемщики": ["Код_приемщика"],
    "Работники": ["Табельный_номер"],
    "Заказы": ["Номер_заказа"],
    "Заказ_оправы": ["Номер_заказа", "Артикул_оправы"],
    "Заказ_линзы": ["Номер_заказа", "Артикул_линзы"],
    "Заказ_услуги": ["Номер_заказа", "Код_услуги"],
    "Касса_заказ": ["Номер_заказа"]  # можно добавить комбинированный PK
}
