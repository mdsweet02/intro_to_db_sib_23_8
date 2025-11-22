from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableView, QMessageBox
from PyQt5.QtCore import QAbstractTableModel, Qt
import pandas as pd
from db import get_table, insert_row, update_row, delete_row, PK_MAP

class PandasModel(QAbstractTableModel):
    def __init__(self, df=pd.DataFrame()):
        super().__init__()
        self._df = df.copy()

    def rowCount(self, parent=None):
        return len(self._df)

    def columnCount(self, parent=None):
        return len(self._df.columns)

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role in (Qt.DisplayRole, Qt.EditRole):
            return str(self._df.iat[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._df.columns[section])
            else:
                return str(self._df.index[section])
        return None

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            self._df.iat[index.row(), index.column()] = value
            return True
        return False

    def get_dataframe(self):
        return self._df

    def update(self, df):
        self.beginResetModel()
        self._df = df.copy()
        self.endResetModel()

class TableForm(QWidget):
    def __init__(self, table_name):
        super().__init__()
        self.setWindowTitle(f"Таблица: {table_name}")
        self.resize(900, 600)
        self.table_name = table_name
        self.df = pd.DataFrame()

        layout = QVBoxLayout()

        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self.load_data)
        layout.addWidget(self.refresh_btn)

        self.add_btn = QPushButton("Добавить запись")
        self.add_btn.clicked.connect(self.add_row)
        layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Удалить запись")
        self.delete_btn.clicked.connect(self.delete_row)
        layout.addWidget(self.delete_btn)

        self.save_btn = QPushButton("Сохранить изменения")
        self.save_btn.clicked.connect(self.save_changes)
        layout.addWidget(self.save_btn)

        self.view = QTableView()
        layout.addWidget(self.view)
        self.setLayout(layout)

        self.load_data()

    def load_data(self):
        try:
            self.df = get_table(self.table_name)
            self.model = PandasModel(self.df)
            self.view.setModel(self.model)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_row(self):
        empty_row = {col: "" for col in self.df.columns}
        try:
            insert_row(self.table_name, list(empty_row.keys()), list(empty_row.values()))
            self.load_data()
            QMessageBox.information(self, "Добавление", "Добавлена пустая запись. Отредактируйте и нажмите 'Сохранить изменения'.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить запись:\n{e}")

    def delete_row(self):
        indexes = self.view.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.warning(self, "Удаление", "Выберите хотя бы одну строку")
            return
        confirm = QMessageBox.question(self, "Удаление", f"Удалить {len(indexes)} выбранные строки?", QMessageBox.Yes | QMessageBox.No)
        if confirm != QMessageBox.Yes:
            return
        pk_cols = PK_MAP.get(self.table_name)
        if pk_cols is None:
            QMessageBox.warning(self, "Ошибка", f"PK не найдены для '{self.table_name}'")
            return
        try:
            for idx in indexes:
                row_data = self.model.get_dataframe().iloc[idx.row()]
                pk_values = [row_data[col] for col in pk_cols]
                delete_row(self.table_name, pk_cols if len(pk_cols)>1 else pk_cols[0],
                           pk_values if len(pk_values)>1 else pk_values[0])
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def save_changes(self):
        df_new = self.model.get_dataframe()
        pk_cols = PK_MAP.get(self.table_name)
        if pk_cols is None:
            QMessageBox.warning(self, "Ошибка", f"PK не найдены для '{self.table_name}'")
            return
        try:
            for i in range(len(df_new)):
                row_new = df_new.iloc[i]
                pk_values = [row_new[col] for col in pk_cols]
                update_cols = [col for col in df_new.columns if col not in pk_cols]
                update_values = [row_new[col] for col in update_cols]
                if update_cols:
                    update_row(self.table_name, pk_cols if len(pk_cols)>1 else pk_cols[0],
                               pk_values if len(pk_values)>1 else pk_values[0],
                               update_cols, update_values)
            QMessageBox.information(self, "Сохранение", "Изменения сохранены")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
