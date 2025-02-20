from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget
import sqlite3

class ContinueReadingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Продолжить читать")
        self.setGeometry(100, 100, 800, 600)
        self.layout = QVBoxLayout()

        self.reading_list = QListWidget()
        self.layout.addWidget(self.reading_list)

        self.load_reading_history()
        self.setLayout(self.layout)

    def load_reading_history(self):
        conn = sqlite3.connect("novels.db")
        cursor = conn.cursor()
        cursor.execute("SELECT novel_id, chapter_id FROM reading_history ORDER BY timestamp DESC LIMIT 10")
        history = cursor.fetchall()
        conn.close()

        for entry in history:
            self.reading_list.addItem(f"Новелла {entry[0]}, Глава {entry[1]}")
