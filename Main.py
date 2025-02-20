import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import PhotoImage
import sqlite3

class NovelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Novel Catalog")
        self.create_db()
        self.create_main_page()

    def create_db(self):
        self.conn = sqlite3.connect("novels.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS novels (
                id INTEGER PRIMARY KEY,
                title TEXT,
                cover TEXT,
                description TEXT
            )
        """)
        self.conn.commit()

    def create_main_page(self):
        """Главная страница с каталогом новелл"""
        if hasattr(self, 'current_frame'):
            self.current_frame.pack_forget()

        self.current_frame = ttk.Frame(self.root)
        self.current_frame.pack(fill="both", expand=True)

        ttk.Label(self.current_frame, text="Catalog of Novels").pack(pady=10)

        self.novel_frame = ttk.Frame(self.current_frame)
        self.novel_frame.pack(fill="both", expand=True)

        self.load_novels()

        ttk.Button(self.current_frame, text="Add Novel", command=self.open_add_novel_page).pack(pady=10)

    def load_novels(self):
        """Загрузка списка новелл из БД"""
        for widget in self.novel_frame.winfo_children():
            widget.destroy()

        self.cursor.execute("SELECT id, title, cover FROM novels")
        row_num, col_num = 0, 0
        for novel_id, title, cover_path in self.cursor.fetchall():
            try:
                novel_cover = PhotoImage(file=cover_path).subsample(4, 4)
            except:
                novel_cover = PhotoImage()  # Заглушка, если изображения нет

            cover_label = ttk.Label(self.novel_frame, image=novel_cover)
            cover_label.image = novel_cover
            cover_label.grid(row=row_num, column=col_num, padx=5, pady=5)
            cover_label.bind("<Button-1>", lambda e, id=novel_id: self.open_novel_page(id))

            ttk.Label(self.novel_frame, text=title, width=20, anchor="center").grid(row=row_num+1, column=col_num, padx=5, pady=5)

            col_num += 1
            if col_num == 7:
                col_num = 0
                row_num += 2

    def open_novel_page(self, novel_id):
        """Открытие страницы новеллы"""
        self.current_frame.pack_forget()
        self.current_frame = ttk.Frame(self.root)
        self.current_frame.pack(fill="both", expand=True)

        self.cursor.execute("SELECT title, cover, description FROM novels WHERE id=?", (novel_id,))
        novel = self.cursor.fetchone()

        if not novel:
            messagebox.showerror("Error", "Novel not found")
            self.create_main_page()
            return

        title, cover_path, description = novel

        ttk.Label(self.current_frame, text=title, font=("Arial", 16)).pack(pady=10)

        try:
            novel_cover = PhotoImage(file=cover_path).subsample(4, 4)
        except:
            novel_cover = PhotoImage()  # Заглушка, если изображения нет

        cover_label = ttk.Label(self.current_frame, image=novel_cover)
        cover_label.image = novel_cover
        cover_label.pack()

        ttk.Label(self.current_frame, text=description, wraplength=400).pack(pady=10)

        ttk.Button(self.current_frame, text="Back", command=self.create_main_page).pack(pady=10)

    def open_add_novel_page(self):
        """Страница добавления новеллы"""
        self.current_frame.pack_forget()
        self.current_frame = ttk.Frame(self.root)
        self.current_frame.pack(fill="both", expand=True)

        ttk.Label(self.current_frame, text="Title:").pack(pady=5)
        self.novel_title_entry = ttk.Entry(self.current_frame)
        self.novel_title_entry.pack(pady=5)

        ttk.Label(self.current_frame, text="Cover Path:").pack(pady=5)
        self.novel_cover_entry = ttk.Entry(self.current_frame)
        self.novel_cover_entry.pack(pady=5)

        ttk.Label(self.current_frame, text="Description:").pack(pady=5)
        self.novel_description_entry = ttk.Entry(self.current_frame)
        self.novel_description_entry.pack(pady=5)

        ttk.Button(self.current_frame, text="Add Novel", command=self.add_novel).pack(pady=10)
        ttk.Button(self.current_frame, text="Back", command=self.create_main_page).pack(pady=10)

    def add_novel(self):
        """Добавление новеллы в БД"""
        title = self.novel_title_entry.get()
        cover = self.novel_cover_entry.get()
        description = self.novel_description_entry.get()

        if not title or not description:
            messagebox.showerror("Error", "Title and description are required")
            return

        self.cursor.execute("INSERT INTO novels (title, cover, description) VALUES (?, ?, ?)", (title, cover, description))
        self.conn.commit()
        self.create_main_page()
        self.load_novels()

if __name__ == "__main__":
    root = tk.Tk()
    app = NovelApp(root)
    root.mainloop()
