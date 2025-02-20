from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget
import sqlite3
from chapter_page import ChapterPage

class NovelPage(QWidget):
    def __init__(self, novel_id):
        super().__init__()
        self.novel_id = novel_id
        self.setWindowTitle("Описание новеллы")
        self.setGeometry(100, 100, 800, 600)
        self.layout = QVBoxLayout()

        self.title_label = QLabel()
        self.layout.addWidget(self.title_label)

        self.chapter_list = QListWidget()
        self.chapter_list.itemClicked.connect(self.open_chapter)
        self.layout.addWidget(self.chapter_list)

        self.load_novel()
        self.setLayout(self.layout)

    def load_novel(self):
        conn = sqlite3.connect("novels.db")
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM novels WHERE id = ?", (self.novel_id,))
        novel = cursor.fetchone()
        self.title_label.setText(novel[0])

        cursor.execute("SELECT id, title FROM chapters WHERE novel_id = ?", (self.novel_id,))
        chapters = cursor.fetchall()
        conn.close()

        for chapter in chapters:
            self.chapter_list.addItem(f"Глава {chapter[0]}: {chapter[1]}")

    def open_chapter(self, item):
        chapter_id = self.chapter_list.row(item) + 1
        self.chapter_page = ChapterPage(self.novel_id, chapter_id)
        self.chapter_page.show()
        self.close()
