from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QTableView, QMessageBox
from PyQt5.QtCore import QAbstractTableModel, Qt
import pandas as pd
from db import execute_query

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

    def update(self, df):
        self.beginResetModel()
        self._df = df.copy()
        self.endResetModel()

class QueryForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Выполнение SQL SELECT запроса")
        self.resize(800, 600)

        layout = QVBoxLayout()

        self.query_text = QTextEdit()
        self.query_text.setPlaceholderText("Введите SQL SELECT запрос...")
        layout.addWidget(self.query_text)

        self.run_btn = QPushButton("Выполнить")
        self.run_btn.clicked.connect(self.run_query)
        layout.addWidget(self.run_btn)

        self.view = QTableView()
        layout.addWidget(self.view)

        self.setLayout(layout)

    def run_query(self):
        sql = self.query_text.toPlainText().strip()
        if not sql.lower().startswith("select"):
            QMessageBox.warning(self, "Ошибка", "Можно выполнять только SELECT-запросы!")
            return
        try:
            df = execute_query(sql)
            self.model = PandasModel(df)
            self.view.setModel(self.model)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
