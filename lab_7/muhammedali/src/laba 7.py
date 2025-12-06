import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pyodbc
import pandas as pd
import sys

# ----------------------------
# Настройки подключения
# ----------------------------
server_name = "DESKTOP-MBGHOG3\\SQLEXPRESS"  
database_name = "лаба2_Әділ"                 # база Поликлиника

# ----------------------------
# Подключение к базе
# ----------------------------
def connect_to_db(server, database):
    try:
        conn = pyodbc.connect(
            f"Driver={{ODBC Driver 17 for SQL Server}};"
            f"Server={server};"
            f"Database={database};"
            f"Trusted_Connection=yes;"
        )
        print(f"Подключение к базе '{database}' успешно!")
        return conn
    except pyodbc.Error as e:
        messagebox.showerror("Ошибка подключения", str(e))
        sys.exit(1)

conn = connect_to_db(server_name, database_name)
cursor = conn.cursor()

# ----------------------------
# Главное окно
# ----------------------------
root = tk.Tk()
root.title(f"Приложение для базы '{database_name}'")
root.geometry("1200x700")

# ----------------------------
# Открытие таблицы
# ----------------------------
def open_table(table_name):
    win = tk.Toplevel(root)
    win.title(table_name)
    win.geometry("1100x600")
    
    tree = ttk.Treeview(win)
    tree.pack(expand=True, fill='both')
    
    def refresh_data():
        for i in tree.get_children():
            tree.delete(i)
        try:
            cursor.execute(f"SELECT * FROM [dbo].[{table_name}]")
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            
            tree["columns"] = columns
            tree["show"] = "headings"
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)
            
            for row in rows:
                tree.insert("", tk.END, values=[str(x) if x is not None else "" for x in row])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить данные из {table_name}:\n{e}")
            win.destroy()
            return

    refresh_data()

    # ----------------------------
    # CRUD функции
    # ----------------------------
    def add_record():
        columns = tree["columns"]
        new_values = []
        for col in columns:
            val = simpledialog.askstring("Ввод", f"Введите значение для {col}:")
            if val is None:
                return
            new_values.append(val)
        placeholders = ",".join("?" for _ in columns)
        try:
            cursor.execute(f"INSERT INTO [dbo].[{table_name}] ({','.join(columns)}) VALUES ({placeholders})", new_values)
            conn.commit()
            refresh_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить запись:\n{e}")

    def delete_record():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите запись для удаления")
            return
        values = tree.item(selected_item)["values"]
        pk_col = tree["columns"][0]
        pk_value = values[0]
        try:
            cursor.execute(f"DELETE FROM [dbo].[{table_name}] WHERE [{pk_col}] = ?", (pk_value,))
            conn.commit()
            refresh_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить запись:\n{e}")

    def update_record():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите запись для изменения")
            return
        values = tree.item(selected_item)["values"]
        updated_values = []
        columns = tree["columns"]
        for i, col in enumerate(columns):
            val = simpledialog.askstring("Изменить", f"{col} (текущее: {values[i]}):", initialvalue=values[i])
            if val is None:
                return
            updated_values.append(val)
        set_clause = ", ".join(f"[{col}]=?" for col in columns[1:])
        try:
            cursor.execute(f"UPDATE [dbo].[{table_name}] SET {set_clause} WHERE [{columns[0]}] = ?", (*updated_values[1:], updated_values[0]))
            conn.commit()
            refresh_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось изменить запись:\n{e}")

    def export_excel():
        try:
            cursor.execute(f"SELECT * FROM [dbo].[{table_name}]")
            rows = cursor.fetchall()
            df = pd.DataFrame.from_records(rows, columns=[col[0] for col in cursor.description])
            df.to_excel(f"{table_name}.xlsx", index=False)
            messagebox.showinfo("Экспорт", f"Данные таблицы {table_name} экспортированы в {table_name}.xlsx")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные:\n{e}")

    # ----------------------------
    # Кнопки CRUD
    # ----------------------------
    btn_frame = tk.Frame(win)
    btn_frame.pack(fill='x', pady=5)
    
    tk.Button(btn_frame, text="Добавить", command=add_record).pack(side='left', padx=5, pady=5)
    tk.Button(btn_frame, text="Изменить", command=update_record).pack(side='left', padx=5, pady=5)
    tk.Button(btn_frame, text="Удалить", command=delete_record).pack(side='left', padx=5, pady=5)
    tk.Button(btn_frame, text="Экспорт в Excel", command=export_excel).pack(side='left', padx=5, pady=5)

# ----------------------------
# SQL-запросы
# ----------------------------
def open_query_window():
    win = tk.Toplevel(root)
    win.title("Выполнение SQL-запроса")
    win.geometry("1100x600")
    
    txt_query = tk.Text(win, height=5)
    txt_query.pack(fill='x', padx=5, pady=5)
    
    tree = ttk.Treeview(win)
    tree.pack(expand=True, fill='both')
    
    def execute_query():
        query = txt_query.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("Ошибка", "Введите SQL-запрос")
            return
        try:
            cursor.execute(query)
            if query.lower().startswith("select"):
                rows = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                tree.delete(*tree.get_children())
                tree["columns"] = columns
                tree["show"] = "headings"
                for col in columns:
                    tree.heading(col, text=col)
                    tree.column(col, width=120)
                for row in rows:
                    tree.insert("", tk.END, values=[str(x) if x is not None else "" for x in row])
            else:
                conn.commit()
                messagebox.showinfo("Выполнено", "Запрос выполнен успешно")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить запрос:\n{e}")
    
    def export_query_result():
        try:
            query = txt_query.get("1.0", tk.END).strip()
            if not query.lower().startswith("select"):
                messagebox.showwarning("Ошибка", "Экспорт возможен только для SELECT")
                return
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            df = pd.DataFrame.from_records(rows, columns=columns)
            df.to_excel("query_result.xlsx", index=False)
            messagebox.showinfo("Экспорт", "Результат запроса экспортирован в query_result.xlsx")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать результат:\n{e}")
    
    btn_frame = tk.Frame(win)
    btn_frame.pack(fill='x', pady=5)
    tk.Button(btn_frame, text="Выполнить", command=execute_query).pack(side='left', padx=5)
    tk.Button(btn_frame, text="Экспорт в Excel", command=export_query_result).pack(side='left', padx=5)

# ----------------------------
# Справка
# ----------------------------
def show_help():
    messagebox.showinfo("Справка", 
        "Главное меню содержит таблицы и пункт SQL-запросы.\n"
        "Выберите таблицу для просмотра и редактирования данных.\n"
        "В окне таблицы доступны кнопки Добавить, Изменить, Удалить и Экспорт.\n"
        "В пункте SQL-запросы можно выполнять SELECT/INSERT/UPDATE/DELETE и экспортировать результат."
    )

# ----------------------------
# Главное меню
# ----------------------------
menubar = tk.Menu(root)

tables_menu = tk.Menu(menubar, tearoff=0)
table_names = [
    "Пациенты", 
    "Врачи", 
    "Категории_врачей", 
    "Расписание",
    "Оплата", 
    "Тарифы", 
    "Занятость_врача", 
    "Амбулаторная_карта",
    "Лекарства_склад", 
    "Назначения"
]

for t in table_names:
    tables_menu.add_command(label=t, command=lambda table=t: open_table(table))

menubar.add_cascade(label="Таблицы", menu=tables_menu)
menubar.add_command(label="SQL-запросы", command=open_query_window)
menubar.add_command(label="Справка", command=show_help)

root.config(menu=menubar)
root.mainloop()
