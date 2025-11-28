import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import openpyxl

# --- Подключение к MS SQL Server ---
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;'
    'DATABASE=test;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()

# --- Получение первичных ключей таблицы ---
def get_primary_key(table_name):
    cursor.execute(f"""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE OBJECTPROPERTY(
            OBJECT_ID(CONSTRAINT_SCHEMA + '.' + QUOTENAME(CONSTRAINT_NAME)), 'IsPrimaryKey') = 1
          AND TABLE_NAME='{table_name}'
    """)
    return [row[0] for row in cursor.fetchall()]

# --- Универсальное приведение типов и очистка значений ---
def convert_value(val, col_type):
    if isinstance(val, tuple) or isinstance(val, str):
        val = str(val).strip("()'\" ")
    if val == "":
        return None
    try:
        if col_type in ("int","bigint","smallint","tinyint"): return int(val)
        elif col_type in ("decimal","numeric","float","real"): return float(val)
    except ValueError:
        return val
    return val

# --- Отображение таблицы с CRUD ---
def show_table(frame, table_name):
    for w in frame.winfo_children():
        w.destroy()

    tree = ttk.Treeview(frame)
    tree.pack(fill=tk.BOTH, expand=True)

    # Колонки
    cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{table_name}'")
    columns = [row[0] for row in cursor.fetchall()]
    tree["columns"] = columns
    tree["show"] = "headings"
    for col in columns:
        tree.heading(col, text=col)

    # Данные
    cursor.execute(f"SELECT * FROM {table_name}")
    for row in cursor.fetchall():
        clean_row = [convert_value(v, 'str') for v in row]  # отображаем красиво
        tree.insert("", tk.END, values=clean_row)

    pk_cols = get_primary_key(table_name)

    # Типы колонок
    cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{table_name}'")
    column_types = {r[0]: r[1].lower() for r in cursor.fetchall()}

    # --- CRUD функции ---
    def add_record():
        values = []
        for col in columns[1:]:
            val = simpledialog.askstring("Добавить", f"{col}:")
            if val is None: return
            values.append(convert_value(val, column_types[col]))
        cursor.execute(f"INSERT INTO {table_name} ({', '.join(columns[1:])}) VALUES ({','.join(['?']*len(values))})", values)
        conn.commit()
        show_table(frame, table_name)

    def delete_record():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Удаление", "Выберите запись")
            return
        item = tree.item(sel[0])
        pk_values = [convert_value(item['values'][columns.index(col)], column_types[col]) for col in pk_cols]
        where_clause = " AND ".join([f"{c}=?" for c in pk_cols])
        try:
            cursor.execute(f"DELETE FROM {table_name} WHERE {where_clause}", tuple(pk_values))
            conn.commit()
            show_table(frame, table_name)
        except Exception as e:
            messagebox.showerror("Ошибка удаления", str(e))

    def edit_record():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Редактирование", "Выберите запись")
            return
        item = tree.item(sel[0])

        # Определяем столбцы, которые можно редактировать (исключаем IDENTITY)
        cursor.execute(f"""
            SELECT COLUMN_NAME, COLUMNPROPERTY(OBJECT_ID(TABLE_SCHEMA + '.' + TABLE_NAME), COLUMN_NAME, 'IsIdentity') AS IsIdentity
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME='{table_name}'
        """)
        column_identity = {row[0]: row[1] for row in cursor.fetchall()}
        
        editable_columns = [c for c in columns if column_identity.get(c) != 1]  # только не-IDENTITY

        new_values = []
        for col in columns:
            if col in editable_columns:
                val = simpledialog.askstring("Редактировать", f"{col}:", initialvalue=item["values"][columns.index(col)])
                if val is None: return
                new_values.append(convert_value(val, column_types[col]))
            else:
                # оставляем прежнее значение для IDENTITY
                new_values.append(item["values"][columns.index(col)])

        pk_values = [convert_value(item['values'][columns.index(col)], column_types[col]) for col in pk_cols]

        set_clause = ", ".join([f"{c}=?" for c in editable_columns])
        where_clause = " AND ".join([f"{c}=?" for c in pk_cols])

        try:
            cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}",
                           (*[new_values[columns.index(c)] for c in editable_columns], *pk_values))
            conn.commit()
            show_table(frame, table_name)
        except Exception as e:
            messagebox.showerror("Ошибка редактирования", str(e))


    def export_excel():
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel","*.xlsx")])
        if not path: return
        cursor.execute(f"SELECT * FROM {table_name}")
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = table_name
        ws.append(columns)
        for row in cursor.fetchall():
            ws.append([convert_value(v, 'str') for v in row])
        wb.save(path)
        messagebox.showinfo("Отчет", f"Сохранено: {path}")

    # Кнопки
    btn_frame = tk.Frame(frame)
    btn_frame.pack(fill=tk.X, pady=5)
    for txt, cmd in [("Добавить", add_record), ("Редактировать", edit_record), ("Удалить", delete_record)]:
        ttk.Button(btn_frame, text=txt, command=cmd).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Экспорт в Excel", command=export_excel).pack(side=tk.RIGHT, padx=5)

# --- Основное окно ---
root = tk.Tk()
root.title("Подсистема Почта")
root.geometry("900x500")

tab_control = ttk.Notebook(root)
frames = {}

for table in ["Страны","Язык_издания","Тип_издания"]:
    frame = ttk.Frame(tab_control)
    tab_control.add(frame, text=table)
    frames[table] = frame
    show_table(frame, table)

tab_control.pack(expand=1, fill="both")

# --- Меню ---
menubar = tk.Menu(root)
root.config(menu=menubar)

def run_query():
    q = simpledialog.askstring("SQL", "Введите SQL:")
    if not q: return
    try:
        cursor.execute(q)
        if q.strip().lower().startswith("select"):
            win = tk.Toplevel(root)
            win.title("Результат")
            txt = tk.Text(win)
            txt.pack(fill=tk.BOTH, expand=True)
            for r in cursor.fetchall(): txt.insert(tk.END, str(r)+"\n")
        else:
            conn.commit()
            messagebox.showinfo("Успех", "Запрос выполнен")
            for t,f in frames.items(): show_table(f,t)
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

queries_menu = tk.Menu(menubar, tearoff=0)
queries_menu.add_command(label="Выполнить SQL", command=run_query)
menubar.add_cascade(label="Запросы", menu=queries_menu)

def show_help():
    win = tk.Toplevel(root)
    win.title("Справка")
    txt = tk.Text(win, wrap=tk.WORD)
    txt.pack(fill=tk.BOTH, expand=True)
    txt.insert(tk.END,
               "Приложение Подсистема Почта\n\n"
               "CRUD:\n- Добавить: Добавление записи\n- Редактировать: Редактирование\n"
               "- Удалить: Удаление\n- Экспорт в Excel: Сохранение таблицы\n\n"
               "SQL: Выполнение произвольных запросов\nСправка: Эта информация")
    txt.config(state=tk.DISABLED)

help_menu = tk.Menu(menubar, tearoff=0)
help_menu.add_command(label="Справка", command=show_help)
menubar.add_cascade(label="Справка", menu=help_menu)

root.mainloop()
