import pyodbc
import tkinter as tk
import pandas as pd
import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog, filedialog
from docx import Document

# ----------------------------
# Подключение к SQL Server
# ----------------------------
server = r"DSSYASIK\SQLEXPRESS"
database = "Расчеты_с_потребителями"

conn_str = (
    r"DRIVER={ODBC Driver 11 for SQL Server};"
    fr"SERVER={server};"
    fr"DATABASE={database};"
    "Trusted_Connection=yes;"
)

try:
    conn = pyodbc.connect(conn_str)
except Exception as e:
    print("Ошибка подключения:", e)
    exit()

# ----------------------------
# Первичные ключи таблиц
# ----------------------------
primary_keys = {
    "Лицевой_счет": "Лицевой_счет",
    "Участок": "Код_участка",
    "Контроллеры": "Код_контроллера",
    "Льготы": "Тип_льготы",
    "Тарифы": None,
    "Показания": None,
    "Квитанция": "Номер_квитанции",
    "Долг_на_начало": None,
    "Приборы_учета": "Номер_прибора"
}

# ----------------------------
# Основные функции
# ----------------------------
def load_table(table):
    try:
        df = pd.read_sql(f"SELECT * FROM dbo.{table}", conn)
        tree.delete(*tree.get_children())
        tree["columns"] = list(df.columns)
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=130, anchor="center")
        for _, row in df.iterrows():
            tree.insert("", "end", values=list(row))
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def add_record():
    table = combo.get()
    df = pd.read_sql(f"SELECT * FROM dbo.{table}", conn)
    data = {}
    for col in df.columns:
        value = simpledialog.askstring("Добавление", f"{col}:")
        if value is None:
            return
        data[col] = value
    cols = ", ".join(data.keys())
    vals = ", ".join(f"'{v}'" for v in data.values())
    sql = f"INSERT INTO dbo.{table} ({cols}) VALUES ({vals})"
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        load_table(table)
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def edit_record():
    table = combo.get()
    pk = primary_keys.get(table)
    if not pk:
        messagebox.showwarning("Ошибка", "Редактирование этой таблицы не поддерживается.")
        return
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Ошибка", "Выберите строку!")
        return
    row_values = tree.item(selected)["values"]
    columns = tree["columns"]
    updates = []
    for i, col in enumerate(columns):
        old = row_values[i]
        new_val = simpledialog.askstring("Редактировать", f"{col}:", initialvalue=str(old))
        if new_val is None:
            return
        updates.append(f"{col} = '{new_val}'")
    pk_value = row_values[columns.index(pk)]
    sql = f"UPDATE dbo.{table} SET {', '.join(updates)} WHERE {pk} = '{pk_value}'"
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        load_table(table)
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def delete_record():
    table = combo.get()
    pk = primary_keys.get(table)
    if not pk:
        messagebox.showwarning("Ошибка", "Удаление этой таблицы не поддерживается.")
        return
    selected = tree.focus()
    if not selected:
        return
    values = tree.item(selected)["values"]
    pk_value = values[list(tree["columns"]).index(pk)]
    sql = f"DELETE FROM dbo.{table} WHERE {pk} = '{pk_value}'"
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        load_table(table)
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def search_record():
    table = combo.get()
    column = simpledialog.askstring("Поиск", "Введите название колонки:")
    if not column:
        return
    value = simpledialog.askstring("Поиск", "Введите значение:")
    if value is None:
        return
    sql = f"SELECT * FROM dbo.{table} WHERE {column} LIKE '%{value}%'"
    try:
        df = pd.read_sql(sql, conn)
        tree.delete(*tree.get_children())
        tree["columns"] = list(df.columns)
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=130, anchor="center")
        for _, row in df.iterrows():
            tree.insert("", "end", values=list(row))
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def custom_query():
    sql = simpledialog.askstring("SQL SELECT", "Введите SELECT запрос:")
    if not sql:
        return
    try:
        df = pd.read_sql(sql, conn)
        tree.delete(*tree.get_children())
        tree["columns"] = list(df.columns)
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=130, anchor="center")
        for _, row in df.iterrows():
            tree.insert("", "end", values=list(row))
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

# ----------------------------
# Экспорт Excel / Word
# ----------------------------
def export_excel():
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx")
    if not file_path:
        return
    data = [tree.item(row)["values"] for row in tree.get_children()]
    df = pd.DataFrame(data, columns=tree["columns"])
    df.to_excel(file_path, index=False)
    messagebox.showinfo("Готово", "Данные экспортированы в Excel!")

