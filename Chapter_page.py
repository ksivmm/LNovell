from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
import sqlite3
from continue_reading import ContinueReadingPage

class ChapterPage(QWidget):
    def __init__(self, novel_id, chapter_id):
        super().__init__()
        self.novel_id = novel_id
        self.chapter_id = chapter_id
        self.setWindowTitle("Чтение главы")
        self.setGeometry(100, 100, 800, 600)
        self.layout = QVBoxLayout()

        self.text_label = QLabel()
        self.layout.addWidget(self.text_label)

        self.load_chapter()
        self.setLayout(self.layout)

    def load_chapter(self):
        conn = sqlite3.connect("novels.db")
        cursor = conn.cursor()
        cursor.execute("SELECT text FROM chapters WHERE id = ? AND novel_id = ?", (self.chapter_id, self.novel_id))
        chapter = cursor.fetchone()
        conn.close()

        self.text_label.setText(chapter[0])
