import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMessageBox
from table_form import TableForm
from query_form import QueryForm

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Оптика — Клиентское приложение")
        self.setGeometry(200, 200, 900, 600)

        menubar = self.menuBar()

        # Меню таблиц
        tables_menu = menubar.addMenu("Таблицы")
        tables = {
            "Оправы": "Оправы",
            "Линзы": "Линзы",
            "Услуги": "Услуги",
            "Приемщики": "Приемщики",
            "Работники": "Работники",
            "Заказы": "Заказы",
            "Заказ оправы": "Заказ_оправы",
            "Заказ линзы": "Заказ_линзы",
            "Заказ услуги": "Заказ_услуги",
            "Касса заказа": "Касса_заказ"
        }
        for name, table in tables.items():
            action = QAction(name, self)
            action.triggered.connect(lambda checked, t=table: self.open_table(t))
            tables_menu.addAction(action)

        # Меню запросов
        query_menu = menubar.addMenu("Запросы")
        run_query_action = QAction("Выполнить запрос", self)
        run_query_action.triggered.connect(self.open_query_window)
        query_menu.addAction(run_query_action)

        # Меню справки
        help_menu = menubar.addMenu("Справка")
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def open_table(self, table_name):
        self.tf = TableForm(table_name)
        self.tf.show()

    def open_query_window(self):
        self.qf = QueryForm()
        self.qf.show()

    def show_about(self):
        QMessageBox.information(self, "О программе",
                                "Клиентское приложение к базе данных 'Оптика'\n"
                                "Ввод, редактирование, просмотр таблиц\n"
                                "Выполнение запросов\n"
                                "Формирование отчетов")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