def export_word():
    file_path = filedialog.asksaveasfilename(defaultextension=".docx")
    if not file_path:
        return
    doc = Document()
    table_word = doc.add_table(rows=1, cols=len(tree["columns"]))
    header_cells = table_word.rows[0].cells
    for i, col in enumerate(tree["columns"]):
        header_cells[i].text = col
    for row in tree.get_children():
        row_vals = tree.item(row)["values"]
        row_cells = table_word.add_row().cells
        for i, val in enumerate(row_vals):
            row_cells[i].text = str(val)
    doc.save(file_path)
    messagebox.showinfo("Готово", "Данные экспортированы в Word!")

# ----------------------------
# Справка
# ----------------------------
def show_help():
    messagebox.showinfo("Справка", 
        "Приложение для работы с таблицами 'Расчеты с потребителями'.\n\n"
        "Доступные функции:\n"
        "- Показ таблиц\n"
        "- Добавление, редактирование и удаление записей\n"
        "- Поиск и SQL SELECT запросы\n"
        "- Экспорт данных в Excel и Word"
    )

# ----------------------------
# GUI
# ----------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

window = ctk.CTk()
window.title("Расчеты с потребителями")
window.geometry("1450x750")

# ----------------------------
# Меню
# ----------------------------
menu_bar = tk.Menu(window)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Выход", command=window.quit)
menu_bar.add_cascade(label="Файл", menu=file_menu)

actions_menu = tk.Menu(menu_bar, tearoff=0)
actions_menu.add_command(label="Добавить запись", command=add_record)
actions_menu.add_command(label="Редактировать запись", command=edit_record)
actions_menu.add_command(label="Удалить запись", command=delete_record)
actions_menu.add_separator()
actions_menu.add_command(label="Экспорт в Excel", command=export_excel)
actions_menu.add_command(label="Экспорт в Word", command=export_word)
menu_bar.add_cascade(label="Действия", menu=actions_menu)

help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="Справка", command=show_help)
menu_bar.add_cascade(label="Справка", menu=help_menu)

window.config(menu=menu_bar)

# ----------------------------
# Верхняя панель
# ----------------------------
top_frame = ctk.CTkFrame(window, height=60, fg_color="#1f1f1f")  # чуть темнее для контраста
top_frame.pack(fill="x", pady=5, padx=5)

combo = ctk.CTkComboBox(top_frame, values=list(primary_keys.keys()), width=300, height=35)
combo.pack(side="left", padx=10, pady=10)

button_style = {"width": 150, "height": 35, "fg_color": "#2a9d8f", "hover_color": "#3ec1c1", "text_color": "white"}

ctk.CTkButton(top_frame, text="Показать таблицу", command=lambda: load_table(combo.get()), **button_style).pack(side="left", padx=10)
ctk.CTkButton(top_frame, text="Поиск", command=search_record, **button_style).pack(side="left", padx=10)
ctk.CTkButton(top_frame, text="SQL SELECT", command=custom_query, **button_style).pack(side="left", padx=10)

# ----------------------------
# Кнопки
# ----------------------------
btn_frame = ctk.CTkFrame(window)
btn_frame.pack(pady=10)
ctk.CTkButton(btn_frame, text="Добавить запись", width=150, command=add_record).grid(row=0, column=0, padx=10)
ctk.CTkButton(btn_frame, text="Редактировать запись", width=150, command=edit_record).grid(row=0, column=1, padx=10)
ctk.CTkButton(btn_frame, text="Удалить запись", width=150, command=delete_record).grid(row=0, column=2, padx=10)
ctk.CTkButton(btn_frame, text="Экспорт Excel", width=150, command=export_excel).grid(row=0, column=3, padx=10)
ctk.CTkButton(btn_frame, text="Экспорт Word", width=150, command=export_word).grid(row=0, column=4, padx=10)

# ----------------------------
# Таблица
# ----------------------------
tree_frame = ctk.CTkFrame(window)
tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
tree = ttk.Treeview(tree_frame, show="headings")
tree.pack(fill="both", expand=True)
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background="#2b2b2b", fieldbackground="#2b2b2b",
                foreground="white", rowheight=28, font=("Arial", 11))
style.map('Treeview', background=[('selected', '#1f6aa5')], foreground=[('selected', 'white')])

window.mainloop()
