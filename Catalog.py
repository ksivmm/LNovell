import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget
from PyQt5.QtGui import QPixmap
import sqlite3
import io
from novel_page import NovelPage

class MainPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Каталог новелл")
        self.setGeometry(100, 100, 800, 600)
        self.layout = QVBoxLayout()

        self.novel_list = QListWidget()
        self.novel_list.itemClicked.connect(self.open_novel_page)
        self.layout.addWidget(self.novel_list)

        self.load_novels()

        self.setLayout(self.layout)

    def load_novels(self):
        conn = sqlite3.connect("novels.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, cover FROM novels")
        novels = cursor.fetchall()
        conn.close()

        for novel in novels:
            item_text = f"{novel[1]}"
            self.novel_list.addItem(item_text)

    def open_novel_page(self, item):
        novel_id = self.novel_list.row(item) + 1
        self.novel_page = NovelPage(novel_id)
        self.novel_page.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_page = MainPage()
    main_page.show()
    sys.exit(app.exec_())
