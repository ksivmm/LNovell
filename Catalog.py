import sys
import io
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QListWidget, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

DB_PATH = "novels.db"

class NovelApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LN Reader")
        self.setGeometry(100, 100, 800, 600)

        self.initUI()

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.novel_list = QListWidget()
        self.layout.addWidget(self.novel_list)

        self.load_novels()

        self.novel_list.itemClicked.connect(self.open_novel_page)

    def load_novels(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, cover FROM novels")
        novels = cursor.fetchall()
        conn.close()

        for novel in novels:
            novel_id, title, cover_data = novel
            item = QLabel(title)
            
            if cover_data:
                image = QPixmap()
                image.loadFromData(cover_data)
                cover_label = QLabel()
                cover_label.setPixmap(image.scaled(100, 150, Qt.KeepAspectRatio))
                self.layout.addWidget(cover_label)
            
            self.novel_list.addItem(title)

    def open_novel_page(self, item):
        novel_title = item.text()
        self.novel_page = NovelPage(novel_title)
        self.novel_page.show()

class NovelPage(QWidget):
    def __init__(self, novel_title):
        super().__init__()
        self.setWindowTitle(novel_title)
        self.setGeometry(150, 150, 600, 400)

        layout = QVBoxLayout(self)
        self.label = QLabel(f"Открыта новелла: {novel_title}")
        layout.addWidget(self.label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NovelApp()
    window.show()
    sys.exit(app.exec_())
