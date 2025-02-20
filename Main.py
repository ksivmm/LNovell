import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import sqlite3
import io

class NovelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Novel Catalog")
        self.create_db()
        self.create_main_page()

    def create_db(self):
        """Создаёт базу данных, если она отсутствует"""
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
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS chapters (
                id INTEGER PRIMARY KEY,
                novel_id INTEGER,
                title TEXT,
                content TEXT,
                FOREIGN KEY (novel_id) REFERENCES novels (id)
            )
        """)
        self.conn.commit()

    def create_main_page(self):
        """Создаёт главную страницу каталога"""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        ttk.Label(self.main_frame, text="Catalog of Novels").pack(pady=10)

        self.novel_frame = ttk.Frame(self.main_frame)
        self.novel_frame.pack(fill="both", expand=True)

        self.load_novels()

        ttk.Button(self.main_frame, text="Add Novel", command=self.open_add_novel_page).pack(pady=10)

    def load_novels(self):
        """Загружает список новелл с обложками"""
        for widget in self.novel_frame.winfo_children():
            widget.destroy()

        self.cursor.execute("SELECT id, title, cover FROM novels")
        row_num, col_num = 0, 0

        for novel_id, title, cover_data in self.cursor.fetchall():
            # Обрабатываем обложку
            if cover_data:
                image = Image.open(io.BytesIO(cover_data))
                image = image.resize((161, 225))
                novel_cover = ImageTk.PhotoImage(image)
            else:
                novel_cover = ImageTk.PhotoImage(Image.new("RGB", (161, 225), "gray"))

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
        """Открывает страницу новеллы"""
        self.main_frame.pack_forget()
        self.novel_frame = ttk.Frame(self.root)
        self.novel_frame.pack(fill="both", expand=True)

        self.cursor.execute("SELECT title, cover, description FROM novels WHERE id=?", (novel_id,))
        title, cover_data, description = self.cursor.fetchone()

        if cover_data:
            image = Image.open(io.BytesIO(cover_data))
            image = image.resize((161, 225))
            novel_cover = ImageTk.PhotoImage(image)
        else:
            novel_cover = ImageTk.PhotoImage(Image.new("RGB", (161, 225), "gray"))

        ttk.Label(self.novel_frame, image=novel_cover).pack(pady=10)
        ttk.Label(self.novel_frame, text=description).pack(pady=10)

        self.chapter_list = ttk.Treeview(self.novel_frame, columns=("Title"), show="headings")
        self.chapter_list.heading("Title", text="Title")
        self.chapter_list.pack(fill="both", expand=True)
        self.chapter_list.bind("<Double-1>", self.open_chapter_page)

        self.cursor.execute("SELECT title FROM chapters WHERE novel_id=?", (novel_id,))
        for (chapter_title,) in self.cursor.fetchall():
            self.chapter_list.insert("", "end", values=(chapter_title,))

        ttk.Button(self.novel_frame, text="Add Chapter", command=lambda: self.open_add_chapter_page(novel_id)).pack(pady=10)
        ttk.Button(self.novel_frame, text="Back", command=self.back_to_main).pack(pady=10)

    def open_add_novel_page(self):
        """Открывает страницу добавления новеллы"""
        self.main_frame.pack_forget()
        self.add_novel_frame = ttk.Frame(self.root)
        self.add_novel_frame.pack(fill="both", expand=True)

        ttk.Label(self.add_novel_frame, text="Title:").pack(pady=5)
        self.novel_title_entry = ttk.Entry(self.add_novel_frame)
        self.novel_title_entry.pack(pady=5)

        ttk.Label(self.add_novel_frame, text="Cover:").pack(pady=5)
        ttk.Button(self.add_novel_frame, text="Upload Cover", command=self.upload_cover).pack(pady=5)

        ttk.Label(self.add_novel_frame, text="Description:").pack(pady=5)
        self.novel_description_entry = ttk.Entry(self.add_novel_frame)
        self.novel_description_entry.pack(pady=5)

        ttk.Button(self.add_novel_frame, text="Add Novel", command=self.add_novel).pack(pady=10)
        ttk.Button(self.add_novel_frame, text="Back", command=self.back_to_main_from_add).pack(pady=10)

        self.cover_data = None

    def upload_cover(self):
        """Загружает обложку и сохраняет её в переменную"""
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, "rb") as file:
                self.cover_data = file.read()

    def add_novel(self):
        """Добавляет новеллу в базу данных"""
        title = self.novel_title_entry.get()
        description = self.novel_description_entry.get()
        self.cursor.execute("INSERT INTO novels (title, cover, description) VALUES (?, ?, ?)", (title, self.cover_data, description))
        self.conn.commit()
        self.back_to_main_from_add()

    def back_to_main_from_add(self):
        """Возвращает на главную страницу после добавления новеллы"""
        self.add_novel_frame.pack_forget()
        self.create_main_page()

    def open_chapter_page(self, event):
        """Открывает страницу главы (пока не реализовано)"""
        messagebox.showinfo("Navigation", "This functionality is not implemented yet.")

    def open_add_chapter_page(self, novel_id):
        """Добавление главы (упрощённое)"""
        messagebox.showinfo("Feature", "Adding chapters will be implemented later.")

    def back_to_main(self):
        """Возвращает на главную страницу"""
        self.novel_frame.pack_forget()
        self.create_main_page()

if __name__ == "__main__":
    root = tk.Tk()
    app = NovelApp(root)
    root.mainloop()
