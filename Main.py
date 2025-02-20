from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QGridLayout, QScrollArea
from PyQt5.QtGui import QPixmap
import sys
import sqlite3
import io

class NovelApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Каталог новелл")
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.setGeometry(100, 100, 800, 600)

        self.create_db()
        self.create_main_page()

    def create_db(self):
        """Создает базу данных, если её нет"""
        self.conn = sqlite3.connect("novels.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS novels (
                id INTEGER PRIMARY KEY,
                title TEXT,
                cover BLOB,
                description TEXT
            )
        """)
        self.conn.commit()

    def create_main_page(self):
        """Создает главную страницу"""
        layout = QVBoxLayout(self)

        # Прокручиваемая область
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        content_widget = QWidget()
        grid = QGridLayout(content_widget)

        self.cursor.execute("SELECT id, title, cover FROM novels")
        novels = self.cursor.fetchall()

        col_count = 4  # Количество колонок
        row, col = 0, 0

        for novel_id, title, cover_data in novels:
            cover_label = QLabel()
            if cover_data:
                pixmap = QPixmap()
                pixmap.loadFromData(cover_data)
                pixmap = pixmap.scaled(161, 225)
            else:
                pixmap = QPixmap(161, 225)
                pixmap.fill("gray")

            cover_label.setPixmap(pixmap)
            cover_label.mousePressEvent = lambda event, novel_id=novel_id: self.open_novel_page(novel_id)

            title_label = QLabel(title)
            title_label.setStyleSheet("color: white; font-size: 12px;")
            title_label.setWordWrap(True)

            grid.addWidget(cover_label, row, col)
            grid.addWidget(title_label, row + 1, col)

            col += 1
            if col >= col_count:
                col = 0
                row += 2

        content_widget.setLayout(grid)
        scroll.setWidget(content_widget)

        layout.addWidget(scroll)
        self.setLayout(layout)

    def open_novel_page(self, novel_id):
        """Открывает страницу новеллы"""
        self.cursor.execute("SELECT title, description FROM novels WHERE id=?", (novel_id,))
        novel = self.cursor.fetchone()

        if novel:
            self.setWindowTitle(novel[0])
            self.setStyleSheet("background-color: #1e1e1e; color: white;")

            for i in reversed(range(self.layout().count())):
                self.layout().itemAt(i).widget().deleteLater()

            title_label = QLabel(novel[0])
            title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

            description_label = QLabel(novel[1])
            description_label.setWordWrap(True)

            back_button = QPushButton("Назад")
            back_button.setStyleSheet("background-color: #333; color: white; padding: 5px;")
            back_button.clicked.connect(self.create_main_page)

            layout = self.layout()
            layout.addWidget(title_label)
            layout.addWidget(description_label)
            layout.addWidget(back_button)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NovelApp()
    window.show()
    sys.exit(app.exec_())
